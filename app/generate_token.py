"""
generate_token.py — Run this ONCE locally to create a Google OAuth token
for Railway deployment.

Usage:
    python generate_token.py

It will:
  1. Open your browser for Google login
  2. Save token.pickle
  3. Print the GOOGLE_TOKEN_BASE64 value → paste it into Railway env vars
"""

import os
import pickle
import base64

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE   = "token.pickle"
CREDS_FILE   = "google_credentials.json"


def generate():
    creds = None

    # Try loading existing token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing existing token...")
        creds.refresh(Request())
    elif not creds or not creds.valid:
        # Interactive browser flow — works only locally
        if not os.path.exists(CREDS_FILE):
            raise FileNotFoundError(
                f"'{CREDS_FILE}' not found. Download it from Google Cloud Console → "
                "APIs & Services → Credentials → OAuth 2.0 Client IDs → Download JSON"
            )
        print("Opening browser for Google OAuth login...")
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

    # Save token.pickle
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)
    print(f"\n✅ token.pickle saved!")

    # Encode to base64 for Railway
    with open(TOKEN_FILE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    print("\n" + "=" * 60)
    print("📋 Copy this value into Railway → Variables:")
    print("=" * 60)
    print(f"\nVariable name:  GOOGLE_TOKEN_BASE64")
    print(f"Variable value: {b64}")
    print("\n" + "=" * 60)
    print("✅ Done! Paste the value above into Railway env vars.")
    print("   The token has a refresh_token so Railway will auto-renew it.")


if __name__ == "__main__":
    generate()
