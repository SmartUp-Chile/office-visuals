# 🌈 Office Visual System

A professional, modular terminal visual effects system for the office.

## Features

- 🎨 **Modular Design**: Each visual is an independent module
- 🔄 **Auto-Discovery**: Automatically finds and loads all visuals
- 📊 **Rich Metadata**: Each visual includes author, version, and description
- 🚀 **Easy Execution**: Simple commands to run from anywhere
- 👥 **Collaborative**: Multiple contributors can add visuals
- ⚡ **Optimized**: Smooth 25 FPS with no flickering

## Quick Start

```bash
# Run the visual slideshow (super easy!)
./run_visuals

# List available visuals
./run_visuals --list

# Show help
./run_visuals --help
```

## Current Visuals

- **Aurora Ascension** by sat with agent window - Trippy aurora borealis patterns ascending upward with hopeful, exciting particle effects
- **Bouncing SmartUp** by Pablo - Purple double chevron bouncing around like the classic DVD logo with sparkle trails
- **Bad Apple ASCII** by gadana - Auto-downloads the legendary Bad Apple silhouette animation and renders it in ASCII
- **Digital Matrix Pro** by sat - Professional Matrix digital rain with multi-layered effects and realistic falling code
- **Intelligence** by sat - Trippy neural-spiral lattice evoking AGI/ASI emergence
- **Fiestas Patrias Chile** by Manu - Animated Chilean flag waving with star effects
- **Gemini's Awakening** by Sat - A neural core visualization representing AI creativity
- **Hyperbolic Purple** by sat - Flowing hyperbolic patterns with sophisticated purple gradients
- **Plasma Field** by sat - Classic plasma effect with flowing rainbow colors
- **Quantum Ghost** by Sat (Architeched by Gemini) - Strange Attractor Density Cloud - Ethereal & Mathematical
- **Hypnotic Spiral** by sat - Mesmerizing spiral patterns radiating from center
- **Möbius Strip** by sat - Elegant möbius strip transformation with smooth color transitions

## Adding New Visuals

1. Create a new `.py` file in `Office/Visuales/visuals/`
2. Inherit from `VisualBase` class
3. Define metadata and implement `generate_frame()` method
4. The system will automatically discover and include your visual

### Example Visual

```python
from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class MyVisual(VisualBase):
    metadata = {
        "name": "My Amazing Visual",
        "author": "Your Name",
        "version": "1.0",
        "description": "Description of your visual"
    }
    
    def generate_frame(self, width, height, time_offset):
        # Your visual logic here
        return pattern_array
```

## Architecture

```
Office/
└── Visuales/
    ├── main.py              # Main runner
    ├── core/
    │   ├── visual_base.py   # Base class for visuals
    │   ├── loader.py        # Auto-discovery system
    │   └── utils.py         # Shared utilities
    └── visuals/
        ├── aurora_ascension.py  # Aurora Ascension
        ├── bouncing_chevron.py  # Bouncing SmartUp
        ├── dj_set.py           # DJ Set Visual
        ├── hyperbolic_purple.py # Hyperbolic Purple
        ├── matrix.py           # Digital Matrix Pro
        ├── mobius.py           # Möbius Strip
        ├── plasma.py           # Plasma Field
        └── spiral.py           # Hypnotic Spiral
```

## Requirements

- Python 3.6+
- Terminal with 256-color support
- Unix-like system (Linux, macOS)

---

Made with ❤️ by the smartup team
