# 🎨 How to Create a New Visual

This guide will walk you through creating your own visual effects for the Office Visual System.

## 📁 File Structure

All visuals go in the `visuals/` directory as `.py` files:

```
office-visuals/
├── visuals/
│   ├── waves.py      # Ocean Waves
│   ├── spiral.py     # Hypnotic Spiral  
│   ├── plasma.py     # Plasma Field
│   ├── matrix.py     # Digital Matrix
│   ├── mobius.py     # Möbius Strip 3D
│   └── your_visual.py ← Your new visual goes here!
├── core/
│   ├── visual_base.py
│   ├── loader.py
│   └── utils.py
└── main.py
```

## 🚀 Quick Start Template

Create a new file in `visuals/` directory (e.g., `visuals/my_visual.py`):

```python
import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class MyVisual(VisualBase):
    """Description of what your visual does"""
    
    metadata = {
        "name": "My Amazing Visual",
        "author": "Your Name",  # ← Put your name here!
        "version": "1.0", 
        "description": "Brief description of your visual effect"
    }
    
    def __init__(self):
        # Initialize any variables your visual needs
        self.my_variable = 0
    
    def generate_frame(self, width, height, time_offset):
        # Your visual logic goes here
        pattern = []
        
        for y in range(height):
            row = ""
            for x in range(width):
                # Calculate what character and color to show at position (x, y)
                char = " "  # Default to space
                color = ""  # Default to no color
                
                # Your visual math here...
                # Use time_offset for animation
                # Use x, y for position-based effects
                
                row += color + char
            
            pattern.append(row + reset_color())
        
        return pattern
```

## 📋 Required Components

### 1. **Imports** (Copy these exactly)
```python
import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color
```

### 2. **Class Definition**
- Must inherit from `VisualBase`
- Class name should end with "Visual" (e.g., `MyVisual`, `FireVisual`)

### 3. **Metadata Dictionary**
```python
metadata = {
    "name": "Display Name",          # What users see
    "author": "Your Name",           # Your name!
    "version": "1.0",               # Version number
    "description": "What it does"    # Brief description
}
```

### 4. **generate_frame() Method**
This is where your visual magic happens!

**Parameters:**
- `width`: Terminal width in characters
- `height`: Terminal height in characters  
- `time_offset`: Animation time (increases continuously)

**Must return:** List of strings, one per row

## 🎨 Creating Visual Effects

### Colors
```python
# Create RGB colors
red_color = rgb_to_ansi(255, 0, 0)
green_color = rgb_to_ansi(0, 255, 0) 
blue_color = rgb_to_ansi(0, 0, 255)

# Dynamic colors
r = int(128 + 127 * math.sin(time_offset))
color = rgb_to_ansi(r, 100, 200)

# Always end rows with reset_color()
row += color + char + reset_color()
```

### Animation
```python
# Use time_offset for smooth animation
wave = math.sin(time_offset * 2.0)  # Oscillates -1 to 1
rotation = time_offset * 0.5        # Continuous rotation

# Position-based effects
distance = math.sqrt(x**2 + y**2)   # Distance from origin
angle = math.atan2(y, x)            # Angle from center
```

### Characters
```python
# ASCII characters
chars = [" ", ".", ":", "+", "*", "#", "@"]

# Unicode blocks  
blocks = ["░", "▒", "▓", "█"]

# Special characters
fancy = ["✦", "★", "◆", "●", "◇", "○"]
```

## 📖 Real Examples

### Simple Ripple Effect
```python
def generate_frame(self, width, height, time_offset):
    cx, cy = width // 2, height // 2
    pattern = []
    
    for y in range(height):
        row = ""
        for x in range(width):
            # Distance from center
            distance = math.sqrt((x - cx)**2 + (y - cy)**2)
            
            # Ripple wave
            wave = math.sin(distance * 0.5 - time_offset * 3)
            
            if wave > 0.5:
                char = "●"
                color = rgb_to_ansi(0, 255, 255)
            else:
                char = " "
                color = ""
            
            row += color + char
        
        pattern.append(row + reset_color())
    
    return pattern
```

### Rotating Pattern
```python
def generate_frame(self, width, height, time_offset):
    cx, cy = width // 2, height // 2
    pattern = []
    
    for y in range(height):
        row = ""
        for x in range(width):
            # Relative position
            dx, dy = x - cx, y - cy
            
            # Rotate coordinates
            angle = time_offset
            rx = dx * math.cos(angle) - dy * math.sin(angle)
            ry = dx * math.sin(angle) + dy * math.cos(angle)
            
            # Create pattern based on rotated coordinates
            if abs(rx) < 2 or abs(ry) < 2:
                char = "█"
                color = rgb_to_ansi(255, 100, 100)
            else:
                char = " "
                color = ""
            
            row += color + char
        
        pattern.append(row + reset_color())
    
    return pattern
```

## 🔥 Pro Tips

### Performance
- **Pre-calculate** expensive operations in `__init__()`
- **Use integers** for coordinates when possible
- **Limit complex calculations** - the visual runs at 25 FPS

### Visual Quality  
- **Use smooth transitions** between colors/characters
- **Add randomness** for organic feel: `random.random()`
- **Consider aspect ratio** - terminal characters are taller than wide
- **Test different terminal sizes** - your visual should work on any size

### Debugging
```python
# Add debug info (remove before final version)
if x == 0 and y == 0:
    print(f"Debug: time={time_offset:.2f}", file=sys.stderr)
```

### Mathematical Functions
```python
# Waves
wave = math.sin(x * 0.1 + time_offset)

# Spirals  
angle = math.atan2(y - cy, x - cx) + time_offset
radius = math.sqrt((x - cx)**2 + (y - cy)**2)

# Noise-like effects
noise = math.sin(x * 0.3) * math.cos(y * 0.2) * math.sin(time_offset)

# Circular patterns
circle = math.sin(math.sqrt((x - cx)**2 + (y - cy)**2) - time_offset)
```

## 🧪 Testing Your Visual

1. **Create your file** in `visuals/` directory
2. **Test it:**
   ```bash
   ./run_visuals --list  # Should show your visual
   ./run_visuals         # Should include it in rotation
   ```
3. **Debug if needed** - check for syntax errors or exceptions

## ✨ Final Checklist

Before sharing your visual:

- [ ] File is in `visuals/` directory with `.py` extension
- [ ] Inherits from `VisualBase`
- [ ] Has complete `metadata` dictionary with your name
- [ ] Implements `generate_frame()` method correctly
- [ ] Returns list of strings (one per row)
- [ ] Uses `reset_color()` at end of each row
- [ ] Tested with `./run_visuals`
- [ ] Looks awesome! 🎨

## 📚 Study Existing Visuals

Look at the existing visuals in `visuals/` to see different techniques:

- **`waves.py`** - Sine wave patterns
- **`spiral.py`** - Polar coordinates  
- **`plasma.py`** - Complex mathematical patterns
- **`matrix.py`** - Character-based animation with drops
- **`mobius.py`** - 3D mathematics and projection

## 🎯 Ideas for New Visuals

- Fire simulation
- Conway's Game of Life
- Mandelbrot/Julia sets
- 3D rotating objects
- Particle systems
- DNA helix
- Sound visualizer patterns
- Geometric kaleidoscope
- Rain/snow effects
- Digital clock/countdown

---

**Happy coding! Create something amazing! 🌈✨**

*Made with ❤️ by the smartup team*