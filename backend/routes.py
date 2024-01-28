from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agent import Agent


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = Agent()


@app.get('/')
async def root():
    return "Welcome to NaturalOS"

class Query(BaseModel):
    question: str

@app.post('/query')
async def query(data: Query):
    response = agent.chat(data.question)
    return {"response" : response}

@app.get('/chat_history')
async def chat_history():
    return agent.get_chat_history()