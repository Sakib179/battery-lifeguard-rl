"""Serve both project interfaces and migrate the local MLflow store."""

import argparse
from contextlib import closing
import os
from pathlib import Path, PurePosixPath
from shutil import copytree
import sqlite3
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
CONTAINER_STORE = Path("/var/lib/lifeguard/mlflow")


def relocated_uri(value, original, destination):
    uri = urlsplit(value)
    if uri.scheme not in ("", "file"):
        return value
    if uri.netloc not in ("", "localhost"):
        raise ValueError(f"Artifact location is not local: {value}")
    original_path = PurePosixPath(unquote(uri.path))
    if not original_path.is_relative_to(original) or ".." in original_path.parts:
        raise ValueError(f"Artifact location is outside the source store: {value}")
    return (destination / original_path.relative_to(original)).as_uri()


def rewrite_artifact_uris(connection, original, destination):
    for experiment_id, location in connection.execute(
        "SELECT experiment_id, artifact_location FROM experiments"
    ).fetchall():
        empty_default = experiment_id == 0 and connection.execute(
            "SELECT 1 FROM runs WHERE experiment_id = ?", (experiment_id,)
        ).fetchone() is None
        location = ((destination / "default").as_uri() if empty_default else
                    relocated_uri(location, original, destination))
        connection.execute(
            "UPDATE experiments SET artifact_location = ? WHERE experiment_id = ?", (location, experiment_id)
        )

    for run_id, uri in connection.execute("SELECT run_uuid, artifact_uri FROM runs").fetchall():
        if uri:
            connection.execute(
                "UPDATE runs SET artifact_uri = ? WHERE run_uuid = ?",
                (relocated_uri(uri, original, destination), run_id),
            )

    for column in ("source", "storage_location"):
        model_locations = connection.execute(
            f"SELECT name, version, {column} FROM model_versions WHERE {column} IS NOT NULL"
        ).fetchall()
        for name, version, uri in model_locations:
            if uri:
                connection.execute(
                    f"UPDATE model_versions SET {column} = ? WHERE name = ? AND version = ?",
                    (relocated_uri(uri, original, destination), name, version),
                )


def migrate(source, original_artifact_root, destination=CONTAINER_STORE):
    """Copy a read-only store, validate it, and publish the copy atomically."""
    source = source.resolve()
    destination = destination.resolve()
    database = source / "mlflow.db"
    artifacts = source / "artifacts"
    if destination.exists():
        raise FileExistsError(f"{destination} is already initialized. Use the existing Docker volume.")
    if not database.is_file() or not artifacts.is_dir():
        raise FileNotFoundError(f"{source} must contain mlflow.db and artifacts/")
    if artifacts.is_symlink() or any(item.is_symlink() for item in artifacts.rglob("*")):
        raise ValueError("The source artifact folder contains symlinks.")
    if not original_artifact_root.is_absolute() or ".." in original_artifact_root.parts:
        raise ValueError("The original artifact root must be an absolute host path.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".migrate-", dir=destination.parent) as scratch:
        staged = Path(scratch) / "store"
        # Named volumes stay readable by the runtime user after publication.
        staged.mkdir()
        copytree(artifacts, staged / "artifacts")
        with (
            closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as original,
            closing(sqlite3.connect(staged / "mlflow.db")) as copy,
        ):
            original.backup(copy)
            with copy:
                rewrite_artifact_uris(copy, original_artifact_root, destination / "artifacts")
                check = copy.execute("PRAGMA quick_check").fetchall()
                if check != [("ok",)]:
                    raise ValueError(f"SQLite integrity check failed: {check}")
                runs = copy.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
                views = copy.execute(
                    "SELECT COUNT(*) FROM experiment_tags WHERE key LIKE 'mlflow.sharedViewState.%'"
                ).fetchone()[0]
        staged.rename(destination)
    return runs, views


def create_app():
    """Mount the static dashboard alongside the native MLflow application."""
    from flask import Blueprint, send_from_directory
    from mlflow.server import (
        ARTIFACT_ROOT_ENV_VAR,
        BACKEND_STORE_URI_ENV_VAR,
        REGISTRY_STORE_URI_ENV_VAR,
        SERVE_ARTIFACTS_ENV_VAR,
        app,
    )
    from mlflow.server.handlers import initialize_backend_stores

    database = CONTAINER_STORE / "mlflow.db"
    if not database.is_file():
        raise RuntimeError("Initialize the Docker volume with the MLflow migration in the project README.")
    database_uri = "sqlite:///" + database.as_posix()
    artifacts = (CONTAINER_STORE / "artifacts").as_uri()
    os.environ[BACKEND_STORE_URI_ENV_VAR] = database_uri
    os.environ[REGISTRY_STORE_URI_ENV_VAR] = database_uri
    os.environ[ARTIFACT_ROOT_ENV_VAR] = artifacts
    os.environ[SERVE_ARTIFACTS_ENV_VAR] = "false"
    initialize_backend_stores(database_uri, database_uri, artifacts)

    dashboard = Blueprint("lifeguard_simulation", __name__, url_prefix="/simulation")

    @dashboard.get("/")
    @dashboard.get("/<path:filename>")
    def serve_simulation(filename="index.html"):
        return send_from_directory(ROOT / "simulation", filename)

    app.register_blueprint(dashboard)
    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    migration = commands.add_parser("migrate", help="Import the current host MLflow store into a fresh volume")
    migration.add_argument("source", type=Path)
    migration.add_argument("--original-artifact-root", type=PurePosixPath, required=True)
    args = parser.parse_args()
    try:
        runs, views = migrate(args.source, args.original_artifact_root)
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.exit(1, f"MLflow migration failed: {exc}\n")
    print(f"Migrated {runs} MLflow runs and {views} saved chart views.")


if __name__ == "__main__":
    main()
