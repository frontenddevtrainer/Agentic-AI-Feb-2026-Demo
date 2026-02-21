# Anthrophic, Google Gemini, Ollma, Groq..
from langchain_openai import ChatOpenAI
# Input
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
# Output
from langchain_core.output_parsers import StrOutputParser
# Later...
from langchain_core.runnables import RunnablePassthrough

from dotenv import load_dotenv

import os

load_dotenv()

llm = ChatOpenAI(temperature=0.3, model="gpt-5.1")

def demo_basic_prompt():
    template = '''
        You are a helpful assistant who always replies cheerfully and with emojis 😄🎉
        Question: {question}
        Answer: 
    '''

    prompt = PromptTemplate(
        input_variables=["question"],
        template=template
    )

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({"question": "What is Agentic AI?"})

    print(result)

if __name__ == "__main__":
    demo_basic_prompt()