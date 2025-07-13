from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from test import ShoppingAgent  # Import the class from test.py

app = FastAPI()
agent = ShoppingAgent()

# Allow frontend (Next.js) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or replace with your Next.js domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

@app.post("/chat")
def chat(message: Message):
    response = agent.run_conversation_chain(message.text)
    return {"reply": response}
