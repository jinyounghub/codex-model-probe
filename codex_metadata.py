"""Read local Codex display labels without reading conversation contents."""

from __future__ import annotations

import ntpath
import sqlite3
from contextlib import closing
from pathlib import Path


def _windows_path(value: str | None) -> str:
    if not value:
        return ""
    if value.startswith("\\\\?\\UNC\\"):
        value = "\\\\" + value[8:]
    elif value.startswith("\\\\?\\"):
        value = value[4:]
    return ntpath.normcase(ntpath.normpath(value))


class CodexMetadataResolver:
    """Resolve exact thread IDs against Codex's local, read-only metadata DBs."""

    def __init__(self, codex_home: Path | None = None):
        self.codex_home = codex_home or Path.home() / ".codex"

    @staticmethod
    def _connect(path: Path):
        if not path.is_file():
            return None
        return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=0.2)

    def resolve(self, thread_id: str | None) -> dict[str, str | None]:
        result = {"conversation_title": None, "project_name": None}
        if not isinstance(thread_id, str) or not thread_id or len(thread_id) > 128:
            return result

        cwd = None
        project_id = None
        try:
            connection = self._connect(self.codex_home / "state_5.sqlite")
            if connection is not None:
                with closing(connection):
                    row = connection.execute(
                        "SELECT name, title, cwd, project_id FROM threads WHERE id = ?",
                        (thread_id,),
                    ).fetchone()
                    if row:
                        name, fallback_title, cwd, project_id = row
                        result["conversation_title"] = name or fallback_title or None
                    if project_id:
                        project = connection.execute(
                            "SELECT name FROM projects WHERE id = ?", (project_id,)
                        ).fetchone()
                        result["project_name"] = project[0] if project else None
                    if cwd and not result["project_name"]:
                        normalized_cwd = _windows_path(cwd)
                        roots = connection.execute(
                            "SELECT projects.name, project_roots.path FROM projects "
                            "JOIN project_roots ON projects.id = project_roots.project_id"
                        )
                        matches = [(len(root_path), name) for name, path in roots
                                   if (root_path := _windows_path(path)) and
                                   (normalized_cwd == root_path or
                                    normalized_cwd.startswith(root_path + "\\"))]
                        if matches:
                            result["project_name"] = max(matches)[1]
        except (OSError, sqlite3.Error, ValueError):
            pass

        if not result["conversation_title"]:
            try:
                connection = self._connect(self.codex_home / "sqlite" / "codex-dev.db")
                if connection is not None:
                    with closing(connection):
                        row = connection.execute(
                            "SELECT display_title FROM local_thread_catalog "
                            "WHERE host_id = 'local' AND thread_id = ?", (thread_id,)
                        ).fetchone()
                        if row:
                            result["conversation_title"] = row[0] or None
            except (OSError, sqlite3.Error, ValueError):
                pass
        return result
