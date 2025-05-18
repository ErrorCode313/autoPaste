"""
Step Paster - A friendly tool to help you paste a series of numbered sentences
Created to be simple enough for anyone to use!

This program helps you:
1. Create a list of sentences with increasing numbers
2. Automatically copy each sentence to your clipboard
3. Detect when you paste the sentence (even in other applications!)
4. Optionally press Enter after pasting

Examples:
- "I climbed 1 step", "I climbed 2 steps", "I climbed 3 steps"...
- "Take medicine day 1", "Take medicine day 2"...
- "Exercise routine #1", "Exercise routine #2"...

To compile this into a standalone executable:
1. Install PyInstaller: pip install pyinstaller
2. Run: pyinstaller --onefile step_paster.py
"""

import pyperclip
import pyautogui
import time
import os
import platform
import sys
from pathlib import Path

FILENAME = "step_paster_list.txt"

def show_welcome():
    """Display a friendly welcome message"""
    print("\n" + "=" * 60)
    print("✨ WELCOME TO THE FRIENDLY STEP PASTER! ✨".center(60))
    print("=" * 60)
    print("\nThis helper makes a list of sentences with numbers that count up.")
    print("For example: 'I climbed 1 step', 'I climbed 2 steps', and so on.")
    print("\nIt will copy each sentence for you, and can even detect when you paste!")
    print("=" * 60 + "\n")

def get_user_input():
    """Get user input with friendly prompts and examples"""
    print("\n🌟 Let's build your sentences! 🌟\n")
    
    print("👇 Here's an example to help you understand:")
    print("   If you want: 'I ate 1 apple', 'I ate 2 apples', etc.")
    print("   • You would start with: 'I ate'")
    print("   • For one item: 'apple'") 
    print("   • For multiple items: 'apples'")
    print("   • You could end with: 'today' (optional)\n")

    # Get sentence structure
    prefix = input("1️⃣ What words should come BEFORE the number? (Example: I climbed)\n   ➤ ").strip()
    singular = input("\n2️⃣ What word to use when there's just ONE? (Example: step)\n   ➤ ").strip()
    plural = input("\n3️⃣ What word to use when there's MORE THAN ONE? (Example: steps)\n   ➤ ").strip()
    suffix = input("\n4️⃣ Any words to add at the END? (Example: today) [Press Enter to skip]\n   ➤ ").strip()

    # Get number range
    print("\n🔢 Now, let's decide what numbers you want to count through:\n")
    start = int(input("5️⃣ What number should we START with? (Example: 1)\n   ➤ "))
    end = int(input("\n6️⃣ What number should we END with? (Example: 10)\n   ➤ "))

    # Preview sentences
    sentence_template = f"{prefix} {{n}} {{word}}"
    if suffix:
        sentence_template += f" {suffix}"
    
    print("\n🔍 Here's a preview of your sentences:")
    for i in range(start, min(start + 3, end + 1)):
        word = singular if i == 1 else plural
        example = sentence_template.replace("{n}", str(i)).replace("{word}", word)
        print(f"   ✓ {example}")
    
    if end > start + 3:
        print(f"   ... and {end - (start + 3)} more sentences.")

    # Ask about pressing Enter automatically
    print("\n⌨️ After you paste your text, I can press Enter for you automatically.")
    press_enter = input("7️⃣ Should I press Enter for you after pasting? (y/n) ➤ ").strip().lower() == 'y'

    return sentence_template, singular, plural, start, end, press_enter

def pluralize(n, singular, plural):
    """Return singular or plural form based on number"""
    return singular if n == 1 else plural

def generate_lines(phrase, singular, plural, start, end):
    """Generate all sentences with proper pluralization"""
    return [
        phrase.replace("{n}", str(i)).replace("{word}", pluralize(i, singular, plural))
        for i in range(start, end + 1)
    ]

def write_to_file(lines):
    """Write all sentences to a file"""
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in lines)

def read_lines():
    """Read remaining lines from file"""
    if not os.path.exists(FILENAME):
        print(f"⚠️ Could not find the file '{FILENAME}'!")
        return []
    with open(FILENAME, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def write_remaining_lines(lines):
    """Write remaining lines back to file"""
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in lines)

def detect_paste_via_clipboard(timeout=999999):
    """Detect paste by monitoring clipboard changes"""
    print("📋 Watching for changes to what's copied...")
    try:
        initial_clipboard = pyperclip.paste()
        start_time = time.time()
        last_check_time = start_time
        
        while True:
            # Check clipboard every 100ms to reduce CPU usage
            current_time = time.time()
            if current_time - last_check_time < 0.1:
                time.sleep(0.01)
                continue
                
            last_check_time = current_time
            
            try:
                current_clipboard = pyperclip.paste()
                # If clipboard content changed, paste detected
                if current_clipboard != initial_clipboard:
                    print("✅ Paste detected! Moving to next sentence.")
                    return True
            except Exception as e:
                # Just continue if there's a clipboard error
                pass
            
            if time.time() - start_time > timeout:
                print("⏱️ Waited too long. Moving to next sentence.")
                return False
            
    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user.")
        return False

def detect_paste_via_keyboard(timeout=999999):
    """Try to detect Ctrl+V using platform-specific keyboard libraries"""
    system = platform.system()
    
    # Windows-specific implementation
    if system == "Windows":
        try:
            import keyboard
            print("⌨️ Waiting for you to press Ctrl+V anywhere...")
            
            paste_detected = [False]
            
            def on_paste():
                paste_detected[0] = True
            
            keyboard.add_hotkey('ctrl+v', on_paste)
            
            start_time = time.time()
            try:
                while not paste_detected[0]:
                    if time.time() - start_time > timeout:
                        print("⏱️ Waited too long. Using another method.")
                        keyboard.unhook_all()
                        return False
                    time.sleep(0.1)
                print("✅ Paste detected! Moving to next sentence.")
                return True
            except KeyboardInterrupt:
                print("\n🛑 Program stopped by user.")
                sys.exit(0)
            finally:
                keyboard.unhook_all()
        except ImportError:
            return False
            
    # macOS-specific implementation
    elif system == "Darwin":  # macOS
        try:
            from pynput import keyboard
            
            print("⌨️ Waiting for you to press Cmd+V anywhere...")
            paste_detected = [False]
            
            def on_press(key):
                try:
                    # Look for cmd+v keypress
                    if key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                        paste_detected[0] = True
                        return False
                except AttributeError:
                    pass
            
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            
            start_time = time.time()
            try:
                while not paste_detected[0]:
                    if time.time() - start_time > timeout:
                        print("⏱️ Waited too long. Using another method.")
                        listener.stop()
                        return False
                    time.sleep(0.1)
                
                print("✅ Paste detected! Moving to next sentence.")
                return True
            except KeyboardInterrupt:
                print("\n🛑 Program stopped by user.")
                listener.stop()
                sys.exit(0)
            finally:
                listener.stop()
        except ImportError:
            return False
    
    # Linux-specific implementation
    elif system == "Linux":
        try:
            import threading
            from Xlib import X, display, XK
            from Xlib.ext import record
            from Xlib.protocol import rq
            
            print("⌨️ Waiting for you to press Ctrl+V anywhere...")
            
            paste_detected = [False]
            ctrl_pressed = [False]
            
            def process_event(reply):
                if reply.category != record.FromServer:
                    return
                
                data = reply.data
                while len(data):
                    event, data = rq.EventField(None).parse_binary_value(
                        data, local_disp.display, None, None)
                    
                    if event.type == X.KeyPress:
                        keycode = event.detail
                        keysym = local_disp.keycode_to_keysym(keycode, 0)
                        
                        if keysym in [XK.XK_Control_L, XK.XK_Control_R]:
                            ctrl_pressed[0] = True
                        elif keysym == XK.XK_v and ctrl_pressed[0]:
                            paste_detected[0] = True
                    
                    elif event.type == X.KeyRelease:
                        keycode = event.detail
                        keysym = local_disp.keycode_to_keysym(keycode, 0)
                        
                        if keysym in [XK.XK_Control_L, XK.XK_Control_R]:
                            ctrl_pressed[0] = False
            
            def run_event_listener():
                disp = display.Display()
                root = disp.screen().root
                
                ctx = disp.record_create_context(
                    0,
                    [record.AllClients],
                    [{
                        'core_requests': (0, 0),
                        'core_replies': (0, 0),
                        'ext_requests': (0, 0, 0, 0),
                        'ext_replies': (0, 0, 0, 0),
                        'delivered_events': (0, 0),
                        'device_events': (X.KeyPress, X.KeyRelease),
                        'errors': (0, 0),
                        'client_started': False,
                        'client_died': False,
                    }]
                )
                
                disp.record_enable_context(ctx, process_event)
                disp.record_free_context(ctx)
            
            local_disp = display.Display()
            event_thread = threading.Thread(target=run_event_listener)
            event_thread.daemon = True
            event_thread.start()
            
            start_time = time.time()
            try:
                while not paste_detected[0]:
                    if time.time() - start_time > timeout:
                        print("⏱️ Waited too long. Using another method.")
                        return False
                    time.sleep(0.1)
                print("✅ Paste detected! Moving to next sentence.")
                return True
            except KeyboardInterrupt:
                print("\n🛑 Program stopped by user.")
                sys.exit(0)
        except (ImportError, AttributeError):
            return False
    
    return False

def wait_for_paste(timeout=999999):
    """Wait for paste event using the best available method"""
    print("\n⏳ I'm ready! Now paste this sentence where you need it.")
    print("   (Use Ctrl+V, or right-click → Paste, or Command+V on Mac)")
    
    # Try keyboard detection first, fall back to clipboard if needed
    if not detect_paste_via_keyboard(timeout):
        print("💡 Using clipboard monitoring instead...")
        detect_paste_via_clipboard(timeout)

def interactive_paste_loop(press_enter):
    """Main loop for copying, pasting and detecting pastes"""
    print("\n" + "=" * 60)
    print("🚀 READY TO START PASTING! 🚀".center(60))
    print("=" * 60)
    
    print("\n📋 Each sentence will be copied to your clipboard automatically.")
    print("📒 All your sentences are also saved in this file:")
    print(f"   {Path(FILENAME).resolve()}")
    print("\n💡 TIPS:")
    print("   • Switch to where you want to paste (e.g., a document or website)")
    print("   • Press Ctrl+V (or Command+V on Mac) to paste each sentence")
    print("   • The program will detect your paste and prepare the next sentence")
    print("   • Press Ctrl+C at any time to stop the program")
    
    print("\n🔍 Press Enter when you're ready to begin...")
    input()
    
    current_line = 1
    total_lines = len(read_lines())
    
    try:
        while True:
            lines = read_lines()
            if not lines:
                print("\n🎉 All done! You've pasted all your sentences.")
                input("\nPress Enter to exit...")
                break
    
            current = lines[0]
            pyperclip.copy(current)
            print(f"\n📎 [{current_line}/{total_lines}] Copied: {current}")
            
            # Wait for paste event
            wait_for_paste()
    
            if press_enter:
                print("⌨️ Pressing Enter for you...")
                time.sleep(0.2)
                pyautogui.press("enter")
    
            write_remaining_lines(lines[1:])
            current_line += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user.")
        print("\nYour progress has been saved. You can continue later!")
        sys.exit(0)

def check_for_existing_file():
    """Check if a previous session file exists and ask to resume"""
    if os.path.exists(FILENAME) and os.stat(FILENAME).st_size > 0:
        print("\n🔍 I found a saved list from before!")
        print(f"   The file is: {Path(FILENAME).resolve()}")
        
        # Show a preview of the content
        try:
            with open(FILENAME, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    print("\n   Preview of saved sentences:")
                    for i, line in enumerate(lines[:3]):
                        print(f"   {i+1}. {line}")
                    if len(lines) > 3:
                        print(f"   ... and {len(lines) - 3} more sentences.")
        except Exception:
            pass
            
        resume = input("\n🔄 Would you like to continue where you left off? (y/n) ➤ ").strip().lower() == 'y'
        
        if resume:
            press_enter = input("\n⌨️ Should I press Enter for you after pasting? (y/n) ➤ ").strip().lower() == 'y'
            return True, press_enter
    
    return False, False

def main():
    """Main function"""
    # Show welcome screen
    show_welcome()
    
    # Check system
    system = platform.system()
    print(f"💻 You're using: {system}")
    
    # Check for existing file
    resume_found, press_enter_resume = check_for_existing_file()
    
    if resume_found:
        interactive_paste_loop(press_enter_resume)
    else:
        # Get user input for new list
        phrase, singular, plural, start, end, press_enter = get_user_input()
        
        # Generate and save lines
        lines = generate_lines(phrase, singular, plural, start, end)
        write_to_file(lines)
        
        print(f"\n✅ Great! I've created {len(lines)} sentences for you.")
        interactive_paste_loop(press_enter)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Oops! Something went wrong: {e}")
        print("\nPlease try again. If the problem continues, contact support.")
        input("\nPress Enter to exit...")
        