from llm import llm
from prompts import PLANNER_PROMPT

def planner(requirement: str): 
    prompt = PLANNER_PROMPT.format( requirement=requirement ) 
    response = llm.invoke(prompt) 
    return response.content