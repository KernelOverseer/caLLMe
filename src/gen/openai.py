from typing import List, Dict
from gen.base import Gen
from openai import OpenAI
import os

class OpenAIGen(Gen):
    def __init__(self,
                 model="gpt-3.5-turbo",
                 api_key=os.getenv("OPENAI_API_KEY"),
                 temperature=0.7,
                 max_tokens=1024
                 ):
        self.openai = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: List[Dict[str, str]] = []):
        """
        Generate text based on the given history.
        
        Args:
        1. messages: List[Dict[str, str]] - The history of messages
        """
        try:
            response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                # temperature=self.temperature,
                # max_tokens=self.max_tokens,
                max_completion_tokens=self.max_tokens,
                stream=True
            )
            for chunk in response:
                    if chunk.choices[0].finish_reason == "stop":
                        break
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    def close(self):
        pass 