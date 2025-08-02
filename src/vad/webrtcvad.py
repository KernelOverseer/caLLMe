"""
This class implements webrtcvad for voice activity detection (VAD).
It uses the webrtcvad library to determine when speech starts and ends in an audio stream.

The webrtcvad class provides a method to listen on the microphone,
when the speech starts, it will start recording the audio, and once the speech ends,
it will stop recording and return the audio.
"""

import asyncio
from typing import List
import webrtcvad
import pyaudio
import logging
from vad.base import VAD
logger = logging.getLogger(__name__)

class WEBRTCVAD(VAD):
    def __init__(self):
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(1) # Aggressive mode
        self.pa = pyaudio.PyAudio()
        
        # Fixed: Use frame size that gives valid duration
        self.rate = 16000
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # For 20ms frames: 16000 * 0.02 = 320 samples
        self.frame_duration_ms = 20  # Valid: 10, 20, or 30 ms
        self.chunk = int(self.rate * self.frame_duration_ms / 1000)  # 320 samples

        self.min_speech_duration = 500 #milliseconds
        self.min_silence_duration = 1000 #milliseconds
        self.max_recording_duration = 10000 #milliseconds
        
        self.pa_config = {
            "chunk": self.chunk,
            "rate": self.rate,
            "channels": self.channels,
            "format": self.format
        }

        logger.debug(f"Opening stream with chunk size {self.chunk}")
        self.stream = self.pa.open(
            rate=self.rate,
            channels=self.channels,
            format=self.format,
            frames_per_buffer=self.chunk,
            input=True,
        )

    async def listen(self):
        """
        Listen on the microphone and return the audio when speech starts and ends.
        """
        logger.info("🎙️  Listening on microphone...")
        try:
            while True:
                data = self.stream.read(self.chunk)
                
                # Add error handling for frame processing
                try:
                    is_speech = self.vad.is_speech(data, self.rate)
                    
                    if is_speech:
                        logger.debug("Speech detected")
                        # TODO: Add your speech handling logic here
                    else:
                        logger.debug("No speech detected")
                        
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
                    continue
                    
                # Add break condition for testing
                await asyncio.sleep(0.001)  # Small delay for async cooperation
                
        except KeyboardInterrupt:
            logger.info("🛑 Stopping VAD...")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()


if __name__ == "__main__":

    async def main():
        vad = WEBRTCVAD()
        await vad.listen()

    asyncio.run(main())