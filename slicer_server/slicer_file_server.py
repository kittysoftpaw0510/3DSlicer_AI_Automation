import os
import io
import contextlib
import time
import json

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(PROJECT_DIR, "slicer_server", "slicer_command_result.json")

print("Slicer file-watcher started (polling, JSON). Waiting for commands...")
print(f"[Slicer] Watching file: {JSON_FILE}")

# --- Add this block to handle Slicer closing ---
should_exit = False
try:
    import slicer
    def on_slicer_quit():
        global should_exit
        print("[Slicer] Slicer is quitting. Exiting server script...")
        should_exit = True
    slicer.app.connect('aboutToQuit()', on_slicer_quit)
except Exception as e:
    print(f"[Slicer] Could not connect to aboutToQuit: {e}")
# --- End block ---

last_processed_timestamp = None

while True:
    if should_exit:
        break
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            timestamp = data.get("timestamp")
            code = data.get("code")
            
            # Only execute if there is code and new timestamp
            if code and timestamp != last_processed_timestamp:
                print(f"[Slicer] Executing command with timestamp: {timestamp}")
                output = io.StringIO()
                try:
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                        exec(code, globals())
                    result = output.getvalue()
                except Exception as e:
                    result = f"[Error] {str(e)}"
                
                # Write result with same timestamp
                result_data = {"timestamp": timestamp, "result": result}
                with open(JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(result_data, f)
                print(f"[Slicer] Result written: {result.strip()}")
                last_processed_timestamp = timestamp
                
                # Exit server if Slicer is closing
                if "quit" in code.lower() or "close" in code.lower():
                    print("[Slicer] Detected quit command, exiting server...")
                    time.sleep(1)  # Give Slicer time to close
                    break
                
        except Exception as e:
            print(f"[Slicer] Error processing JSON file: {e}")
    
    time.sleep(0.1)
    
    # Keep Slicer GUI responsive
    try:
        import slicer
        slicer.app.processEvents()
    except Exception:
        pass 