import os
import importlib.util
import inspect
from .visual_base import VisualBase

class VisualLoader:
    """Auto-discovers and loads visual modules"""
    
    def __init__(self, visuals_dir):
        self.visuals_dir = visuals_dir
        self.visuals = {}
        self.load_all_visuals()
    
    def load_all_visuals(self):
        """Scan visuals directory and load all visual classes"""
        if not os.path.exists(self.visuals_dir):
            print(f"Warning: Visuals directory {self.visuals_dir} not found")
            return
        
        for filename in os.listdir(self.visuals_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                self.load_visual_from_file(filename)
    
    def load_visual_from_file(self, filename):
        """Load a visual class from a Python file"""
        try:
            module_name = filename[:-3]  # Remove .py extension
            file_path = os.path.join(self.visuals_dir, filename)
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find visual classes in module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, VisualBase) and 
                    obj != VisualBase):
                    
                    visual_instance = obj()
                    meta = visual_instance.get_metadata()
                    visual_name = meta.get('name', name)
                    self.visuals[visual_name] = visual_instance
                    ai = meta.get('ai_creator')
                    ai_note = f" • AI: {ai}" if ai else ""
                    print(f"✓ Loaded visual: {visual_name} by {meta.get('author', 'Unknown')}{ai_note}")
        
        except Exception as e:
            print(f"✗ Failed to load {filename}: {e}")
    
    def get_all_visuals(self):
        """Get all loaded visuals"""
        return self.visuals
    
    def get_visual_by_name(self, name):
        """Get a specific visual by name"""
        return self.visuals.get(name)
    
    def list_visuals(self):
        """Print all available visuals"""
        if not self.visuals:
            print("No visuals loaded")
            return
        
        print("Available Visuals:")
        for name, visual in self.visuals.items():
            meta = visual.get_metadata()
            print(f"  • {name} v{meta.get('version', '1.0')} - {meta.get('description', 'No description')}")
            ai = meta.get('ai_creator')
            if ai:
                print(f"    Author: {meta.get('author', 'Unknown')} and {ai}")
            else:
                print(f"    Author: {meta.get('author', 'Unknown')}")
    
    def reload_visuals(self):
        """Reload all visuals (useful for development)"""
        self.visuals.clear()
        self.load_all_visuals()
