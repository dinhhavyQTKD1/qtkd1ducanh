"""
Audit Logger for Nam Việt AI Agent
Records step-by-step tool calls, data transformations, rule evaluations, and agent reasoning.
"""
import os
import json
import datetime
from config.settings import OUTPUTS_DIR

class AuditLogger:
    def __init__(self, run_id=None):
        self.run_id = run_id or datetime.datetime.now().strftime("RUN-%Y%m%d-%H%M%S")
        self.logs = []
        self.log_file_txt = os.path.join(OUTPUTS_DIR, "audit_trail.log")
        self.log_file_json = os.path.join(OUTPUTS_DIR, "execution_log.json")

    def log(self, step: str, action: str, details: dict, rule_id: str = None, status: str = "SUCCESS"):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "run_id": self.run_id,
            "step": step,
            "action": action,
            "rule_id": rule_id or "N/A",
            "status": status,
            "details": details
        }
        self.logs.append(entry)
        
        # Write to human-readable log file immediately
        with open(self.log_file_txt, "a", encoding="utf-8") as f:
            f.write(f"[{entry['timestamp']}] [{entry['step']}] [{entry['action']}] "
                    f"Rule: {entry['rule_id']} | Status: {entry['status']}\n")
            f.write(f"  Details: {json.dumps(details, ensure_ascii=False)}\n\n")

    def save_json(self):
        with open(self.log_file_json, "w", encoding="utf-8") as f:
            json.dump({
                "run_id": self.run_id,
                "generated_at": datetime.datetime.now().isoformat(),
                "total_steps": len(self.logs),
                "events": self.logs
            }, f, ensure_ascii=False, indent=2)

    def print_summary(self):
        print(f"\n[AUDIT LOG] Completed run {self.run_id} with {len(self.logs)} traced events.")
        print(f"[AUDIT LOG] Detailed logs written to:\n  - {self.log_file_txt}\n  - {self.log_file_json}")

