import os
from groq import Groq
from openai import OpenAI
from typing import List, Dict, Any, Union
import io

class OpennaiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided either as parameter or environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.text_model = "gpt-4o-mini"

    def generate_text(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate text from conversation history using OpenAI's LLM.
        
        Args:
            conversation_history: List of message dicts with 'role' and 'content' keys
                                Examples: [{"role": "user", "content": "Hello"}]
        
        Returns:
            Generated text response as string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=conversation_history,
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    def generate_text_streaming(self, conversation_history: List[Dict[str, str]]):
        """
        Generate text from conversation history using OpenAI's LLM.
        
        Args:
            conversation_history: List of message dicts with 'role' and 'content' keys
            
        Returns:
            Generator of text chunks as they are generated
        """
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=conversation_history,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].finish_reason == "stop":
                    break
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Error generating text streaming: {str(e)}")

class GroqClient:
    def __init__(self, api_key: str = None, language: str = "ar"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be provided either as parameter or environment variable")
        
        self.client = Groq(api_key=self.api_key)
        self.language = language
        # self.text_model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.text_model = "llama-3.1-8b-instant"
        # self.transcription_model = "whisper-large-v3"
        self.transcription_model = "whisper-large-v3-turbo"

        self.openai_client = OpennaiClient()

    def generate_text(self, conversation_history: List[Dict[str, str]]) -> str:
        # return self.openai_client.generate_text(conversation_history)
        """
        Generate text from conversation history using Groq's LLM.
        
        Args:
            conversation_history: List of message dicts with 'role' and 'content' keys
                                Examples: [{"role": "user", "content": "Hello"}]
        
        Returns:
            Generated text response as string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=conversation_history,
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    def generate_text_streaming(self, conversation_history: List[Dict[str, str]]):
        # yield from self.openai_client.generate_text_streaming(conversation_history)
        # return
        """
        Generate text from conversation history using Groq's LLM.
        
        Args:
            conversation_history: List of message dicts with 'role' and 'content' keys
            
        Returns:
            Generator of text chunks as they are generated
        """
        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=conversation_history,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].finish_reason == "stop":
                    break
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Error generating text streaming: {str(e)}")

    def transcribe_audio(self, audio_file: Union[str, bytes, io.IOBase]) -> str:
        """
        Transcribe audio file to text using Groq's Whisper model.
        
        Args:
            audio_file: Path to audio file, bytes, or file-like object
        
        Returns:
            Transcribed text as string
        """
        try:
            # Handle different input types
            if isinstance(audio_file, str):
                # If it's a file path, open it
                with open(audio_file, "rb") as f:
                    response = self.client.audio.transcriptions.create(
                        file=f,
                        model=self.transcription_model,
                        language=self.language
                    )
            elif isinstance(audio_file, bytes):
                # If it's bytes, create a file-like object
                audio_buffer = io.BytesIO(audio_file)
                audio_buffer.name = "audio.wav"  # Groq needs a filename
                response = self.client.audio.transcriptions.create(
                    file=audio_buffer,
                    model=self.transcription_model,
                    language=self.language
                )
            else:
                # Assume it's already a file-like object
                response = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.transcription_model,
                    language=self.language
                )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")

    def generate_speech(self, text: str, output_file: str = None) -> Union[str, bytes]:
        """
        Generate speech audio from text using Groq's TTS model.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (default: "Khalid-PlayAI")
            output_file: Optional path to save audio file
        
        Returns:
            If output_file is provided, returns the file path.
            Otherwise, returns the audio data as bytes.
        """
        try:
            if self.language == "ar":
                model = "playai-tts-arabic"
                voice = "Khalid-PlayAI"
            else:
                model = "playai-tts"
                voice = "Quinn-PlayAI"
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format="wav"
            )
            
            if output_file:
                # Save to file and return the file path
                response.write_to_file(output_file)
                return output_file
            else:
                # Return audio data as bytes
                return response.content
                
        except Exception as e:
            raise Exception(f"Error generating speech: {str(e)}")
