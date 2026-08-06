import subprocess
from pathlib import Path

from models import ExecutionResult


class PythonRunner:

    def run(
        self,
        project_path: Path,
        entry_file: str = "app.py"
    ) -> ExecutionResult:

        target = project_path / entry_file

        if not target.exists():

            return ExecutionResult(
                success=False,
                stderr=f"{entry_file} not found."
            )

        result = subprocess.run(
            ["python", str(target)],
            capture_output=True,
            text=True
        )

        return ExecutionResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode
        )