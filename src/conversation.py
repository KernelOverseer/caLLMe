from vad.silerovad import SileroVAD
from stt.groqWhisper import GroqWhisper
from tts.groqPlayai import GroqPlayai
from gen.groq import GroqGen
from player import Player
import logging
import asyncio

logger = logging.getLogger(__name__)

class Conversation:
    def __init__(self,
                 vad=SileroVAD(),
                 stt=GroqWhisper(),
                 tts=GroqPlayai(),
                 gen=GroqGen(),
                 player=Player(),
                 max_audio_queue=2,
                 initial_history=[]
                 ):
        self.vad = vad
        self.stt = stt
        self.tts = tts
        self.gen = gen
        self.player = player
        self.history = initial_history
        self.max_audio_queue = max_audio_queue
        # Track the current response generation task
        self.current_response_task = None
    
    async def _yield_sentence(self, generator, min_length=50):
        sentence = ""
        separators = ['.', '?', '!', ',', '\n']
        async for token in generator:
            # Check if task was cancelled
            if asyncio.current_task().cancelled():
                logger.debug("Generation cancelled")
                return
                
            sentence += token
            if len(sentence.strip()) > min_length and sentence[-1] in separators:
                yield sentence
                sentence = ""
        if sentence:
            yield sentence

    async def generate_assistant_response(self, text: str):
        logger.debug("Generating assistant response")
        try:
            self.history.append({"role": "user", "content": text})
            async for sentence in self._yield_sentence(self.gen.generate(self.history)):
                # Check if task was cancelled between sentences
                if asyncio.current_task().cancelled():
                    logger.debug("Response generation cancelled")
                    return

                self.history.append({"role": "assistant", "content": sentence})
                logger.debug(f"Assistant sentence: {sentence}")
                
                # Wait until queue has space before generating speech
                while self.player.queue.qsize() >= self.max_audio_queue:
                    # Check if task was cancelled while waiting
                    if asyncio.current_task().cancelled():
                        logger.debug("Response generation cancelled while waiting for queue space")
                        return
                    
                    await asyncio.sleep(0.1)  # Wait 100ms before checking again
                
                speech = await self.tts.generate_speech(sentence)
                logger.debug(f"Speech enqueued")
                self.player.enqueue(speech)
        except asyncio.CancelledError:
            logger.debug("Response generation was cancelled")
            # Don't re-raise, just exit gracefully
        except Exception as e:
            logger.error(f"Error in generate_assistant_response: {e}")

    async def listen(self):
        logger.info("🎙️  Listening for voice input...")
        def interrupt():
            if self.current_response_task and not self.current_response_task.done():
                self.current_response_task.cancel()            
            # Stop and restart audio playback
            self.player.stop()
        
        self.player.stop()
        async for chunk in self.vad.listen(interrupt=interrupt):
            logger.debug("Audio received")
            
            # Cancel current response generation if running
            if self.current_response_task and not self.current_response_task.done():
                logger.debug("Cancelling current response generation")
                self.current_response_task.cancel()
            
            # Stop and restart audio playback
            self.player.stop()
            self.player.play()
            
            # Transcribe the new audio
            transcription = await self.stt.transcribe(chunk)
            logger.info(f"📝 User said: {transcription}")
            
            # Start new response generation in background
            self.current_response_task = asyncio.create_task(
                self.generate_assistant_response(transcription),
            )