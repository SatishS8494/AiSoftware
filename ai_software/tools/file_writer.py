import os
import tempfile
from pathlib import Path

from config import settings
from logger import get_logger
from models import GeneratedFile


log = get_logger("file_writer")


class UnsafeWritePathError(Exception):
    """Raised when a target path escapes the configured workspace."""


class FileWriter:
    def __init__(self, workspace: Path | str | None = None):
        self.workspace = Path(workspace or settings.workspace_path).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _resolve_safely(self, relative_path: str) -> Path:
        candidate = (self.workspace / relative_path).resolve()
        try:
            candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise UnsafeWritePathError(
                f"Refusing to write outside workspace: {relative_path!r} -> {candidate}"
            ) from exc
        return candidate

    def write(self, generated_file: GeneratedFile) -> Path:
        target = self._resolve_safely(generated_file.path)
        target.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: temp file in the same directory, then os.replace.
        fd, tmp_name = tempfile.mkstemp(
            dir=str(target.parent), prefix=".__tmp_", suffix=target.suffix
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(generated_file.content)
            os.replace(tmp_name, target)
        except Exception:
            # Best-effort cleanup if replace never happened.
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

        log.info("wrote %s (%d bytes)", target.relative_to(self.workspace), target.stat().st_size)
        return target
