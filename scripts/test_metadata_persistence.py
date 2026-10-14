#!/usr/bin/env python3
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Codex <codex@agents.invalid>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.

"""Reproduce metadata durability, legacy upgrade, XML import and SQL call counts.

Run with a Python environment containing Gramps' runtime/test dependencies and PyGObject, using source trees with their normal built resources. For example::

    git worktree add --detach /tmp/gramps-5.2.4 v5.2.4
    python scripts/test_metadata_persistence.py --legacy-source /tmp/gramps-5.2.4 --output /tmp/metadata-after

Run this same script against an older checkout to demonstrate the regression::

    python scripts/test_metadata_persistence.py --source /path/to/before --resources /path/to/built/share --checks durability performance --output /tmp/metadata-before

The legacy checkout generates a real schema-20 SQLite database and Gramps XML export. They are independent transfer paths: upgrading SQLite is not XML import. The xml check terminates the importer without closing its database; xml-close checks the normal lifecycle. XML import uses four-digit ID prefixes matching the legacy fixture, avoiding the normal five-digit normalization in newer Gramps.

No downloaded or personal data is used. Every database and configuration lives under a new output directory. Writer processes deliberately call os._exit(0), so neither close(), Python finalizers nor atexit handlers can save metadata. Independent reader processes verify the results. Exit status is nonzero on any failed assertion. JSON results, expected/actual snapshots and worker logs remain in the output directory. SQL counts include execute() and commit() calls; they are not measurements of network round trips or production latency.
"""

# -------------------------------------------------------------------------
# Standard Python modules
# -------------------------------------------------------------------------
import argparse
import importlib
import hashlib
import json
import os
from pathlib import Path
import pickle
import shutil
import sqlite3
import subprocess
import sys
import time
from contextlib import closing, nullcontext
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

PERSON_HANDLE = "0000000000000001"
NOTE_HANDLE = "000000000000eeee"


def write_json(path: Path, value: Any) -> None:
    """Save readable, UTF-8 evidence without serializing private runtime objects."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def api() -> SimpleNamespace:
    """Import the selected source tree only inside an isolated worker process."""
    return SimpleNamespace(
        db=importlib.import_module("gramps.gen.db"),
        lib=importlib.import_module("gramps.gen.lib"),
        sqlite=importlib.import_module("gramps.plugins.db.dbapi.sqlite"),
        user=importlib.import_module("gramps.gen.user"),
    )


def set_formats(db: Any, formats: list) -> None:
    """Exercise each revision's own name-format API, including the old regression."""
    if hasattr(db, "set_name_formats"):
        db.set_name_formats(formats)
    else:
        db.name_formats = formats


def populate(gramps: SimpleNamespace, db: Any, count: int = 1) -> None:
    """Create synthetic records with Unicode text, links, custom types and IDs."""
    with gramps.db.DbTxn("Synthetic metadata fixture", db) as trans:
        for index in range(count):
            person = gramps.lib.Person()
            person.set_handle(f"{index + 1:016x}")
            person.set_gramps_id(f"I{index + 1:04d}")
            person.get_primary_name().set_first_name(f"Élodie{index}")
            person.set_gender(gramps.lib.Person.FEMALE)
            if index == 0:
                person.add_note(NOTE_HANDLE)
            db.add_person(person, trans)
        note = gramps.lib.Note()
        note.set_handle(NOTE_HANDLE)
        note.set("Synthetic transcription: café, Montréal, 1901.")
        note.set_type("Fixture transcription")
        db.add_note(note, trans)
    db.bookmarks.append(PERSON_HANDLE)
    db.note_bookmarks.append(NOTE_HANDLE)
    owner = gramps.lib.Researcher()
    owner.set_name("Synthetic researcher Élodie")
    owner.set_email("fixture@example.invalid")
    db.set_researcher(owner)
    set_formats(db, [(99, "Synthetic format", "%f", True)])
    db.set_default_person_handle(PERSON_HANDLE)
    db.set_mediapath("synthetic-media")


def snapshot(db: Any) -> dict:
    """Compare meaningful record values and metadata across schema representations."""
    people = []
    for handle in sorted(db.get_person_handles()):
        person = db.get_person_from_handle(handle)
        people.append(
            {
                "handle": handle,
                "id": person.get_gramps_id(),
                "name": person.get_primary_name().get_first_name(),
                "gender": person.get_gender(),
                "notes": person.get_note_list(),
            }
        )
    notes = []
    for handle in sorted(db.get_note_handles()):
        note = db.get_note_from_handle(handle)
        notes.append(
            {
                "handle": handle,
                "id": note.get_gramps_id(),
                "text": note.get(),
                "type": str(note.get_type()),
            }
        )
    result = {
        "people": people,
        "notes": notes,
        "bookmarks": db.get_bookmarks().get(),
        "note_bookmarks": db.get_note_bookmarks().get(),
        "researcher": db.get_researcher().serialize(),
        # XML may allocate a different format number; the definition must survive.
        "name_formats": [list(row[1:]) for row in db.name_formats],
        "note_types": sorted(db.get_note_types()),
        "statistics": db.genderStats.stats,
        "default_person": db.get_default_handle(),
        "media_path": db.get_mediapath(),
    }
    return json.loads(json.dumps(result))


def worker(args: argparse.Namespace) -> None:
    """Run one phase with the selected Gramps modules and configuration."""
    gramps = api()
    db = gramps.sqlite.SQLite()
    dbdir = args.output / args.database
    if args.worker in ("legacy", "durability"):
        dbdir.mkdir()
        db.load(str(dbdir))
        populate(gramps, db)
        if args.worker == "legacy":
            # Genuine old-version export, followed by a normal old-version close.
            export = importlib.import_module("gramps.plugins.export.exportxml")
            writer = export.XmlWriter(db, gramps.user.User(), 0, compress=0)
            if not writer.write(str(args.output / "legacy.gramps")):
                raise AssertionError("Legacy XML export failed")
            db.close()
            db.undodb.close()
            db = gramps.sqlite.SQLite()
            db.load(str(dbdir))
        write_json(args.output / f"{args.worker}-expected.json", snapshot(db))
    elif args.worker == "upgrade":
        # Refusing an unapproved upgrade must leave the legacy SQLite bytes intact.
        original_bytes = (dbdir / "sqlite.db").read_bytes()
        try:
            db.load(str(dbdir))
        except gramps.db.DbUpgradeRequiredError:
            pass
        else:
            raise AssertionError("Legacy database did not require an explicit upgrade")
        if (dbdir / "sqlite.db").read_bytes() != original_bytes:
            raise AssertionError("Refusing the upgrade modified the legacy database")
        db = gramps.sqlite.SQLite()
        db.load(str(dbdir), force_schema_upgrade=True)
        if db.get_schema_version() != db.VERSION[0]:
            raise AssertionError("Upgrade did not reach the selected version's schema")
        write_json(args.output / "upgrade-in-process.json", snapshot(db))
        write_json(
            args.output / "upgrade-schema.json",
            {
                "schema_version": db.get_schema_version(),
                "expected_schema_version": db.VERSION[0],
                "serializer": db.serializer.__name__,
                "refused_upgrade_preserved_bytes": True,
            },
        )
    elif args.worker in ("xml", "xml-close"):
        dbdir.mkdir()
        db.load(str(dbdir))
        db.set_feature("skip-import-additions", True)
        # Match the old fixture's configured ID width; otherwise the importer
        # intentionally normalizes numeric IDs to the new five-digit default.
        db.set_person_id_prefix("I%04d")
        db.set_note_id_prefix("N%04d")
        importer = importlib.import_module("gramps.plugins.importer.importxml")
        importer.importData(db, str(args.output / "legacy.gramps"), gramps.user.User())
        write_json(args.output / f"{args.worker}-in-process.json", snapshot(db))
        if args.worker == "xml-close":
            db.close()
            db.undodb.close()
    elif args.worker == "read":
        db.load(str(dbdir), mode=gramps.db.DBMODE_R)
        write_json(args.output / f"{args.database}-actual.json", snapshot(db))
        db.close(update=False)
        db.undodb.close()
    elif args.worker == "performance":
        performance(gramps, db, dbdir, args.output)
    elif args.worker == "rollback":
        rollback(gramps, db, dbdir, args.output)
    else:
        raise ValueError(args.worker)
    # Deliberately bypass database close, finalizers and atexit, even after import.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


def performance(gramps: SimpleNamespace, db: Any, dbdir: Path, output: Path) -> None:
    """Measure the complete note edit and close, exposing shifted work."""
    dbdir.mkdir()
    db.load(str(dbdir))
    populate(gramps, db, count=100)
    db.close()
    db.undodb.close()
    db = gramps.sqlite.SQLite()
    db.load(str(dbdir))
    results = []
    for generated in (False, True):
        note = gramps.lib.Note()
        note.set_handle("000000000000ff01" if generated else "000000000000ff00")
        if not generated:
            note.set_gramps_id("N9000")
        note.set("Unrelated synthetic note")
        with (
            patch.object(db.dbapi, "execute", wraps=db.dbapi.execute) as execute,
            patch.object(db.dbapi, "commit", wraps=db.dbapi.commit) as commit,
        ):
            started = time.monotonic()
            with gramps.db.DbTxn("Synthetic note edit", db) as trans:
                db.add_note(note, trans)
            elapsed = time.monotonic() - started
        results.append(
            {
                "phase": "note_edit",
                "generated_id": generated,
                "sql_calls": execute.call_count + commit.call_count,
                "metadata_statements": sum(
                    "metadata" in call.args[0].lower()
                    for call in execute.call_args_list
                ),
                "statistics_statements": sum(
                    "gender_stats" in call.args[0].lower()
                    for call in execute.call_args_list
                ),
                "commits": commit.call_count,
                "seconds": elapsed,
            }
        )
        with (
            patch.object(db.dbapi, "execute", wraps=db.dbapi.execute) as execute,
            patch.object(db.dbapi, "commit", wraps=db.dbapi.commit) as commit,
        ):
            db.close()
            db.undodb.close()
        results.append(
            {
                "phase": "close",
                "generated_id": generated,
                "sql_calls": execute.call_count + commit.call_count,
                "commits": commit.call_count,
            }
        )
        db = gramps.sqlite.SQLite()
        db.load(str(dbdir))
    write_json(output / "performance.json", results)


def rollback(gramps: SimpleNamespace, db: Any, dbdir: Path, output: Path) -> None:
    """Verify rollback of records and metadata, including a commit-time failure."""
    dbdir.mkdir()
    db.load(str(dbdir))
    before = snapshot(db)
    for fail_commit in (False, True):
        try:
            with (
                patch.object(
                    db.dbapi,
                    "commit",
                    side_effect=RuntimeError("Injected commit failure"),
                )
                if fail_commit
                else nullcontext()
            ):
                with gramps.db.DbTxn("Aborted fixture", db) as trans:
                    note = gramps.lib.Note()
                    note.set_handle(NOTE_HANDLE)
                    note.set_type("Aborted type")
                    db.add_note(note, trans)
                    db.bookmarks.append(PERSON_HANDLE)
                    if not fail_commit:
                        raise RuntimeError("Injected body failure")
        except RuntimeError:
            pass
        else:
            raise AssertionError("Expected transaction failure")
        if snapshot(db) != before:
            raise AssertionError("Aborted changes remain in memory")
    write_json(output / "rollback-expected.json", before)
    db.close()
    db.undodb.close()


def revision(source: Path) -> str:
    """Identify the exact source revision and whether it has local edits."""
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=source, text=True
    )
    return head + ("+working-tree" if dirty else "")


def run_worker(
    args: argparse.Namespace, phase: str, database: str, source: Path
) -> None:
    """Launch a fresh interpreter and preserve diagnostics for reproduction."""
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(source),
            "GRAMPSHOME": str(args.output / "config" / phase),
            "XDG_CONFIG_HOME": str(args.output / "config" / phase),
            "XDG_DATA_HOME": str(args.output / "data" / phase),
            "XDG_CACHE_HOME": str(args.output / "cache" / phase),
            "GDK_BACKEND": "-",
            "GRAMPS_RESOURCES": str(args.resources),
        }
    )
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        phase,
        "--output",
        str(args.output),
        "--database",
        database,
    ]
    result = subprocess.run(
        command,
        cwd=source,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    (args.output / f"{database}-{phase}.log").write_text(
        result.stdout + result.stderr, encoding="utf-8"
    )
    if result.returncode:
        raise RuntimeError(
            f"Worker {phase} exited {result.returncode}: {result.stderr[-2500:]}"
        )


def compare(args: argparse.Namespace, database: str, expected: str) -> None:
    """Read through a new Gramps instance and compare persisted semantic values."""
    run_worker(args, "read", database, args.source)
    wanted = json.loads((args.output / f"{expected}-expected.json").read_text())
    actual = json.loads((args.output / f"{database}-actual.json").read_text())
    differences = [key for key in wanted if wanted[key] != actual[key]]
    if differences:
        raise AssertionError("Persisted values differ: " + ", ".join(differences))


def main() -> int:
    """Run independent reproduction cases and retain their evidence."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Gramps checkout under test",
    )
    parser.add_argument(
        "--legacy-source",
        type=Path,
        help="Unmodified Gramps 5.2.4 checkout, used to generate legacy fixtures",
    )
    parser.add_argument(
        "--resources",
        type=Path,
        help="Built Gramps share directory; defaults to SOURCE/build/share",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New output directory; must not already exist",
    )
    parser.add_argument(
        "--checks",
        nargs="+",
        choices=(
            "durability",
            "rollback",
            "performance",
            "migration",
            "xml",
            "xml-close",
        ),
        default=[
            "durability",
            "rollback",
            "performance",
            "migration",
            "xml",
            "xml-close",
        ],
    )
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--database", help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.worker:
        worker(args)
        return 0
    args.source = args.source.resolve()
    args.resources = (args.resources or args.source / "build/share").resolve()
    if {"migration", "xml", "xml-close"} & set(args.checks) and not args.legacy_source:
        parser.error("--legacy-source is required for migration and XML tests")
    args.output.mkdir(parents=True, exist_ok=False)
    results: dict[str, Any] = {
        "source": str(args.source),
        "revision": revision(args.source),
        "python": sys.version,
        "resources": str(args.resources),
        "checks": {},
    }
    source_diff = subprocess.check_output(["git", "diff", "HEAD"], cwd=args.source)
    (args.output / "source.diff").write_bytes(source_diff)
    results["source_diff_sha256"] = hashlib.sha256(source_diff).hexdigest()
    results["reproducer_sha256"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    if args.legacy_source:
        args.legacy_source = args.legacy_source.resolve()
        results["legacy_revision"] = revision(args.legacy_source)
        run_worker(args, "legacy", "legacy-db", args.legacy_source)
        with closing(sqlite3.connect(args.output / "legacy-db/sqlite.db")) as conn:
            columns = [row[1] for row in conn.execute("PRAGMA table_info(metadata)")]
            version = pickle.loads(
                conn.execute(
                    "SELECT value FROM metadata WHERE setting='version'"
                ).fetchone()[0]
            )
        if "json_data" in columns or int(version) != 20:
            raise AssertionError(
                "Legacy generator must produce schema 20 without JSON metadata"
            )
        results["legacy_schema"] = {
            "version": int(version),
            "metadata_columns": columns,
        }
    for check in args.checks:
        try:
            if check == "migration":
                shutil.copytree(args.output / "legacy-db", args.output / "upgraded-db")
                run_worker(args, "upgrade", "upgraded-db", args.source)
                compare(args, "upgraded-db", "legacy")
            elif check in ("xml", "xml-close"):
                run_worker(args, check, f"{check}-db", args.source)
                compare(args, f"{check}-db", "legacy")
            else:
                run_worker(args, check, check, args.source)
                if check != "performance":
                    compare(args, check, check)
            results["checks"][check] = {"passed": True}
        except (AssertionError, RuntimeError, subprocess.TimeoutExpired) as error:
            results["checks"][check] = {"passed": False, "error": str(error)}
        print(json.dumps({"check": check, **results["checks"][check]}), flush=True)
        write_json(args.output / "results.json", results)
    return 0 if all(value["passed"] for value in results["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
