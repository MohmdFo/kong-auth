#!/usr/bin/env python3
"""
Sample service for testing Kong JWT authentication
This is a simple HTTP server that Kong will proxy requests to
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
from urllib.parse import urlparse, parse_qs

class SampleServiceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Get headers for debugging
        headers = dict(self.headers)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response_data = {
            "message": "Hello from Sample Service!",
            "timestamp": time.time(),
            "path": path,
            "method": "GET",
            "query_params": query_params,
            "headers": {
                "user_agent": headers.get('User-Agent', 'Unknown'),
                "content_type": headers.get('Content-Type', 'None'),
                "authorization": "Bearer ***" if headers.get('Authorization') else "None"
            },
            "kong_headers": {
                "x_consumer_id": headers.get('X-Consumer-ID', 'None'),
                "x_consumer_username": headers.get('X-Consumer-Username', 'None'),
                "x_authenticated_consumer": headers.get('X-Authenticated-Consumer', 'None')
            }
        }
        
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        try:
            body = json.loads(post_data.decode('utf-8')) if post_data else {}
        except json.JSONDecodeError:
            body = {"error": "Invalid JSON"}
        
        headers = dict(self.headers)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response_data = {
            "message": "POST request received",
            "timestamp": time.time(),
            "path": self.path,
            "method": "POST",
            "body": body,
            "headers": {
                "user_agent": headers.get('User-Agent', 'Unknown'),
                "content_type": headers.get('Content-Type', 'None'),
                "authorization": "Bearer ***" if headers.get('Authorization') else "None"
            },
            "kong_headers": {
                "x_consumer_id": headers.get('X-Consumer-ID', 'None'),
                "x_consumer_username": headers.get('X-Consumer-Username', 'None'),
                "x_authenticated_consumer": headers.get('X-Authenticated-Consumer', 'None')
            }
        }
        
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging to show requests"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8001):
    """Run the sample service server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SampleServiceHandler)
    print(f"Sample service running on http://localhost:{port}")
    print("Available endpoints:")
    print(f"  GET  http://localhost:{port}/")
    print(f"  GET  http://localhost:{port}/api/v1/status")
    print(f"  POST http://localhost:{port}/api/v1/data")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server() 