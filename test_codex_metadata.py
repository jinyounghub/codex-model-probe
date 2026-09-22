import sqlite3
import tempfile
import unittest
from pathlib import Path

from codex_metadata import CodexMetadataResolver


class CodexMetadataTests(unittest.TestCase):
    def test_exact_thread_title_and_saved_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            connection = sqlite3.connect(home / "state_5.sqlite")
            connection.executescript("""
                CREATE TABLE threads (id TEXT PRIMARY KEY, name TEXT, title TEXT, cwd TEXT, project_id TEXT);
                CREATE TABLE projects (id TEXT PRIMARY KEY, name TEXT);
                CREATE TABLE project_roots (project_id TEXT, path TEXT);
            """)
            connection.execute("INSERT INTO threads VALUES (?, ?, ?, ?, ?)",
                               ("thread-1", "저장소 스킬과 문서 확인", "first message",
                                "\\\\?\\D:\\Documents\\ChatGPT\\naver\\src", None))
            connection.execute("INSERT INTO projects VALUES (?, ?)", ("project-1", "naver"))
            connection.execute("INSERT INTO project_roots VALUES (?, ?)",
                               ("project-1", "D:\\Documents\\ChatGPT\\naver"))
            connection.commit()
            connection.close()

            resolver = CodexMetadataResolver(home)
            self.assertEqual(resolver.resolve("thread-1"), {
                "conversation_title": "저장소 스킬과 문서 확인", "project_name": "naver"
            })
            self.assertEqual(resolver.resolve("another-thread"), {
                "conversation_title": None, "project_name": None
            })

    def test_missing_database_returns_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(CodexMetadataResolver(Path(directory)).resolve("thread-1"), {
                "conversation_title": None, "project_name": None
            })


if __name__ == "__main__":
    unittest.main()
