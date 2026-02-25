from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()
model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Conversation memory (use Redis on Railway for prod)
conversation_history: dict[str, list] = {}


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


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/process-email")
async def process_email(payload: EmailPayload):
    history = conversation_history.get(payload.session_id, [])
    human_msg = HumanMessage(
        content=f"New email from {payload.sender}\nSubject: {payload.subject}\n\n{payload.body}"
    )
    messages = [
        SystemMessage(content="You are an AI assistant that summarizes emails and suggests replies."),
        *history,
        human_msg,
    ]

    response: AIMessage = model.invoke(messages)
    reply = response.content

    logger.info(f"Email response: {reply[:50]}...")

    conversation_history[payload.session_id] = [*history, human_msg, response]

    return {"reply": reply}


@app.post("/process-teams")
async def process_teams(payload: TeamsPayload):
    history = conversation_history.get(payload.session_id, [])
    human_msg = HumanMessage(
        content=f"{payload.user} in #{payload.channel}: {payload.message}"
    )
    messages = [
        SystemMessage(content="You are a helpful Teams bot. Be concise."),
        *history,
        human_msg,
    ]

    response: AIMessage = model.invoke(messages)
    reply = response.content

    conversation_history[payload.session_id] = [*history, human_msg, response]

    return {"reply": reply}


@app.get("/health")
async def health():
    return {"status": "ok"}