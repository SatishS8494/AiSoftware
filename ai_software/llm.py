from langchain_groq import ChatGroq

from config import settings


llm = ChatGroq(
    model=settings.model_name,
    api_key=settings.groq_api_key,
    temperature=0,
)

