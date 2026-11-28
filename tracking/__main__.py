"""Import results or open the local native MLflow tracking server."""

import argparse
import os
from pathlib import Path
import sys

from . import use_local_dependencies
from .charts import VIEWS, chart_url

DEFAULT_PORT = 5500


def main():
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, help="Local store directory, defaults to .mlflow in this project")
    commands = parser.add_subparsers(dest="command", required=True)
    load = commands.add_parser("import", help="Import saved benchmark results")
    load.add_argument("--notebook", type=int, choices=(22, 23))
    load.add_argument("--report", type=Path, help="A Notebook 22 or 23 results directory or ZIP")
    load.add_argument("--record-execution", action="store_true", help="Record a completed local notebook export")
    serve = commands.add_parser("serve", help="Run the MLflow UI on localhost in the foreground")
    serve.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local port (default: %(default)s)")
    links = commands.add_parser("links", help="List experiment and current overview URLs")
    links.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local port (default: %(default)s)")
    charts = commands.add_parser("charts", help="Open or list focused native MLflow chart views")
    charts.add_argument("view", choices=tuple(VIEWS), nargs="?")
    charts.add_argument("--open", action="store_true", help="Open the selected view in the default browser")
    charts.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local port (default: %(default)s)")
    args = parser.parse_args()
    if args.command == "import" and args.report and not args.notebook:
        parser.error("--report requires --notebook")
    if args.command == "import" and args.record_execution and (
        not args.notebook or not args.report or not args.report.is_dir()
    ):
        parser.error("--record-execution requires --notebook and a completed report directory")
    if args.command in ("serve", "links", "charts") and not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    use_local_dependencies()
    from .importer import DEFAULT_STORE, import_saved, local_client, publish_notebook_report, store_settings

    root, database, artifacts = store_settings(args.store or DEFAULT_STORE)
    if args.command == "import":
        root.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(root / "matplotlib"))
        os.environ.setdefault("XDG_CACHE_HOME", str(root / "cache"))
        if args.record_execution:
            results = publish_notebook_report(args.notebook, args.report, root)
        else:
            results = import_saved(root, args.notebook, args.report)
        for result in results:
            print(f"{result['study']} · {result['new_runs']} imported, {result['reused_runs']} reused", flush=True)
    elif args.command == "serve":
        if not (root / "mlflow.db").is_file():
            parser.exit(1, "Import the saved reports before opening MLflow.\n")
        print(f"LifeGuard-RL MLflow · http://127.0.0.1:{args.port} · Press Ctrl+C to stop", flush=True)
        os.execv(sys.executable, [sys.executable, "-m", "mlflow", "server", "--backend-store-uri", database,
                                  "--default-artifact-root", artifacts, "--no-serve-artifacts", "--host", "127.0.0.1",
                                  "--port", str(args.port), "--workers", "1"])
    elif args.command == "charts":
        if not (root / "mlflow.db").is_file():
            parser.exit(1, "Import the saved reports before opening MLflow charts.\n")
        client = local_client(root)
        view = args.view or ("discharge-soh" if args.open else None)
        if view:
            url = chart_url(client, view, args.port)
            if url is None:
                parser.exit(1, "Import the saved reports for this chart with tracking import.\n")
            print(url, flush=True)
            if args.open:
                import webbrowser

                webbrowser.open(url)
        else:
            for key, selection in VIEWS.items():
                url = chart_url(client, key, args.port)
                if url:
                    print(f"{key} · {selection.title}\n  {url}")
    else:
        client = local_client(root)
        base = f"http://127.0.0.1:{args.port}/#/experiments"
        for entry in sorted(client.search_experiments(), key=lambda study: study.name):
            if entry.tags.get("project") != "LifeGuard-RL":
                continue
            print(entry.name)
            exp = f"{base}/{entry.experiment_id}"
            print(f"  Runs  {exp}")
            runs = client.search_runs([entry.experiment_id], "tags.run_kind = 'overview' and attributes.status = 'FINISHED'",
                                      order_by=["attributes.start_time DESC"], max_results=1)
            if runs:
                print(f"  Plots {exp}/runs/{runs[0].info.run_id}")


if __name__ == "__main__":
    main()
