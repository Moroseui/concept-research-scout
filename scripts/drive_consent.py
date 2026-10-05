#!/usr/bin/env python3
"""One-time operator-only Drive Picker consent, via loopback and SSH forwarding.

No live credentials are created merely by installing this script. Use a Production
personal OAuth desktop client, not an expiring Testing grant. Never pipe the URL,
callback, downloaded client file or token file into model conversations or Git.
"""

import argparse
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from wsgiref.simple_server import make_server, WSGIRequestHandler
from orchestrator.drive_evidence import SCOPE, private_write


def callback_fields(uri, expected_state):
    values = parse_qs(urlsplit(uri).query)
    if (
        values.get("state") != [expected_state]
        or "error" in values
        or len(values.get("code", [])) != 1
    ):
        raise ValueError("GOOGLE_CALLBACK_STATE_OR_CONSENT_REFUSED")
    ids = values.get("picked_file_ids", [""])[0].split(",")
    import re

    if not ids or any(not re.fullmatch("[A-Za-z0-9_-]{5,200}", i) for i in ids):
        raise ValueError("ACTUAL_PICKED_FILE_IDS_REQUIRED")
    return ids


def consent(client_file, destination, port):
    from google_auth_oauthlib.flow import InstalledAppFlow
    from orchestrator.phone_notifications import protected_read

    if os.getuid() != 0:
        raise ValueError("OPERATOR_SETUP_ADMIN_REQUIRED")
    destination = Path(destination)
    if (
        destination.exists()
        or destination.parent.is_symlink()
        or destination.parent.stat().st_mode & 0o077
    ):
        raise ValueError("FRESH_PROTECTED_CONSENT_DESTINATION_REQUIRED")
    client = json.loads(protected_read(client_file))
    installed = client.get("installed", {})
    if (
        installed.get("auth_uri")
        not in (
            "https://accounts.google.com/o/oauth2/auth",
            "https://accounts.google.com/o/oauth2/v2/auth",
        )
        or installed.get("token_uri") != "https://oauth2.googleapis.com/token"
    ):
        raise ValueError("GOOGLE_DESKTOP_CLIENT_REQUIRED")
    # Use the endpoint in Google's hosted Picker documentation; preserve the
    # original downloaded client file unchanged.
    client["installed"]["auth_uri"] = "https://accounts.google.com/o/oauth2/v2/auth"
    flow = InstalledAppFlow.from_client_config(
        client, [SCOPE], autogenerate_code_verifier=True
    )
    flow.redirect_uri = f"http://localhost:{port}/"
    url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        trigger_onepick="true",
        allow_multiple="true",
        include_granted_scopes="false",
    )
    response = []

    class Quiet(WSGIRequestHandler):
        def log_message(self, *args):
            pass

    def app(environ, start):
        uri = flow.redirect_uri + "?" + environ.get("QUERY_STRING", "")
        try:
            ids = callback_fields(uri, state)
        except ValueError:
            start("400 Bad Request", [("Content-Type", "text/plain")])
            return [b"Consent not accepted; return to the operator terminal."]
        response.append((uri, ids))
        start("200 OK", [("Content-Type", "text/plain")])
        return [
            b"Google selection received. Check the operator terminal for token exchange completion."
        ]

    with make_server("127.0.0.1", port, app, handler_class=Quiet) as server:
        server.timeout = 300
        print(
            "Open this private consent URL in your browser (do not paste it into chat):",
            flush=True,
        )
        print(url, flush=True)
        server.handle_request()
    if len(response) != 1:
        raise ValueError("CONSENT_NOT_COMPLETED_NO_CREDENTIAL_INSTALLED")
    uri, ids = response[0]
    flow.fetch_token(authorization_response=uri.replace("http://", "https://", 1))
    creds = flow.credentials
    if not creds.refresh_token or set(creds.granted_scopes or creds.scopes) != {SCOPE}:
        raise ValueError("PERSISTENT_NARROW_GRANT_REQUIRED")
    destination.mkdir(mode=0o700)
    private_write(destination / "oauth.json", json.loads(creds.to_json()))
    private_write(
        destination / "picked-files.json",
        {
            "file_ids": ids,
            "scope": SCOPE,
            "installation_status": "PENDING_REGISTRY_AND_SERVICE_REVIEW",
        },
    )
    print(
        json.dumps(
            {
                "status": "CONSENT_SAVED_PRIVATELY",
                "selected_files": len(ids),
                "installed_service": False,
            }
        )
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--production-client-confirmed",
        action="store_true",
        help="Operator checked OAuth publishing status is In production; not Testing",
    )
    p.add_argument("--client", required=True)
    p.add_argument("--private-destination", required=True)
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    if not args.production_client_confirmed:
        p.error(
            "Confirm Production status in Google Auth platform before issuing a persistent grant"
        )
    consent(args.client, args.private_destination, args.port)
