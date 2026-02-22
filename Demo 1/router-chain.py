"""
LCEL Router Chain
=================
Implements a multi-chain routing pipeline using LangChain Expression Language (LCEL).

Flow:
  User message
    → [Classifier Chain]  — decides: "billing" | "support" | "general"
    → [LCEL Router]       — branches to the matching specialist chain
    → [Billing / Support / General Chain]
    → Response back to User

Concepts demonstrated:
  - Chain composition with the | operator
  - RunnableLambda for custom routing logic
  - RunnableBranch for conditional branching
  - Three specialist chains, each with its own system prompt
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough

from dotenv import load_dotenv

load_dotenv()

# ── Model ─────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# ── Output parser (shared) ────────────────────────────────────────────────────

parser = StrOutputParser()

# ── Step 1: Classifier Chain ──────────────────────────────────────────────────
# Reads the user message and returns exactly one label: billing | support | general

classifier_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a routing assistant. Classify the user's message into exactly one of "
     "these categories and reply with ONLY that single word (lowercase):\n"
     "  billing  — questions about payments, invoices, subscriptions, refunds, pricing\n"
     "  support  — technical issues, bugs, errors, how-to questions, account problems\n"
     "  general  — everything else (greetings, company info, feedback, etc.)"),
    ("human", "{message}"),
])

classifier_chain = classifier_prompt | llm | parser

# ── Step 2: Specialist Chains ─────────────────────────────────────────────────

# -- Billing --
billing_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly billing specialist. Help the customer with payment questions, "
     "invoices, subscription changes, refunds, and pricing. Be clear and concise."),
    ("human", "{message}"),
])
billing_chain = billing_prompt | llm | parser

# -- Support --
support_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert technical support agent. Help the customer troubleshoot issues, "
     "understand features, and resolve account problems. Provide step-by-step guidance."),
    ("human", "{message}"),
])
support_chain = support_prompt | llm | parser

# -- General --
general_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful and friendly general-purpose assistant for our company. "
     "Answer questions about the company, handle greetings, and address any topic "
     "not covered by billing or technical support."),
    ("human", "{message}"),
])
general_chain = general_prompt | llm | parser

# ── Step 3: Router (RunnableBranch) ───────────────────────────────────────────
# Receives {"message": str, "category": str} and dispatches to the right chain.

router = RunnableBranch(
    (lambda x: x["category"].strip().lower() == "billing",  billing_chain),
    (lambda x: x["category"].strip().lower() == "support",  support_chain),
    general_chain,   # default branch
)

# ── Step 4: Full Pipeline ─────────────────────────────────────────────────────
# 1. Keep the original message AND classify it in one step.
# 2. Pass both through the router.

full_pipeline = (
    RunnablePassthrough.assign(
        category=RunnableLambda(lambda x: classifier_chain.invoke({"message": x["message"]}))
    )
    | router
)

# ── Runner ────────────────────────────────────────────────────────────────────

def chat(message: str) -> str:
    """Send a message through the router pipeline and return the response."""
    return full_pipeline.invoke({"message": message})


def run_demo() -> None:
    test_messages = [
        "I was charged twice for my subscription last month, can you help?",
        "I keep getting a 500 error when I try to log in — what should I do?",
        "Hi! What does your company actually do?",
    ]

    for msg in test_messages:
        print("=" * 60)
        print(f"USER:  {msg}")

        # Show the category so we can verify routing
        category = classifier_chain.invoke({"message": msg}).strip().lower()
        print(f"ROUTE: [{category.upper()}]")
        print("-" * 60)

        response = chat(msg)
        print(f"AGENT: {response}")
        print()


if __name__ == "__main__":
    run_demo()
