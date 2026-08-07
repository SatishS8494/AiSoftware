import re
from llm import llm 
from prompts import FIX_PROMPT 
from state import ProjectState 
from agents.base_agent import BaseAgent
from text_utils import strip_code_fences
from tools.package_validator import validate_dependency_manifest


def _find_erroring_file(state: ProjectState):
    """Locate the GeneratedFile mentioned in stderr; fall back to the entry file or the last file."""
    stderr = ""
    if state.execution_result and state.execution_result.stderr:
        stderr = state.execution_result.stderr

    # Dependency-install failures always point at the manifest for that ecosystem
    manifest_by_marker = [
        (("pip install failed", "No matching distribution", "Could not find a version"), "requirements.txt"),
        (("npm install failed", "npm ERR", "E404", "ENOTFOUND"), "package.json"),
        (("mvn package failed", "Could not resolve dependencies", "Failed to execute goal"), "pom.xml"),
    ]
    for markers, manifest_name in manifest_by_marker:
        if any(m in stderr for m in markers):
            for gf in state.generated_files:
                if gf.path.endswith(manifest_name):
                    return gf

    known_paths = [gf.path for gf in state.generated_files]

    # Match filenames (basename) that appear in stderr
    for path in known_paths:
        basename = path.split("/")[-1].split("\\")[-1]
        if basename and re.search(rf"\b{re.escape(basename)}\b", stderr):
            return next(gf for gf in state.generated_files if gf.path == path)

    # Fallback: entry-point app.py if present, else last generated file
    for gf in state.generated_files:
        if gf.path.endswith("app.py"):
            return gf
    return state.generated_files[-1]


class FixAgent(BaseAgent): 
    def __init__(self, llm): 
        super().__init__(llm)

    def run( self, state: ProjectState ) -> ProjectState: 
        state.fix_attempts += 1
        generated_file = _find_erroring_file(state)
        prompt = FIX_PROMPT.format( 
            file_path=generated_file.path, 
            source_code=generated_file.content, 
            execution=state.execution_result.model_dump_json(indent=2),
            bug_report=state.bug_report.model_dump_json(indent=2) ) 
        response = llm.invoke(prompt) 
        fixed_content = strip_code_fences(response.content)
        fixed_content, removed = validate_dependency_manifest(generated_file.path, fixed_content)
        if removed:
            state.errors.append(
                f"{generated_file.path}: fixer removed unknown packages {removed}"
            )
        generated_file.content = fixed_content

        # Ensure writer_node (which writes generated_files[-1]) picks up the fixed file.
        state.generated_files.remove(generated_file)
        state.generated_files.append(generated_file)
        state.current_file = generated_file.path
        return state