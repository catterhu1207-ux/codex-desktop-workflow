import io
import json
import unittest
from unittest import mock

from codex_desktop_workflow import workflow


class Connection(io.BytesIO):
    def recv(self, size):
        return self.read(size)

    def sendall(self, payload):
        pass


class StartupProbeTests(unittest.TestCase):
    def evaluate(self, response):
        data = json.dumps(response).encode()
        frame = bytes([0x81, len(data)]) if len(data) < 126 else bytes([0x81, 126]) + len(data).to_bytes(2, "big")
        connection = Connection(b"HTTP/1.1 101 Switching Protocols\r\n\r\n" + frame + data)
        targets = io.BytesIO(json.dumps([{"type": "page", "url": "app://-/index.html", "webSocketDebuggerUrl": "ws://127.0.0.1:1234/devtools/page/test"}]).encode())
        with mock.patch.object(workflow.urllib.request, "urlopen", return_value=targets), mock.patch.object(workflow.socket, "create_connection", return_value=connection):
            return workflow._cdp_evaluate(1234, "test")

    def test_sent_command_is_not_a_successful_evaluation(self):
        self.assertFalse(self.evaluate({"id": 1, "result": {"result": {"value": False}}}))
        self.assertFalse(self.evaluate({"id": 1, "result": {"exceptionDetails": {"text": "not ready"}}}))
        self.assertTrue(self.evaluate({"id": 1, "result": {"result": {"value": True}}}))

    def test_navigation_waits_for_complete_document_and_bridge(self):
        import subprocess
        with mock.patch.object(workflow, "_cdp_evaluate", return_value=False) as evaluate:
            self.assertFalse(workflow._request_renderer_attestation(1234))
            expression = evaluate.call_args.args[1]
        script = """
const document = {readyState: 'loading'};
let scheduled = 0, callback;
const setTimeout = fn => { scheduled++; callback = fn; };
const location = {href: 'app://-/index.html'};
const expression = EXPRESSION;
const assert = value => { if (!value) throw Error('startup navigation race'); };
assert(eval(expression) === false && scheduled === 0);
document.readyState = 'complete';
assert(eval(expression) === false && scheduled === 0);
globalThis.electronBridge = {};
assert(eval(expression) === true && scheduled === 1 && location.href === 'app://-/index.html');
callback();
assert(location.href === 'app://-/local/codex-desktop-workflow-acceptance');
""".replace("EXPRESSION", json.dumps(expression))
        result = subprocess.run(["node", "-"], input=script, text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
