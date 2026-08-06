from langchain_groq import ChatGroq 
from config import * 


llm = ChatGroq( model="llama-3.1-8b-instant", temperature=0 )
