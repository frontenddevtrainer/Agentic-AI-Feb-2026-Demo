"""
LCEL Conditional Chain — Context Sufficiency Check
===================================================
Implements a conditional branching pipeline using LangChain Expression Language (LCEL).

Flow:
  User message (with optional context)
    → [Context Checker Chain]  — decides: "sufficient" | "insufficient"
    → [LCEL Branch]            — routes based on context availability
        ├── sufficient   → [Answer Chain]   — responds based on provided context
        └── insufficient → [Follow-up Chain] — asks clarifying questions

Concepts demonstrated:
  - Chain composition with the | operator
  - RunnableLambda for custom routing logic
  - RunnableBranch for conditional branching (True / False paths)
  - RunnablePassthrough.assign to enrich the input dict mid-pipeline
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough

from dotenv import load_dotenv

load_dotenv()

# ── Model ─────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
parser = StrOutputParser()

# ── Step 1: Context Checker Chain ─────────────────────────────────────────────
# Evaluates whether the user's message contains enough context to give a
# meaningful, specific answer.  Returns exactly one word: sufficient | insufficient

context_checker_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a context evaluator. Determine whether the user's message contains "
     "enough information to give a meaningful, specific answer.\n\n"
     "Reply with ONLY one of these two words (lowercase):\n"
     "  sufficient   — the message has enough context to answer specifically\n"
     "  insufficient — the message is vague, missing key details, or too broad\n\n"
     "Be strict: if any key detail is missing that would significantly change the "
     "answer, reply 'insufficient'."),
    ("human", "{message}"),
])

context_checker_chain = context_checker_prompt | llm | parser

# ── Step 2: Answer Chain  (True / sufficient branch) ─────────────────────────
# Used when the user HAS provided enough context.
# Answers based strictly on what the user said.

answer_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a knowledgeable and helpful assistant. The user has provided enough "
     "context in their message. Answer their question clearly and specifically, "
     "based on the information they gave. Do not invent details not implied by "
     "their message."),
    ("human", "{message}"),
])
answer_chain = answer_prompt | llm | parser

# ── Step 3: Follow-up Chain  (False / insufficient branch) ────────────────────
# Used when the user has NOT provided enough context.
# Acknowledges the question and asks 2-3 targeted clarifying questions.

followup_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant who needs more information before answering. "
     "The user's message lacks enough detail for a specific, useful response. "
     "Do NOT attempt to answer yet. Instead:\n"
     "1. Briefly acknowledge what the user is asking about.\n"
     "2. Explain in one sentence why you need more detail.\n"
     "3. Ask 2-3 concise, targeted follow-up questions to collect the missing context.\n"
     "Keep your tone friendly and conversational."),
    ("human", "{message}"),
])
followup_chain = followup_prompt | llm | parser

# ── Step 4: Conditional Branch (RunnableBranch) ───────────────────────────────
# Receives {"message": str, "context_status": str} and dispatches accordingly.

branch = RunnableBranch(
    (lambda x: x["context_status"].strip().lower() == "sufficient", answer_chain),
    followup_chain,   # default branch — insufficient context
)

# ── Step 5: Full Pipeline ─────────────────────────────────────────────────────
# 1. Keep the original message AND run the context check in one step.
# 2. Pass the enriched dict through the conditional branch.

full_pipeline = (
    RunnablePassthrough.assign(
        context_status=RunnableLambda(
            lambda x: context_checker_chain.invoke({"message": x["message"]})
        )
    )
    | branch
)

# ── Public interface ──────────────────────────────────────────────────────────

def chat(message: str) -> str:
    """Send a user message through the conditional pipeline and return the response."""
    return full_pipeline.invoke({"message": message})


# ── Demo ──────────────────────────────────────────────────────────────────────

def run_demo() -> None:
    test_messages = [
        # Sufficient context — should answer directly
        "I bought a Python course on Udemy on January 15th for $19.99 "
        "but I never received a receipt. How do I get one?",

        # Insufficient context — should ask follow-up questions
        "How do I fix the error?",

        # Sufficient context — should answer directly
        "My MacBook Pro M2 running macOS Sonoma crashes every time I open "
        "Photoshop 2024. I've already reinstalled it twice. What else can I try?",

        # Insufficient context — should ask follow-up questions
        "What's the best plan for me?",
    ]

    for msg in test_messages:
        print("=" * 70)
        print(f"USER:    {msg}")

        status = context_checker_chain.invoke({"message": msg}).strip().lower()
        print(f"CONTEXT: [{status.upper()}]")
        print("-" * 70)

        response = chat(msg)
        print(f"AGENT:   {response}")
        print()


if __name__ == "__main__":
    run_demo()
