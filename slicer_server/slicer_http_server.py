import http.server
import socketserver
import threading
import io
import contextlib
import time

PORT = 8000

class CodeExecutionHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/execute":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            self.wfile.flush()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        code = self.rfile.read(content_length).decode('utf-8')
        print(f"[HTTP] Executing code synchronously:\n{code}")

        output = io.StringIO()
        try:
            start_time = time.time()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                exec(code, globals())
            result = output.getvalue()
            elapsed = time.time() - start_time
            if elapsed > 5:
                result += f"\n[Warning] Code execution took {elapsed:.2f} seconds."
        except Exception as e:
            result = f"[Error] {str(e)}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [Slicer HTTP] Code executed. Result:\n{result}")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(result.encode('utf-8'))
        self.wfile.flush()

    def log_message(self, format, *args):
        return

def start_server():
    with socketserver.TCPServer(("", PORT), CodeExecutionHandler) as httpd:
        print(f"Serving on port {PORT} (POST to /execute)")
        httpd.serve_forever()

# Start the HTTP server in a background thread
if not hasattr(threading.current_thread(), "slicer_http_server_started"):
    threading.current_thread().slicer_http_server_started = True
    threading.Thread(target=start_server, daemon=True).start()
    print(f"Slicer HTTP server started in background thread on port {PORT}.") 