"""KORA single-user ChatGPT OAuth PKCE authentication.

Adapted from TimLL123456/custom-harness/auth.py; retains its local
~/.config/siwc-harness-demo/ credential format and host registration.
Do not use as a multi-user or remote-browser authentication service.
"""

import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import secrets
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import jwt
from jwt import PyJWKClient
import requests

API = "https://api.openai.com/v1"
AUTH_URL = "https://auth.openai.com/api/accounts/authorize"
TOKEN_URL = "https://auth.openai.com/api/accounts/oauth/token"
ISSUER = "https://auth.openai.com"
SCOPES = "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct"
HOME = Path.home() / ".config" / "siwc-harness-demo"
CREDS = HOME / "credentials.json"
HOST = HOME / "host.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def save_json(path, data):
    """Write atomically and restrict file permissions on POSIX systems."""
    HOME.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        HOME.chmod(0o700)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        if os.name == "posix":
            os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
    if os.name == "posix":
        path.chmod(0o600)


def host_id():
    saved = read_json(HOST)
    if saved:
        return saved["ext_agent_host_id"]
    value = f"urn:uuid:{uuid.uuid4()}"
    save_json(HOST, {"ext_agent_host_id": value})
    return value


def token_request(data):
    response = requests.post(TOKEN_URL, data={**data, "resource": API}, timeout=30)
    response.raise_for_status()
    return response.json()


def login(previous=None):
    """Register/sign in via a loopback OAuth PKCE callback."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).decode().rstrip("=")
    state, nonce = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    callback = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path != "/auth/callback":
                self.send_error(404)
                return
            params = {key: value[0] for key, value in parse_qs(parsed.query).items()}
            if params.get("state") != state:
                self.send_error(400, "Invalid state")
                return
            callback.update(params)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b"Sign-in received. Return to the terminal.")

        def log_message(self, *_args):
            pass  # Don't log authorization codes contained in callback URLs.

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        redirect = f"http://127.0.0.1:{server.server_port}/auth/callback"
        client_id = previous["client_id"] if previous else "dynamic_agent_client"
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect,
            "scope": SCOPES,
            "resource": API,
            "state": state,
            "nonce": nonce,
            "code_challenge_method": "S256",
            "code_challenge": challenge,
            "ext_agent_host_id": host_id(),
        }
        if not previous:
            params["agent_name_hint"] = "SIWC Harness Demo"
        url = AUTH_URL + "?" + urlencode(params)
        print("Opening ChatGPT sign-in in your browser...")
        if not webbrowser.open(url):
            print("Open this URL in a browser on this computer:\n" + url)
        server.timeout = 2
        deadline = time.monotonic() + 300
        while not callback and time.monotonic() < deadline:
            server.handle_request()

    if not callback:
        raise RuntimeError("Sign-in timed out")
    if callback.get("error"):
        raise RuntimeError("Sign-in was declined")
    if not callback.get("code"):
        raise RuntimeError("No authorization code was received")

    issued_id = callback.get("client_id")
    if previous:
        if issued_id and issued_id != client_id:
            raise RuntimeError("Unexpected OAuth client ID")
        issued_id = client_id
    elif not issued_id or not issued_id.startswith("oaiapp_"):
        raise RuntimeError("Registration did not return a valid client ID")

    tokens = token_request({
        "grant_type": "authorization_code",
        "client_id": issued_id,
        "code": callback["code"],
        "code_verifier": verifier,
        "redirect_uri": redirect,
    })
    key = PyJWKClient(ISSUER + "/.well-known/jwks.json").get_signing_key_from_jwt(
        tokens["id_token"]
    )
    claims = jwt.decode(
        tokens["id_token"], key.key, algorithms=["RS256", "ES256"],
        audience=issued_id, issuer=ISSUER,
        options={"require": ["exp", "iss", "aud", "sub"]},
    )
    if claims.get("nonce") != nonce:
        raise RuntimeError("ID token nonce mismatch")
    if previous and claims["sub"] != previous["subject"]:
        raise RuntimeError("Different ChatGPT account selected")
    scopes = tokens.get("scope", "").split()
    if "chatgpt.tokens.use.direct" not in scopes:
        raise RuntimeError("ChatGPT plan usage permission was not granted")

    saved = {
        "client_id": issued_id,
        "subject": claims["sub"],
        "email": claims.get("email"),
        "ext_agent_host_id": host_id(),
        "id_token": tokens["id_token"],
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "scopes": scopes,
        "expires_at": time.time() + int(tokens["expires_in"]),
    }
    save_json(CREDS, saved)
    print("Sign-in successful.")
    return saved


@contextmanager
def _credentials_refresh_lock():
    """Serialize rotated OAuth refresh tokens across terminal processes."""
    HOME.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        HOME.chmod(0o700)
    fd = os.open(HOME / "credentials.lock", os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(fd, "r+b") as handle:
        if os.name == "nt":
            import msvcrt
            # Windows byte-range locking requires a stable first byte.
            if not handle.read(1):
                handle.seek(0)
                handle.write(b"0")
                handle.flush()
            deadline = time.monotonic() + 120
            while True:
                try:
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("SIWC credential-refresh lock timed out")
                    time.sleep(0.2)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def access_token(saved):
    """Return a valid token; re-read disk *inside* the interprocess refresh lock."""
    if time.time() < float(saved.get("expires_at", 0)) - 120:
        return saved["access_token"]
    with _credentials_refresh_lock():
        # Another terminal may already have refreshed and rotated the token.
        current = read_json(CREDS)
        if not current:
            raise RuntimeError("SIWC credentials disappeared; sign in again")
        if time.time() >= float(current.get("expires_at", 0)) - 120:
            tokens = token_request({
                "grant_type": "refresh_token",
                "client_id": current["client_id"],
                "refresh_token": current["refresh_token"],
            })
            scopes = tokens.get("scope", " ".join(current.get("scopes", []))).split()
            if "chatgpt.tokens.use.direct" not in scopes:
                raise RuntimeError("Refreshed token lacks ChatGPT plan usage permission")
            current.update({
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "scopes": scopes,
                "expires_at": time.time() + int(tokens["expires_in"]),
            })
            save_json(CREDS, current)
        saved.update(current)
        return current["access_token"]

if __name__ == "__main__":
    # Explicit interactive opt-in; batch inference never launches a login browser.
    current = read_json(CREDS)
    login(previous=current)
