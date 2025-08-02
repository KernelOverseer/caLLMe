import pyaudio
import asyncio
import concurrent.futures

class Listener:
    def __init__(self, rate=16000, chunk_ms=32, format=pyaudio.paInt16, channels=1):
        self.pyaudio = pyaudio.PyAudio()
        self.rate = rate
        self.chunk_ms = chunk_ms
        self.format = format
        self.channels = channels
        self.chunk = int(self.rate * self.chunk_ms / 1000)
        self.stream = self.pyaudio.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=self.chunk
        )

    def listen(self):
        while True:
            data = self.stream.read(self.chunk)
            yield data

    async def listen_async(self):
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while True:
                # Run the blocking read in a thread
                data = await loop.run_in_executor(executor, self.stream.read, self.chunk)
                yield data

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
    
    def __del__(self):
        self.close()
        self.pyaudio.terminate()