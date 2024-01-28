from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import AgentConfig
from agent import Agent
from stt import record_audio
from pathlib import Path
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteAgent:
    def __init__(
        self
    ) -> None:
        self.agent = Agent()
    
    def update_config(self, config: AgentConfig):
        chat_memory = self.agent.chat_memory
        self.agent = Agent(config)
        self.agent.chat_memory = chat_memory

route_agent = RouteAgent()


@app.get('/')
async def root():
    return "Welcome to NaturalOS"


@app.get('/config')
async def get_config():
    return route_agent.agent.config


@app.put('/config')
async def set_config(data: AgentConfig):
    route_agent.update_config(data)
    return route_agent.agent.config


class Query(BaseModel):
    question: str
    is_voice: bool = True


@app.post('/query')
async def query(data: Query):
    if data.question == "":
        question = record_audio("audio.wav")
    else:
        question = data.question
    response = route_agent.agent.chat(question, is_voice=data.is_voice)
    return {"response" : response}


@app.get('/chat_history')
async def chat_history():
    return route_agent.agent.get_chat_history()


@app.get('/workflows')
async def workflows():
    root_path = route_agent.agent.db.root_path
    # Ensure that root_path is a Path object
    if not isinstance(root_path, Path):
        root_path = Path(root_path)
    
    # List file names in the directory
    file_names = [file.name for file in root_path.iterdir() if file.is_file()]

    return file_names