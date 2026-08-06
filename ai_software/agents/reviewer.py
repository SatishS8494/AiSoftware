from llm import llm

from prompts import REVIEWER_PROMPT

from models import ReviewReport
from base_agent import BaseAgent
from state import ProjectState


class ReviewerAgent(BaseAgent):

    def __init__(self):

        super().__init__( llm.with_structured_output( ReviewReport ) )

    def run(
        self,
        state: ProjectState
    ) -> ProjectState:

        latest = state.generated_files[-1]

        prompt = REVIEWER_PROMPT.format(

            file=latest.path,

            code=latest.content

        )

        report = self.llm.invoke(
            prompt
        )

        state.review_report = report

        return state