"""
get_youtube_token.py
────────────────────
Run this ONCE on your local machine to get your YouTube OAuth refresh token.
Then add the token to GitHub Secrets as YOUTUBE_REFRESH_TOKEN.

Usage:
    python get_youtube_token.py

Requirements:
    pip install google-auth-oauthlib
"""

from google_auth_oauthlib.flow import InstalledAppFlow


def main():
    print("=" * 55)
    print("  WildStrikeAI — YouTube OAuth Token Generator")
    print("=" * 55)
    print(
        "\nYou need a Google Cloud project with YouTube Data API v3 enabled."
        "\nCreate OAuth 2.0 credentials (Desktop app type) at:"
        "\nhttps://console.cloud.google.com/apis/credentials\n"
    )

    client_id = input("Paste your OAuth Client ID     : ").strip()
    client_secret = input("Paste your OAuth Client Secret : ").strip()

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    # Opens browser for Google sign-in — tries ports until one is free
    creds = None
    for port in [8085, 8090, 8091, 8092, 9000]:
        try:
            creds = flow.run_local_server(port=port, prompt="consent", access_type="offline")
            break
        except OSError:
            print(f"  Port {port} in use, trying next...")
    if creds is None:
        raise RuntimeError("Could not find a free port. Close other apps and retry.")

    print("\n" + "=" * 55)
    print("  SUCCESS — Add these 3 values to GitHub Secrets")
    print("=" * 55)
    print(f"\n  YOUTUBE_CLIENT_ID     = {client_id}")
    print(f"  YOUTUBE_CLIENT_SECRET = {client_secret}")
    print(f"  YOUTUBE_REFRESH_TOKEN = {creds.refresh_token}")
    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
