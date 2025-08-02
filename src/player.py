from abc import ABC, abstractmethod
import threading
import simpleaudio as sa
import io
import queue
import wave
import logging
import time
import os
from pydub import AudioSegment
logger = logging.getLogger(__name__)

class BasePlayer(ABC):
    @abstractmethod
    def play(self, audio: bytes):
        """
        Start playing the audio queue.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop the player. and clear the queue.
        """
        pass

    @abstractmethod
    def enqueue(self, audio: bytes):
        """
        Enqueue an audio to the player.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close the player. and clean up the resources.
        """
        pass

    def __del__(self):
        self.close()

class Player(BasePlayer):
    def __init__(self):
        self.queue = queue.Queue()
        self._stop_event = threading.Event()
        self.current_play_obj = None

        self.playing = False

        # Configuration
        self.wait_threshold = 3  # seconds to wait before starting hold music

        # Load hold / waiting music
        self.hold_wave_obj = None
        self.hold_play_obj = None
        self.hold_playing = False

        try:
            hold_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'waiting.mp3')
            hold_segment = AudioSegment.from_mp3(hold_path)

            # Apply a gentle 2-second fade-in so the music comes in smoothly
            hold_segment = hold_segment.fade_in(2000)

            # Convert AudioSegment to a WaveObject that simpleaudio can play
            self.hold_wave_obj = sa.WaveObject(
                hold_segment.raw_data,
                num_channels=hold_segment.channels,
                bytes_per_sample=hold_segment.sample_width,
                sample_rate=hold_segment.frame_rate,
            )
            logger.debug("Hold music loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load hold music: {e}")

        # Start worker thread after initialization is complete
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
    
    def enqueue(self, audio: bytes):
        self.queue.put(audio)

    def play(self):
        self._stop_event.clear()
        self.playing = True
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self):
        if self.current_play_obj:
            self.current_play_obj.stop()
            self.current_play_obj = None
        self._stop_event.set()
        self.playing = False
        with self.queue.mutex:
            self.queue.queue.clear()
    
    def close(self):
        self.stop()
        if self.thread.is_alive():
            self.thread.join()
    
    def wait(self):
        self.thread.join()

    def _worker(self):
        while True:
            try:
                # If a stop was requested, clean up and continue
                if self._stop_event.is_set():
                    self._stop_event.clear()

                    # Stop any ongoing playback (normal or hold)
                    if self.current_play_obj and self.current_play_obj.is_playing():
                        self.current_play_obj.stop()
                    if self.hold_play_obj and self.hold_play_obj.is_playing():
                        self.hold_play_obj.stop()

                    self.current_play_obj = None
                    self.hold_play_obj = None
                    self.hold_playing = False
                    continue

                # Try to get audio to play; timeout so we can decide on hold music
                try:
                    audio = self.queue.get(timeout=self.wait_threshold)
                except queue.Empty:
                    if not self.playing:
                        continue
                    # Queue has been empty for wait_threshold seconds
                    if self.hold_wave_obj is not None:
                        if not self.hold_playing:
                            logger.debug("Starting hold music")
                            self.hold_play_obj = self.hold_wave_obj.play()
                            self.hold_playing = True
                        # If hold music finished playing, loop it
                        elif self.hold_play_obj and not self.hold_play_obj.is_playing():
                            self.hold_play_obj = self.hold_wave_obj.play()
                    # No audio to play right now; loop back
                    continue

                # We have real audio to play; ensure hold music stops
                if self.hold_playing and self.hold_play_obj:
                    self.hold_play_obj.stop()
                    self.hold_playing = False
                    self.hold_play_obj = None

                logger.debug(f"Playing queued audio: {len(audio)} bytes")

                # Create a BytesIO object from the audio bytes
                wav_io = io.BytesIO(audio)

                # Use Python's wave module to read the WAV data
                with wave.open(wav_io, 'rb') as wave_read:
                    # Create WaveObject from the wave_read object
                    wave_obj = sa.WaveObject.from_wave_read(wave_read)

                # Play the queued audio
                self.current_play_obj = wave_obj.play()

                # Wait briefly to ensure loading
                time.sleep(0.05)

                # Wait for playback to complete or stop event
                while self.current_play_obj and self.current_play_obj.is_playing():
                    if self._stop_event.is_set():
                        self.current_play_obj.stop()
                        self.current_play_obj = None
                        self._stop_event.clear()
                        break
                    time.sleep(0.01)  # Prevent busy waiting

                logger.debug("Queued audio playback completed")

            except Exception as e:
                logger.error(f"Error playing audio: {e}")
                continue