from prompts import TESTER_PROMPT
from models import BugReport
from state import ProjectState
from agents.base_agent import BaseAgent


class TesterAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__( llm.with_structured_output( BugReport ) )

    def run(
        self,
        state: ProjectState
    ) -> ProjectState:

        prompt = TESTER_PROMPT.format(
            execution=state.execution_result.model_dump_json(
                indent=2
            )
        )

        report = self.llm.invoke(
            prompt
        )

        state.bug_report = report

        return state