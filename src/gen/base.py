from abc import ABC, abstractmethod
from typing import List, Dict

class Gen(ABC):
    """
    Abstract base class for Text Generation AI implementations.
    
    All Gen classes should inherit from this base class and implement the abstract methods.
    """
    
    @abstractmethod
    def __init__(self):
        """
        Initialize the Gen instance.
        
        This method should set up any necessary configuration, models, or audio processing
        parameters specific to the Gen implementation.
        """
        pass
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]] = []):
        """
        Generate text based on the given history.
        
        Args:
        1. messages: List[Dict[str, str]] - The history of messages
        
        Returns:
            Generator of text chunks as they are generated
        """
        pass
    
    @abstractmethod
    def close(self):
        """
        Clean up resources used by the Gen instance.
        
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