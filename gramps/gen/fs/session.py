# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       Nick Hall
# Copyright (C) 2025-2026  Gabriel Rios
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
"""
session/auth bits for FamilySearch
handles env/profile setup, oauth, and the small request wrappers for the rest of gen.fs

useful env vars:
- GRAMPS_FS_DEBUG turns on debug logging
- GRAMPS_FS_ENV picks beta or prod
- GRAMPS_FS_AUTH_METHOD picks auto/webkit/loopback/manual
- GRAMPS_FS_AUTH_PROVIDER picks direct or foundation
- GRAMPS_FS_LISTENER_TIMEOUT controls the callback wait time
- GRAMPS_FS_BETA_APP_KEY / GRAMPS_FS_PROD_APP_KEY override app keys
- GRAMPS_FS_BETA_REDIRECT / GRAMPS_FS_PROD_REDIRECT override redirects
- GRAMPS_FS_FOUNDATION_BASE_URL points at the middleware base URL
- GRAMPS_FS_FOUNDATION_ACCESS_CODE supplies the per-user middleware key
"""

# -------------------------------------------------------------------------
#
# Future imports
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import base64
import hashlib
import logging
import os
import re
import secrets
import socket
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from typing import Any, ClassVar
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

# -------------------------------------------------------------------------
#
# Third-party modules
#
# -------------------------------------------------------------------------
import certifi
import requests

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.constfunc import win

LOG = logging.getLogger(__name__)
_DEBUG_LOGGING_CONFIGURED = False

GLOBAL_SESSION: "Session | None" = None
SESSION: "Session | None" = None

DEFAULT_LOOPBACK_REDIRECT = "http://127.0.0.1:57938/familysearch-auth"


def _debug_enabled() -> bool:
    val = os.environ.get("GRAMPS_FS_DEBUG", "").strip().lower()
    if val in ("1", "true", "yes", "on"):
        return True
    try:
        return bool(config.get("familysearch.debug"))
    except Exception:
        return False


def _configure_debug_logging() -> None:
    global _DEBUG_LOGGING_CONFIGURED

    if _DEBUG_LOGGING_CONFIGURED or not _debug_enabled():
        return

    LOG.setLevel(logging.DEBUG)
    if not LOG.handlers and not logging.getLogger().handlers:
        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter("[FS DEBUG %(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        )
        LOG.addHandler(handler)
        LOG.propagate = False

    _DEBUG_LOGGING_CONFIGURED = True


class FSException(Exception):
    pass


class FSPermission(Exception):
    pass


def _dbg(msg: str) -> None:
    if not _debug_enabled():
        return
    _configure_debug_logging()
    LOG.debug(msg)


def _safe(s: str | None, max_len: int = 900) -> str:
    if s is None:
        return ""
    s = str(s)
    return s if len(s) <= max_len else (s[:max_len] + "...(truncated)...")


def _mask(s: str | None, keep: int = 6) -> str:
    if not s:
        return ""
    s = str(s)
    if len(s) <= keep:
        return "*" * len(s)
    return s[:keep] + ("*" * (len(s) - keep))


_LOG_REDACTED = "redacted"
_SENSITIVE_LOG_KEYS = {
    "access_token",
    "api_key",
    "app_key",
    "client_id",
    "client_secret",
    "code",
    "code_challenge",
    "code_verifier",
    "email",
    "id_token",
    "ip_address",
    "refresh_token",
    "redirect_uri",
    "state",
    "token",
    "username",
}

_SENSITIVE_URL_RE = re.compile(
    r"(?i)([?&])(client_id|redirect_uri|state|code|code_challenge|code_verifier|access_token|refresh_token|id_token|ip_address)=([^&#]*)"
)
_SENSITIVE_ENCODED_URL_RE = re.compile(
    r"(?i)(%3[fF]|%26)(client_id|redirect_uri|state|code|code_challenge|code_verifier|access_token|refresh_token|id_token|ip_address)%3[dD]([^%#&]*)"
)


def _is_sensitive_log_key(key: str | None) -> bool:
    key = (key or "").strip().lower()
    if not key:
        return False
    if key in _SENSITIVE_LOG_KEYS:
        return True
    return "token" in key or "secret" in key


def _safe_log_value(key: str | None, value: Any, max_len: int = 220) -> str:
    if value is None:
        return ""
    text = str(value)
    if _is_sensitive_log_key(key):
        return _LOG_REDACTED
    return _safe(text, max_len)


def _safe_mapping_for_log(values: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in (values or {}).items():
        if isinstance(value, (list, tuple)):
            safe[key] = [_safe_log_value(key, item) for item in value]
        else:
            safe[key] = _safe_log_value(key, value)
    return safe


def _safe_url_for_log(url: str | None, max_len: int = 500) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        safe_qs = parse_qs(parsed.query, keep_blank_values=True)
        query = urlencode(_safe_mapping_for_log(safe_qs), doseq=True)
        fragment = _LOG_REDACTED if parsed.fragment else ""
        sanitized = urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                query,
                fragment,
            )
        )
        sanitized = _SENSITIVE_URL_RE.sub(r"\1\2=redacted", sanitized)
        sanitized = _SENSITIVE_ENCODED_URL_RE.sub(r"\1\2%3Dredacted", sanitized)
        return _safe(sanitized or url, max_len)
    except Exception:
        fallback = _SENSITIVE_URL_RE.sub(r"\1\2=redacted", url)
        fallback = _SENSITIVE_ENCODED_URL_RE.sub(r"\1\2%3Dredacted", fallback)
        return _safe(fallback, max_len)


def _safe_http_request_line_for_log(first_line: str | None, max_len: int = 350) -> str:
    first_line = (first_line or "").strip()
    if not first_line:
        return ""
    parts = first_line.split(" ")
    if len(parts) < 2:
        return _safe(first_line, max_len)
    method = parts[0]
    target = _safe_url_for_log(parts[1], max_len=max_len)
    rest = " ".join(parts[2:]).strip()
    safe_line = " ".join(part for part in (method, target, rest) if part)
    return _safe(safe_line, max_len)


def _cookie_summary(jar) -> str:
    try:
        items: list[str] = []
        for c in jar:
            items.append(f"{c.name}@{c.domain}")
        items = sorted(set(items))
        if not items:
            return "(none)"
        if len(items) > 25:
            return ", ".join(items[:25]) + f", ...(+{len(items) - 25})"
        return ", ".join(items)
    except Exception:
        return "(unavailable)"


def _cfg_get(key: str, default: Any = None) -> Any:
    try:
        return config.get(key)
    except Exception:
        return default


def _cfg_set(key: str, value: Any) -> None:
    try:
        config.set(key, value)
    except Exception:
        return


def _is_loopback_redirect(uri: str) -> bool:
    try:
        p = urlparse(uri)
        return p.hostname in ("127.0.0.1", "localhost")
    except Exception:
        return False


def _extract_redirect_params_from_text(text: str) -> dict[str, str]:
    """Pull oauth response params from pasted text or a full redirect URL."""
    text = (text or "").strip()
    if not text:
        return {}
    if text.startswith("http://") or text.startswith("https://"):
        try:
            qs = parse_qs(urlparse(text).query, keep_blank_values=True)
            return {k: (v[0] if v else "").strip() for k, v in qs.items()}
        except Exception:
            return {}
    return {"code": text}


def _extract_code_from_text(text: str) -> str:
    """Pull the auth code out of pasted text or a full redirect URL."""
    return (_extract_redirect_params_from_text(text).get("code", "") or "").strip()


def _urlsafe_b64_no_padding(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _generate_pkce_verifier() -> str:
    return secrets.token_urlsafe(64)


def _generate_pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return _urlsafe_b64_no_padding(digest)


class FamilySearchSession:
    """Small context holder the GUI can bind state onto"""

    def __init__(self, *args, **kwargs):
        self._dbstate = None
        self._uistate = None
        self._track = None
        self._last_person_handle = None

    def bind_context(self, dbstate=None, uistate=None, track=None, person_handle=None):
        if dbstate is not None:
            self._dbstate = dbstate
        if uistate is not None:
            self._uistate = uistate
        if track is not None:
            self._track = track
        elif uistate is not None:
            self._track = getattr(uistate, "track", None) or getattr(
                uistate, "_track", None
            )
        if person_handle:
            self._last_person_handle = person_handle


class NullStatusIndicator:
    """status indicator for the core sesh layer"""

    def __init__(self):
        self.state = "DISCONNECTED"
        self.detail = ""
        self.http = None

    def create_widget(self):
        return None

    def show_window(self, parent=None):
        return None

    def set(self, state: str, detail: str = "", http: int | None = None):
        self.state = state
        self.detail = detail or ""
        self.http = http


class Listener(threading.Thread):
    """listener for oauth redirects."""

    def __init__(self, host: str, port: int, expected_path: str, timeout_s: int = 300):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.expected_path = expected_path or "/"
        self.timeout_s = timeout_s
        self.result: dict[str, str] = {}
        self.error: str | None = None

    def run(self):
        try:
            _dbg(
                f"Listener starting; bind {self.host}:{self.port} "
                f"expected_path={self.expected_path!r} timeout={self.timeout_s}s"
            )
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(5)
                s.settimeout(self.timeout_s)

                try:
                    conn, addr = s.accept()
                except socket.timeout:
                    raise TimeoutError(
                        f"Callback not received within {self.timeout_s}s"
                    )

                _dbg(f"Listener accepted connection from {addr}")
                with conn:
                    raw = conn.recv(8192)
                    text = raw.decode("utf-8", errors="replace")
                    first_line = text.splitlines()[0] if text else ""
                    _dbg(
                        "Listener first line: "
                        f"{_safe_http_request_line_for_log(first_line, 350)}"
                    )

                    parts = first_line.split(" ")
                    req_path = parts[1] if len(parts) >= 2 else ""
                    path_only = req_path.split("?", 1)[0] if req_path else ""
                    query = req_path.split("?", 1)[1] if "?" in req_path else ""

                    if (
                        self.expected_path
                        and path_only
                        and path_only != self.expected_path
                    ):
                        _dbg(
                            f"Listener WARNING: unexpected path {path_only!r} "
                            f"expected {self.expected_path!r}"
                        )

                    qs = parse_qs(query, keep_blank_values=True)
                    self.result = {k: (v[0] if v else "") for k, v in qs.items()}
                    _dbg(
                        f"Listener parsed params: {_safe_mapping_for_log(self.result)}"
                    )

                    if "error" in self.result or "error_description" in self.result:
                        msg = (
                            "Access denied or error returned. You can close this tab.\n"
                        )
                    else:
                        msg = "Success! You can now return to Gramps.\n"

                    conn.sendall(b"HTTP/1.1 200 OK\r\n")
                    conn.sendall(f"Content-Length: {len(msg)}\r\n".encode("utf-8"))
                    conn.sendall(b"Content-Type: text/plain\r\n\r\n")
                    conn.sendall(msg.encode("utf-8"))
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            _dbg(f"Listener exception: {self.error}")


AUTH_AUTO = "auto"
AUTH_WEBKIT = "webkit"
AUTH_LOOPBACK = "loopback"
AUTH_MANUAL = "manual"

AUTH_PROVIDER_DIRECT = "direct"
AUTH_PROVIDER_FOUNDATION = "foundation"

ENV_BETA = "beta"
ENV_PROD = "prod"


@dataclass(frozen=True)
class EnvProfile:

    env: str
    fs_url: str
    ident_url: str
    api_url: str
    web_url: str
    app_key: str
    redirect: str


def _normalize_auth_provider(value: str) -> str:
    value = (value or AUTH_PROVIDER_DIRECT).strip().lower()
    if value == AUTH_PROVIDER_FOUNDATION:
        return AUTH_PROVIDER_FOUNDATION
    return AUTH_PROVIDER_DIRECT


def _normalize_base_url(value: str) -> str:
    return (value or "").strip().rstrip("/")


class Session(requests.Session):
    """Main FamilySearch session used by the core layer"""

    _shared: ClassVar["Session | None"] = None
    _last_instance: ClassVar["Session | None"] = None

    status_indicator: Any
    _status_state: str
    _status_detail: str
    _status_http: int | None
    _tools_window_shown: bool
    _auth_win: Any
    listener: Listener | None

    def __init__(self, server: int = 0, app_key: str = "", redirect: str = ""):
        super().__init__()

        self.verify = certifi.where()
        try:
            self.max_redirects = 10
        except Exception:
            pass

        self._legacy_server = int(server or 0)
        self._legacy_app_key = (app_key or "").strip()
        self._legacy_redirect = (redirect or "").strip()

        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.id_token: str | None = None
        self.foundation_base_url: str = _normalize_base_url(
            os.environ.get("GRAMPS_FS_FOUNDATION_BASE_URL", "").strip()
            or str(_cfg_get("familysearch.middleware.base-url", "") or "").strip()
        )
        self.foundation_access_code: str = (
            os.environ.get("GRAMPS_FS_FOUNDATION_ACCESS_CODE", "").strip()
            or str(_cfg_get("familysearch.middleware.access-code", "") or "").strip()
        )
        self.foundation_session_token: str = ""
        self.foundation_login_id: str = ""
        self._foundation_auth_payload: dict[str, Any] | None = None
        self.connected: bool = False
        self.last_probe_http: int | None = None
        self.last_probe_detail: str = ""
        self.username: str = ""
        self._oauth_code: str = ""
        self._oauth_error: str = ""
        self._oauth_state: str = ""
        self._pkce_verifier: str = ""
        self._pkce_challenge: str = ""

        self.oauth_scope: str = (
            os.environ.get("GRAMPS_FS_OAUTH_SCOPE", "").strip()
            or str(_cfg_get("familysearch.scope", "") or "").strip()
            or "profile email qualifies_for_affiliate_account country"
        )
        self.listen_timeout: int = int(
            os.environ.get("GRAMPS_FS_LISTENER_TIMEOUT", "300") or "300"
        )
        self.auth_provider: str = _normalize_auth_provider(
            os.environ.get("GRAMPS_FS_AUTH_PROVIDER", "").strip()
            or str(
                _cfg_get("familysearch.auth-provider", AUTH_PROVIDER_FOUNDATION) or ""
            )
        )

        self.status_indicator = NullStatusIndicator()
        self._status_state: str = "DISCONNECTED"
        self._status_detail: str = "No token yet"
        self._status_http: int | None = None
        self._tools_window_shown: bool = False
        self._auth_win: Any = None

        env = (
            os.environ.get("GRAMPS_FS_ENV", "").strip().lower()
            or str(_cfg_get("familysearch.env", "") or "").strip().lower()
        )
        if env not in (ENV_BETA, ENV_PROD):
            legacy_server = _cfg_get("familysearch.server", None)
            if legacy_server is None:
                legacy_server = self._legacy_server
            env = ENV_BETA if int(legacy_server or 0) == 0 else ENV_PROD

        self._auth_method_chosen: str = (
            os.environ.get("GRAMPS_FS_AUTH_METHOD", "").strip().lower()
            or str(_cfg_get("familysearch.auth_method", AUTH_AUTO) or AUTH_AUTO)
            .strip()
            .lower()
        )
        if self._auth_method_chosen not in (
            AUTH_AUTO,
            AUTH_WEBKIT,
            AUTH_LOOPBACK,
            AUTH_MANUAL,
        ):
            self._auth_method_chosen = AUTH_AUTO

        self._beta_profile = self._build_profile(ENV_BETA)
        self._prod_profile = self._build_profile(ENV_PROD)
        self._profile: EnvProfile = (
            self._beta_profile if env == ENV_BETA else self._prod_profile
        )
        self._apply_profile(self._profile, clear_state=False)

        self.listen_host = "127.0.0.1"
        self.listen_port = 57938
        self.listen_path = "/familysearch-auth"
        self.listener: Listener | None = None
        self._auth_ui_cancelled: bool = False
        self._closing_auth_window: bool = False
        self._recompute_listener()

        global GLOBAL_SESSION, SESSION
        GLOBAL_SESSION = self
        SESSION = self
        try:
            Session._shared = self
            Session._last_instance = self
        except Exception:
            pass

        self._set_status("DISCONNECTED", "No token yet")

        app_key_log = (
            "hidden-by-foundation"
            if self._using_foundation_middleware()
            else _mask(self.app_key)
        )
        _dbg(
            "Session initialized: "
            f"env={self._profile.env} auth_provider={self.auth_provider} "
            f"fs_url={self.fs_url} ident_url={self.ident_url} api_url={self.api_url} "
            f"app_key={app_key_log} redirect={self.redirect} scope={self.oauth_scope!r}"
        )

    @classmethod
    def from_config(cls) -> "Session":
        """Build a session from config-backed values."""
        legacy_server = _cfg_get("familysearch.server", 0)
        legacy_app = _cfg_get("familysearch.app-key", "") or ""
        legacy_redirect = (
            _cfg_get("familysearch.redirect", "") or DEFAULT_LOOPBACK_REDIRECT
        )
        return cls(int(legacy_server or 0), str(legacy_app), str(legacy_redirect))

    def _build_profile(self, env: str) -> EnvProfile:
        """Build one beta/prod profile from env + config values."""
        env = (env or "").strip().lower()
        if env not in (ENV_BETA, ENV_PROD):
            env = ENV_PROD

        if env == ENV_BETA:
            fs_url = "https://beta.familysearch.org/"
            ident_url = "https://identbeta.familysearch.org/"
            api_url = "https://apibeta.familysearch.org/"
            web_url = "https://beta.familysearch.org/"

            app_key = (
                os.environ.get("GRAMPS_FS_BETA_APP_KEY", "").strip()
                or str(_cfg_get("familysearch.beta.app_key", "") or "").strip()
                or str(_cfg_get("familysearch.app-key", "") or "").strip()
                or (self._legacy_app_key if int(self._legacy_server or 0) == 0 else "")
            ).strip()

            redirect = (
                os.environ.get("GRAMPS_FS_BETA_REDIRECT", "").strip()
                or str(_cfg_get("familysearch.beta.redirect", "") or "").strip()
                or str(_cfg_get("familysearch.redirect", "") or "").strip()
                or (self._legacy_redirect or "")
                or DEFAULT_LOOPBACK_REDIRECT
            ).strip()

            return EnvProfile(
                env=ENV_BETA,
                fs_url=fs_url,
                ident_url=ident_url,
                api_url=api_url,
                web_url=web_url,
                app_key=app_key,
                redirect=redirect,
            )

        fs_url = "https://www.familysearch.org/"
        ident_url = "https://ident.familysearch.org/"
        api_url = "https://api.familysearch.org/"
        web_url = "https://www.familysearch.org/"

        app_key = (
            os.environ.get("GRAMPS_FS_PROD_APP_KEY", "").strip()
            or str(_cfg_get("familysearch.prod.app_key", "") or "").strip()
            or str(_cfg_get("familysearch.app-key", "") or "").strip()
            or (self._legacy_app_key if int(self._legacy_server or 0) != 0 else "")
        ).strip()

        redirect = (
            os.environ.get("GRAMPS_FS_PROD_REDIRECT", "").strip()
            or str(_cfg_get("familysearch.prod.redirect", "") or "").strip()
            or str(_cfg_get("familysearch.redirect", "") or "").strip()
            or (self._legacy_redirect or "")
            or DEFAULT_LOOPBACK_REDIRECT
        ).strip()

        return EnvProfile(
            env=ENV_PROD,
            fs_url=fs_url,
            ident_url=ident_url,
            api_url=api_url,
            web_url=web_url,
            app_key=app_key,
            redirect=redirect,
        )

    def _apply_profile(self, prof: EnvProfile, clear_state: bool = True) -> None:
        """Apply the chosen profile and optionally clear auth state."""
        self._profile = prof
        self.fs_url = prof.fs_url
        self.ident_url = prof.ident_url
        self.api_url = prof.api_url
        self.web_url = prof.web_url
        self.app_key = (prof.app_key or "").strip()
        self.redirect = (prof.redirect or "").strip()

        if clear_state:
            try:
                self.cookies.clear()
            except Exception:
                pass
            self.access_token = None
            self.refresh_token = None
            self.id_token = None
            self.foundation_session_token = ""
            self.foundation_login_id = ""
            self._foundation_auth_payload = None
            self._auth_ui_cancelled = False
            self.connected = False
            self.last_probe_http = None
            self.last_probe_detail = ""
            self._oauth_code = ""
            self._oauth_error = ""
            self._oauth_state = ""
            self._pkce_verifier = ""
            self._pkce_challenge = ""
            self._set_status("DISCONNECTED", "Switched environment; no token")

        self._recompute_listener()

    @staticmethod
    def _response_is_empty_json(r: requests.Response) -> bool:
        try:
            if r.status_code == 204:
                return True
            clen = r.headers.get("Content-Length")
            if clen is not None and clen.strip() == "0":
                return True
            if not r.content:
                return True
            if hasattr(r, "text") and (r.text is None or r.text.strip() == ""):
                return True
        except Exception:
            pass
        return False

    def _iterate_ui_events(self) -> None:
        return

    def _get_parent_window(self):
        return None

    def get_status_widget(self):
        return self.status_indicator.create_widget()

    def _set_status(self, state: str, detail: str = "", http: int | None = None):
        self._status_state = state
        self._status_detail = detail or ""
        self._status_http = http
        _dbg(f"status: {state} detail={_safe(detail, 220)} http={http}")
        try:
            self.status_indicator.set(state, detail=detail, http=http)
        except Exception:
            pass

    def _supports_embedded_webkit(self) -> bool:
        return False

    def _open_auth_ui(
        self, auth_url: str, capture_code: bool = False, expected_state: str = ""
    ) -> bool:
        return False

    def _close_auth_window(self) -> None:
        self._closing_auth_window = True
        self._auth_win = None
        self._closing_auth_window = False

    def _prompt_for_auth_code(self, auth_url: str) -> str:
        try:
            if sys.stdin and sys.stdin.isatty():
                print(
                    "After approving access in your browser, paste the authorization code"
                    " or the full redirect URL here:"
                )
                text = input("> ").strip()
                params = _extract_redirect_params_from_text(text)
                if (
                    text.startswith("http://") or text.startswith("https://")
                ) and not self._validate_oauth_state(params):
                    return ""
                if "error" in params or "error_description" in params:
                    err = params.get("error", "")
                    desc = params.get("error_description", "")
                    self._set_status("ERROR", f"{err} {desc}".strip())
                    return ""
                return (params.get("code", "") or "").strip()
        except Exception:
            pass
        return ""

    def _maybe_show_tools_window(self) -> None:
        return

    def _fs_join(self, base: str, path: str) -> str:
        return base.rstrip("/") + "/" + str(path).lstrip("/")

    def _using_foundation_middleware(self) -> bool:
        return self.auth_provider == AUTH_PROVIDER_FOUNDATION

    def _foundation_url(self, path: str) -> str:
        return self._fs_join(self.foundation_base_url, path)

    def _foundation_proxy_url(self, path: str) -> str:
        return self._foundation_url("v1/fs/proxy/" + str(path).lstrip("/"))

    def _foundation_proxy_absolute_url(self, url: str) -> str:
        return self._foundation_url(
            "v1/fs/proxy-abs?" + urlencode({"url": str(url).strip()})
        )

    def _is_proxyable_foundation_url(self, url: str) -> bool:
        try:
            parsed = urlparse(str(url).strip())
        except Exception:
            return False
        host = (parsed.netloc or "").strip().lower()
        if not host:
            return False
        allowed = set()
        for candidate in (
            self.api_url,
            self.fs_url,
            self.web_url,
        ):
            try:
                candidate_host = (urlparse(candidate).netloc or "").strip().lower()
            except Exception:
                candidate_host = ""
            if candidate_host:
                allowed.add(candidate_host)
        if getattr(self._profile, "env", ENV_PROD) == ENV_PROD:
            allowed.add("familysearch.org")
        return host in allowed

    def _foundation_headers(
        self,
        *,
        include_session: bool = False,
        include_json: bool = False,
    ) -> dict[str, str]:
        headers = {"accept": "application/json"}
        if include_json:
            headers["content-type"] = "application/json"
        if self.foundation_access_code:
            headers["x-gramps-access-code"] = self.foundation_access_code
        if include_session and self.foundation_session_token:
            headers["authorization"] = "Bearer " + self.foundation_session_token
        return headers

    def _clone_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        cloned = dict(kwargs)
        headers = cloned.get("headers")
        if isinstance(headers, dict):
            cloned["headers"] = dict(headers)
        return cloned

    def _ensure_api_headers(self, kwargs):
        headers = kwargs.setdefault("headers", {})
        if not any(k.lower() == "accept" for k in headers.keys()):
            headers["accept"] = "application/x-fs-v1+json"
        if self._using_foundation_middleware() and self.foundation_access_code:
            if not any(k.lower() == "x-gramps-access-code" for k in headers.keys()):
                headers["x-gramps-access-code"] = self.foundation_access_code
        auth_token = self.access_token
        if self._using_foundation_middleware() and self.foundation_session_token:
            auth_token = self.foundation_session_token
        if auth_token and not any(k.lower() == "authorization" for k in headers.keys()):
            headers["authorization"] = "Bearer " + auth_token

    def _refresh_direct_access_token(self) -> bool:
        refresh_token = (self.refresh_token or "").strip()
        if not refresh_token or not (self.app_key or "").strip():
            return False

        try:
            url = urljoin(self.ident_url, "cis-web/oauth2/v3/token")
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.app_key,
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
            }
            r = super().post(url, data=payload, headers=headers, verify=self.verify)
            data = r.json()
            if r.status_code >= 400 or not isinstance(data, dict):
                _dbg(
                    f"direct refresh failed HTTP {r.status_code}: "
                    f"{_safe(getattr(r, 'text', ''), 220)}"
                )
                return False
            access_token = (data.get("access_token") or "").strip()
            if not access_token:
                return False
            self.access_token = access_token
            self.refresh_token = (data.get("refresh_token") or refresh_token).strip()
            return True
        except Exception as e:
            _dbg(f"direct refresh exception: {type(e).__name__}: {e}")
            return False

    def _refresh_foundation_access_token(self) -> bool:
        if (
            not self.foundation_base_url
            or not self.foundation_access_code
            or not self.foundation_session_token
            or not self.foundation_login_id
        ):
            return False

        try:
            r = super().post(
                self._foundation_url("v1/fs/token/refresh"),
                json={"login_id": self.foundation_login_id, "env": self._profile.env},
                headers=self._foundation_headers(
                    include_session=True, include_json=True
                ),
                verify=self.verify,
            )
            data = r.json()
            if r.status_code >= 400 or not isinstance(data, dict):
                _dbg(
                    f"foundation refresh failed HTTP {r.status_code}: "
                    f"{_safe(getattr(r, 'text', ''), 220)}"
                )
                return False
            session_token = (
                str(data.get("foundation_session_token") or "").strip()
                or str(data.get("access_token") or "").strip()
            )
            if not session_token:
                return False
            self.access_token = session_token
            self.foundation_session_token = session_token
            return True
        except Exception as e:
            _dbg(f"foundation refresh exception: {type(e).__name__}: {e}")
            return False

    def refresh_access_token(self) -> bool:
        if self._using_foundation_middleware():
            return self._refresh_foundation_access_token()
        return self._refresh_direct_access_token()

    def _request_with_api_retry(self, method_name: str, url: str, **kwargs):
        method = getattr(super(), method_name)
        _dbg(f"{method_name.upper()} {url}")
        response = method(url, **kwargs)
        if response.status_code != 401:
            return response
        if not self.refresh_access_token():
            return response

        retry_kwargs = self._clone_kwargs(kwargs)
        headers = retry_kwargs.setdefault("headers", {})
        if self.access_token:
            headers["authorization"] = "Bearer " + self.access_token
        _dbg(f"{method_name.upper()} {url} retry after token refresh")
        return method(url, **retry_kwargs)

    def _route_api_request(self, method_name: str, url: str, **kwargs):
        text_url = str(url)
        if self._using_foundation_middleware() and text_url.startswith(
            ("http://", "https://")
        ):
            if self._is_proxyable_foundation_url(text_url):
                url = self._foundation_proxy_absolute_url(text_url)
                self._ensure_api_headers(kwargs)
                return self._request_with_api_retry(method_name, url, **kwargs)
        if not text_url.startswith("http"):
            if self._using_foundation_middleware():
                url = self._foundation_proxy_url(text_url)
            else:
                url = self._fs_join(self.api_url, text_url)
            self._ensure_api_headers(kwargs)
            return self._request_with_api_retry(method_name, url, **kwargs)
        _dbg(f"{method_name.upper()} {url}")
        return getattr(super(), method_name)(url, **kwargs)

    def get(self, url, **kwargs):
        return self._route_api_request("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self._route_api_request("post", url, **kwargs)

    def head(self, url, **kwargs):
        return self._route_api_request("head", url, **kwargs)

    def put(self, url, **kwargs):
        return self._route_api_request("put", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._route_api_request("patch", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._route_api_request("delete", url, **kwargs)

    def write_log(self, text: str) -> None:
        _dbg(str(text))

    def get_url(self, url, headers=None, params=None):
        return self.get(url, headers=headers or {}, params=params)

    def post_url(self, url, data=None, headers=None):
        return self.post(url, data=data, headers=headers or {})

    def head_url(self, url, headers=None):
        return self.head(url, headers=headers or {})

    @property
    def logged(self) -> bool:
        return bool(self.access_token)

    @logged.setter
    def logged(self, _val: bool) -> None:
        return

    @property
    def client_id(self) -> str:
        return self.app_key

    @client_id.setter
    def client_id(self, v: str) -> None:
        self.app_key = (v or "").strip()

    def get_jsonurl(self, url: str, headers: dict | None = None):
        """GET json from an FS endpoint and smooth over the common edge cases."""
        try:
            r = self.get_url(url, headers=headers)
        except requests.exceptions.RequestException as e:
            self.write_log(
                f"WARNING: request failed for {url}: {type(e).__name__}: {e}"
            )
            return None

        if r is None or r == "error":
            return r

        if isinstance(r, requests.Response) and self._response_is_empty_json(r):
            return {}

        if not isinstance(r, requests.Response):
            return None

        if r.status_code == 401:
            self.write_log(f"WARNING: 401 from {url}")
            return None

        if r.status_code == 403:
            try:
                msg = r.json().get("errors", [{}])[0].get("message")
            except Exception:
                msg = None
            if msg == "Unable to get ordinances.":
                return "error"

        if r.status_code >= 400:
            self.write_log(
                f"WARNING: HTTP {r.status_code} from {url}: {_safe(getattr(r, 'text', ''), 200)}"
            )
            return None

        try:
            return r.json()
        except Exception as e:
            body_preview = ""
            try:
                body_preview = _safe(getattr(r, "text", ""), 220)
            except Exception:
                pass
            self.write_log(
                f"WARNING: JSON decode failed from {url}: {type(e).__name__}: {e}"
                + (f"; body preview: {body_preview}" if body_preview else "")
            )
            return None

    def _recompute_listener(self) -> None:
        """Recompute the loopback listener bind settings from the redirect url."""
        r = urlparse(self.redirect or DEFAULT_LOOPBACK_REDIRECT)
        self.listen_timeout = int(
            os.environ.get("GRAMPS_FS_LISTENER_TIMEOUT", str(self.listen_timeout))
            or str(self.listen_timeout)
        )
        if r.hostname in ("127.0.0.1", "localhost"):
            self.listen_host = r.hostname or "127.0.0.1"
            self.listen_port = r.port or 57938
            self.listen_path = r.path or "/familysearch-auth"
        else:
            self.listen_host = "127.0.0.1"
            self.listen_port = 57938
            self.listen_path = "/familysearch-auth"

    def listen(self) -> str:
        while self.listener and self.listener.is_alive():
            time.sleep(0.1)
            self._iterate_ui_events()

        _dbg(
            f"listen(): finished. error={getattr(self.listener, 'error', None)!r} "
            f"result={getattr(self.listener, 'result', None)!r}"
        )

        if self.listener and self.listener.error:
            self._set_status("ERROR", self.listener.error)
            return ""

        if self.listener and (
            "error_description" in self.listener.result
            or "error" in self.listener.result
        ):
            err = self.listener.result.get("error", "")
            desc = self.listener.result.get("error_description", "")
            self._set_status("ERROR", f"{err} {desc}".strip())
            return ""

        if self.listener and not self._validate_oauth_state(self.listener.result):
            return ""

        return self.listener.result.get("code", "") if self.listener else ""

    def _validate_oauth_state(self, params: dict[str, str] | None) -> bool:
        expected_state = (self._oauth_state or "").strip()
        if not expected_state:
            return True

        got_state = ((params or {}).get("state", "") or "").strip()
        if got_state == expected_state:
            return True

        if got_state:
            self._set_status("ERROR", "OAuth state mismatch")
        else:
            self._set_status("ERROR", "OAuth state missing from callback")

        _dbg(
            "oauth state validation failed: "
            f"expected={expected_state!r} got={got_state!r}"
        )
        return False

    def canonical_web_url(self, url: str) -> str:
        """Normalize FamilySearch web URLs for the current environment."""
        if not url:
            return ""
        url = str(url).strip()
        if not url.startswith(("http://", "https://")):
            return url
        if getattr(self._profile, "env", ENV_PROD) == ENV_BETA:
            return url
        try:
            p = urlparse(url)
            host = (p.netloc or "").lower()
            if host in (
                "beta.familysearch.org",
                "familysearch.org",
                "www.familysearch.org",
            ):
                return urlunparse(
                    (
                        p.scheme or "https",
                        "www.familysearch.org",
                        p.path or "",
                        p.params or "",
                        p.query or "",
                        p.fragment or "",
                    )
                )
            return url
        except Exception:
            return url

    def probe_api(self, reason: str = "") -> bool:
        """Hit a simple FS endpoint so we know whether the token still works."""
        if not self.access_token:
            self.connected = False
            self.last_probe_http = None
            self.last_probe_detail = "No access token"
            self._set_status(
                "DISCONNECTED", f"{reason}: no token" if reason else "No token"
            )
            return False

        self._set_status(
            "PROBING",
            (
                f"{reason}: GET platform/users/current"
                if reason
                else "GET platform/users/current"
            ),
        )
        try:
            r = self.get("platform/users/current")
            http = r.status_code
            self.last_probe_http = http
            self.last_probe_detail = (r.reason or "") or "OK"
            if http == 200:
                self.connected = True
                self._set_status("CONNECTED", "API probe OK", http=http)
                self._maybe_show_tools_window()
                return True
            self.connected = False
            self._set_status(
                "API_FAIL",
                _safe(r.text, 200) or (r.reason or "API probe failed"),
                http=http,
            )
            return False
        except Exception as e:
            self.connected = False
            self.last_probe_http = None
            self.last_probe_detail = f"{type(e).__name__}: {e}"
            self._set_status("ERROR", self.last_probe_detail)
            return False

    def get_current_person(self) -> str:
        if not self.access_token:
            raise FSException("Not connected (no access token).")
        r = self.get("platform/tree/current-person")
        return r.text

    def logout(self) -> None:
        if (
            self._using_foundation_middleware()
            and self.foundation_base_url
            and self.foundation_access_code
            and self.foundation_session_token
            and self.foundation_login_id
        ):
            try:
                super().post(
                    self._foundation_url("v1/fs/logout"),
                    json={
                        "login_id": self.foundation_login_id,
                        "env": self._profile.env,
                    },
                    headers=self._foundation_headers(
                        include_session=True, include_json=True
                    ),
                    verify=self.verify,
                )
            except Exception as e:
                _dbg(f"foundation logout exception: {type(e).__name__}: {e}")
        self.access_token = None
        self.refresh_token = None
        self.id_token = None
        self.foundation_session_token = ""
        self.foundation_login_id = ""
        self._foundation_auth_payload = None
        self._auth_ui_cancelled = False
        self._oauth_state = ""
        self._pkce_verifier = ""
        self._pkce_challenge = ""
        try:
            self.cookies.clear()
        except Exception:
            pass
        self.connected = False
        self.last_probe_http = None
        self.last_probe_detail = "Logged out"
        self._set_status("DISCONNECTED", "Logged out")

    def _available_methods(self) -> list[str]:
        methods = [AUTH_AUTO, AUTH_LOOPBACK, AUTH_MANUAL]
        if (not win()) and self._supports_embedded_webkit():
            methods.insert(1, AUTH_WEBKIT)
        return methods

    def _choose_effective_method(self, requested: str) -> str:
        requested = (requested or AUTH_AUTO).strip().lower()
        avail = self._available_methods()
        if requested != AUTH_AUTO and requested in avail:
            return requested

        if (not win()) and self._supports_embedded_webkit():
            return AUTH_WEBKIT

        if _is_loopback_redirect(self.redirect or ""):
            return AUTH_LOOPBACK
        return AUTH_MANUAL

    def login(self, username: str = "", password: str = "") -> bool:
        self.username = username or self.username or ""
        return True

    def _open_browser_url(self, url: str) -> bool:
        try:
            return bool(webbrowser.open(url, new=1, autoraise=True))
        except Exception as e:
            _dbg(f"browser open failed: {type(e).__name__}: {e}")
            return False

    def _print_browser_url(self, url: str) -> None:
        try:
            print("Open this URL in your browser to continue FamilySearch login:")
            print(url)
        except Exception:
            pass

    def _choose_foundation_method(self, requested: str) -> str:
        requested = (requested or AUTH_AUTO).strip().lower()
        if requested == AUTH_MANUAL:
            return AUTH_MANUAL
        if requested == AUTH_WEBKIT:
            if (not win()) and self._supports_embedded_webkit():
                return AUTH_WEBKIT
            return AUTH_LOOPBACK
        if requested == AUTH_LOOPBACK:
            return AUTH_LOOPBACK
        if (not win()) and self._supports_embedded_webkit():
            return AUTH_WEBKIT
        return AUTH_LOOPBACK

    def _launch_foundation_login_ui(self, browser_url: str, method: str) -> None:
        method = (method or AUTH_AUTO).strip().lower()
        if _debug_enabled():
            self._print_browser_url(browser_url)
        if method == AUTH_WEBKIT and (not win()):
            self._set_status("AWAITING_BROWSER", "Opening embedded login window")
            if self._open_auth_ui(browser_url, capture_code=False):
                return
            self._set_status(
                "AWAITING_BROWSER",
                "Embedded WebKit unavailable; opening system browser",
            )

        if method == AUTH_MANUAL:
            self._set_status(
                "AWAITING_BROWSER", "Open the middleware login URL in your browser"
            )
            self._print_browser_url(browser_url)
            return

        self._set_status("AWAITING_BROWSER", "Opening middleware login in browser")
        opened = self._open_browser_url(browser_url)
        if not opened:
            self._set_status(
                "AWAITING_BROWSER", "Open the middleware login URL in your browser"
            )
            self._print_browser_url(browser_url)

    def _poll_foundation_login(
        self, login_id: str, poll_interval: float, timeout_s: int
    ) -> dict[str, Any]:
        deadline = time.time() + max(1, int(timeout_s or self.listen_timeout))
        url = self._foundation_url(f"v1/fs/login/status/{login_id}")
        headers = self._foundation_headers()

        while time.time() < deadline:
            if self._auth_ui_cancelled:
                self._set_status("DISCONNECTED", "Login canceled")
                return {}
            self._set_status("AWAITING_BROWSER", "Waiting for middleware approval")
            try:
                r = super().get(url, headers=headers, verify=self.verify)
            except Exception as e:
                self._set_status(
                    "ERROR", f"Middleware status failed: {type(e).__name__}"
                )
                _dbg(f"foundation status exception: {type(e).__name__}: {e}")
                return {}

            try:
                data = r.json()
            except Exception as e:
                self._set_status("ERROR", "Middleware returned non-JSON status")
                _dbg(
                    f"foundation status non-JSON: {type(e).__name__}: {e} "
                    f"body={_safe(getattr(r, 'text', ''), 220)}"
                )
                return {}

            if r.status_code >= 400:
                err = (
                    data.get("message")
                    if isinstance(data, dict)
                    else getattr(r, "text", "")
                )
                self._set_status(
                    "ERROR",
                    f"Middleware status failed: {_safe(str(err), 200)}",
                    http=r.status_code,
                )
                return {}

            if not isinstance(data, dict):
                self._set_status("ERROR", "Middleware returned invalid status payload")
                return {}

            status = str(data.get("status") or "").strip().lower()
            if status == "approved":
                return data
            if status == "failed":
                self._set_status(
                    "ERROR",
                    str(data.get("message") or data.get("error") or "Login failed"),
                )
                return {}

            detail = str(data.get("detail") or "Waiting for FamilySearch approval")
            self._set_status("AWAITING_BROWSER", detail)
            time.sleep(max(3.0, float(poll_interval or 2.0)))
            self._iterate_ui_events()

        self._set_status("ERROR", "Timed out waiting for middleware approval")
        return {}

    def _authorize_via_foundation(self, method: str) -> str:
        if not self.foundation_base_url:
            self._set_status(
                "ERROR", "Foundation middleware base URL is not configured"
            )
            return ""
        if not self.foundation_access_code:
            self._set_status(
                "ERROR", "Foundation middleware access code is not configured"
            )
            return ""

        self._foundation_auth_payload = None
        self.foundation_session_token = ""
        self.foundation_login_id = ""
        self._auth_ui_cancelled = False
        self._set_status("AUTHORIZING", "Starting middleware login")
        try:
            r = super().post(
                self._foundation_url("v1/fs/login/start"),
                json={"env": self._profile.env, "username": self.username or ""},
                headers=self._foundation_headers(include_json=True),
                verify=self.verify,
            )
            data = r.json()
        except Exception as e:
            _dbg(f"foundation start exception: {type(e).__name__}: {e}")
            self._set_status(
                "ERROR", f"Middleware login start failed: {type(e).__name__}"
            )
            return ""

        if r.status_code >= 400 or not isinstance(data, dict):
            message = ""
            if isinstance(data, dict):
                message = str(data.get("message") or data.get("error") or "").strip()
            if not message:
                message = _safe(getattr(r, "text", ""), 200) or "Login start failed"
            self._set_status("ERROR", message, http=r.status_code)
            return ""

        login_id = str(data.get("login_id") or "").strip()
        browser_url = str(data.get("browser_url") or "").strip()
        poll_interval = float(data.get("poll_interval") or 2.0)
        if not login_id or not browser_url:
            self._set_status(
                "ERROR", "Middleware login start returned an incomplete payload"
            )
            return ""

        effective = self._choose_foundation_method(method)
        self._launch_foundation_login_ui(browser_url, effective)
        try:
            approved = self._poll_foundation_login(
                login_id, poll_interval=poll_interval, timeout_s=self.listen_timeout
            )
        finally:
            if effective == AUTH_WEBKIT:
                self._close_auth_window()
        if not approved:
            return ""

        self._foundation_auth_payload = approved
        return login_id

    def _apply_foundation_login_payload(self, data: dict[str, Any]) -> bool:
        foundation_session_token = (
            str(data.get("foundation_session_token") or "").strip()
            or str(data.get("access_token") or "").strip()
        )
        login_id = str(data.get("login_id") or "").strip() or self.foundation_login_id
        if not foundation_session_token or not login_id:
            self._set_status("ERROR", "Middleware approval payload is incomplete")
            return False

        self.access_token = foundation_session_token
        self.refresh_token = None
        self.id_token = None
        self.foundation_session_token = foundation_session_token
        self.foundation_login_id = login_id
        self._foundation_auth_payload = None
        self._oauth_state = ""
        self._set_status("TOKEN_ACQUIRED", "Proxy session acquired from middleware")
        try:
            self.probe_api(reason="post-token")
        except Exception as e:
            _dbg(f"foundation probe_api failed: {type(e).__name__}: {e}")
        return True

    def _get_token_via_foundation(self, login_id: str) -> bool:
        login_id = (login_id or "").strip()
        data = self._foundation_auth_payload
        if data is None:
            if not login_id:
                self._set_status("ERROR", "No middleware login session")
                return False
            data = self._poll_foundation_login(login_id, poll_interval=1.0, timeout_s=5)
            if not data:
                return False
        if login_id and not str(data.get("login_id") or "").strip():
            data = dict(data)
            data["login_id"] = login_id
        return self._apply_foundation_login_payload(data)

    def authorize(self, username: str | None = None, *args, **kwargs) -> str:
        """Pick the active env/method and start oauth"""
        if username:
            self.username = username

        # env
        forced_env = os.environ.get("GRAMPS_FS_ENV", "").strip().lower()
        env = forced_env or str(_cfg_get("familysearch.env", "") or "").strip().lower()
        if env not in (ENV_BETA, ENV_PROD):
            legacy_server = _cfg_get("familysearch.server", self._legacy_server)
            env = ENV_BETA if int(legacy_server or 0) == 0 else ENV_PROD

        prof = self._beta_profile if env == ENV_BETA else self._prod_profile
        self._apply_profile(prof, clear_state=True)

        forced_method = os.environ.get("GRAMPS_FS_AUTH_METHOD", "").strip().lower()
        req_method = forced_method or self._auth_method_chosen or AUTH_AUTO

        if self._using_foundation_middleware():
            return self._authorize_via_foundation(req_method) or ""

        if not (self.app_key or "").strip():
            self._set_status(
                "ERROR",
                "No app key (client_id) configured (Integrations ? FamilySearch ? App key)",
            )
            return ""
        if not (self.redirect or "").strip():
            self._set_status(
                "ERROR",
                "No redirect configured (Integrations ? FamilySearch ? Redirect URL)",
            )
            return ""

        effective = self._choose_effective_method(req_method)
        return self._oauth_authorize_only(effective) or ""

    def get_token(self, auth_code: str) -> bool:
        """Exchange auth code for an access token."""
        if self._using_foundation_middleware():
            return self._get_token_via_foundation(auth_code)
        if not auth_code:
            self._set_status("ERROR", "No auth code")
            return False
        try:
            self._set_status("EXCHANGING_TOKEN", "Posting code to token endpoint")
            url = urljoin(self.ident_url, "cis-web/oauth2/v3/token")
            payload = {
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect,
                "client_id": self.app_key,
                "code": auth_code,
            }
            if self._pkce_verifier:
                payload["code_verifier"] = self._pkce_verifier
            headers = {
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
            }
            _dbg(f"POST {url}")
            r = super().post(url, data=payload, headers=headers, verify=self.verify)

            try:
                data = r.json()
            except Exception as e:
                self._set_status(
                    "ERROR", "Token endpoint returned non-JSON", http=r.status_code
                )
                _dbg(
                    f"get_token(): non-JSON: {type(e).__name__}: {e} body={_safe(getattr(r, 'text', ''), 900)}"
                )
                return False

            if isinstance(data, dict) and data.get("access_token"):
                self.access_token = data["access_token"]
                self.refresh_token = data.get("refresh_token")
                self.id_token = data.get("id_token")
                self._oauth_state = ""
                self._set_status("TOKEN_ACQUIRED", "Access token acquired")
                try:
                    self.probe_api(reason="post-token")
                except Exception as e:
                    _dbg(f"get_token(): probe_api failed: {type(e).__name__}: {e}")
                return True

            err = data.get("error") if isinstance(data, dict) else "token_error"
            desc = (
                (data.get("error_description") or data.get("message"))
                if isinstance(data, dict)
                else ""
            )
            self._set_status("ERROR", f"{err} {desc}".strip(), http=r.status_code)
            _dbg(
                f"get_token(): failed HTTP {r.status_code}: error={err!r} desc={desc!r}"
            )
            return False
        except Exception as e:
            _dbg(f"get_token(): exception: {type(e).__name__}: {e}")
            self._set_status("ERROR", f"token exchange failed: {type(e).__name__}")
            return False

    def _auth_url(self, state: str) -> str:
        base = urljoin(self.ident_url, "cis-web/oauth2/v3/authorization")
        params = {
            "client_id": self.app_key,
            "redirect_uri": self.redirect,
            "response_type": "code",
            "scope": self.oauth_scope,
            "state": state,
        }
        if self._pkce_challenge:
            params["code_challenge"] = self._pkce_challenge
            params["code_challenge_method"] = "S256"
        if self.username:
            params["username"] = self.username
        return base + "?" + urlencode(params)

    def _oauth_authorize_only(self, method: str) -> str:
        """Run just the authorize half of oauth and return the code"""
        method = (method or AUTH_AUTO).strip().lower()

        if method == AUTH_LOOPBACK and not _is_loopback_redirect(self.redirect):
            self._set_status(
                "ERROR", "Loopback method requires a localhost redirect URL"
            )
            return ""

        state = secrets.token_urlsafe(18)
        self._oauth_state = state
        self._pkce_verifier = _generate_pkce_verifier()
        self._pkce_challenge = _generate_pkce_challenge(self._pkce_verifier)
        auth_url = self._auth_url(state)
        self._oauth_code = ""
        self._oauth_error = ""

        # loopback wins when the redirect is loopback-capable.
        if _is_loopback_redirect(self.redirect):
            return self._authorize_via_loopback(auth_url)
        if method == AUTH_WEBKIT and (not win()):
            return self._authorize_via_webkit_capture(auth_url, expected_state=state)
        return self._authorize_via_manual(auth_url)

    def _authorize_via_loopback(self, auth_url: str) -> str:
        """redirect flow to capture the oauth code"""
        self._set_status("AUTHORIZING", "Preparing loopback listener")
        self._recompute_listener()
        self.listener = Listener(
            self.listen_host, self.listen_port, self.listen_path, self.listen_timeout
        )
        self.listener.start()

        self._set_status("AUTHORIZING", "Opening system browser (loopback callback)")
        try:
            print("Open this URL in your browser to continue FamilySearch login:")
            print(auth_url)
        except Exception:
            pass
        opened = False
        try:
            opened = bool(webbrowser.open(auth_url, new=1, autoraise=True))
        except Exception as e:
            _dbg(f"loopback browser open failed: {type(e).__name__}: {e}")

        if not opened:
            try:
                print("Open this URL in your browser to continue FamilySearch login:")
                print(auth_url)
            except Exception:
                pass

        code = self.listen().strip()
        if code:
            self._set_status("AUTH_CODE_RECEIVED", "Auth code received")
        return code

    def _authorize_via_webkit_capture(self, auth_url: str, expected_state: str) -> str:
        """Use embedded webkit to capture the auth code directly."""
        if win():
            self._set_status("ERROR", "WebKit method is not available on Windows")
            return ""
        if not self._supports_embedded_webkit():
            self._set_status(
                "ERROR", "Embedded WebKit not available; use manual method"
            )
            return ""

        ok = self._open_auth_ui(
            auth_url, capture_code=True, expected_state=expected_state
        )
        if not ok:
            self._set_status(
                "ERROR", "Embedded WebKit not available; use manual method"
            )
            return ""

        self._set_status("AUTHORIZING", "Waiting for redirect (capturing code)")
        deadline = time.time() + self.listen_timeout
        while time.time() < deadline and not self._oauth_code and not self._oauth_error:
            time.sleep(0.1)
            self._iterate_ui_events()

        if self._oauth_error:
            self._set_status("ERROR", self._oauth_error)
            self._close_auth_window()
            return ""

        if not self._oauth_code:
            self._set_status("ERROR", "Timed out waiting for redirect")
            self._close_auth_window()
            return ""

        self._set_status("AUTH_CODE_RECEIVED", "Auth code received")
        self._close_auth_window()
        return self._oauth_code

    def _authorize_via_manual(self, auth_url: str) -> str:
        """Open the browser and ask the user to paste the code back. (usually for Windows)"""
        self._set_status("AUTHORIZING", "Opening system browser (manual code entry)")
        try:
            print("Open this URL in your browser to continue FamilySearch login:")
            print(auth_url)
        except Exception:
            pass
        opened = False
        try:
            opened = bool(webbrowser.open(auth_url, new=1, autoraise=True))
        except Exception as e:
            _dbg(f"manual browser open failed: {type(e).__name__}: {e}")

        if not opened:
            try:
                print("Open this URL in your browser to continue FamilySearch login:")
                print(auth_url)
            except Exception:
                pass

        code = self._prompt_for_auth_code(auth_url)
        if not code:
            self._set_status("ERROR", "No code provided")
            return ""

        self._set_status("AUTH_CODE_RECEIVED", "Auth code received")
        return code


def get_active_session():
    return (
        GLOBAL_SESSION
        or SESSION
        or getattr(Session, "_shared", None)
        or getattr(Session, "_last_instance", None)
    )
