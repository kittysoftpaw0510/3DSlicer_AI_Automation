import os
import io
import contextlib
import time
import json
import slicer
import qt

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(PROJECT_DIR, "slicer_server", "slicer_command_result.json")

print("Slicer file-watcher started (QTimer polling, JSON). Waiting for commands...")
print(f"[Slicer] Watching file: {JSON_FILE}")

last_processed_timestamp = None
should_exit = False

def write_result_to_file(timestamp, result):
    result_data = {"timestamp": timestamp, "result": result}
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(result_data, f)

def poll_json_file():
    global last_processed_timestamp, should_exit
    if should_exit:
        print("[Slicer] Exiting server script (should_exit set).")
        return
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
                write_result_to_file(timestamp, result)

                print(f"[Slicer] Result written: {result.strip()}")
                last_processed_timestamp = timestamp
                # Exit server if Slicer is closing
                if "quit" in code.lower() or "close" in code.lower():
                    print("[Slicer] Detected quit command, exiting server...")
                    should_exit = True
                    return
        except Exception as e:
            print(f"[Slicer] Error processing JSON file: {e}")
    # Schedule next poll if not exiting
    if not should_exit:
        qt.QTimer.singleShot(100, poll_json_file)

def on_slicer_quit():
    global should_exit
    print("[Slicer] Slicer is quitting. Exiting server script...")
    should_exit = True

write_result_to_file(time.time(), "3DSlicer has been successfully opened.")

slicer.app.connect('aboutToQuit()', on_slicer_quit)
qt.QTimer.singleShot(0, poll_json_file) 