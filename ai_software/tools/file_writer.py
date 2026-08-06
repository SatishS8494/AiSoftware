from pathlib import Path 
from models import GeneratedFile 

WORKSPACE = Path("workspace") 

class FileWriter: 
    def write( self, generated_file: GeneratedFile ): 
        file_path = WORKSPACE / generated_file.path 
        file_path.parent.mkdir( parents=True, exist_ok=True ) 
        file_path.write_text( generated_file.content, encoding="utf-8" )