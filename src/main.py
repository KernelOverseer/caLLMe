import os
import logging
from conversation import Conversation

# Configure logging globally
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s │ %(name)-20s │ %(levelname)-8s │ %(message)s',
    datefmt='%H:%M:%S'
)

# Suppress verbose httpx logs from API clients
logging.getLogger('httpx').setLevel(logging.WARNING)

convo = Conversation(
    initial_history=[
        {"role": "system", "content": (
            "You are talking on the phone as a friendly Arch Linux enthusiast. "
            "Speak in short, conversational sentences, explaining Linux in general, "
            "highlighting Arch Linux's philosophy (KISS, rolling-release, user control), "
            "and advocating for free and open-source software. "
            "Keep the tone casual and enthusiastic, like chatting with a friend over the phone."
        )},
        {"role": "user", "content": "Hey, I keep hearing about Linux. What's the big deal?"},
    ]
)

async def main():
    conversation = convo
    await conversation.listen()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())