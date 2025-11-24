from abc import ABC, abstractmethod

class VisualBase(ABC):
    """Base class for all visual effects"""
    
    metadata = {
        "name": "Base Visual",
        "author": "sat",
        "version": "1.0",
        "description": "Base class for visual effects",
        # Optional: AI model that assisted/created this visual
        # If absent or empty, consumers should not display it
        "ai_creator": None,
    }
    
    @abstractmethod
    def generate_frame(self, width, height, time_offset):
        """Generate a single frame of the visual effect"""
        pass
    
    def get_metadata(self):
        """Get visual metadata"""
        return self.metadata
    
    def get_config(self):
        """Get visual configuration (can be overridden)"""
        return {}
