"""
Web Server & Vercel Serverless Entry Point for Nam Việt Software AI Agent
Supports:
1. Vercel ASGI: app = FastAPI() (when fastapi is available)
2. Vercel WSGI / Standard: app, application (WSGI callable)
3. Vercel BaseHTTPRequestHandler: class handler(BaseHTTPRequestHandler)
4. Localhost Standalone: HTTPServer on http://localhost:8000
Zero external dependencies required for local execution!
"""
import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

from config.settings import BASE_DIR, DATA_DIR, OUTPUTS_DIR, load_rules
from agent.orchestrator import NamVietAgentOrchestrator
from web.generate_dashboard import generate_dashboard

PORT = 8000

def load_file(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default if default is not None else {}
    return default if default is not None else {}

def get_dashboard_html():
    # Check /tmp/dashboard.html first (if updated on Vercel), else web/dashboard.html
    tmp_file = "/tmp/dashboard.html"
    if os.path.exists(tmp_file):
        try:
            with open(tmp_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass

    dashboard_file = os.path.join(BASE_DIR, "web", "dashboard.html")
    if not os.path.exists(dashboard_file):
        generate_dashboard()
    with open(dashboard_file, "r", encoding="utf-8") as f:
        return f.read()

def get_presentation_html():
    presentation_file = os.path.join(BASE_DIR, "web", "presentation.html")
    with open(presentation_file, "r", encoding="utf-8") as f:
        return f.read()

FAVICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="#f472b6"/><text y=".9em" x="20" font-size="70">🌸</text></svg>'.encode("utf-8")

# =============================================================================
# 1. BaseHTTPRequestHandler Implementation (handler & NamVietAPIHandler)
# =============================================================================
class handler(BaseHTTPRequestHandler):
    """
    Standard BaseHTTPRequestHandler.
    Vercel natively hooks into this class when named 'handler'.
    """
    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_content, status_code=200):
        body = html_content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html", "/dashboard"]:
            self._send_html(get_dashboard_html())

        elif path in ["/presentation", "/slides", "/slide"]:
            self._send_html(get_presentation_html())

        elif path == "/favicon.ico":
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(FAVICON_SVG)))
            self.end_headers()
            self.wfile.write(FAVICON_SVG)

        elif path == "/api/status":
            summary = load_file(os.path.join(OUTPUTS_DIR, "summary_report.json"), {})
            self._send_json({
                "status": "ONLINE",
                "service": "NamViet AI Lead Dispatcher",
                "version": "2.0.0",
                "port": PORT,
                "summary": summary
            })

        elif path == "/api/summary":
            self._send_json(load_file(os.path.join(OUTPUTS_DIR, "summary_report.json"), {}))

        elif path == "/api/customers":
            self._send_json(load_file(os.path.join(OUTPUTS_DIR, "master_customers.json"), []))

        elif path == "/api/tasks":
            self._send_json(load_file(os.path.join(OUTPUTS_DIR, "sales_task_assignments.json"), {}))

        elif path == "/api/escalations":
            self._send_json(load_file(os.path.join(OUTPUTS_DIR, "manager_escalations.json"), []))

        elif path == "/api/dnc":
            self._send_json(load_file(os.path.join(OUTPUTS_DIR, "do_not_contact.json"), []))

        elif path == "/api/audit":
            self._send_json(load_file(os.path.join(OUTPUTS_DIR, "execution_log.json"), {}))

        else:
            self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            payload = {}

        if path == "/api/run":
            dataset_type = payload.get("dataset", "standard")
            if dataset_type == "700_benchmark":
                target_file = os.path.join(DATA_DIR, "leads_700_benchmark.json")
            elif dataset_type == "uploaded":
                target_file = os.path.join(DATA_DIR, "uploaded_leads.json")
            else:
                target_file = os.path.join(DATA_DIR, "leads_input.json")

            if not os.path.exists(target_file):
                self._send_json({"error": f"Dataset file {target_file} not found"}, 400)
                return

            orchestrator = NamVietAgentOrchestrator(leads_file=target_file)
            results = orchestrator.execute_pipeline()
            generate_dashboard()

            self._send_json({
                "success": True,
                "message": f"AI Agent executed successfully with dataset '{dataset_type}'",
                "summary": results["summary"]
            })

        elif path == "/api/upload":
            leads_data = payload.get("leads", [])
            if not isinstance(leads_data, list) or len(leads_data) == 0:
                self._send_json({"error": "Payload must contain a non-empty 'leads' array"}, 400)
                return

            upload_file = os.path.join(DATA_DIR, "uploaded_leads.json")
            try:
                with open(upload_file, "w", encoding="utf-8") as f:
                    json.dump(leads_data, f, ensure_ascii=False, indent=2)
            except OSError:
                upload_file = "/tmp/uploaded_leads.json"
                with open(upload_file, "w", encoding="utf-8") as f:
                    json.dump(leads_data, f, ensure_ascii=False, indent=2)

            orchestrator = NamVietAgentOrchestrator(leads_file=upload_file)
            results = orchestrator.execute_pipeline()
            generate_dashboard()

            self._send_json({
                "success": True,
                "message": f"Uploaded {len(leads_data)} leads and executed AI Agent pipeline successfully!",
                "summary": results["summary"]
            })

        elif path == "/api/approve-escalation":
            cust_id = payload.get("customer_id")
            chosen_rep = payload.get("rep_name", "Nguyễn Văn An")

            escalations_file = os.path.join(OUTPUTS_DIR, "manager_escalations.json")
            escalations = load_file(escalations_file, [])
            updated = [e for e in escalations if e.get("customer_id") != cust_id]

            with open(escalations_file, "w", encoding="utf-8") as f:
                json.dump(updated, f, ensure_ascii=False, indent=2)

            generate_dashboard()
            self._send_json({
                "success": True,
                "customer_id": cust_id,
                "assigned_to": chosen_rep,
                "remaining_escalations": len(updated)
            })

        else:
            self.send_error(404, "Endpoint Not Found")

# Alias for backwards compatibility
NamVietAPIHandler = handler


# =============================================================================
# 2. FastAPI Integration (When FastAPI is installed on Vercel)
# =============================================================================
try:
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

if HAS_FASTAPI:
    app = FastAPI(
        title="Nam Việt Software AI Agent",
        description="Hệ thống AI Agent Sàng lọc & Điều phối Khách hàng B2B (AI301 - Đề 02)",
        version="2.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=HTMLResponse)
    @app.get("/index.html", response_class=HTMLResponse)
    @app.get("/dashboard", response_class=HTMLResponse)
    def fast_dashboard():
        return HTMLResponse(content=get_dashboard_html(), status_code=200)

    @app.get("/presentation", response_class=HTMLResponse)
    @app.get("/slides", response_class=HTMLResponse)
    @app.get("/slide", response_class=HTMLResponse)
    def fast_presentation():
        return HTMLResponse(content=get_presentation_html(), status_code=200)

    @app.get("/favicon.ico")
    def fast_favicon():
        return Response(content=FAVICON_SVG, media_type="image/svg+xml")

    @app.get("/api/status")
    def fast_status():
        summary = load_file(os.path.join(OUTPUTS_DIR, "summary_report.json"), {})
        return {
            "status": "ONLINE",
            "service": "NamViet AI Lead Dispatcher (FastAPI / Vercel)",
            "version": "2.0.0",
            "port": PORT,
            "summary": summary
        }

    @app.get("/api/summary")
    def fast_summary():
        return load_file(os.path.join(OUTPUTS_DIR, "summary_report.json"), {})

    @app.get("/api/customers")
    def fast_customers():
        return load_file(os.path.join(OUTPUTS_DIR, "master_customers.json"), [])

    @app.get("/api/tasks")
    def fast_tasks():
        return load_file(os.path.join(OUTPUTS_DIR, "sales_task_assignments.json"), {})

    @app.get("/api/escalations")
    def fast_escalations():
        return load_file(os.path.join(OUTPUTS_DIR, "manager_escalations.json"), [])

    @app.get("/api/dnc")
    def fast_dnc():
        return load_file(os.path.join(OUTPUTS_DIR, "do_not_contact.json"), [])

    @app.get("/api/audit")
    def fast_audit():
        return load_file(os.path.join(OUTPUTS_DIR, "execution_log.json"), {})

    @app.post("/api/run")
    async def fast_run(request: Request):
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        dataset_type = payload.get("dataset", "standard")
        if dataset_type == "700_benchmark":
            target_file = os.path.join(DATA_DIR, "leads_700_benchmark.json")
        elif dataset_type == "uploaded":
            target_file = os.path.join(DATA_DIR, "uploaded_leads.json")
        else:
            target_file = os.path.join(DATA_DIR, "leads_input.json")

        if not os.path.exists(target_file):
            return JSONResponse(status_code=400, content={"error": f"Dataset file {target_file} not found"})

        orchestrator = NamVietAgentOrchestrator(leads_file=target_file)
        results = orchestrator.execute_pipeline()
        generate_dashboard()
        return {
            "success": True,
            "message": f"AI Agent executed successfully with dataset '{dataset_type}'",
            "summary": results["summary"]
        }

    @app.post("/api/upload")
    async def fast_upload(request: Request):
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        leads_data = payload.get("leads", [])
        if not isinstance(leads_data, list) or len(leads_data) == 0:
            return JSONResponse(status_code=400, content={"error": "Payload must contain a non-empty 'leads' array"})

        upload_file = os.path.join(DATA_DIR, "uploaded_leads.json")
        try:
            with open(upload_file, "w", encoding="utf-8") as f:
                json.dump(leads_data, f, ensure_ascii=False, indent=2)
        except OSError:
            upload_file = "/tmp/uploaded_leads.json"
            with open(upload_file, "w", encoding="utf-8") as f:
                json.dump(leads_data, f, ensure_ascii=False, indent=2)

        orchestrator = NamVietAgentOrchestrator(leads_file=upload_file)
        results = orchestrator.execute_pipeline()
        generate_dashboard()
        return {
            "success": True,
            "message": f"Uploaded {len(leads_data)} leads and executed AI Agent pipeline successfully!",
            "summary": results["summary"]
        }

    @app.post("/api/approve-escalation")
    async def fast_approve(request: Request):
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        cust_id = payload.get("customer_id")
        chosen_rep = payload.get("rep_name", "Nguyễn Văn An")

        escalations_file = os.path.join(OUTPUTS_DIR, "manager_escalations.json")
        escalations = load_file(escalations_file, [])
        updated = [e for e in escalations if e.get("customer_id") != cust_id]

        with open(escalations_file, "w", encoding="utf-8") as f:
            json.dump(updated, f, ensure_ascii=False, indent=2)

        generate_dashboard()
        return {
            "success": True,
            "customer_id": cust_id,
            "assigned_to": chosen_rep,
            "remaining_escalations": len(updated)
        }

    application = app

else:
    # WSGI fallback when FastAPI is not installed
    def wsgi_app(environ, start_response):
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")

        if method == "OPTIONS":
            start_response("200 OK", [
                ("Access-Control-Allow-Origin", "*"),
                ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                ("Access-Control-Allow-Headers", "Content-Type")
            ])
            return [b""]

        if method == "GET":
            if path in ["/", "/index.html", "/dashboard"]:
                content = get_dashboard_html().encode("utf-8")
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(content)))])
                return [content]
            elif path in ["/presentation", "/slides", "/slide"]:
                content = get_presentation_html().encode("utf-8")
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(content)))])
                return [content]
            elif path == "/favicon.ico":
                start_response("200 OK", [("Content-Type", "image/svg+xml"), ("Content-Length", str(len(FAVICON_SVG)))])
                return [FAVICON_SVG]
            elif path == "/api/status":
                data = json.dumps({"status": "ONLINE", "service": "NamViet AI Lead Dispatcher", "version": "2.0.0"}).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]
            elif path == "/api/summary":
                data = json.dumps(load_file(os.path.join(OUTPUTS_DIR, "summary_report.json"), {})).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]
            elif path == "/api/customers":
                data = json.dumps(load_file(os.path.join(OUTPUTS_DIR, "master_customers.json"), [])).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]
            elif path == "/api/tasks":
                data = json.dumps(load_file(os.path.join(OUTPUTS_DIR, "sales_task_assignments.json"), {})).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]
            elif path == "/api/escalations":
                data = json.dumps(load_file(os.path.join(OUTPUTS_DIR, "manager_escalations.json"), [])).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]
            elif path == "/api/dnc":
                data = json.dumps(load_file(os.path.join(OUTPUTS_DIR, "do_not_contact.json"), [])).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]
            elif path == "/api/audit":
                data = json.dumps(load_file(os.path.join(OUTPUTS_DIR, "execution_log.json"), {})).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]

        elif method == "POST":
            content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
            body = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"
            try:
                payload = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                payload = {}

            if path == "/api/run":
                dataset_type = payload.get("dataset", "standard")
                if dataset_type == "700_benchmark":
                    target_file = os.path.join(DATA_DIR, "leads_700_benchmark.json")
                elif dataset_type == "uploaded":
                    target_file = os.path.join(DATA_DIR, "uploaded_leads.json")
                else:
                    target_file = os.path.join(DATA_DIR, "leads_input.json")

                orchestrator = NamVietAgentOrchestrator(leads_file=target_file)
                results = orchestrator.execute_pipeline()
                generate_dashboard()

                data = json.dumps({
                    "success": True,
                    "message": f"AI Agent executed successfully with dataset '{dataset_type}'",
                    "summary": results["summary"]
                }).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]

            elif path == "/api/upload":
                leads_data = payload.get("leads", [])
                upload_file = os.path.join(DATA_DIR, "uploaded_leads.json")
                try:
                    with open(upload_file, "w", encoding="utf-8") as f:
                        json.dump(leads_data, f, ensure_ascii=False, indent=2)
                except OSError:
                    upload_file = "/tmp/uploaded_leads.json"
                    with open(upload_file, "w", encoding="utf-8") as f:
                        json.dump(leads_data, f, ensure_ascii=False, indent=2)

                orchestrator = NamVietAgentOrchestrator(leads_file=upload_file)
                results = orchestrator.execute_pipeline()
                generate_dashboard()

                data = json.dumps({
                    "success": True,
                    "message": f"Uploaded {len(leads_data)} leads and executed AI Agent pipeline successfully!",
                    "summary": results["summary"]
                }).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]

            elif path == "/api/approve-escalation":
                cust_id = payload.get("customer_id")
                chosen_rep = payload.get("rep_name", "Nguyễn Văn An")
                escalations_file = os.path.join(OUTPUTS_DIR, "manager_escalations.json")
                escalations = load_file(escalations_file, [])
                updated = [e for e in escalations if e.get("customer_id") != cust_id]

                with open(escalations_file, "w", encoding="utf-8") as f:
                    json.dump(updated, f, ensure_ascii=False, indent=2)

                generate_dashboard()
                data = json.dumps({
                    "success": True,
                    "customer_id": cust_id,
                    "assigned_to": chosen_rep,
                    "remaining_escalations": len(updated)
                }).encode("utf-8")
                start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(data)))])
                return [data]

        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not Found"]

    app = wsgi_app
    application = wsgi_app


# =============================================================================
# 3. Localhost Standalone Runner
# =============================================================================
def is_port_in_use(p):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', p)) == 0

def run_server():
    global PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        PORT = int(sys.argv[1])
    elif "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            PORT = int(sys.argv[idx + 1])
    elif is_port_in_use(PORT):
        PORT = 8080
    if is_port_in_use(PORT):
        PORT = 8888

    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, handler)

    print("=" * 80)
    print("      CÔNG TY CỔ PHẦN PHẦN MỀM NAM VIỆT - AI AGENT LOCALHOST SERVER")
    print("=" * 80)
    print(f"[+] Server dang chay tai dia chi: http://localhost:{PORT}")
    print(f"[+] Mo trinh duyet (Chrome/Edge/Firefox) va truy cap: http://localhost:{PORT}")
    print(f"[+] Framework Backend: {'FastAPI (ASGI)' if HAS_FASTAPI else 'http.server (Zero-Dependency Standard Library)'}")
    print(f"[+] REST APIs san sang:")
    print(f"    - GET  /api/status        : Kiem tra trang thai server")
    print(f"    - GET  /api/summary       : Xem bao cao tong hop")
    print(f"    - GET  /api/customers     : Danh sach Master Customers")
    print(f"    - GET  /api/tasks         : Danh sach cong viec 8 NVKD")
    print(f"    - GET  /api/escalations   : Danh sach can Truong phong duyet")
    print(f"    - GET  /api/dnc           : Danh sach chan lien he (DNC)")
    print(f"    - GET  /api/audit         : Nhat ky truy vet kiem toan")
    print(f"    - POST /api/run           : Kich hoat chay Agent truc tiep")
    print(f"    - POST /api/upload        : Nap bo du lieu moi tu UI")
    print("-" * 80)
    print("[*] Nhan Ctrl+C de dung server khi hoan tat.")
    print("=" * 80)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Dung server localhost.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
