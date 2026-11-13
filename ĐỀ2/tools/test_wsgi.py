import io
import sys
from server import app

def test_endpoint(path, method="GET", body=b""):
    env = {
        "PATH_INFO": path,
        "REQUEST_METHOD": method,
        "wsgi.input": io.BytesIO(body),
        "CONTENT_LENGTH": str(len(body))
    }
    status_list = []
    headers_list = []
    def start_response(status, headers):
        status_list.append(status)
        headers_list.extend(headers)

    res = app(env, start_response)
    data = b"".join(res)
    print(f"[{method}] {path:<20} -> {status_list[0]} ({len(data):,} bytes)")
    return status_list[0]

if __name__ == "__main__":
    print("Testing WSGI Application Endpoints:")
    assert test_endpoint("/") == "200 OK"
    assert test_endpoint("/presentation") == "200 OK"
    assert test_endpoint("/favicon.ico") == "200 OK"
    assert test_endpoint("/api/status") == "200 OK"
    assert test_endpoint("/api/summary") == "200 OK"
    assert test_endpoint("/api/customers") == "200 OK"
    assert test_endpoint("/api/tasks") == "200 OK"
    assert test_endpoint("/api/escalations") == "200 OK"
    assert test_endpoint("/api/dnc") == "200 OK"
    assert test_endpoint("/api/audit") == "200 OK"
    assert test_endpoint("/api/run", method="POST", body=b'{"dataset":"standard"}') == "200 OK"
    print("All WSGI endpoints (GET & POST) verified 100% OK!")
