import torch
import numpy as np
import asyncio
import logging
import wave
import io
from collections import deque

from vad.listener import Listener
from vad.base import VAD
logger = logging.getLogger(__name__)

class SileroVAD(VAD):
    def __init__(self, on_threshold=0.8, off_threshold=0.3, on_consecutive=5, off_consecutive=20, prebuffer_ms=500, min_recording_ms=1000):
        self.listener = Listener()
        self.vad_model, utils = torch.hub.load(
            'snakers4/silero-vad',
            'silero_vad',
            force_reload=False,
            onnx=False
        )
        (self.get_speech_timestamps, _, _, _, _) = utils
        
        self.on_threshold = on_threshold
        self.off_threshold = off_threshold
        self.on_consecutive = on_consecutive
        self.off_consecutive = off_consecutive
        self.speech_active = False
        self.on_count = self.off_count = 0

        # Calculate prebuffer size based on chunk duration
        # Each chunk is listener.chunk_ms (32ms by default)
        self.prebuffer_chunks = max(1, int(prebuffer_ms / self.listener.chunk_ms))
        logger.debug(f"Pre-buffer size: {self.prebuffer_chunks} chunks ({self.prebuffer_chunks * self.listener.chunk_ms}ms)")
        
        # Use deque with maxlen for efficient circular buffer
        self.prebuffer = deque(maxlen=self.prebuffer_chunks)
        self.speech_buffer = []
        self.min_recording_ms = min_recording_ms
    def _pcm_to_wav(self, pcm_data):
        """Convert PCM audio data to WAV format"""
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.listener.channels)  # mono
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(self.listener.rate)  # 16000 Hz
            wav_file.writeframes(pcm_data)
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()

    async def listen(self, interrupt: callable = None):
        for chunk in self.listener.listen():
            pcm = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768
            audio = torch.from_numpy(pcm)
            
            prob = self.vad_model(audio, self.listener.rate).max().item()
            
            # Always add chunk to prebuffer (circular buffer)
            self.prebuffer.append(chunk)

            speech_duration = (len(self.speech_buffer) - self.prebuffer_chunks) * self.listener.chunk_ms

            if not self.speech_active:
                if prob > self.on_threshold:
                    self.on_count += 1
                    if self.on_count >= self.on_consecutive:
                        self.speech_active = True
                        self.off_count = 0
                        logger.info("🗣️  Speech start")
                        # Add prebuffer chunks to speech_buffer when speech starts
                        self.speech_buffer.extend(list(self.prebuffer))
                else:
                    self.on_count = 0
            else:
                if prob < self.off_threshold:
                    self.off_count += 1
                    if self.off_count >= self.off_consecutive:
                        self.speech_active = False
                        # Process the accumulated speech buffer
                        if speech_duration >= self.min_recording_ms:
                            logger.info(f"🔇  Speech end (duration: {speech_duration}ms)")
                            pcm_audio = b''.join(self.speech_buffer)
                            wav_audio = self._pcm_to_wav(pcm_audio)
                            yield wav_audio
                            self.speech_buffer = []
                        else:
                            logger.info(f"🔇  Speech end (duration: {speech_duration}ms) not enough")
                            self.speech_buffer = []
                        self.on_count = 0
                else:
                    self.off_count = 0
                    if interrupt and speech_duration >= self.min_recording_ms:
                        interrupt()
                    
            # Add current chunk to speech buffer if speech is active
            if self.speech_active:
                self.speech_buffer.append(chunk)
            
            # Yield control back to the event loop
            await asyncio.sleep(0)
    
    def close(self):
        self.listener.close()

    def __del__(self):
        self.close()

if __name__ == "__main__":
    async def main():
        vad = SileroVAD()
        async for chunk in vad.listen_async():
            print(len(chunk))

    asyncio.run(main())