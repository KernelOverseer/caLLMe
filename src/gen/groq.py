from typing import List, Dict
from gen.base import Gen
from groq import Groq
import os

class GroqGen(Gen):
    def __init__(self,
                 model="llama3-8b-8192",
                 api_key=os.getenv("GROQ_API_KEY"),
                 temperature=0.7,
                 max_tokens=1024,
                 stream=True):
        self.groq = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

    async def generate(self, messages: List[Dict[str, str]] = []):
        """
        Generate text based on the given history.
        
        Args:
        1. messages: List[Dict[str, str]] - The history of messages
        """
        try:
            if self.stream:
                response = self.groq.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=self.stream
            )
                for chunk in response:
                        if chunk.choices[0].finish_reason == "stop":
                            break
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
            else:
                response = self.groq.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    def close(self):
        pass