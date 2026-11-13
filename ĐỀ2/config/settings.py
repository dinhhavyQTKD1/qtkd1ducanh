"""
Settings & Path Management for Nam Việt AI Agent
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Support Vercel Serverless read-only filesystem (/tmp is writable)
IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
if IS_VERCEL:
    OUTPUTS_DIR = "/tmp/outputs"
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    # Copy pre-generated outputs to /tmp/outputs if not present
    src_outputs = os.path.join(BASE_DIR, "outputs")
    if os.path.exists(src_outputs):
        import shutil
        for item in os.listdir(src_outputs):
            s_file = os.path.join(src_outputs, item)
            d_file = os.path.join(OUTPUTS_DIR, item)
            if not os.path.exists(d_file) and os.path.isfile(s_file):
                try:
                    shutil.copy2(s_file, d_file)
                except Exception:
                    pass
else:
    OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

os.makedirs(DATA_DIR, exist_ok=True)

RULES_FILE = os.path.join(CONFIG_DIR, "business_rules.json")

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

