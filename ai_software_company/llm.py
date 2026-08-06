from langchain_groq import ChatGroq 
from config import * 


llm = ChatGroq( model="llama-3.3-70b-versatile", temperature=0 )
