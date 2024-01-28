from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"project": "NaturalOS"}

@app.post('/query')
async def query(question: str):
    return {"response" : question}
