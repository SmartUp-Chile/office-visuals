#!/usr/bin/env python3
import time
import sys
import os
import select
import termios
import tty

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.loader import VisualLoader
from core.utils import (
    get_terminal_size,
    hide_cursor,
    show_cursor,
    move_cursor_home,
    rgb_to_ansi,
    reset_color,
    clear_screen,
)

class VisualRunner:
    """Main runner that displays visuals in rotation"""
    
    def __init__(self, single_visual=None):
        visuals_dir = os.path.join(os.path.dirname(__file__), 'visuals')
        self.loader = VisualLoader(visuals_dir)
        self.current_visual_index = 0
        self.frame_count = 0
        self.pattern_duration = 500  # frames per visual
        self.single_visual = single_visual
        self.last_enter_time = 0.0
        self.double_tap_window = 0.5  # seconds
        self._orig_term_settings = None
        
    def run(self):
        try:
            all_visuals = self.loader.get_all_visuals()
            
            if self.single_visual:
                # Run single visual mode
                if self.single_visual not in all_visuals:
                    print(f"❌ Visual '{self.single_visual}' not found!")
                    print("Available visuals:")
                    for name in all_visuals.keys():
                        print(f"  • {name}")
                    return
                visuals = [all_visuals[self.single_visual]]
            else:
                # Run slideshow mode
                visuals = list(all_visuals.values())
                
            if not visuals:
                print("❌ No visuals found! Add some .py files to the visuals/ directory.")
                return
            
            # Welcome message
            hide_cursor()

            # Put terminal into cbreak mode to capture quick Enter taps without echo
            self._enable_cbreak_mode()
            if self.single_visual:
                print(f"🌈 RUNNING SINGLE VISUAL: {visuals[0].get_metadata()['name']} 🌈")
                print("Press Ctrl+C to exit\n")
                time.sleep(2)
            else:
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
                
                # Switch visuals periodically (only if not running single visual)
                if not self.single_visual and self.frame_count > 0 and self.frame_count % self.pattern_duration == 0:
                    # Clear screen for smooth transition
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
                    
                    # Status info with right alignment
                    meta = current_visual.get_metadata()
                    ai = meta.get('ai_creator')
                    ai_suffix = f" and {ai}" if ai else ""
                    left_text = f"{rgb_to_ansi(200, 150, 255)}🎨 {meta['name']} by {meta['author']}{ai_suffix}{reset_color()}"
                    right_text = (
                        f"{rgb_to_ansi(255, 180, 220)}"
                        f"Frame: {self.frame_count} | Enter x2 → next | Ctrl+C exit"
                        f"{reset_color()}"
                    )
                    
                    # Calculate padding for right alignment
                    # Account for ANSI color codes by counting visible characters only
                    left_visible = len(f"🎨 {meta['name']} by {meta['author']}{ai_suffix}")
                    right_visible = len("Frame: {} | Enter x2 → next | Ctrl+C exit".format(self.frame_count))
                    padding = max(0, width - left_visible - right_visible)
                    
                    status = left_text + " " * padding + right_text
                    frame_buffer.append(status)
                    
                    # Display entire frame
                    print('\n'.join(frame_buffer), end="", flush=True)
                    
                except Exception as e:
                    print(f"❌ Error in visual {meta['name']}: {e}")
                    self.current_visual_index = (self.current_visual_index + 1) % len(visuals)

                # Handle quick double-Enter to skip to the next visual
                self._handle_input(visuals)

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
        finally:
            self._restore_terminal()

    def _handle_input(self, visuals):
        """Check stdin for quick double-Enter and skip visual when detected."""
        if self.single_visual or not sys.stdin.isatty():
            return

        try:
            ready, _, _ = select.select([sys.stdin], [], [], 0)
        except (ValueError, OSError):  # stdin closed or invalid
            return

        while ready:
            try:
                char = sys.stdin.read(1)
            except (IOError, OSError):
                break

            now = time.time()
            if char in ("\n", "\r"):
                if now - self.last_enter_time <= self.double_tap_window:
                    self._skip_to_next_visual(visuals)
                    self.last_enter_time = 0.0
                else:
                    self.last_enter_time = now
            else:
                self.last_enter_time = 0.0

            # Drain any remaining buffered characters for this frame
            ready, _, _ = select.select([sys.stdin], [], [], 0)

    def _skip_to_next_visual(self, visuals):
        clear_screen()
        self.current_visual_index = (self.current_visual_index + 1) % len(visuals)
        self.frame_count = 0

    def _enable_cbreak_mode(self):
        """Put terminal in cbreak mode and disable echo so Enter taps don't litter the screen."""
        if not sys.stdin.isatty():
            return

        fd = sys.stdin.fileno()
        try:
            self._orig_term_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            attrs = termios.tcgetattr(fd)
            attrs[3] = attrs[3] & ~termios.ECHO  # lflag index
            termios.tcsetattr(fd, termios.TCSADRAIN, attrs)
        except termios.error:
            self._orig_term_settings = None

    def _restore_terminal(self):
        if self._orig_term_settings and sys.stdin.isatty():
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._orig_term_settings)
            except termios.error:
                pass

def main():
    """Entry point for the visual system"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            visuals_dir = os.path.join(os.path.dirname(__file__), 'visuals')
            loader = VisualLoader(visuals_dir)
            loader.list_visuals()
            return
        elif sys.argv[1] == '--single':
            if len(sys.argv) < 3:
                print("❌ Please specify a visual name after --single")
                print("Use --list to see available visuals")
                return
            visual_name = sys.argv[2]
            runner = VisualRunner(single_visual=visual_name)
            runner.run()
            return
        elif sys.argv[1].startswith('--debug'):
            # Debug: render a single frame of a specific visual
            # Usage: main.py --debug[=N] <visual name>
            # Examples:
            #   ./run_visuals --debug "Bouncing SmartUp"      -> frame 0
            #   ./run_visuals --debug=12 "Bouncing SmartUp"    -> frame 12
            arg = sys.argv[1]
            if '=' in arg:
                try:
                    frame_index = int(arg.split('=', 1)[1])
                except ValueError:
                    print("❌ Invalid --debug value. Use an integer, e.g., --debug=12")
                    return
            else:
                frame_index = 0

            if len(sys.argv) < 3:
                print("❌ Please specify a visual name after --debug")
                print("Use --list to see available visuals")
                return

            visual_name = sys.argv[2]
            visuals_dir = os.path.join(os.path.dirname(__file__), 'visuals')
            loader = VisualLoader(visuals_dir)
            all_visuals = loader.get_all_visuals()
            if visual_name not in all_visuals:
                print(f"❌ Visual '{visual_name}' not found!")
                print("Available visuals:")
                for name in all_visuals.keys():
                    print(f"  • {name}")
                return

            visual = all_visuals[visual_name]
            width, height = get_terminal_size()
            height -= 1
            time_offset = frame_index * 0.08
            try:
                pattern = visual.generate_frame(width, height, time_offset)
                print('\n'.join(pattern))
            except Exception as e:
                print(f"❌ Error in visual {visual.get_metadata().get('name', visual_name)}: {e}")
            return
        elif sys.argv[1] == '--help':
            print("Office Visual System")
            print("Usage:")
            print("  python main.py                    - Run visual slideshow")
            print("  python main.py --list             - List available visuals")
            print("  python main.py --single <name>    - Run single visual continuously")
            print("  python main.py --debug[=N] <name> - Print a single frame N (default 0)")
            print("  python main.py --help             - Show this help")
            return
    
    runner = VisualRunner()
    runner.run()

if __name__ == "__main__":
    main()
