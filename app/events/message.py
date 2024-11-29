from app.main import app


@app.event("message")
async def handle_message_events(body, logger):
    logger.info(body)
