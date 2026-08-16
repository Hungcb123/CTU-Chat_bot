from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

from fastapi import HTTPException


def _load_require_admin():
    """Compile the real dependency without importing database/JWT modules."""

    source_path = Path(__file__).resolve().parents[1] / "app" / "api" / "auth.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "require_admin"
    )
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {
        "Depends": lambda dependency: dependency,
        "get_current_user": lambda: None,
        "HTTPException": HTTPException,
        "User": object,
    }
    exec(compile(module, str(source_path), "exec"), namespace)
    return namespace["require_admin"]


require_admin = _load_require_admin()


class RequireAdminTests(unittest.IsolatedAsyncioTestCase):
    async def test_admin_role_is_accepted(self):
        user = SimpleNamespace(role=" Admin ")
        self.assertIs(await require_admin(user), user)

    async def test_non_admin_role_is_rejected(self):
        for role in (None, "", "student", "teacher"):
            with self.subTest(role=role):
                with self.assertRaises(HTTPException) as raised:
                    await require_admin(SimpleNamespace(role=role))
                self.assertEqual(raised.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
