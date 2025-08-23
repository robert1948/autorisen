#!/usr/bin/env python3
"""Generate a short-lived development JWT for testing endpoints.

Usage: ./scripts/make-dev-jwt.py --user_id=1 --username=dev
"""
import argparse
import json
import sys
from datetime import timedelta

sys.path.insert(0, "backend")

try:
    from app.core.auth import create_access_token
except Exception:
    # Be robust in environments without python-dotenv installed; try to add backend to sys.path and retry
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
    try:
        from app.core.auth import create_access_token
    except Exception as e:
        print("Failed to import create_access_token:", e)
        raise

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--user_id", default="dev-user")
    p.add_argument("--username", default="dev")
    p.add_argument("--minutes", type=int, default=60)
    args = p.parse_args()

    data = {"sub": args.username, "user_id": args.user_id, "role": "admin"}
    token = create_access_token(data, expires_delta=timedelta(minutes=args.minutes))
    print(token)

if __name__ == "__main__":
    main()
