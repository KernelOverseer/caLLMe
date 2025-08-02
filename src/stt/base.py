from abc import ABC, abstractmethod

class STT(ABC):
    """
    Abstract base class for Speech-to-Text (STT) implementations.
    
    All STT classes should inherit from this base class and implement the abstract methods.
    """

    @abstractmethod
    def __init__(self):
        """
        Initialize the STT instance.
        
        This method should set up any necessary configuration, models, or audio processing
        parameters specific to the STT implementation.
        """
        pass

    @abstractmethod
    async def transcribe(self, audio: bytes) -> str:
        """
        Transcribe audio data and return the text result.
        
        Args:
        1. audio: bytes - The audio data to transcribe
        
        Returns:
            str: The transcribed text result
        """
        pass

    @abstractmethod
    def close(self):
        """
        Clean up resources used by the STT instance.
        
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
