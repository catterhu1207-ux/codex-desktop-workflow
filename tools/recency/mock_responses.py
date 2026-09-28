"""Local, credential-free Responses fixture used only by isolated UI runs."""
import json
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class FixtureServer:
    def __init__(self):
        self.requests = []
        self.release = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
                owner.requests.append({'path': self.path, 'payload': payload, 'received': time.time()})
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                rid = 'resp_' + uuid.uuid4().hex
                iid = 'msg_' + uuid.uuid4().hex

                def send(kind, **fields):
                    record = {'type': kind, **fields}
                    self.wfile.write(('event: ' + kind + '\ndata: ' + json.dumps(record) + '\n\n').encode())
                    self.wfile.flush()

                try:
                    send('response.created', response={'id': rid, 'object': 'response', 'status': 'in_progress', 'output': []})
                    owner.release.wait(40)
                    item = {'id': iid, 'type': 'message', 'role': 'assistant', 'status': 'completed', 'content': [{'type': 'output_text', 'text': 'Synthetic local task completed.', 'annotations': []}]}
                    send('response.output_item.added', output_index=0, item={**item, 'status': 'in_progress', 'content': []})
                    send('response.content_part.added', output_index=0, item_id=iid, content_index=0, part={'type': 'output_text', 'text': '', 'annotations': []})
                    send('response.output_text.delta', output_index=0, item_id=iid, content_index=0, delta='Synthetic local task completed.')
                    send('response.output_item.done', output_index=0, item=item)
                    send('response.completed', response={'id': rid, 'object': 'response', 'status': 'completed', 'output': [item], 'usage': {'input_tokens': 10, 'output_tokens': 5, 'total_tokens': 15}})
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                    pass

            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"object":"list","data":[]}')

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()
