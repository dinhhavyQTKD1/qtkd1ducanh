"""
Vercel Serverless Function Entry Point for Nam Việt Software AI Agent
Exports: app, application, handler
Compatible with Vercel's @vercel/python runtime.
"""
import sys
import os

# Add root directory to sys.path so modules can be imported seamlessly on Vercel
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app, application, handler

# Explicit exports for Vercel
__all__ = ["app", "application", "handler"]

