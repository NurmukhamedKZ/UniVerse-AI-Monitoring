# main.py
from fastapi import FastAPI, HTTPException
from langchain.agents import create_agent
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage, AIMessage
import logging

import os
from dotenv import load_dotenv

# Configure the logger to show INFO level logs and above
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s"
)

# Use __name__ (with double underscores)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()
model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
agent = create_agent(
    model=model
)

# Conversation memory (use Redis on Railway for prod)
conversation_history = {}

class EmailPayload(BaseModel):
    sender: str
    subject: str
    body: str
    session_id: str = "default"

class TeamsPayload(BaseModel):
    user: str
    message: str
    channel: str
    session_id: str = "default"

@app.post("/process-email")
async def process_email(payload: EmailPayload):
    history = conversation_history.get(payload.session_id, [])
    messages = [
        SystemMessage(content="You are an AI assistant that summarizes emails and suggests replies."),
        *history,
        HumanMessage(content=f"New email from {payload.sender}\nSubject: {payload.subject}\n\n{payload.body}")
    ]
    
    response = agent.invoke({"messages": messages})

    logger.info(f"Email response: {response['messages'][-1].content[:50]}...")
    
    reply = response["messages"][-1].content
    conversation_history[payload.session_id] = response["messages"][1:]
    
    return {"reply": reply}

@app.post("/process-teams")
async def process_teams(payload: TeamsPayload):
    history = conversation_history.get(payload.session_id, [])
    
    messages = [
        SystemMessage(content="You are a helpful Teams bot. Be concise."),
        *history,
        HumanMessage(content=f"{payload.user} in #{payload.channel}: {payload.message}")
    ]
    
    response = agent.invoke({"messages": messages})
    
    reply = response["messages"][-1].content
    conversation_history[payload.session_id] = response["messages"][1:]
    
    return {"reply": reply}

@app.get("/health")
async def health():
    return {"status": "ok"}