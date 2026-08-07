import subprocess
import sys
from pathlib import Path

from models import ExecutionResult


RUN_TIMEOUT_SECONDS = 60


def _install_result_from(step: str, r: subprocess.CompletedProcess) -> ExecutionResult:
    return ExecutionResult(
        success=False,
        stdout=r.stdout,
        stderr=f"{step} failed:\n{r.stderr}",
        return_code=r.returncode,
    )


def _run_with_timeout(cmd, cwd, shell=False):
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            shell=shell,
            timeout=RUN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=124,
            stdout=(e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")),
            stderr=f"Process timed out after {RUN_TIMEOUT_SECONDS}s (likely a long-running server).",
        )


def _run_python(project_path: Path) -> ExecutionResult:
    req = project_path / "requirements.txt"
    if req.exists():
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req)],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            return _install_result_from("pip install", r)

    entry = project_path / "app.py"
    if not entry.exists():
        return ExecutionResult(success=False, stderr="app.py not found.")

    r = _run_with_timeout([sys.executable, str(entry)], cwd=project_path)
    return ExecutionResult(
        success=r.returncode == 0,
        stdout=r.stdout,
        stderr=r.stderr,
        return_code=r.returncode,
    )


def _run_node(project_path: Path) -> ExecutionResult:
    pkg = project_path / "package.json"
    if not pkg.exists():
        return ExecutionResult(success=False, stderr="package.json not found.")

    r = subprocess.run(
        "npm install",
        capture_output=True,
        text=True,
        cwd=str(project_path),
        shell=True,
    )
    if r.returncode != 0:
        return _install_result_from("npm install", r)

    r = _run_with_timeout("npm start", cwd=project_path, shell=True)
    return ExecutionResult(
        success=r.returncode == 0,
        stdout=r.stdout,
        stderr=r.stderr,
        return_code=r.returncode,
    )


def _run_java(project_path: Path) -> ExecutionResult:
    pom = project_path / "pom.xml"
    if not pom.exists():
        return ExecutionResult(success=False, stderr="pom.xml not found.")

    r = subprocess.run(
        "mvn -q -DskipTests package",
        capture_output=True,
        text=True,
        cwd=str(project_path),
        shell=True,
    )
    if r.returncode != 0:
        return _install_result_from("mvn package", r)

    jars = list((project_path / "target").glob("*.jar"))
    if not jars:
        return ExecutionResult(
            success=False,
            stderr="Build succeeded but no jar was produced under target/.",
        )

    r = _run_with_timeout(f'java -jar "{jars[0]}"', cwd=project_path, shell=True)
    return ExecutionResult(
        success=r.returncode == 0,
        stdout=r.stdout,
        stderr=r.stderr,
        return_code=r.returncode,
    )


RUNNERS = {
    "python": _run_python,
    "node": _run_node,
    "java": _run_java,
}


def run_project(project_path: Path, language: str) -> ExecutionResult:
    fn = RUNNERS.get((language or "python").lower())
    if fn is None:
        return ExecutionResult(
            success=False,
            stderr=f"Unsupported language: {language!r}. Supported: {sorted(RUNNERS)}",
        )
    return fn(project_path)
