from abc import ABC, abstractmethod

class TTS(ABC):
    """
    Abstract base class for Text-to-Speech (TTS) implementations.
    
    All TTS classes should inherit from this base class and implement the abstract methods.
    """

    @abstractmethod
    def __init__(self):
        """
        Initialize the TTS instance.
        
        This method should set up any necessary configuration, models, or audio processing
        parameters specific to the TTS implementation.
        """
        pass

    @abstractmethod
    async def generate_speech(self, text: str) -> bytes:
        """
        Generate speech audio from text.
        
        Args:
        1. text: str - The text to generate speech for
        
        Returns:
            bytes: The generated speech audio
        """
        pass

    @abstractmethod
    def close(self):
        """
        Clean up resources used by the TTS instance.
        
        This method should properly close audio streams, release models,
        and clean up any other resources to prevent memory leaks.
        """
        pass
    
    def __del__(self):
        """
        Destructor that ensures resources are cleaned up.
        
        This method should call the close method to ensure resources are properly released.
        """
        self.close()
