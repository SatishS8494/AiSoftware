from planner import planner 
from coder import coder 
from file_generator import generate_project

def main(): 
    print("=" * 60) 
    print("🏢 AI Software Company") 
    print("=" * 60) 
    requirement = input( "\n👤 Client Requirement:\n\n" ) 
    print("\n🧠 Planner Agent Working...\n") 
    plan = planner(requirement)
    print(plan)  
    print("👨‍💻 Coder Agent Working...\n")
    project = coder(plan) 
    folder = generate_project(project)
    print("\n✅ Project Generated Successfully\n") 
    print(folder)


if __name__ == "__main__": 
    main()