"""Import saved LifeGuard-RL results into a project-local MLflow store."""

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time

from mlflow.entities import Metric, Param
from mlflow.tracking import MlflowClient

from .reports import ROOT, Report, Run, experiments

ARCHIVED = "imported_saved_results"
EXECUTION = "notebook_execution"
DEFAULT_STORE = ROOT / ".mlflow"


def store_settings(root):
    root = Path(root).expanduser().resolve()
    return root, "sqlite:///" + (root / "mlflow.db").as_posix(), (root / "artifacts").as_uri()


def local_client(root=DEFAULT_STORE):
    root, database, _ = store_settings(root)
    root.mkdir(parents=True, exist_ok=True)
    return MlflowClient(tracking_uri=database)


def text(value):
    return value if isinstance(value, str) else json.dumps(value, sort_keys=True)


def parse_identity(program, run):
    return sha256((program + "\0" + run.key).encode()).hexdigest()


def experiment_id(client, study, artifact_root):
    found = client.get_experiment_by_name(study.name)
    if found is not None:
        return found.experiment_id
    fragment = study.title.lower().replace(" ", "-")
    return client.create_experiment(study.name, artifact_location=f"{artifact_root}/{fragment}",
                                    tags={"project": "LifeGuard-RL", "dataset": study.dataset})


def write_overview(study, directory):
    plots = directory / "plots"
    plots.mkdir()
    study.plotter(plots)
    sources = []
    for report, name in study.files:
        contents = report.read(name)
        rel = Path("sources") / f"notebook-{report.notebook:02d}" / name
        dest = directory / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(contents)
        sources.append({"notebook": report.notebook, "artifact": rel.as_posix(),
                        "sha256": sha256(contents).hexdigest()})
    manifest = {"experiment": study.name, "dataset": study.dataset, "report_fingerprint": study.fingerprint,
                "source_files": sources}
    (directory / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (directory / "README.md").write_text(
        f"# {study.title}\n\n"
        "Open the PNG files in **plots**. The original report tables and scoring definitions are in **sources**.\n\n"
        "Use the experiment run list to compare evaluations with the same parameters. Runs tagged "
        "`training_history` use the training steps present in the source log.\n",
        encoding="utf-8",
    )


def export_run(client, exp_id, study, run, identity, provenance, artifact_writer=None):
    digest, run_key = identity
    tags = {"mlflow.runName": run.name, "project": "LifeGuard-RL", "dataset": study.dataset,
            "notebook": str(run.notebook), "evidence": run.evidence, "run_kind": "evaluation",
            "provenance": provenance, "report_fingerprint": digest, "logical_run": run_key,
            **run.tags}
    if "step_axis" in run.params:
        tags["step_axis"] = run.params["step_axis"]
    created = client.create_run(exp_id, tags=tags)
    run_id = created.info.run_id
    try:
        now = int(time.time() * 1000)
        points = [Metric(name, value, now, step) for name, series in run.metrics.items() for step, value in series]
        parameters = [Param(key, text(val)) for key, val in run.params.items()]
        if parameters or points:
            client.log_batch(run_id, metrics=points, params=parameters)
        if artifact_writer:
            with TemporaryDirectory(prefix="lifeguard-mlflow-") as scratch:
                artifact_writer(Path(scratch))
                client.log_artifacts(run_id, scratch)
        client.set_terminated(run_id, status="FINISHED")
    except BaseException:
        client.set_terminated(run_id, status="FAILED")
        raise
    return run_id


def import_experiments(client, artifact_root, studies, provenance):
    summaries = []
    for study in studies:
        exp_id = experiment_id(client, study, artifact_root)
        digest = study.fingerprint
        overview = Run("Benchmark overview", "benchmark_summary", max(report.notebook for report, _ in study.files),
                       {}, {}, {"run_kind": "overview"})
        past = client.search_runs([exp_id], f"tags.report_fingerprint = '{digest}'", max_results=1000)
        completed = {r.data.tags["logical_run"]: r.info.run_id for r in past
                     if r.info.status == "FINISHED" and "logical_run" in r.data.tags}
        new, reused, overview_id = 0, 0, None
        for run in (overview, *study.runs):
            key = parse_identity(study.name, run)
            if key in completed:
                run_id = completed[key]
                reused += 1
            else:
                writer = (lambda folder: write_overview(study, folder)) if run is overview else None
                run_id = export_run(client, exp_id, study, run, (digest, key), provenance, writer)
                new += 1
            if run is overview:
                overview_id = run_id
        summaries.append(dict(study=study.name, experiment_id=exp_id, overview_run_id=overview_id,
                              fingerprint=digest, new_runs=new, reused_runs=reused))
    return summaries


def import_saved(root=DEFAULT_STORE, notebook=None, path=None, provenance=ARCHIVED):
    studies = experiments(notebook, path)
    _, _, artifacts = store_settings(root)
    return import_experiments(local_client(root), artifacts, studies, provenance)


def publish_notebook_report(notebook, report_dir, root=DEFAULT_STORE):
    """Log a completed notebook export and reuse evaluation runs for identical evidence."""
    report = Report(notebook, report_dir)
    report.read("summary.md")
    config = report.config()
    summaries = import_saved(root, notebook, report.path, EXECUTION)
    export_id = str((report.path / "summary.md").stat().st_mtime_ns)
    client = local_client(root)
    exp_id = summaries[0]["experiment_id"]
    identity = sha256((str(report.path)+":"+export_id).encode()).hexdigest()
    prior = client.search_runs([exp_id], f"tags.export_id = '{identity}'", max_results=20)
    if any(item.info.status == "FINISHED" for item in prior):
        return summaries
    tags = {"mlflow.runName": f"Notebook {notebook} export", "project": "LifeGuard-RL", "notebook": str(notebook),
            "run_kind": "notebook_export", "evidence": "notebook_export", "export_id": identity,
            "provenance": EXECUTION, "controller_reused": text(config.get("controller_reused", False))}
    entry = client.create_run(exp_id, tags=tags)
    run_id = entry.info.run_id
    try:
        with TemporaryDirectory(prefix="lifeguard-mlflow-export-") as scratch:
            output = Path(scratch) / "export.json"
            output.write_text(json.dumps({"notebook": notebook, "controller_reused": config.get("controller_reused", False),
                                          "experiments": summaries}, indent=2) + "\n", encoding="utf-8")
            client.log_artifact(run_id, str(output))
        client.set_terminated(run_id, status="FINISHED")
    except BaseException:
        client.set_terminated(run_id, status="FAILED")
        raise
    return summaries
