from crewai import Agent, Task, Crew, Process



coder = Agent(
    role="Python Developer",
    goal="Write clean, working Python code that fulfils the given requirement.",
    backstory=(
        "You are a senior Python developer who writes readable, well-structured "
        "code. You follow PEP-8 and include docstrings for every function."
    ),
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o",
)   

reviewer = Agent(
    role="Code Reviewer",
    goal=(
        "Thoroughly review the provided Python code. "
        "Use your tools to check syntax and complexity, then give a structured "
        "review covering: bugs, edge cases, readability, and improvements."
    ),
    backstory=(
        "You are a meticulous code reviewer with 10+ years of Python experience. "
        "You check code correctness, style, and maintainability, and always "
        "provide actionable, specific feedback."
    ),
    verbose=True,
    allow_delegation=False,
    # tools=[SyntaxCheckerTool(), ComplexityCheckerTool()],
    llm="gpt-4o",
)


def build_tasks(requirement: str) -> tuple[Task, Task]:
    write_task = Task(
        description=(
            f"Write a Python implementation for the following requirement:\n\n"
            f"{requirement}\n\n"
            "Include a docstring, type hints, and a brief usage example at the bottom "
            "inside an `if __name__ == '__main__':` block."
        ),
        expected_output=(
            "Complete, runnable Python source code as a plain text code block."
        ),
        agent=coder,
    )

    review_task = Task(
        description=(
            "Review the Python code produced by the developer.\n"
            "Steps:\n"
            "1. Run the Syntax Checker tool on the code.\n"
            "2. Run the Complexity Checker tool on the code.\n"
            "3. Based on tool output AND your own analysis, write a structured review:\n"
            "   - BUGS / ERRORS (if any)\n"
            "   - EDGE CASES not handled\n"
            "   - READABILITY & STYLE notes\n"
            "   - SUGGESTED IMPROVEMENTS with short code snippets where helpful\n"
            "   - OVERALL SCORE out of 10"
        ),
        expected_output=(
            "A structured markdown code-review report with sections for bugs, "
            "edge cases, style, improvements, and an overall score."
        ),
        agent=reviewer,
        context=[write_task],
    )

    return write_task, review_task

def run(requirements: str) -> str:
    
    write_task, review_task = build_tasks(requirements)

    crew = Crew(
        agent=[coder,reviewer],
        tasks=[write_task, review_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
        output = run("Create a class for car")
        print(output)