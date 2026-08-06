from pathlib import Path 

WORKSPACE = Path( "workspace/generated_projects" ) 

def generate_project(project): 
    project_folder = WORKSPACE / project["project_name"] 
    project_folder.mkdir( parents=True, exist_ok=True ) 
    for file in project["files"]:
        file_path = project_folder / file["path"] 
        file_path.parent.mkdir( parents=True, exist_ok=True ) 
        file_path.write_text( file["content"], encoding="utf-8" ) 
        return project_folder