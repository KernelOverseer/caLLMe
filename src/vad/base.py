from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

class VAD(ABC):
    """
    Abstract base class for Voice Activity Detection (VAD) implementations.
    
    All VAD classes should inherit from this base class and implement the abstract methods.
    """
    
    @abstractmethod
    def __init__(self):
        """
        Initialize the VAD instance.
        
        This method should set up any necessary configuration, models, or audio processing
        parameters specific to the VAD implementation.
        """
        pass
    
    @abstractmethod
    async def listen(self) -> AsyncGenerator[bytes, None]:
        """
        Listen for speech activity and yield audio chunks when speech is detected.
        
        This method should:
        1. Continuously monitor audio input
        2. Detect when speech starts and ends
        3. Yield audio data (as bytes) when speech segments are complete
        
        Yields:
            bytes: Audio data containing detected speech segments
        """
        pass
    
    @abstractmethod
    def close(self):
        """
        Clean up resources used by the VAD instance.
        
        This method should properly close audio streams, release models,
        and clean up any other resources to prevent memory leaks.
        """
        pass
    
    def __del__(self):
        """
        Destructor that ensures resources are cleaned up.
        
        Default implementation calls close(). Subclasses can override
        if additional cleanup is needed.
        """
        try:
            self.close()
        except:
            # Ignore errors during destruction
            pass
    