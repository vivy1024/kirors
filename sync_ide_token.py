"""
Sync Kiro IDE token to kirors credentials.json
Run as scheduled task every 5 minutes.
"""
import json
import os
import sys
import urllib.request

TOKEN_FILE = os.path.expandvars(r"%USERPROFILE%\.aws\sso\cache\kiro-auth-token.json")
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "credentials.json")
KIRORS_ADMIN_URL = "http://localhost:5580/api/admin/credentials/1/reset"
KIRORS_ADMIN_KEY = "123456"

def main():
    if not os.path.exists(TOKEN_FILE):
        print("IDE token file not found, skipping")
        return

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    if not os.path.exists(CREDENTIALS_FILE):
        print("credentials.json not found")
        return

    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        creds = json.load(f)

    if not creds:
        print("credentials.json is empty")
        return

    current_access = creds[0].get("accessToken", "")
    new_access = token_data.get("accessToken", "")

    if current_access == new_access:
        print("Token unchanged, skipping")
        return

    # Update tokens for all credentials (same session, different regions)
    for cred in creds:
        cred["accessToken"] = token_data["accessToken"]
        cred["refreshToken"] = token_data["refreshToken"]
        cred["expiresAt"] = "2099-01-01T00:00:00.000Z"

    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f, indent=2, ensure_ascii=False)

    print(f"Token synced. New expires: {token_data['expiresAt']}")

    # Reset credential in kirors to pick up new token
    try:
        req = urllib.request.Request(
            KIRORS_ADMIN_URL,
            method="POST",
            headers={"x-api-key": KIRORS_ADMIN_KEY},
        )
        urllib.request.urlopen(req, timeout=5)
        print("kirors credential reset triggered")
    except Exception as e:
        print(f"Failed to reset kirors: {e}")

if __name__ == "__main__":
    main()
