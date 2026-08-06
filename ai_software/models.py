from pydantic import BaseModel, Field 
from typing import List , Optional


class ProjectRequirement(BaseModel): 
    user_request: str 


class ProjectPlan(BaseModel): 
    project_name: str 
    description: str 
    tech_stack: List[str] = Field(default_factory=list) 
    features: List[str] = Field(default_factory=list) 
    development_steps: List[str] = Field(default_factory=list) 


class ProjectManifest(BaseModel): 
    project_name: str 
    folders: List[str] = Field(default_factory=list) 
    files: List[str] = Field(default_factory=list)


class GeneratedFile(BaseModel): 
    path: str 
    content: str

class GeneratedProject(BaseModel):
    project_name: str 
    files: List[GeneratedFile] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0


class BugReport(BaseModel):
    success: bool
    summary: str
    probable_cause: str
    recommendation: str

class ReviewReport(BaseModel):
    approved: bool
    score: int
    strengths: list[str]
    improvements: list[str]
    summary: str