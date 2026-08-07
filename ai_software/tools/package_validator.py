import json
import re
import urllib.error
import urllib.request
from functools import lru_cache
from typing import List, Tuple

from logger import get_logger


log = get_logger("package_validator")


HTTP_TIMEOUT_SECONDS = 5


@lru_cache(maxsize=1024)
def _is_pypi_package(name: str) -> bool:
    url = f"https://pypi.org/pypi/{name}/json"
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        return e.code < 400
    except (urllib.error.URLError, TimeoutError, OSError):
        # Network unreachable → don't strip anything; caller decides.
        return True


@lru_cache(maxsize=1024)
def _is_npm_package(name: str) -> bool:
    url = f"https://registry.npmjs.org/{name}"
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        return e.code < 400
    except (urllib.error.URLError, TimeoutError, OSError):
        return True


_PYPI_LINE_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._\-]*)")


def _clean_requirements_txt(content: str) -> Tuple[str, List[str]]:
    kept_lines: List[str] = []
    removed: List[str] = []
    for raw in content.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            kept_lines.append(line)
            continue
        m = _PYPI_LINE_RE.match(stripped)
        if not m:
            kept_lines.append(line)
            continue
        pkg_name = m.group(1)
        if _is_pypi_package(pkg_name):
            kept_lines.append(line)
        else:
            removed.append(pkg_name)
    cleaned = "\n".join(kept_lines).rstrip() + "\n"
    return cleaned, removed


def _clean_package_json(content: str) -> Tuple[str, List[str]]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return content, []

    removed: List[str] = []
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps = data.get(section)
        if not isinstance(deps, dict):
            continue
        for name in list(deps.keys()):
            if not _is_npm_package(name):
                removed.append(name)
                deps.pop(name, None)

    cleaned = json.dumps(data, indent=2) + "\n"
    return cleaned, removed


def validate_dependency_manifest(path: str, content: str) -> Tuple[str, List[str]]:
    """Validate declared dependencies against PyPI/npm.

    Returns (cleaned_content, removed_package_names). If path is not a
    recognized dependency manifest, returns (content, []) unchanged.
    """
    if path.endswith("requirements.txt"):
        cleaned, removed = _clean_requirements_txt(content)
    elif path.endswith("package.json"):
        cleaned, removed = _clean_package_json(content)
    else:
        return content, []

    if removed:
        log.warning("stripped unknown packages from %s: %s", path, removed)
    return cleaned, removed
