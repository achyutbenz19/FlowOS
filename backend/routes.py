from fastapi import FastAPI
from pydantic import BaseModel
from langchain_agent import Agent


app = FastAPI()
agent = Agent()


@app.get('/')
async def root():
    return "Welcome to NaturalOS"

class Query(BaseModel):
    question: str

@app.post('/query')
async def query(data: Query):
    response = agent.chat(data.question)['output']
    return {"response" : response}
