import subprocess
import sys
from pathlib import Path

from models import ExecutionResult


class PythonRunner:

    def _install_requirements(self, project_path: Path):
        requirements = project_path / "requirements.txt"
        if not requirements.exists():
            return None
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return ExecutionResult(
                success=False,
                stdout=result.stdout,
                stderr=f"pip install failed:\n{result.stderr}",
                return_code=result.returncode
            )
        return None

    def run(
        self,
        project_path: Path,
        entry_file: str = "app.py"
    ) -> ExecutionResult:

        install_failure = self._install_requirements(project_path)
        if install_failure is not None:
            return install_failure

        target = project_path / entry_file

        if not target.exists():

            return ExecutionResult(
                success=False,
                stderr=f"{entry_file} not found."
            )

        result = subprocess.run(
            [sys.executable, str(target)],
            capture_output=True,
            text=True,
            cwd=str(project_path)
        )

        return ExecutionResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode
        )