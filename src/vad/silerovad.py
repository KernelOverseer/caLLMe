import torch
import numpy as np
import asyncio
import logging

from vad.listener import Listener
from vad.base import VAD
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SileroVAD(VAD):
    def __init__(self, on_threshold=0.6, off_threshold=0.3, on_consecutive=3, off_consecutive=5):
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

        self.speech_buffer = []

    async def listen(self):
        for chunk in self.listener.listen():
            pcm = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768
            audio = torch.from_numpy(pcm)
            
            prob = self.vad_model(audio, self.listener.rate).max().item()
            if not self.speech_active:
                if prob > self.on_threshold:
                    self.on_count += 1
                    if self.on_count >= self.on_consecutive:
                        self.speech_active = True
                        self.off_count = 0
                        logger.info("🗣️  Speech start")
                else:
                    self.on_count = 0
            else:
                if prob < self.off_threshold:
                    self.off_count += 1
                    if self.off_count >= self.off_consecutive:
                        self.speech_active = False
                        self.on_count = 0
                        logger.info("🔇  Speech end")
                else:
                    self.off_count = 0
            if self.speech_active:
                self.speech_buffer.append(chunk)
            else:
                if self.speech_buffer:
                    yield b''.join(self.speech_buffer)
                    self.speech_buffer = []
    
    def close(self):
        self.listener.close()

    def __del__(self):
        self.close()

if __name__ == "__main__":
    async def main():
        vad = SileroVAD()
        async for chunk in vad.listen():
            print(len(chunk))

    asyncio.run(main())