from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from llm import llm
from models import Document
from rag import RAGRetriever

retriever = RAGRetriever()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful assistant answering questions from a knowledge base.

Use ONLY the information provided in the context to answer the question.

If the context does not contain enough information to answer the question,
say that you don't know based on the available information.

Do not make up facts.

Context:
{context}""",
        ),
        ("human", "{question}"),
    ]
)


def format_docs(docs: list[Document]):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)
