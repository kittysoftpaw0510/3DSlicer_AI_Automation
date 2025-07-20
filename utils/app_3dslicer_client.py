import time
import os
import json

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(PROJECT_DIR, "slicer_server", "slicer_command_result.json")

class SlicerClient:
    def __init__(self, json_file=JSON_FILE):
        self.json_file = json_file

    def send_code(self, code: str, timeout: int = 30) -> str:
        """
        Writes a JSON object with timestamp and code to a file for Slicer to execute, then polls for the result with the matching timestamp.
        """
        timestamp = str(time.time())
        data = {"timestamp": timestamp, "code": code}
        
        # Write command to file
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print(f"[Client] Wrote command with timestamp: {timestamp}")
        
        # Poll for result
        start = time.time()
        while time.time() - start < timeout:
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    result_data = json.load(f)
                
                # Check if result has matching timestamp
                if (isinstance(result_data, dict) 
                    and result_data.get("timestamp") == timestamp 
                    and "result" in result_data):
                    return result_data["result"]
                    
            except Exception:
                pass
            
            time.sleep(0.05)
        
        return "[Timeout] No result from Slicer."
