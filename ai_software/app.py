from graph import graph
from state import ProjectState

def main(): 
    requirement = input( "Requirement:\n" ) 
    state = ProjectState( requirement=requirement ) 
    result = graph.invoke(state)
    print() 
    print("=" * 60)
    print("Generated Files")

    print("=" * 60)

    for file in result["generated_files"]:

        print(file.path)

        print()

    print("Total Files")

    print(len(result["generated_files"]))
    execution = result["execution_result"]

    print()

    print("=" * 60)
    print("Execution Result")
    print("=" * 60)

    print("Success :", execution.success)
    print("Return Code :", execution.return_code)

    print()

    print("STDOUT")
    print(execution.stdout)

    print()

    print("STDERR")
    print(execution.stderr)

    report = result["bug_report"]

    print()

    print("=" * 60)
    print("Bug Report")
    print("=" * 60)

    print("Success :", report.success)
    print("Summary :", report.summary)
    print("Cause :", report.probable_cause)
    print("Recommendation :", report.recommendation)


if __name__ == "__main__": 
    main()