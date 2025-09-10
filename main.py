#!/usr/bin/env python3
import time
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loader import VisualLoader
from core.utils import get_terminal_size, hide_cursor, show_cursor, move_cursor_home, rgb_to_ansi, reset_color

class VisualRunner:
    """Main runner that displays visuals in rotation"""
    
    def __init__(self):
        visuals_dir = os.path.join(os.path.dirname(__file__), 'visuals')
        self.loader = VisualLoader(visuals_dir)
        self.current_visual_index = 0
        self.frame_count = 0
        self.pattern_duration = 150  # frames per visual
        
    def run(self):
        try:
            visuals = list(self.loader.get_all_visuals().values())
            if not visuals:
                print("❌ No visuals found! Add some .py files to the visuals/ directory.")
                return
            
            # Welcome message
            hide_cursor()
            print("🌈 OFFICE VISUAL SYSTEM 🌈")
            print(f"Found {len(visuals)} visuals:")
            self.loader.list_visuals()
            print("\nPress Ctrl+C to exit\n")
            time.sleep(3)
            
            # Get terminal size once
            width, height = get_terminal_size()
            height -= 1  # Reserve space for status line only
            
            while True:
                current_visual = visuals[self.current_visual_index]
                time_offset = self.frame_count * 0.08
                
                # Switch visuals periodically
                if self.frame_count > 0 and self.frame_count % self.pattern_duration == 0:
                    # Clear screen for smooth transition
                    from core.utils import clear_screen
                    clear_screen()
                    self.current_visual_index = (self.current_visual_index + 1) % len(visuals)
                    current_visual = visuals[self.current_visual_index]
                
                # Move cursor to top without clearing
                move_cursor_home()
                
                # Generate frame
                try:
                    pattern = current_visual.generate_frame(width, height, time_offset)
                    
                    # Build frame buffer
                    frame_buffer = []
                    for row in pattern:
                        frame_buffer.append(row)
                    
                    # Status info
                    meta = current_visual.get_metadata()
                    status = f"{rgb_to_ansi(255, 255, 0)}🎨 {meta['name']} by {meta['author']} | Frame: {self.frame_count} | Press Ctrl+C to exit{reset_color()}"
                    frame_buffer.append(status)
                    
                    # Display entire frame
                    print('\n'.join(frame_buffer), end="", flush=True)
                    
                except Exception as e:
                    print(f"❌ Error in visual {meta['name']}: {e}")
                    self.current_visual_index = (self.current_visual_index + 1) % len(visuals)
                
                self.frame_count += 1
                time.sleep(0.04)  # ~25 FPS
                
        except KeyboardInterrupt:
            show_cursor()
            print("\n\n✨ Thanks for watching the office visuals! ✨")
            sys.exit(0)
        except Exception as e:
            show_cursor()
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)

def main():
    """Entry point for the visual system"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            visuals_dir = os.path.join(os.path.dirname(__file__), 'visuals')
            loader = VisualLoader(visuals_dir)
            loader.list_visuals()
            return
        elif sys.argv[1] == '--help':
            print("Office Visual System")
            print("Usage:")
            print("  python main.py          - Run visual slideshow")
            print("  python main.py --list   - List available visuals")
            print("  python main.py --help   - Show this help")
            return
    
    runner = VisualRunner()
    runner.run()

if __name__ == "__main__":
    main()