from tts.base import TTS
from groq import Groq
import os

class GroqPlayai(TTS):
    def __init__(self, model="playai-tts", voice="Quinn-PlayAI", api_key=os.getenv("GROQ_API_KEY")):
        self.groq = Groq(api_key=api_key)
        self.model = model
        self.voice = voice

    async def generate_speech(self, text: str) -> bytes:
        response = self.groq.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            response_format="wav")
        return response.content
    
    def close(self):
        pass