# from llm import llm 
# from prompts import CODER_PROMPT 

# def coder(plan: str): 
#     prompt = CODER_PROMPT.format( plan=plan ) 
#     response = llm.invoke(prompt) 
#     return response.content


import json 
from llm import llm 
from prompts import CODER_PROMPT 

def coder(plan: str): 
    prompt = CODER_PROMPT.format( plan=plan ) 
    response = llm.invoke(prompt) 
    content = response.content.strip() 
    if content.startswith("```json"): 
        content = content.replace("```json", "") 
        content = content.replace("```", "").strip() 
        return json.loads(content)