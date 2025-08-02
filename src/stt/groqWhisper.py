from groq import Groq
import os
from stt.base import STT

class GroqWhisper(STT):
    def __init__(self, model="whisper-large-v3-turbo", api_key=os.getenv("GROQ_API_KEY"), language="en"):
        self.groq = Groq(api_key=api_key)
        self.model = model
        self.language = language

    async def transcribe(self, audio: bytes) -> str:
        response = self.groq.audio.transcriptions.create(
            file=audio,
            model=self.model,
            language=self.language
        )
        return response.text
    
    def close(self):
        pass