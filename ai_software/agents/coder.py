from llm import llm
from prompts import CODER_PROMPT
from models import GeneratedFile
from state import ProjectState
from agents.base_agent import BaseAgent
from text_utils import strip_code_fences


class CoderAgent(BaseAgent):

    def __init__(self, llm): 
        super().__init__(llm)

    def run(
        self,
        state: ProjectState
    ) -> ProjectState:

        if not state.pending_files:
            return state

        file_path = state.pending_files.pop(0)
        state.current_file = file_path

        prompt = CODER_PROMPT.format(
            plan=state.plan.model_dump_json(indent=2),
            manifest=state.manifest.model_dump_json(indent=2),
            file=file_path
        )

        try:
            llm_response = llm.invoke(prompt)

            generated_file = GeneratedFile(
                path=file_path,
                content=strip_code_fences(llm_response.content)
            )

            state.generated_files.append(generated_file)
            state.generation_success = True

        except Exception as error:
            state.errors.append(str(error))
            state.generation_success = False

        return state