from pydantic import BaseModel, Field 
from typing import List, Optional 
from models import ( ProjectPlan, ProjectManifest, GeneratedFile, ExecutionResult, BugReport, ReviewReport )


class ProjectState(BaseModel): 
    requirement: str 
    plan: ProjectPlan | None = None
    manifest: ProjectManifest | None = None
    pending_files: list[str] = Field( default_factory=list )
    generated_files: List[GeneratedFile] = Field( default_factory=list ) 
    current_file: str | None = None
    current_content: Optional[str] = None 
    retry_count: int = 0 
    max_retries: int = 2
    fix_attempts: int = 0
    max_fix_attempts: int = 3
    review_report: ReviewReport | None = None
    execution_result: ExecutionResult | None = None
    bug_report: BugReport | None = None
    errors: List[str] = Field( default_factory=list ) 
    completed: bool = False