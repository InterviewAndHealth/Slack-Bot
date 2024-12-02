import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from app import BOT_TOKEN, SIGNING_SECRET

logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t  %(message)s")
logging.getLogger("uvicorn.access").addFilter(
    lambda record: "GET / " not in record.getMessage()
)

app = AsyncApp(
    name="Slack Bot",
    token=BOT_TOKEN,
    signing_secret=SIGNING_SECRET,
)


app_handler = AsyncSlackRequestHandler(app)

api = FastAPI(
    title="Slack Bot",
    description="A Slack Bot for managing deployments and more!",
    version="0.1.0",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/")
async def root():
    return {"message": "Welcome to the Slack Bot!"}


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


import app.events
