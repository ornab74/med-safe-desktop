from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import queue
import random
import re
import shutil
import struct
import sys
import tempfile
import threading
import time
import tkinter as tk
import uuid
import errno
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta
import hashlib
from pathlib import Path
from threading import RLock
from tkinter import filedialog, messagebox, simpledialog
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    import httpx
except Exception as exc:
    httpx = None
    HTTPX_IMPORT_ERROR = exc
else:
    HTTPX_IMPORT_ERROR = None

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
except Exception as exc:
    AESGCM = None
    Scrypt = None
    CRYPTO_IMPORT_ERROR = exc
else:
    CRYPTO_IMPORT_ERROR = None

try:
    import psutil
except Exception:
    psutil = None

try:
    import pennylane as qml
    from pennylane import numpy as pnp
except Exception:
    qml = None
    pnp = None

try:
    import customtkinter as ctk
except Exception as exc:
    ctk = None
    CUSTOMTKINTER_IMPORT_ERROR = exc
else:
    CUSTOMTKINTER_IMPORT_ERROR = None

plyer_camera = None
plyer_filechooser = None
Permission = None
request_permissions = None


class _LegacyUIStub:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, _name: str) -> Any:
        def _stub(*_args: Any, **_kwargs: Any) -> Any:
            return None

        return _stub


def ListProperty(value: Any) -> Any:
    return value


def NumericProperty(value: Any) -> Any:
    return value


def StringProperty(value: Any) -> Any:
    return value


def dp(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def Color(*_args: Any, **_kwargs: Any) -> None:
    return None


def Line(*_args: Any, **_kwargs: Any) -> None:
    return None


def Rectangle(*_args: Any, **_kwargs: Any) -> None:
    return None


def RoundedRectangle(*_args: Any, **_kwargs: Any) -> None:
    return None


class Texture(_LegacyUIStub):
    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> "Texture":
        _ = args, kwargs
        return cls()

    def blit_buffer(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class Animation(_LegacyUIStub):
    repeat = False

    def __and__(self, _other: Any) -> "Animation":
        return self

    def __add__(self, _other: Any) -> "Animation":
        return self

    @staticmethod
    def cancel_all(*_args: Any, **_kwargs: Any) -> None:
        return None


class Clock:
    @staticmethod
    def schedule_once(*_args: Any, **_kwargs: Any) -> None:
        return None

    @staticmethod
    def schedule_interval(*_args: Any, **_kwargs: Any) -> None:
        return None


class Widget(_LegacyUIStub):
    pass


class MDApp(_LegacyUIStub):
    pass


class MDFlatButton(_LegacyUIStub):
    pass


class MDRaisedButton(_LegacyUIStub):
    pass


class MDDialog(_LegacyUIStub):
    def open(self) -> None:
        return None

    def dismiss(self) -> None:
        return None


class TwoLineListItem(_LegacyUIStub):
    pass


class Builder:
    @staticmethod
    def load_string(_value: str) -> Any:
        return SimpleNamespace(ids={})


MODEL_REPO = "https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm/resolve/main/"
MODEL_FILE = "gemma-4-E2B-it.litertlm"
EXPECTED_HASH = "ab7838cdfc8f77e54d8ca45eadceb20452d9f01e4bfade03e5dce27911b27e42"
NETWORK_TIMEOUT = httpx.Timeout(connect=15.0, read=120.0, write=120.0, pool=15.0) if httpx is not None else None
MAX_IMAGE_BYTES = 20 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
INFERENCE_BACKEND_OPTIONS = ("Auto", "CPU", "GPU")
FILE_ENCRYPTION_MAGIC = b"MSAFEF01"
FILE_ENCRYPTION_CHUNK_SIZE = 4 * 1024 * 1024
KEY_WRAP_MAGIC = b"MSKEY001"
KEY_WRAP_SALT_LEN = 16
KEY_WRAP_NONCE_LEN = 12
TEMP_FILE_PREFIXES: Tuple[str, ...] = (
    "gemma_model.",
    "gemma_download.",
    "gemma_sealed.",
    "medsafe_rotate_model.",
)
STALE_TEMP_FILE_AGE_SECONDS = 30.0 * 60.0
DOSE_HISTORY_DUPLICATE_WINDOW_SECONDS = 5 * 60.0
DOSE_RELOG_GUARD_SECONDS = 90.0
NAMED_DOSE_PRESETS: Tuple[Tuple[str, int], ...] = (
    ("Breakfast", 8 * 60),
    ("Daytime", 10 * 60),
    ("Mid day", 12 * 60),
    ("Lunch", 13 * 60),
    ("Dinner", 18 * 60),
    ("Nighttime", 21 * 60),
)
NAMED_DOSE_PRESET_MAP = {label.lower(): minutes for label, minutes in NAMED_DOSE_PRESETS}
EXERCISE_HABITS: Tuple[Tuple[str, str, float], ...] = (
    ("walk", "Walk", 15.0),
    ("light", "Light Exercise", 10.0),
    ("stretch", "Stretch", 5.0),
)
RECOVERY_SUPPORT_MILESTONES: Tuple[Tuple[int, int, str], ...] = (
    (1, 10, "Day 1 reset"),
    (3, 15, "3-day foothold"),
    (7, 25, "1-week streak"),
    (14, 40, "2-week streak"),
    (30, 75, "30-day milestone"),
    (60, 120, "60-day milestone"),
    (90, 180, "90-day milestone"),
    (180, 320, "180-day milestone"),
    (365, 700, "1-year milestone"),
)
DEFAULT_SETTINGS = {
    "inference_backend": "Auto",
    "auto_selected_inference_backend": "",
    "enable_native_image_input": True,
    "setup_complete": False,
    "startup_password_enabled": False,
    "allow_checklist_uncheck": False,
    "text_size": "Default",
    "assistant_chat_font_delta": 2,
}
TEXT_SIZE_OPTIONS: Tuple[str, ...] = ("Tiny", "Compact", "Small", "Default", "Large", "Extra Large", "Huge")
TEXT_SIZE_SCALE_MAP: Dict[str, float] = {
    "Tiny": 0.72,
    "Compact": 0.82,
    "Small": 0.92,
    "Default": 1.00,
    "Large": 1.12,
    "Extra Large": 1.24,
    "Huge": 1.38,
}
TEXT_SIZE_BASE_FONT_MAP: Dict[str, int] = {
    "Tiny": 9,
    "Compact": 10,
    "Small": 12,
    "Default": 13,
    "Large": 15,
    "Extra Large": 17,
    "Huge": 19,
}
HELP_FLOW_STEPS: Tuple[Tuple[str, str, str, str], ...] = (
    ("A", "Dashboard", "Triage Today", "See due, missed, upcoming, and the best next action."),
    ("B", "Medications", "Shape The Regimen", "Add, edit, archive, and review medication history."),
    ("C", "Dashboard", "Check The Slots", "Use the daily checklist to reconcile what happened today."),
    ("D", "Safety", "Review Risk", "Run focused or all-meds safety checks before relying on changes."),
    ("E", "Pill Bottle Scanner", "Import Context", "Use bottle photos when label details can reduce manual typing."),
    ("F", "Dental", "Keep Routines Visible", "Track brushing, flossing, rinsing, hygiene review, and recovery."),
    ("G", "Exercise", "Maintain Movement", "Log walking, light exercise, and stretching rhythms."),
    ("H", "Recovery", "Protect Momentum", "Save recovery plans, check-ins, resets, milestones, and reminders."),
    ("I", "Chat", "Ask Locally", "Use the local chat for summaries and practical next steps."),
    ("J", "Settings", "Tune The Runtime", "Adjust model, backend, image input, text size, and privacy settings."),
    ("K", "Settings", "Close Securely", "Leave the vault encrypted and the next launch policy clear."),
)
HELP_FEATURE_GUIDE: Tuple[Tuple[str, str], ...] = (
    ("Dashboard", "Start here for due/missed meds, the daily checklist, timeline, nudge, and selected-med history."),
    ("Medications", "Use this to create current regimen entries and complete/archive finished meds without losing past doses."),
    ("Safety", "Run local regimen checks when meds change or when you want one place to review per-medication risk."),
    ("Pill Bottle Scanner", "Import from a bottle photo, then manually confirm name, dose, interval, max daily amount, and directions."),
    ("Dental", "Keep hygiene habits, visible review notes, and dental recovery information together in the encrypted vault."),
    ("Exercise", "Set gentle walking, movement, and stretch intervals with daily minute goals."),
    ("Recovery", "Track streaks, check-ins, relapse resets, points, milestones, reminders, and a coping plan."),
    ("Chat", "Ask the local chat for practical summaries; switch modes for general, therapy-style, or recovery support."),
    ("Settings", "Control model download, backend, image input, text size, checklist undo, key rotation, and startup unlock."),
)
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
JSON_BLOCK_RE = re.compile(r"\{.*\}", re.S)
ASSISTANT_CONTEXT_TOKEN_LIMIT = 4000
ASSISTANT_CONTEXT_TARGET_TOKENS = 3400
ASSISTANT_CONTEXT_RECENT_TURNS = 8
ASSISTANT_CONTEXT_COMPACT_TRIGGER_TOKENS = 3000
ASSISTANT_CONTEXT_MAX_MESSAGES = 28
ASSISTANT_SUMMARY_MAX_CHARS = 2600
ASSISTANT_COMPACTION_PROMPT = """
MedSafe rolling chat compaction prompt v3:
Compress older local chat turns into a durable memory packet that fits a small 4k-token model.
Preserve only information needed for future answers. Do not invent. Do not keep private scratchpad text.
Organize the summary into: stable user preferences, medication/schedule facts mentioned in chat, dental/recovery/movement context, decisions already made, warnings or safety boundaries, unresolved questions, and tone/style preferences.
Prefer exact medication names, dose numbers, dates, intervals, and user corrections. Drop greetings, duplicate reassurance, filler, and obsolete drafts.
Keep the summary compact, neutral, and action-oriented. Mark uncertainty explicitly.
""".strip()
ACTION_BLOCK_RE = re.compile(r"\[action\]\s*([A-Za-z]+)\s*\[/action\]", re.I | re.S)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

APP_PATHS: Optional["AppPaths"] = None
litert_lm = None
LITERT_IMPORT_ERROR = None
_CRYPTO_LOCK = RLock()


@dataclass
class AppPaths:
    root: Path
    models_dir: Path
    media_dir: Path
    cache_dir: Path
    temp_dir: Path
    key_path: Path
    vault_path: Path
    settings_path: Path
    plain_model_path: Path
    encrypted_model_path: Path


def _set_owner_only_permissions(path: Path, *, is_dir: bool = False) -> None:
    try:
        os.chmod(path, 0o700 if is_dir else 0o600)
    except Exception:
        pass


def set_app_paths(root: Union[str, Path]) -> AppPaths:
    global APP_PATHS

    base = Path(root).expanduser()
    base.mkdir(parents=True, exist_ok=True)
    paths = AppPaths(
        root=base,
        models_dir=base / "models",
        media_dir=base / "media",
        cache_dir=base / ".litert_cache",
        temp_dir=base / ".tmp",
        key_path=base / ".enc_key",
        vault_path=base / "medsafe_vault.json.aes",
        settings_path=base / "settings.json",
        plain_model_path=(base / "models" / MODEL_FILE),
        encrypted_model_path=(base / "models" / f"{MODEL_FILE}.aes"),
    )
    for directory in (paths.root, paths.models_dir, paths.media_dir, paths.cache_dir, paths.temp_dir):
        directory.mkdir(parents=True, exist_ok=True)
        _set_owner_only_permissions(directory, is_dir=True)
    APP_PATHS = paths
    return paths


def default_storage_root() -> Path:
    if sys.platform.startswith("win"):
        appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if appdata:
            return Path(appdata).expanduser() / "MedSafe"
        return Path.home() / "AppData" / "Local" / "MedSafe"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MedSafe"
    xdg_home = os.environ.get("XDG_DATA_HOME")
    if xdg_home:
        return Path(xdg_home).expanduser() / "medsafe"
    return Path.home() / ".local" / "share" / "medsafe"


def desktop_platform_name() -> str:
    if sys.platform.startswith("win"):
        return "Windows"
    if sys.platform == "darwin":
        return "macOS"
    if sys.platform.startswith("linux"):
        return "Linux"
    return "desktop"


def require_paths() -> AppPaths:
    if APP_PATHS is None:
        return set_app_paths(default_storage_root())
    return APP_PATHS


def human_size(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(max(0, value))
    unit = units[0]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            break
        size /= 1024.0
    return f"{size:.1f}{unit}" if unit != "B" else f"{int(size)}B"


def sanitize_text(value: Any, *, max_chars: int = 4000) -> str:
    text = CONTROL_CHARS_RE.sub("", str(value or "")).strip()
    if len(text) > max_chars:
        return text[:max_chars].rstrip()
    return text


def sanitize_stream_delta(value: Any, *, max_chars: int = 4000) -> str:
    text = CONTROL_CHARS_RE.sub("", str(value or ""))
    if len(text) > max_chars:
        return text[:max_chars]
    return text


def safe_float(value: Any) -> float:
    try:
        return float(str(value).strip())
    except Exception:
        return 0.0


def normalize_setting_choice(value: Any, options: Tuple[str, ...], default: str) -> str:
    text = sanitize_text(value, max_chars=32)
    if not text:
        return default
    for option in options:
        if text.lower() == option.lower():
            return option
    return default


def markdown_to_plain_text(value: Any, *, max_chars: int = 3000) -> str:
    text = sanitize_text(value, max_chars=max_chars)
    if not text:
        return ""
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"^```[a-zA-Z0-9_-]*\s*$", "", text, flags=re.M)
    text = text.replace("```", "")
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "• ", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "| ", text, flags=re.M)
    for pattern in (r"\*\*(.+?)\*\*", r"__(.+?)__", r"\*(.+?)\*", r"_(.+?)_"):
        text = re.sub(pattern, r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}.{threading.get_ident()}.{uuid.uuid4().hex}")
    try:
        tmp.write_bytes(data)
        tmp.replace(path)
        _set_owner_only_permissions(path)
    except OSError as exc:
        safe_cleanup([tmp])
        if exc.errno == errno.ENOSPC:
            raise RuntimeError(
                f"No space left on device. Free disk space near {path.parent} and try again, then refresh the vault."
            ) from exc
        raise
    except Exception:
        safe_cleanup([tmp])
        raise


def _atomic_write_via_handle(path: Path, writer: Callable[[Any], None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}.{threading.get_ident()}.{uuid.uuid4().hex}")
    try:
        with tmp.open("wb") as handle:
            writer(handle)
        tmp.replace(path)
        _set_owner_only_permissions(path)
    except OSError as exc:
        if exc.errno == errno.ENOSPC:
            raise RuntimeError(
                f"No space left on device. Free disk space near {path.parent} and try again, then refresh the vault."
            ) from exc
        raise
    finally:
        safe_cleanup([tmp])


def require_crypto() -> None:
    if AESGCM is None or Scrypt is None:
        detail = f" Import error: {CRYPTO_IMPORT_ERROR}" if CRYPTO_IMPORT_ERROR else ""
        raise RuntimeError("cryptography is required for the encrypted local vault." + detail)


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def aes_encrypt(data: bytes, key: bytes) -> bytes:
    require_crypto()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aes.encrypt(nonce, data, None)


def aes_decrypt(data: bytes, key: bytes) -> bytes:
    require_crypto()
    aes = AESGCM(key)
    nonce, payload = data[:12], data[12:]
    return aes.decrypt(nonce, payload, None)


def derive_password_key(password: str, salt: bytes) -> bytes:
    require_crypto()
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(password.encode("utf-8"))


def is_protected_key_blob(data: bytes) -> bool:
    return data.startswith(KEY_WRAP_MAGIC) and len(data) > len(KEY_WRAP_MAGIC) + KEY_WRAP_SALT_LEN + KEY_WRAP_NONCE_LEN


def protect_raw_key(raw_key: bytes, password: str) -> bytes:
    require_crypto()
    clean_password = sanitize_text(password, max_chars=256)
    if len(clean_password) < 6:
        raise ValueError("Startup password must be at least 6 characters.")
    if len(raw_key) != 32:
        raise ValueError("Vault key must be 32 bytes.")
    salt = os.urandom(KEY_WRAP_SALT_LEN)
    nonce = os.urandom(KEY_WRAP_NONCE_LEN)
    wrap_key = derive_password_key(clean_password, salt)
    payload = AESGCM(wrap_key).encrypt(nonce, raw_key, KEY_WRAP_MAGIC)
    return KEY_WRAP_MAGIC + salt + nonce + payload


def unlock_protected_key(blob: bytes, password: str) -> bytes:
    require_crypto()
    if not is_protected_key_blob(blob):
        raise ValueError("Key file is not password-protected.")
    clean_password = sanitize_text(password, max_chars=256)
    if not clean_password:
        raise ValueError("Enter the startup password.")
    offset = len(KEY_WRAP_MAGIC)
    salt = blob[offset : offset + KEY_WRAP_SALT_LEN]
    nonce_start = offset + KEY_WRAP_SALT_LEN
    nonce_end = nonce_start + KEY_WRAP_NONCE_LEN
    nonce = blob[nonce_start:nonce_end]
    payload = blob[nonce_end:]
    raw_key = AESGCM(derive_password_key(clean_password, salt)).decrypt(nonce, payload, KEY_WRAP_MAGIC)
    if len(raw_key) != 32:
        raise ValueError("Unlocked vault key length is invalid.")
    return raw_key


def encrypt_file(src: Path, dest: Path, key: bytes) -> None:
    require_crypto()
    aes = AESGCM(key)

    def writer(handle: Any) -> None:
        handle.write(FILE_ENCRYPTION_MAGIC)
        handle.write(struct.pack(">I", FILE_ENCRYPTION_CHUNK_SIZE))
        with src.open("rb") as source:
            while True:
                chunk = source.read(FILE_ENCRYPTION_CHUNK_SIZE)
                if not chunk:
                    break
                nonce = os.urandom(12)
                encrypted = aes.encrypt(nonce, chunk, None)
                handle.write(struct.pack(">I", len(encrypted)))
                handle.write(nonce)
                handle.write(encrypted)

    _atomic_write_via_handle(dest, writer)


def decrypt_file(src: Path, dest: Path, key: bytes) -> None:
    require_crypto()
    header_len = len(FILE_ENCRYPTION_MAGIC)
    with src.open("rb") as handle:
        header = handle.read(header_len)
        if header == FILE_ENCRYPTION_MAGIC:
            chunk_size_raw = handle.read(4)
            if len(chunk_size_raw) != 4:
                raise ValueError("Encrypted model header is truncated.")
            chunk_size = struct.unpack(">I", chunk_size_raw)[0]
            if chunk_size <= 0 or chunk_size > 64 * 1024 * 1024:
                raise ValueError("Encrypted model chunk size is invalid.")
            aes = AESGCM(key)

            def writer(out_handle: Any) -> None:
                while True:
                    length_raw = handle.read(4)
                    if not length_raw:
                        return
                    if len(length_raw) != 4:
                        raise ValueError("Encrypted model chunk length is truncated.")
                    encrypted_len = struct.unpack(">I", length_raw)[0]
                    if encrypted_len < 16 or encrypted_len > chunk_size + 16:
                        raise ValueError("Encrypted model chunk length is invalid.")
                    nonce = handle.read(12)
                    if len(nonce) != 12:
                        raise ValueError("Encrypted model nonce is truncated.")
                    payload = handle.read(encrypted_len)
                    if len(payload) != encrypted_len:
                        raise ValueError("Encrypted model chunk payload is truncated.")
                    out_handle.write(aes.decrypt(nonce, payload, None))

            _atomic_write_via_handle(dest, writer)
            return

    _atomic_write_bytes(dest, aes_decrypt(src.read_bytes(), key))


def safe_cleanup(paths: List[Path]) -> None:
    for path in paths:
        try:
            if not path.exists():
                continue
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink()
        except Exception:
            pass


def temp_file_pid(name: str) -> Optional[int]:
    clean_name = sanitize_text(name, max_chars=260)
    for prefix in TEMP_FILE_PREFIXES:
        if not clean_name.startswith(prefix):
            continue
        pid_text = clean_name[len(prefix):].split(".", 1)[0]
        if pid_text.isdigit():
            try:
                return int(pid_text)
            except Exception:
                return None
    return None


def pid_looks_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if psutil is not None:
        try:
            return bool(psutil.pid_exists(pid))
        except Exception:
            pass
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except Exception:
        return True


def cleanup_stale_temp_files(paths: AppPaths, *, min_age_seconds: float = STALE_TEMP_FILE_AGE_SECONDS) -> Tuple[int, int]:
    reclaimed_bytes = 0
    removed_count = 0
    now = time.time()
    try:
        candidates = list(paths.temp_dir.iterdir())
    except Exception:
        return reclaimed_bytes, removed_count
    for candidate in candidates:
        name = candidate.name
        if not any(name.startswith(prefix) for prefix in TEMP_FILE_PREFIXES):
            continue
        try:
            stat = candidate.stat()
        except Exception:
            continue
        candidate_pid = temp_file_pid(name)
        remove_immediately = candidate_pid is not None and not pid_looks_alive(candidate_pid)
        if not remove_immediately and (now - stat.st_mtime) < max(60.0, float(min_age_seconds)):
            continue
        size = int(stat.st_size) if candidate.is_file() else 0
        safe_cleanup([candidate])
        if not candidate.exists():
            reclaimed_bytes += max(0, size)
            removed_count += 1
    return reclaimed_bytes, removed_count


def _tmp_path(prefix: str, suffix: str) -> Path:
    paths = require_paths()
    return paths.temp_dir / f"{prefix}.{os.getpid()}.{threading.get_ident()}.{uuid.uuid4().hex}{suffix}"


def format_duration(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    hours, remainder = divmod(total, 3600)
    minutes, _ = divmod(remainder, 60)
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"


def format_timestamp(ts: float) -> str:
    if not ts:
        return "Not logged yet"
    return time.strftime("%b %d, %I:%M %p", time.localtime(ts))


def format_relative_due(target_ts: Optional[float], now_ts: float) -> str:
    if target_ts is None:
        return "Flexible schedule"
    delta = target_ts - now_ts
    if abs(delta) < 60:
        return "Due now"
    if delta > 0:
        return f"In {format_duration(delta)}"
    return f"{format_duration(abs(delta))} overdue"


def normalize_dose_action_text(value: Any, fallback: str = "Caution") -> str:
    lowered = sanitize_text(value, max_chars=40).strip().lower()
    if lowered in {"safe", "low"}:
        return "Safe"
    if lowered in {"unsafe", "high"}:
        return "Unsafe"
    if lowered in {"caution", "medium", "warn", "warning"}:
        return "Caution"
    return fallback


def resolve_dose_action_from_context(value: Any, context: Dict[str, Any]) -> str:
    requested = normalize_dose_action_text(value, "Caution")
    deterministic = normalize_dose_action_text(context.get("deterministic_level"), "Caution")
    if deterministic == "Unsafe":
        return "Unsafe"
    if deterministic == "Caution":
        return "Caution"
    if deterministic == "Safe" and context.get("duplicate_ts") is None:
        return "Safe"
    return requested


def extract_action_tag(text: str, fallback: str = "Caution") -> str:
    clean = sanitize_text(text, max_chars=400).strip()
    match = ACTION_BLOCK_RE.search(clean)
    if match:
        return normalize_dose_action_text(match.group(1), fallback)
    first_token = clean.split(None, 1)[0] if clean else ""
    return normalize_dose_action_text(first_token, fallback)


def extract_tagged_block(text: str, tag: str, fallback: str = "") -> str:
    clean = sanitize_text(text, max_chars=1200)
    safe_tag = sanitize_text(tag, max_chars=40).lower()
    if not clean or not safe_tag:
        return fallback
    match = re.search(rf"\[{re.escape(safe_tag)}\](.*?)\[/\s*{re.escape(safe_tag)}\]", clean, re.I | re.S)
    if not match:
        return fallback
    return sanitize_text(match.group(1), max_chars=400).strip() or fallback


def normalize_assistant_mode(value: Any) -> str:
    lowered = sanitize_text(value or "", max_chars=40).strip().lower()
    if lowered in {"therapy", "therapist", "support"}:
        return "Therapy"
    if lowered in {"recovery", "recovery coach", "recoverycoach", "coach", "sobriety", "clean"}:
        return "Recovery Coach"
    return "General"


def mg_from_text(text: str) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s*mg\b", text, re.I)
    return safe_float(match.group(1)) if match else 0.0


def infer_interval_from_text(text: str) -> float:
    lowered = sanitize_text(text, max_chars=500).lower()
    for pattern in (
        r"every\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr)\b",
        r"every\s+(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr)\b",
        r"q(\d+(?:\.\d+)?)h\b",
    ):
        match = re.search(pattern, lowered)
        if match:
            if match.lastindex and match.lastindex >= 2 and match.group(2):
                return min(safe_float(match.group(1)), safe_float(match.group(2)))
            return safe_float(match.group(1))
    named = {
        "once daily": 24.0,
        "daily": 24.0,
        "twice daily": 12.0,
        "two times daily": 12.0,
        "three times daily": 8.0,
        "four times daily": 6.0,
        "every morning": 24.0,
        "nightly": 24.0,
        "at bedtime": 24.0,
    }
    for phrase, hours in named.items():
        if phrase in lowered:
            return hours
    return 0.0


def infer_max_daily_mg(text: str, dose_mg: float) -> float:
    lowered = sanitize_text(text, max_chars=500).lower()
    match = re.search(r"(?:max(?:imum)?|not more than|do not exceed)\s+(\d+(?:\.\d+)?)\s*mg", lowered)
    if match:
        return safe_float(match.group(1))
    if dose_mg > 0:
        tablet_match = re.search(r"(?:max(?:imum)?|not more than|do not exceed)\s+(\d+(?:\.\d+)?)\s+(?:tablets|capsules|pills?)", lowered)
        if tablet_match:
            return safe_float(tablet_match.group(1)) * dose_mg
        dose_count_match = re.search(
            r"(?:max(?:imum)?(?:\s+of)?|up to|not more than|do not exceed|no more than)\s+(\d+(?:\.\d+)?)\s+(?:doses?|times?)\s+(?:in|per)\s+24\s*(?:hours?|hrs?|hr|h)\b",
            lowered,
        )
        if dose_count_match:
            return safe_float(dose_count_match.group(1)) * dose_mg
    return 0.0


def collect_system_metrics() -> Dict[str, float]:
    if psutil is None:
        raise RuntimeError("psutil is not available for local entropy metrics.")

    cpu = psutil.cpu_percent(interval=0.05) / 100.0
    mem = psutil.virtual_memory().percent / 100.0
    try:
        load_raw = os.getloadavg()[0]
        cpu_count = psutil.cpu_count(logical=True) or 1
        load1 = max(0.0, min(1.0, load_raw / max(1.0, float(cpu_count))))
    except Exception:
        load1 = cpu
    try:
        temp_groups = psutil.sensors_temperatures()
        if temp_groups:
            first_group = next(iter(temp_groups.values()))
            first_value = first_group[0].current
            temp = max(0.0, min(1.0, (first_value - 20.0) / 70.0))
        else:
            temp = 0.0
    except Exception:
        temp = 0.0
    return {"cpu": cpu, "mem": mem, "load1": load1, "temp": temp}


def metrics_to_rgb(metrics: Dict[str, float]) -> Tuple[float, float, float]:
    cpu = metrics.get("cpu", 0.1)
    mem = metrics.get("mem", 0.1)
    temp = metrics.get("temp", 0.1)
    load1 = metrics.get("load1", 0.0)
    r = cpu * (1.0 + load1)
    g = mem * (1.0 + load1 * 0.5)
    b = temp * (0.5 + cpu * 0.5)
    top = max(r, g, b, 1.0)
    return (
        float(max(0.0, min(1.0, r / top))),
        float(max(0.0, min(1.0, g / top))),
        float(max(0.0, min(1.0, b / top))),
    )


def pennylane_entropic_score(rgb: Tuple[float, float, float], shots: int = 96) -> float:
    if qml is None or pnp is None:
        r, g, b = rgb
        seed = (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255)
        fallback_random = random.Random(seed)
        base = (0.34 * r) + (0.38 * g) + (0.28 * b)
        noise = (fallback_random.random() - 0.5) * 0.06
        return max(0.0, min(1.0, base + noise))

    device = qml.device("default.qubit", wires=2, shots=shots)

    @qml.qnode(device)
    def circuit(a: float, b: float, c: float):
        qml.RX(a * math.pi, wires=0)
        qml.RY(b * math.pi, wires=1)
        qml.CNOT(wires=[0, 1])
        qml.RZ(c * math.pi, wires=1)
        qml.RX((a + b) * math.pi / 2.0, wires=0)
        qml.RY((b + c) * math.pi / 2.0, wires=1)
        return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))

    a, b, c = map(float, rgb)
    try:
        ev0, ev1 = circuit(a, b, c)
        combined = ((ev0 + 1.0) / 2.0 * 0.58) + ((ev1 + 1.0) / 2.0 * 0.42)
        score = 1.0 / (1.0 + math.exp(-6.0 * (combined - 0.5)))
        return float(max(0.0, min(1.0, score)))
    except Exception:
        return float(max(0.0, min(1.0, (a + b + c) / 3.0)))


def entropic_summary_text(score: float) -> str:
    if score >= 0.75:
        level = "high"
    elif score >= 0.45:
        level = "medium"
    else:
        level = "low"
    return f"entropic_score={score:.3f} (level={level})"


def risk_level_from_score(score: float) -> str:
    clamped = max(0.0, min(100.0, score))
    if clamped >= 70.0:
        return "High"
    if clamped >= 40.0:
        return "Medium"
    return "Low"


def normalized_risk_level_text(value: Any, score: float) -> str:
    lowered = sanitize_text(value, max_chars=24).lower()
    if lowered == "low":
        return "Low"
    if lowered == "medium":
        return "Medium"
    if lowered == "high":
        return "High"
    return risk_level_from_score(score)


def context_signature_rgb(domain: str, context_text: str) -> Tuple[float, float, float]:
    digest = hashlib.sha256(
        f"{sanitize_text(domain, max_chars=64)}|{sanitize_text(context_text, max_chars=2400)}".encode("utf-8")
    ).digest()
    return (
        digest[2] / 255.0,
        digest[11] / 255.0,
        digest[23] / 255.0,
    )


def keyword_risk_pressure(domain: str, context_text: str) -> float:
    lowered = sanitize_text(context_text, max_chars=2400).lower()
    if not lowered:
        return 0.0
    pressure = 0.0
    cues = {
        "medication_label": (
            ("max", 0.05),
            ("warning", 0.06),
            ("prn", 0.06),
            ("as needed", 0.06),
            ("with food", 0.04),
        ),
        "medication_dose_safety": (
            ("exceed", 0.12),
            ("too soon", 0.12),
            ("duplicate", 0.10),
            ("missed", 0.06),
            ("overdue", 0.06),
            ("limit", 0.10),
        ),
        "dental_hygiene": (
            ("bleeding", 0.10),
            ("swelling", 0.10),
            ("pain", 0.08),
            ("redness", 0.08),
        ),
        "dental_recovery": (
            ("swelling", 0.18),
            ("bleeding", 0.16),
            ("pus", 0.20),
            ("fever", 0.20),
            ("worse", 0.14),
            ("infection", 0.18),
            ("pain", 0.10),
            ("throbbing", 0.12),
            ("redness", 0.12),
        ),
    }.get(domain, ())
    for token, boost in cues:
        if token in lowered:
            pressure += boost
    return max(0.0, min(1.0, pressure))


def build_quantum_risk_packet(domain: str, context_text: str) -> Dict[str, Any]:
    configs = {
        "medication_label": {
            "domain_label": "medication_label",
            "base_bias": 0.58,
            "prior_rule": "Treat the local prior as conservative review pressure only. Visible label evidence wins, and blurry or conflicting text should raise risk instead of being guessed.",
            "summary_low": "Low review risk prior. Still confirm the label before relying on the imported schedule.",
            "summary_medium": "Medium review risk prior. Re-check the medication name, dose, interval, and max daily limit before relying on the import.",
            "summary_high": "High review risk prior. Verify every key label detail manually before saving or using this medication schedule.",
        },
        "medication_dose_safety": {
            "domain_label": "medication_dose_safety",
            "base_bias": 0.36,
            "prior_rule": "Use the local prior as a tie-breaker only after the stored dose, interval, and last-24-hour total are checked. Hard numeric contradictions win over the prior.",
            "summary_low": "Low dose-safety prior. The stored schedule looks internally consistent, but still respect the bottle and personal care instructions.",
            "summary_medium": "Medium dose-safety prior. The local schedule may be close to a limit, early, or missing details, so review carefully before logging.",
            "summary_high": "High dose-safety prior. The local schedule looks too close to a stored limit, too early, duplicated, or numerically inconsistent.",
        },
        "dental_hygiene": {
            "domain_label": "dental_hygiene",
            "base_bias": 0.42,
            "prior_rule": "Use the local prior only as a gentle caution signal. Visible plaque, redness, swelling, or blurry framing should raise risk, but do not diagnose disease.",
            "summary_low": "Low follow-up risk prior. Keep the routine consistent and monitor normally.",
            "summary_medium": "Medium follow-up risk prior. If the photo shows buildup or gum irritation, pay closer attention and tighten the routine.",
            "summary_high": "High follow-up risk prior. Visible concerns or poor image clarity should push toward a closer self-check and possible dentist follow-up.",
        },
        "dental_recovery": {
            "domain_label": "dental_recovery",
            "base_bias": 0.57,
            "prior_rule": "Use the local prior as conservative follow-up pressure only. Visible warning signs or worsening symptom notes should raise risk, but do not diagnose or overstate certainty.",
            "summary_low": "Low follow-up risk prior. Continue conservative aftercare and keep monitoring the site.",
            "summary_medium": "Medium follow-up risk prior. Compare the photo with your aftercare plan and watch closely for worsening symptoms.",
            "summary_high": "High follow-up risk prior. Visible warning signs or worsening notes deserve a careful re-check and may justify contacting a dentist.",
        },
        "assistant_context": {
            "domain_label": "assistant_context",
            "base_bias": 0.32,
            "prior_rule": "Use the local _quantum:state and RGB signal only as context-routing metadata for emphasis, ordering, and caution tone. Never present it as clinical evidence or certainty.",
            "summary_low": "Low context pressure. Keep the answer direct and focused on the user's exact request.",
            "summary_medium": "Medium context pressure. Include the most relevant vault facts, likely next action, and any missing details.",
            "summary_high": "High context pressure. Lead with safety boundaries, concrete next actions, and what should be verified before acting.",
        },
    }
    config = configs.get(domain, configs["dental_hygiene"])
    fallback_metrics = {"cpu": 0.20, "mem": 0.24, "load1": 0.16, "temp": 0.05}
    try:
        metrics = collect_system_metrics()
        metrics_line = "cpu={cpu:.2f},mem={mem:.2f},load={load1:.2f},temp={temp:.2f}".format(
            cpu=metrics.get("cpu", 0.0),
            mem=metrics.get("mem", 0.0),
            load1=metrics.get("load1", 0.0),
            temp=metrics.get("temp", 0.0),
        )
    except Exception:
        metrics = fallback_metrics
        metrics_line = "unavailable"

    metrics_rgb = metrics_to_rgb(metrics)
    signature_rgb = context_signature_rgb(domain, context_text)
    sim_rgb = (
        max(0.0, min(1.0, (metrics_rgb[0] * 0.52) + (signature_rgb[0] * 0.48))),
        max(0.0, min(1.0, (metrics_rgb[1] * 0.48) + (signature_rgb[1] * 0.52))),
        max(0.0, min(1.0, (metrics_rgb[2] * 0.40) + (signature_rgb[2] * 0.60))),
    )
    entropy_score = pennylane_entropic_score(sim_rgb)
    entropy_text = entropic_summary_text(entropy_score)
    metric_pressure = (
        (metrics.get("cpu", 0.0) * 0.34)
        + (metrics.get("mem", 0.0) * 0.26)
        + (metrics.get("load1", 0.0) * 0.25)
        + (metrics.get("temp", 0.0) * 0.15)
    )
    context_pressure = (signature_rgb[0] * 0.42) + (signature_rgb[1] * 0.34) + (signature_rgb[2] * 0.24)
    keyword_pressure = keyword_risk_pressure(domain, context_text)
    risk_fraction = max(
        0.0,
        min(
            1.0,
            (config["base_bias"] * 0.46)
            + (entropy_score * 0.24)
            + (metric_pressure * 0.12)
            + (context_pressure * 0.12)
            + (keyword_pressure * 0.06),
        ),
    )
    risk_score = round(risk_fraction * 100.0, 1)
    risk_level = risk_level_from_score(risk_score)
    summary_key = f"summary_{risk_level.lower()}"
    summary = config.get(summary_key, config["summary_medium"])
    prompt_block = "\n".join(
        [
            "[quantum_risk_sim]",
            "mode: medsafe_quantum_risk_v1",
            f"domain: {config['domain_label']}",
            f"tag: _quantum:state/{config['domain_label']}/{risk_level.lower()}",
            f"system_metrics: {metrics_line}",
            "psutil_cpu: {:.2f}".format(metrics.get("cpu", 0.0)),
            "psutil_ram: {:.2f}".format(metrics.get("mem", 0.0)),
            "psutil_load1: {:.2f}".format(metrics.get("load1", 0.0)),
            "psutil_temp: {:.2f}".format(metrics.get("temp", 0.0)),
            f"quantum_state: {entropy_text}",
            "metrics_rgb: {:.2f},{:.2f},{:.2f}".format(*metrics_rgb),
            "context_signature_rgb: {:.2f},{:.2f},{:.2f}".format(*signature_rgb),
            "sim_signal_rgb: {:.2f},{:.2f},{:.2f}".format(*sim_rgb),
            f"local_prior_risk_score: {risk_score:.1f}",
            f"local_prior_risk_level: {risk_level}",
            f"prior_rule: {config['prior_rule']}",
            "[/quantum_risk_sim]",
        ]
    )
    return {
        "domain": config["domain_label"],
        "metrics": dict(metrics),
        "metrics_line": metrics_line,
        "metrics_rgb": metrics_rgb,
        "signature_rgb": signature_rgb,
        "sim_rgb": sim_rgb,
        "entropy_text": entropy_text,
        "quantum_state_label": f"_quantum:state/{config['domain_label']}/{risk_level.lower()}",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_summary": summary,
        "prompt_block": prompt_block,
        "prior_rule": config["prior_rule"],
    }


def build_assistant_quantum_context(
    data: Dict[str, Any],
    selected_med_id: Optional[str],
    prompt: str,
    mode: str,
) -> Dict[str, Any]:
    active_mode = normalize_assistant_mode(mode)
    seed = "\n\n".join(
        [
            f"assistant_mode={active_mode}",
            build_schedule_context(data, selected_med_id),
            build_recent_assistant_context(list(data.get("assistant_history") or []), data.get("assistant_context_memory") or {}, token_budget=700),
            f"user_prompt={sanitize_text(prompt, max_chars=1500)}",
        ]
    )
    packet = build_quantum_risk_packet("assistant_context", seed)
    metrics = dict(packet.get("metrics") or {})
    route = "direct"
    if packet.get("risk_level") == "High":
        route = "safety_first"
    elif packet.get("risk_level") == "Medium":
        route = "context_expand"
    prompt_block = "\n".join(
        [
            "[assistant_quantum_rag]",
            "mode: medsafe_quantum_rgb_rag_v2",
            f"assistant_mode: {active_mode}",
            f"tag: {packet.get('quantum_state_label', '_quantum:state/assistant_context/medium')}",
            f"rag_route: {route}",
            "psutil: cpu={:.2f}, ram={:.2f}, load1={:.2f}, temp={:.2f}".format(
                metrics.get("cpu", 0.0),
                metrics.get("mem", 0.0),
                metrics.get("load1", 0.0),
                metrics.get("temp", 0.0),
            ),
            "rgb_metrics: {:.2f},{:.2f},{:.2f}".format(*packet.get("metrics_rgb", (0.0, 0.0, 0.0))),
            "rgb_signature: {:.2f},{:.2f},{:.2f}".format(*packet.get("signature_rgb", (0.0, 0.0, 0.0))),
            "rgb_simulation: {:.2f},{:.2f},{:.2f}".format(*packet.get("sim_rgb", (0.0, 0.0, 0.0))),
            f"context_pressure: {packet.get('risk_level')} {safe_float(packet.get('risk_score')):.1f}",
            f"context_summary: {sanitize_text(packet.get('risk_summary') or '', max_chars=240)}",
            "instruction: Treat this as private local routing metadata for answer structure only, not medical proof.",
            packet.get("prompt_block", ""),
            "[/assistant_quantum_rag]",
        ]
    )
    packet["rag_route"] = route
    packet["assistant_prompt_block"] = prompt_block
    return packet


def normalize_risk_fields(
    raw_payload: Dict[str, Any],
    fallback_packet: Dict[str, Any],
    *,
    summary_keys: Tuple[str, ...] = ("risk_summary", "review_summary"),
) -> Dict[str, Any]:
    raw_score = raw_payload.get("risk_score")
    if raw_score is None:
        raw_score = raw_payload.get("review_risk_score")
    score = safe_float(raw_score if raw_score is not None else fallback_packet.get("risk_score", 0.0))
    if 0.0 < score <= 1.0:
        score *= 100.0
    score = max(0.0, min(100.0, score))
    if raw_score in (None, "", 0, 0.0) and score <= 0.0:
        score = max(0.0, min(100.0, safe_float(fallback_packet.get("risk_score"))))
    level = normalized_risk_level_text(
        raw_payload.get("risk_level") or raw_payload.get("review_risk_level") or "",
        score,
    )
    summary = ""
    for key in summary_keys:
        summary = sanitize_text(raw_payload.get(key) or "", max_chars=260)
        if summary:
            break
    if not summary:
        summary = sanitize_text(fallback_packet.get("risk_summary") or "", max_chars=260)
    return {
        "risk_score": score,
        "risk_level": level,
        "risk_summary": summary,
    }


def dental_hygiene_defaults() -> Dict[str, Any]:
    return {
        "brush_interval_hours": 12.0,
        "floss_interval_hours": 24.0,
        "rinse_interval_hours": 24.0,
        "last_brush_ts": 0.0,
        "last_floss_ts": 0.0,
        "last_rinse_ts": 0.0,
        "latest_score": 0.0,
        "latest_rating": "",
        "latest_summary": "",
        "latest_suggestions": "",
        "latest_warning_flags": "",
        "latest_risk_score": 0.0,
        "latest_risk_level": "",
        "latest_risk_summary": "",
        "latest_photo": "",
        "latest_timestamp": 0.0,
        "history": [],
    }


def dental_recovery_defaults() -> Dict[str, Any]:
    return {
        "enabled": False,
        "procedure_type": "",
        "procedure_date": "",
        "symptom_notes": "",
        "care_notes": "",
        "latest_score": 0.0,
        "latest_status": "",
        "latest_summary": "",
        "latest_advice": "",
        "latest_warning_flags": "",
        "latest_risk_score": 0.0,
        "latest_risk_level": "",
        "latest_risk_summary": "",
        "latest_photo": "",
        "latest_timestamp": 0.0,
        "daily_logs": [],
    }


def exercise_defaults() -> Dict[str, Any]:
    return {
        "walk_interval_hours": 4.0,
        "light_interval_hours": 8.0,
        "stretch_interval_hours": 2.0,
        "daily_walk_goal_minutes": 30.0,
        "daily_light_goal_minutes": 20.0,
        "daily_stretch_goal_minutes": 10.0,
        "last_walk_ts": 0.0,
        "last_light_ts": 0.0,
        "last_stretch_ts": 0.0,
        "notes": "",
        "history": [],
    }


def recovery_support_defaults() -> Dict[str, Any]:
    return {
        "enabled": False,
        "goal_name": "Recovery",
        "clean_start_date": "",
        "last_relapse_date": "",
        "relapse_count": 0,
        "best_streak_days": 0,
        "points": 0,
        "cycle": 1,
        "milestones_claimed": [],
        "motivation": "",
        "coping_plan": "",
        "latest_note": "",
        "latest_checkin_ts": 0.0,
        "latest_mood": 5.0,
        "latest_craving": 0.0,
        "reminder_time": "8:00 PM",
        "history": [],
    }


def dose_safety_review_defaults() -> Dict[str, Any]:
    return {
        "timestamp": 0.0,
        "med_id": "",
        "med_name": "",
        "dose_mg": 0.0,
        "source_label": "",
        "action": "",
        "display": "",
        "message": "",
        "raw": "",
        "quantum_level": "",
        "quantum_score": 0.0,
        "deterministic_level": "",
        "deterministic_message": "",
    }


def safety_reviews_defaults() -> Dict[str, Any]:
    return {
        "timestamp": 0.0,
        "signature": "",
        "pending": False,
        "reason": "",
        "per_med": [],
        "regimen": {
            "action": "",
            "display": "",
            "message": "",
            "raw": "",
            "signature": "",
        },
    }


def normalized_med_entry(item: Any, *, default_archived_ts: float = 0.0) -> Optional[Dict[str, Any]]:
    if not isinstance(item, dict):
        return None
    history_rows = []
    for row in item.get("history", []) or []:
        if isinstance(row, dict):
            entry = [
                safe_float(row.get("timestamp") or row.get("taken_ts") or 0.0),
                max(0.0, safe_float(row.get("dose_mg") or row.get("amount_mg") or row.get("dose") or 0.0)),
            ]
            scheduled_ts = safe_float(row.get("scheduled_ts") or 0.0)
            slot_key = sanitize_text(row.get("slot_key") or "", max_chars=64)
            if scheduled_ts > 0.0 or slot_key:
                entry.extend([scheduled_ts, slot_key])
            if entry[0] > 0.0 and entry[1] > 0.0:
                history_rows.append(entry)
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            entry = [safe_float(row[0]), max(0.0, safe_float(row[1]))]
            scheduled_ts = safe_float(row[2]) if len(row) >= 3 else 0.0
            slot_key = sanitize_text(row[3] if len(row) >= 4 else "", max_chars=64)
            if scheduled_ts > 0.0 or slot_key:
                entry.extend([scheduled_ts, slot_key])
            if entry[0] > 0.0 and entry[1] > 0.0:
                history_rows.append(entry)
    created_ts = safe_float(item.get("created_ts") or 0.0)
    if created_ts <= 0.0:
        created_ts = safe_float(item.get("last_taken_ts") or 0.0)
    if created_ts <= 0.0 and not history_rows:
        created_ts = time.time()
    archived_ts = max(0.0, safe_float(item.get("archived_ts") or default_archived_ts))
    return {
        "id": sanitize_text(item.get("id") or uuid.uuid4().hex[:12], max_chars=32),
        "name": sanitize_text(item.get("name") or "Medication", max_chars=120),
        "dose_mg": max(0.0, safe_float(item.get("dose_mg"))),
        "interval_hours": max(0.0, safe_float(item.get("interval_hours"))),
        "max_daily_mg": max(0.0, safe_float(item.get("max_daily_mg"))),
        "created_ts": created_ts,
        "archived_ts": archived_ts,
        "first_dose_time": sanitize_text(item.get("first_dose_time") or "", max_chars=20),
        "custom_times_text": sanitize_text(item.get("custom_times_text") or "", max_chars=320),
        "schedule_text": sanitize_text(item.get("schedule_text") or "", max_chars=240),
        "notes": sanitize_text(item.get("notes") or "", max_chars=600),
        "source": sanitize_text(item.get("source") or "manual", max_chars=40),
        "source_photo": sanitize_text(item.get("source_photo") or "", max_chars=180),
        "last_taken_ts": safe_float(item.get("last_taken_ts")),
        "history": history_rows[-240:],
    }


def vault_defaults() -> Dict[str, Any]:
    return {
        "version": 3,
        "meds": [],
        "med_archives": [],
        "assistant_history": [],
        "assistant_context_memory": assistant_context_memory_defaults(),
        "dose_safety_review": dose_safety_review_defaults(),
        "safety_reviews": safety_reviews_defaults(),
        "vision_imports": [],
        "dental_hygiene": dental_hygiene_defaults(),
        "dental_recovery": dental_recovery_defaults(),
        "exercise": exercise_defaults(),
        "recovery_support": recovery_support_defaults(),
        "last_notifications": {},
    }


def ensure_vault_shape(raw: Any) -> Dict[str, Any]:
    base = vault_defaults()
    if not isinstance(raw, dict):
        return base

    meds: List[Dict[str, Any]] = []
    med_archives: List[Dict[str, Any]] = []
    for item in raw.get("meds", []) or []:
        parsed_med = normalized_med_entry(item)
        if parsed_med is None:
            continue
        if medication_is_archived(parsed_med):
            med_archives.append(parsed_med)
        else:
            meds.append(parsed_med)
    for item in raw.get("med_archives", []) or []:
        parsed_med = normalized_med_entry(item, default_archived_ts=time.time())
        if parsed_med is not None:
            med_archives.append(parsed_med)

    assistant_history = []
    for item in raw.get("assistant_history", []) or []:
        if not isinstance(item, dict):
            continue
        assistant_history.append(
            {
                "role": sanitize_text(item.get("role") or "assistant", max_chars=16) or "assistant",
                "mode": normalize_assistant_mode(item.get("mode") or "General"),
                "content": sanitize_text(item.get("content") or "", max_chars=10000),
                "timestamp": safe_float(item.get("timestamp") or time.time()),
            }
        )

    assistant_context_memory = normalize_assistant_context_memory(raw.get("assistant_context_memory") or {})

    dose_safety_raw = raw.get("dose_safety_review") if isinstance(raw.get("dose_safety_review"), dict) else {}
    dose_safety_review = dose_safety_review_defaults()
    dose_safety_review["timestamp"] = safe_float(dose_safety_raw.get("timestamp") or 0.0)
    dose_safety_review["med_id"] = sanitize_text(dose_safety_raw.get("med_id") or "", max_chars=32)
    dose_safety_review["med_name"] = sanitize_text(dose_safety_raw.get("med_name") or "", max_chars=120)
    dose_safety_review["dose_mg"] = max(0.0, safe_float(dose_safety_raw.get("dose_mg") or 0.0))
    dose_safety_review["source_label"] = sanitize_text(dose_safety_raw.get("source_label") or "", max_chars=60)
    dose_safety_review["action"] = normalize_dose_action_text(dose_safety_raw.get("action") or "", "")
    dose_safety_review["display"] = sanitize_text(dose_safety_raw.get("display") or "", max_chars=160)
    dose_safety_review["message"] = sanitize_text(dose_safety_raw.get("message") or "", max_chars=420)
    dose_safety_review["raw"] = sanitize_text(dose_safety_raw.get("raw") or "", max_chars=400)
    dose_safety_review["quantum_level"] = sanitize_text(dose_safety_raw.get("quantum_level") or "", max_chars=40)
    dose_safety_review["quantum_score"] = max(0.0, min(100.0, safe_float(dose_safety_raw.get("quantum_score") or 0.0)))
    dose_safety_review["deterministic_level"] = sanitize_text(dose_safety_raw.get("deterministic_level") or "", max_chars=40)
    dose_safety_review["deterministic_message"] = sanitize_text(dose_safety_raw.get("deterministic_message") or "", max_chars=260)

    safety_reviews_raw = raw.get("safety_reviews") if isinstance(raw.get("safety_reviews"), dict) else {}
    safety_reviews = safety_reviews_defaults()
    safety_reviews["timestamp"] = safe_float(safety_reviews_raw.get("timestamp") or 0.0)
    safety_reviews["signature"] = sanitize_text(safety_reviews_raw.get("signature") or "", max_chars=120)
    safety_reviews["pending"] = bool(safety_reviews_raw.get("pending", False))
    safety_reviews["reason"] = sanitize_text(safety_reviews_raw.get("reason") or "", max_chars=160)
    parsed_per_med: List[Dict[str, Any]] = []
    for item in safety_reviews_raw.get("per_med", []) or []:
        if not isinstance(item, dict):
            continue
        parsed_per_med.append(
            {
                "timestamp": safe_float(item.get("timestamp") or 0.0),
                "med_id": sanitize_text(item.get("med_id") or "", max_chars=32),
                "med_name": sanitize_text(item.get("med_name") or "", max_chars=120),
                "action": normalize_dose_action_text(item.get("action") or "", ""),
                "display": sanitize_text(item.get("display") or "", max_chars=160),
                "message": sanitize_text(item.get("message") or "", max_chars=420),
                "raw": sanitize_text(item.get("raw") or "", max_chars=400),
                "deterministic_level": sanitize_text(item.get("deterministic_level") or "", max_chars=40),
                "deterministic_message": sanitize_text(item.get("deterministic_message") or "", max_chars=260),
            }
        )
    safety_reviews["per_med"] = parsed_per_med[:48]
    regimen_raw = safety_reviews_raw.get("regimen") if isinstance(safety_reviews_raw.get("regimen"), dict) else {}
    safety_reviews["regimen"] = {
        "action": normalize_dose_action_text(regimen_raw.get("action") or "", ""),
        "display": sanitize_text(regimen_raw.get("display") or "", max_chars=160),
        "message": sanitize_text(regimen_raw.get("message") or "", max_chars=420),
        "raw": sanitize_text(regimen_raw.get("raw") or "", max_chars=400),
        "signature": sanitize_text(regimen_raw.get("signature") or "", max_chars=120),
    }

    imports = []
    for item in raw.get("vision_imports", []) or []:
        if not isinstance(item, dict):
            continue
        imports.append(
            {
                "timestamp": safe_float(item.get("timestamp") or time.time()),
                "image_name": sanitize_text(item.get("image_name") or "", max_chars=160),
                "med_id": sanitize_text(item.get("med_id") or "", max_chars=32),
                "summary": sanitize_text(item.get("summary") or "", max_chars=500),
                "risk_score": max(0.0, min(100.0, safe_float(item.get("risk_score")))),
                "risk_level": normalized_risk_level_text(item.get("risk_level") or "", safe_float(item.get("risk_score"))),
                "risk_summary": sanitize_text(item.get("risk_summary") or "", max_chars=260),
            }
        )

    hygiene_raw = raw.get("dental_hygiene") if isinstance(raw.get("dental_hygiene"), dict) else {}
    hygiene = dental_hygiene_defaults()
    hygiene["brush_interval_hours"] = max(1.0, safe_float(hygiene_raw.get("brush_interval_hours") or hygiene["brush_interval_hours"]))
    hygiene["floss_interval_hours"] = max(1.0, safe_float(hygiene_raw.get("floss_interval_hours") or hygiene["floss_interval_hours"]))
    hygiene["rinse_interval_hours"] = max(1.0, safe_float(hygiene_raw.get("rinse_interval_hours") or hygiene["rinse_interval_hours"]))
    hygiene["last_brush_ts"] = safe_float(hygiene_raw.get("last_brush_ts"))
    hygiene["last_floss_ts"] = safe_float(hygiene_raw.get("last_floss_ts"))
    hygiene["last_rinse_ts"] = safe_float(hygiene_raw.get("last_rinse_ts"))
    hygiene["latest_score"] = max(0.0, min(100.0, safe_float(hygiene_raw.get("latest_score"))))
    hygiene["latest_rating"] = sanitize_text(hygiene_raw.get("latest_rating") or "", max_chars=80)
    hygiene["latest_summary"] = sanitize_text(hygiene_raw.get("latest_summary") or "", max_chars=500)
    hygiene["latest_suggestions"] = sanitize_text(hygiene_raw.get("latest_suggestions") or "", max_chars=700)
    hygiene["latest_warning_flags"] = sanitize_text(hygiene_raw.get("latest_warning_flags") or "", max_chars=400)
    hygiene["latest_risk_score"] = max(0.0, min(100.0, safe_float(hygiene_raw.get("latest_risk_score"))))
    hygiene["latest_risk_level"] = normalized_risk_level_text(hygiene_raw.get("latest_risk_level") or "", hygiene["latest_risk_score"])
    hygiene["latest_risk_summary"] = sanitize_text(hygiene_raw.get("latest_risk_summary") or "", max_chars=260)
    hygiene["latest_photo"] = sanitize_text(hygiene_raw.get("latest_photo") or "", max_chars=180)
    hygiene["latest_timestamp"] = safe_float(hygiene_raw.get("latest_timestamp"))
    hygiene_history = []
    for item in hygiene_raw.get("history", []) or []:
        if not isinstance(item, dict):
            continue
        hygiene_history.append(
            {
                "timestamp": safe_float(item.get("timestamp") or time.time()),
                "image_name": sanitize_text(item.get("image_name") or "", max_chars=160),
                "score": max(0.0, min(100.0, safe_float(item.get("score")))),
                "rating": sanitize_text(item.get("rating") or "", max_chars=80),
                "summary": sanitize_text(item.get("summary") or "", max_chars=300),
                "suggestions": sanitize_text(item.get("suggestions") or "", max_chars=400),
                "warning_flags": sanitize_text(item.get("warning_flags") or "", max_chars=240),
                "confidence": max(0.0, min(1.0, safe_float(item.get("confidence")))),
                "risk_score": max(0.0, min(100.0, safe_float(item.get("risk_score")))),
                "risk_level": normalized_risk_level_text(item.get("risk_level") or "", safe_float(item.get("risk_score"))),
                "risk_summary": sanitize_text(item.get("risk_summary") or "", max_chars=220),
            }
        )
    hygiene["history"] = hygiene_history[-20:]

    recovery_raw = raw.get("dental_recovery") if isinstance(raw.get("dental_recovery"), dict) else {}
    recovery = dental_recovery_defaults()
    recovery["enabled"] = bool(recovery_raw.get("enabled", False))
    recovery["procedure_type"] = sanitize_text(recovery_raw.get("procedure_type") or "", max_chars=120)
    recovery["procedure_date"] = sanitize_text(recovery_raw.get("procedure_date") or "", max_chars=20)
    recovery["symptom_notes"] = sanitize_text(recovery_raw.get("symptom_notes") or "", max_chars=600)
    recovery["care_notes"] = sanitize_text(recovery_raw.get("care_notes") or "", max_chars=600)
    recovery["latest_score"] = max(0.0, min(100.0, safe_float(recovery_raw.get("latest_score"))))
    recovery["latest_status"] = sanitize_text(recovery_raw.get("latest_status") or "", max_chars=120)
    recovery["latest_summary"] = sanitize_text(recovery_raw.get("latest_summary") or "", max_chars=700)
    recovery["latest_advice"] = sanitize_text(recovery_raw.get("latest_advice") or "", max_chars=900)
    recovery["latest_warning_flags"] = sanitize_text(recovery_raw.get("latest_warning_flags") or "", max_chars=400)
    recovery["latest_risk_score"] = max(0.0, min(100.0, safe_float(recovery_raw.get("latest_risk_score"))))
    recovery["latest_risk_level"] = normalized_risk_level_text(recovery_raw.get("latest_risk_level") or "", recovery["latest_risk_score"])
    recovery["latest_risk_summary"] = sanitize_text(recovery_raw.get("latest_risk_summary") or "", max_chars=260)
    recovery["latest_photo"] = sanitize_text(recovery_raw.get("latest_photo") or "", max_chars=180)
    recovery["latest_timestamp"] = safe_float(recovery_raw.get("latest_timestamp"))
    daily_logs = []
    for item in recovery_raw.get("daily_logs", []) or []:
        if not isinstance(item, dict):
            continue
        daily_logs.append(
            {
                "timestamp": safe_float(item.get("timestamp") or time.time()),
                "image_name": sanitize_text(item.get("image_name") or "", max_chars=160),
                "day_number": max(0, int(safe_float(item.get("day_number") or 0))),
                "score": max(0.0, min(100.0, safe_float(item.get("score")))),
                "status": sanitize_text(item.get("status") or "", max_chars=120),
                "summary": sanitize_text(item.get("summary") or "", max_chars=400),
                "advice": sanitize_text(item.get("advice") or "", max_chars=500),
                "warning_flags": sanitize_text(item.get("warning_flags") or "", max_chars=260),
                "confidence": max(0.0, min(1.0, safe_float(item.get("confidence")))),
                "risk_score": max(0.0, min(100.0, safe_float(item.get("risk_score")))),
                "risk_level": normalized_risk_level_text(item.get("risk_level") or "", safe_float(item.get("risk_score"))),
                "risk_summary": sanitize_text(item.get("risk_summary") or "", max_chars=220),
            }
        )
    recovery["daily_logs"] = daily_logs[-30:]

    exercise_raw = raw.get("exercise") if isinstance(raw.get("exercise"), dict) else {}
    exercise = exercise_defaults()
    exercise["walk_interval_hours"] = max(0.5, safe_float(exercise_raw.get("walk_interval_hours") or exercise["walk_interval_hours"]))
    exercise["light_interval_hours"] = max(0.5, safe_float(exercise_raw.get("light_interval_hours") or exercise["light_interval_hours"]))
    exercise["stretch_interval_hours"] = max(0.5, safe_float(exercise_raw.get("stretch_interval_hours") or exercise["stretch_interval_hours"]))
    exercise["daily_walk_goal_minutes"] = max(1.0, safe_float(exercise_raw.get("daily_walk_goal_minutes") or exercise["daily_walk_goal_minutes"]))
    exercise["daily_light_goal_minutes"] = max(1.0, safe_float(exercise_raw.get("daily_light_goal_minutes") or exercise["daily_light_goal_minutes"]))
    exercise["daily_stretch_goal_minutes"] = max(1.0, safe_float(exercise_raw.get("daily_stretch_goal_minutes") or exercise["daily_stretch_goal_minutes"]))
    exercise["last_walk_ts"] = safe_float(exercise_raw.get("last_walk_ts"))
    exercise["last_light_ts"] = safe_float(exercise_raw.get("last_light_ts"))
    exercise["last_stretch_ts"] = safe_float(exercise_raw.get("last_stretch_ts"))
    exercise["notes"] = sanitize_text(exercise_raw.get("notes") or "", max_chars=800)
    exercise_history = []
    for item in exercise_raw.get("history", []) or []:
        if not isinstance(item, dict):
            continue
        habit_name = sanitize_text(item.get("habit") or "", max_chars=16).lower()
        if habit_name not in {"walk", "light", "stretch"}:
            continue
        exercise_history.append(
            {
                "timestamp": safe_float(item.get("timestamp") or time.time()),
                "habit": habit_name,
                "minutes": max(0.0, safe_float(item.get("minutes"))),
            }
        )
    exercise["history"] = exercise_history[-240:]

    recovery_support_raw = raw.get("recovery_support") if isinstance(raw.get("recovery_support"), dict) else {}
    recovery_support = recovery_support_defaults()
    recovery_support["enabled"] = bool(recovery_support_raw.get("enabled", False))
    recovery_support["goal_name"] = sanitize_text(recovery_support_raw.get("goal_name") or recovery_support["goal_name"], max_chars=120) or "Recovery"
    recovery_support["clean_start_date"] = sanitize_text(recovery_support_raw.get("clean_start_date") or "", max_chars=20)
    recovery_support["last_relapse_date"] = sanitize_text(recovery_support_raw.get("last_relapse_date") or "", max_chars=20)
    recovery_support["relapse_count"] = max(0, int(safe_float(recovery_support_raw.get("relapse_count") or 0)))
    recovery_support["best_streak_days"] = max(0, int(safe_float(recovery_support_raw.get("best_streak_days") or 0)))
    recovery_support["points"] = max(0, int(safe_float(recovery_support_raw.get("points") or 0)))
    recovery_support["cycle"] = max(1, int(safe_float(recovery_support_raw.get("cycle") or 1)))
    recovery_support["milestones_claimed"] = [
        sanitize_text(item, max_chars=24)
        for item in list(recovery_support_raw.get("milestones_claimed") or [])
        if sanitize_text(item, max_chars=24)
    ][-64:]
    recovery_support["motivation"] = sanitize_text(recovery_support_raw.get("motivation") or "", max_chars=1200)
    recovery_support["coping_plan"] = sanitize_text(recovery_support_raw.get("coping_plan") or "", max_chars=1200)
    recovery_support["latest_note"] = sanitize_text(recovery_support_raw.get("latest_note") or "", max_chars=1200)
    recovery_support["latest_checkin_ts"] = safe_float(recovery_support_raw.get("latest_checkin_ts"))
    recovery_support["latest_mood"] = max(0.0, min(10.0, safe_float(recovery_support_raw.get("latest_mood") or recovery_support["latest_mood"])))
    recovery_support["latest_craving"] = max(0.0, min(10.0, safe_float(recovery_support_raw.get("latest_craving") or recovery_support["latest_craving"])))
    reminder_time = sanitize_text(recovery_support_raw.get("reminder_time") or recovery_support["reminder_time"], max_chars=20)
    recovery_support["reminder_time"] = reminder_time if not reminder_time or parse_clock_minutes(reminder_time) is not None else recovery_support_defaults()["reminder_time"]
    recovery_history = []
    for item in recovery_support_raw.get("history", []) or []:
        if not isinstance(item, dict):
            continue
        event_type = sanitize_text(item.get("type") or "", max_chars=20).lower()
        if event_type not in {"checkin", "relapse", "milestone"}:
            continue
        recovery_history.append(
            {
                "timestamp": safe_float(item.get("timestamp") or time.time()),
                "type": event_type,
                "note": sanitize_text(item.get("note") or "", max_chars=1200),
                "streak_days": max(0, int(safe_float(item.get("streak_days") or 0))),
                "points_delta": int(safe_float(item.get("points_delta") or 0)),
                "mood": max(0.0, min(10.0, safe_float(item.get("mood") or 0.0))),
                "craving": max(0.0, min(10.0, safe_float(item.get("craving") or 0.0))),
                "label": sanitize_text(item.get("label") or "", max_chars=120),
            }
        )
    recovery_support["history"] = recovery_history[-240:]

    base["meds"] = meds
    base["med_archives"] = med_archives[-240:]
    base["assistant_context_memory"] = assistant_context_memory
    base["assistant_history"] = assistant_history[-ASSISTANT_CONTEXT_MAX_MESSAGES:]
    base["dose_safety_review"] = dose_safety_review
    base["safety_reviews"] = safety_reviews
    base["vision_imports"] = imports[-16:]
    base["dental_hygiene"] = hygiene
    base["dental_recovery"] = recovery
    base["exercise"] = exercise
    base["recovery_support"] = recovery_support
    if isinstance(raw.get("last_notifications"), dict):
        base["last_notifications"] = dict(raw["last_notifications"])
    return base


class EncryptedVault:
    def __init__(self, paths: AppPaths):
        self.paths = paths
        self.lock = RLock()
        self.cached_key: Optional[bytes] = None
        self.session_password: Optional[str] = None

    def clear_cached_key(self) -> None:
        with self.lock:
            self.cached_key = None
            self.session_password = None

    def key_status(self) -> str:
        """Return missing, raw, protected, or invalid for the local vault key file."""
        with self.lock:
            if not self.paths.key_path.exists():
                return "missing"
            try:
                data = self.paths.key_path.read_bytes()
            except Exception:
                return "invalid"
            if is_protected_key_blob(data):
                return "protected"
            if len(data) == 32:
                return "raw"
            return "invalid"

    def is_key_protected(self) -> bool:
        return self.key_status() == "protected"

    def is_unlocked(self) -> bool:
        return self.cached_key is not None

    def validate_current_password(self, password: Optional[str]) -> bytes:
        """Validate the current startup password against the key file even if the vault is already unlocked."""
        with self.lock:
            data = self.paths.key_path.read_bytes()
            if is_protected_key_blob(data):
                active_password = sanitize_text(password or "", max_chars=256)
                if not active_password:
                    raise RuntimeError("Current startup password is required.")
                try:
                    raw_key = unlock_protected_key(data, active_password)
                except Exception as exc:
                    raise RuntimeError("Current startup password could not unlock the encrypted vault.") from exc
                if self.cached_key is not None and raw_key != self.cached_key:
                    raise RuntimeError("Current startup password did not match the unlocked vault key.")
                self.cached_key = raw_key
                self.session_password = active_password
                return raw_key
            if len(data) == 32:
                self.cached_key = data
                self.session_password = None
                return data
            raise RuntimeError("The local vault key file is invalid. Raw key files must be exactly 32 bytes.")

    def save_key(self, raw_key: bytes, password: Optional[str] = None) -> bytes:
        with self.lock:
            if len(raw_key) != 32:
                raise ValueError("Vault key must be 32 bytes.")
            blob = protect_raw_key(raw_key, password) if password else raw_key
            _atomic_write_bytes(self.paths.key_path, blob)
            self.cached_key = raw_key
            self.session_password = sanitize_text(password, max_chars=256) if password else None
            return raw_key

    def get_or_create_key(self, password: Optional[str] = None, *, allow_create: bool = True) -> bytes:
        with self.lock:
            if self.paths.key_path.exists():
                data = self.paths.key_path.read_bytes()
                if is_protected_key_blob(data):
                    if password is not None:
                        return self.validate_current_password(password)
                    if self.cached_key is not None:
                        return self.cached_key
                    active_password = sanitize_text(self.session_password or "", max_chars=256)
                    if not active_password:
                        raise RuntimeError("A startup password is required to unlock this encrypted vault.")
                    return self.validate_current_password(active_password)
                if len(data) == 32:
                    self.cached_key = data
                    self.session_password = None
                    return self.cached_key
                raise RuntimeError("The local vault key file is invalid. Raw key files must be exactly 32 bytes.")
            if not allow_create:
                raise RuntimeError("The local vault key is missing.")
            require_crypto()
            key = AESGCM.generate_key(256)
            return self.save_key(key, password=password)

    def enable_password(self, password: str, current_password: Optional[str] = None) -> None:
        with self.lock:
            if self.key_status() == "protected":
                raw_key = self.validate_current_password(current_password)
            else:
                raw_key = self.get_or_create_key(allow_create=True)
            self.save_key(raw_key, password=password)

    def disable_password(self, current_password: Optional[str] = None) -> None:
        with self.lock:
            raw_key = self.validate_current_password(current_password) if self.key_status() == "protected" else self.get_or_create_key()
            self.save_key(raw_key, password=None)

    def rotate_key(self, new_password: Optional[str] = None, current_password: Optional[str] = None) -> None:
        with self.lock:
            current_key = self.validate_current_password(current_password) if self.key_status() == "protected" else self.get_or_create_key()
            if new_password is None and self.is_key_protected():
                new_password = current_password or self.session_password
            require_crypto()
            next_key = AESGCM.generate_key(256)
            original_key_blob = self.paths.key_path.read_bytes() if self.paths.key_path.exists() else None
            original_vault_blob = self.paths.vault_path.read_bytes() if self.paths.vault_path.exists() else None
            next_vault_blob = aes_encrypt(aes_decrypt(original_vault_blob, current_key), next_key) if original_vault_blob else None
            temp_plain = _tmp_path("medsafe_rotate_model", ".litertlm")
            temp_encrypted = _tmp_path("medsafe_rotate_model", ".litertlm.aes")
            model_replaced = False
            try:
                if self.paths.encrypted_model_path.exists():
                    decrypt_file(self.paths.encrypted_model_path, temp_plain, current_key)
                    encrypt_file(temp_plain, temp_encrypted, next_key)
                    temp_encrypted.replace(self.paths.encrypted_model_path)
                    _set_owner_only_permissions(self.paths.encrypted_model_path)
                    model_replaced = True
                if next_vault_blob is not None:
                    _atomic_write_bytes(self.paths.vault_path, next_vault_blob)
                self.save_key(next_key, password=new_password)
            except Exception as exc:
                if original_vault_blob is not None:
                    _atomic_write_bytes(self.paths.vault_path, original_vault_blob)
                else:
                    safe_cleanup([self.paths.vault_path])
                if original_key_blob is not None:
                    _atomic_write_bytes(self.paths.key_path, original_key_blob)
                else:
                    safe_cleanup([self.paths.key_path])
                if model_replaced:
                    safe_cleanup([self.paths.encrypted_model_path])
                self.cached_key = current_key
                self.session_password = current_password or self.session_password
                raise RuntimeError(
                    "Key rotation failed. The vault key and medication vault were restored; re-download the model if needed."
                ) from exc
            finally:
                safe_cleanup([temp_plain, temp_encrypted])

    def load(self, password: Optional[str] = None) -> Dict[str, Any]:
        with self.lock:
            if not self.paths.vault_path.exists():
                return vault_defaults()
            try:
                plaintext = aes_decrypt(
                    self.paths.vault_path.read_bytes(),
                    self.get_or_create_key(password=password, allow_create=False),
                )
                return ensure_vault_shape(json.loads(plaintext.decode("utf-8")))
            except RuntimeError:
                raise
            except Exception as exc:
                raise RuntimeError(
                    "Encrypted vault could not be read. MedSafe blocked saving to avoid overwriting existing data."
                ) from exc

    def save(self, data: Dict[str, Any], password: Optional[str] = None) -> None:
        with self.lock:
            payload = json.dumps(ensure_vault_shape(data), ensure_ascii=False, indent=2).encode("utf-8")
            _atomic_write_bytes(self.paths.vault_path, aes_encrypt(payload, self.get_or_create_key(password=password)))


def load_settings(paths: Optional[AppPaths] = None) -> Dict[str, Any]:
    target = (paths or require_paths()).settings_path
    if not target.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_SETTINGS)
    settings = dict(DEFAULT_SETTINGS)
    settings.update({key: raw.get(key, default) for key, default in DEFAULT_SETTINGS.items()})
    settings["inference_backend"] = normalize_setting_choice(settings.get("inference_backend"), INFERENCE_BACKEND_OPTIONS, "Auto")
    settings["auto_selected_inference_backend"] = normalize_setting_choice(
        settings.get("auto_selected_inference_backend"),
        ("", "CPU", "GPU"),
        "",
    )
    settings["enable_native_image_input"] = bool(settings.get("enable_native_image_input", True))
    settings["setup_complete"] = bool(settings.get("setup_complete", False))
    settings["startup_password_enabled"] = bool(settings.get("startup_password_enabled", False))
    settings["allow_checklist_uncheck"] = bool(settings.get("allow_checklist_uncheck", False))
    settings["text_size"] = normalize_setting_choice(settings.get("text_size"), TEXT_SIZE_OPTIONS, "Default")
    try:
        settings["assistant_chat_font_delta"] = max(-6, min(10, int(settings.get("assistant_chat_font_delta", 2))))
    except Exception:
        settings["assistant_chat_font_delta"] = 2
    return settings


def save_settings(settings: Dict[str, Any], paths: Optional[AppPaths] = None) -> None:
    target = (paths or require_paths()).settings_path
    _atomic_write_bytes(target, json.dumps(load_settings(paths) | settings, indent=2).encode("utf-8"))


def existing_app_install(paths: AppPaths) -> bool:
    # Model artifacts alone should not bypass first-run setup.
    return any(path.exists() for path in (paths.key_path, paths.vault_path, paths.settings_path))


def require_litert_lm() -> None:
    global litert_lm, LITERT_IMPORT_ERROR
    if litert_lm is None and LITERT_IMPORT_ERROR is None:
        try:
            import litert_lm as litert_lm_module
        except Exception as exc:
            LITERT_IMPORT_ERROR = exc
        else:
            litert_lm = litert_lm_module
    if litert_lm is None:
        detail = f" Import error: {LITERT_IMPORT_ERROR}" if LITERT_IMPORT_ERROR else ""
        raise RuntimeError("LiteRT-LM is not installed on this device yet." + detail)


def _litert_backend_attr(*names: str) -> Any:
    require_litert_lm()
    for name in names:
        try:
            return getattr(litert_lm.Backend, name)
        except Exception:
            continue
    return None


def _litert_cpu_backend() -> Any:
    backend = _litert_backend_attr("CPU")
    if backend is None:
        raise RuntimeError("This LiteRT-LM build does not expose a CPU backend.")
    return backend


def _litert_gpu_backend() -> Any:
    backend = _litert_backend_attr("GPU", "WEBGPU", "WEB_GPU", "GPU_WEBGPU")
    if backend is None:
        available = ", ".join(name for name in dir(litert_lm.Backend) if not name.startswith("_"))
        raise RuntimeError(f"GPU backend not available in LiteRT-LM. Available: {available or 'unknown'}")
    return backend


def gpu_inference_looks_available() -> bool:
    if os.environ.get("MEDSAFE_DISABLE_GPU_AUTO") == "1":
        return False
    if os.environ.get("MEDSAFE_FORCE_GPU_AUTO") == "1":
        return True
    if os.path.exists("/dev/dri"):
        try:
            return any(Path("/dev/dri").glob("renderD*"))
        except Exception:
            return False
    return any(Path(path).exists() for path in ("/dev/nvidia0", "/dev/nvidiactl"))


def choose_auto_inference_backend_name() -> str:
    gpu_backend = _litert_backend_attr("GPU", "WEBGPU", "WEB_GPU", "GPU_WEBGPU")
    return "GPU" if gpu_backend is not None and gpu_inference_looks_available() else "CPU"


def resolve_inference_backend_name(preference: str = "Auto") -> Tuple[str, bool]:
    selected = normalize_setting_choice(preference, INFERENCE_BACKEND_OPTIONS, "Auto")
    if selected != "Auto":
        return selected, False
    settings = load_settings()
    saved = normalize_setting_choice(settings.get("auto_selected_inference_backend"), ("", "CPU", "GPU"), "")
    if saved:
        return saved, True
    auto_selected = choose_auto_inference_backend_name()
    save_settings({"auto_selected_inference_backend": auto_selected})
    return auto_selected, True


def backend_value_for_name(backend_name: str) -> Any:
    if backend_name == "GPU":
        return _litert_gpu_backend()
    return _litert_cpu_backend()


def validate_image_path(image_path: Union[str, Path]) -> Path:
    raw_path = Path(image_path).expanduser()
    if raw_path.is_symlink():
        raise ValueError("Symlinked images are not allowed.")
    path = raw_path.resolve(strict=True)
    if not path.is_file():
        raise ValueError("Selected image is not a regular file.")
    if path.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        raise ValueError(f"Unsupported image type. Allowed extensions: {allowed}.")
    size = path.stat().st_size
    if size <= 0:
        raise ValueError("Selected image is empty.")
    if size > MAX_IMAGE_BYTES:
        raise ValueError(f"Selected image is too large. Limit: {human_size(MAX_IMAGE_BYTES)}.")
    with path.open("rb") as handle:
        header = handle.read(16)
    looks_like_jpeg = path.suffix.lower() in {".jpg", ".jpeg"} and header.startswith(b"\xff\xd8\xff")
    looks_like_png = path.suffix.lower() == ".png" and header.startswith(b"\x89PNG\r\n\x1a\n")
    looks_like_webp = path.suffix.lower() == ".webp" and header[:4] == b"RIFF" and header[8:12] == b"WEBP"
    if not (looks_like_jpeg or looks_like_png or looks_like_webp):
        raise ValueError("Selected image bytes do not match the file extension.")
    return path


def configured_model_supports_native_image_input() -> bool:
    lowered = MODEL_FILE.lower()
    return any(marker in lowered for marker in ("gemma-4", "gemma-3n", "multimodal", "vision"))


def image_metadata_prompt(image_path: Path, *, native_requested: bool, native_allowed: bool) -> str:
    return (
        "\n\n[Validated image attachment]\n"
        f"filename: {sanitize_text(image_path.name, max_chars=160)}\n"
        f"type: {sanitize_text(image_path.suffix.lower(), max_chars=16)}\n"
        f"size: {human_size(image_path.stat().st_size)}\n"
        f"sha256: {sha256_file(image_path)}\n"
        f"image_input_mode: {'native pixels enabled' if native_requested and native_allowed else 'metadata only'}\n"
        "security_note: only use visible evidence from the image.\n"
    )


def create_default_messages(system_text: Optional[str] = None) -> List[dict]:
    if not system_text:
        return []
    return [{"role": "system", "content": [{"type": "text", "text": system_text}]}]


def response_to_text(response: dict) -> str:
    if not isinstance(response, dict):
        return sanitize_text(response)
    parts = response.get("content", [])
    texts: List[str] = []
    for item in parts:
        if isinstance(item, dict) and item.get("type") == "text":
            texts.append(item.get("text", ""))
    return sanitize_text("".join(texts), max_chars=10000)


def response_to_stream_text(response: Any) -> str:
    if not isinstance(response, dict):
        return sanitize_stream_delta(response, max_chars=10000)
    parts = response.get("content", [])
    texts: List[str] = []
    for item in parts:
        if isinstance(item, dict) and item.get("type") == "text":
            texts.append(str(item.get("text", "")))
    return sanitize_stream_delta("".join(texts), max_chars=10000)


def create_user_message(user_text: str, image_path: Optional[str] = None) -> Any:
    clean_text = sanitize_text(user_text, max_chars=9000)
    if not image_path:
        return clean_text
    safe_image_path = validate_image_path(image_path)
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": clean_text},
            {"type": "image", "path": str(safe_image_path)},
        ],
    }


def load_litert_engine(
    model_path: Path,
    cache_dir: Optional[Path] = None,
    *,
    enable_vision: bool = False,
    inference_backend: str = "Auto",
):
    require_litert_lm()
    try:
        litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)
    except Exception:
        pass

    backend_name, auto_selected = resolve_inference_backend_name(inference_backend)
    try:
        backend_value = backend_value_for_name(backend_name)
    except RuntimeError:
        if auto_selected and backend_name == "GPU":
            save_settings({"auto_selected_inference_backend": "CPU"})
            backend_name = "CPU"
            backend_value = _litert_cpu_backend()
        else:
            raise

    engine_kwargs = {
        "backend": backend_value,
        "cache_dir": str(cache_dir or require_paths().cache_dir),
    }
    if enable_vision:
        engine_kwargs["vision_backend"] = backend_value
    try:
        return litert_lm.Engine(str(model_path), **engine_kwargs)
    except TypeError as exc:
        if enable_vision:
            raise RuntimeError(
                "This LiteRT-LM build rejected native vision input. Upgrade LiteRT-LM before using bottle-photo import."
            ) from exc
        raise
    except Exception as exc:
        if auto_selected and backend_name == "GPU":
            save_settings({"auto_selected_inference_backend": "CPU"})
            cpu_backend = _litert_cpu_backend()
            engine_kwargs["backend"] = cpu_backend
            if enable_vision:
                engine_kwargs["vision_backend"] = cpu_backend
            return litert_lm.Engine(str(model_path), **engine_kwargs)
        raise exc


@contextmanager
def temporary_litert_cache():
    paths = require_paths()
    cache_path = paths.cache_dir / f"worker_{os.getpid()}_{time.time_ns()}"
    cache_path.mkdir(parents=True, exist_ok=False)
    try:
        yield cache_path
    finally:
        shutil.rmtree(cache_path, ignore_errors=True)


@contextmanager
def unlocked_model_path(key: bytes):
    paths = require_paths()
    if paths.encrypted_model_path.exists():
        cleanup_stale_temp_files(paths)
        temp_model = _tmp_path("gemma_model", ".litertlm")
        decrypt_file(paths.encrypted_model_path, temp_model, key)
        try:
            yield temp_model
        finally:
            safe_cleanup([temp_model])
        return
    if paths.plain_model_path.exists():
        yield paths.plain_model_path
        return
    raise FileNotFoundError("Gemma 4 model not found. Download it from the Settings tab first.")


def litert_chat_blocking(
    key: bytes,
    user_text: str,
    *,
    system_text: Optional[str] = None,
    image_path: Optional[str] = None,
    native_image_input: bool = False,
    inference_backend: str = "Auto",
) -> str:
    safe_image_path = validate_image_path(image_path) if image_path else None
    native_allowed = bool(safe_image_path) and native_image_input and configured_model_supports_native_image_input()
    prompt_text = sanitize_text(user_text, max_chars=12000)
    model_image_path = str(safe_image_path) if native_allowed and safe_image_path else None
    if safe_image_path is not None and not native_allowed:
        prompt_text += image_metadata_prompt(
            safe_image_path,
            native_requested=native_image_input,
            native_allowed=native_allowed,
        )

    with unlocked_model_path(key) as model_path, temporary_litert_cache() as cache_dir:
        engine = load_litert_engine(
            model_path,
            cache_dir=cache_dir,
            enable_vision=bool(model_image_path),
            inference_backend=inference_backend,
        )
        with engine:
            messages = create_default_messages(system_text)
            with engine.create_conversation(messages=messages) as conversation:
                return response_to_text(conversation.send_message(create_user_message(prompt_text, model_image_path)))


def litert_chat_streaming(
    key: bytes,
    user_text: str,
    *,
    system_text: Optional[str] = None,
    image_path: Optional[str] = None,
    native_image_input: bool = False,
    inference_backend: str = "Auto",
    on_delta: Optional[Callable[[str], None]] = None,
) -> Tuple[str, bool]:
    safe_image_path = validate_image_path(image_path) if image_path else None
    native_allowed = bool(safe_image_path) and native_image_input and configured_model_supports_native_image_input()
    prompt_text = sanitize_text(user_text, max_chars=12000)
    model_image_path = str(safe_image_path) if native_allowed and safe_image_path else None
    if safe_image_path is not None and not native_allowed:
        prompt_text += image_metadata_prompt(
            safe_image_path,
            native_requested=native_image_input,
            native_allowed=native_allowed,
        )

    with unlocked_model_path(key) as model_path, temporary_litert_cache() as cache_dir:
        engine = load_litert_engine(
            model_path,
            cache_dir=cache_dir,
            enable_vision=bool(model_image_path),
            inference_backend=inference_backend,
        )
        with engine:
            messages = create_default_messages(system_text)
            with engine.create_conversation(messages=messages) as conversation:
                user_message = create_user_message(prompt_text, model_image_path)
                stream_sender = None
                for method_name in (
                    "send_message_stream",
                    "send_message_streaming",
                    "stream_message",
                    "send_message_async",
                ):
                    candidate = getattr(conversation, method_name, None)
                    if callable(candidate):
                        stream_sender = candidate
                        break
                if not callable(stream_sender):
                    return response_to_text(conversation.send_message(user_message)), False

                accumulated = ""
                emitted = False

                def ingest_chunk(chunk: Any) -> None:
                    nonlocal accumulated, emitted
                    chunk_text = response_to_stream_text(chunk)
                    if not chunk_text:
                        return
                    if chunk_text.startswith(accumulated):
                        delta = chunk_text[len(accumulated) :]
                        accumulated = chunk_text
                    else:
                        delta = chunk_text
                        accumulated += chunk_text
                    if delta:
                        emitted = True
                        if on_delta is not None:
                            on_delta(sanitize_stream_delta(delta, max_chars=2000))

                try:
                    stream_result = stream_sender(user_message)
                except TypeError:
                    return response_to_text(conversation.send_message(user_message)), False
                if isinstance(stream_result, dict):
                    return response_to_text(stream_result), False
                if hasattr(stream_result, "__aiter__") or hasattr(stream_result, "__await__"):
                    import asyncio

                    async def consume_async_stream() -> Tuple[str, bool]:
                        nonlocal accumulated, emitted
                        async_source = stream_result
                        if hasattr(async_source, "__await__") and not hasattr(async_source, "__aiter__"):
                            async_source = await async_source
                        if hasattr(async_source, "__aiter__"):
                            async for async_chunk in async_source:
                                ingest_chunk(async_chunk)
                            return sanitize_text(accumulated, max_chars=10000), emitted
                        final_text = response_to_text(async_source)
                        return sanitize_text(final_text, max_chars=10000), False

                    return asyncio.run(consume_async_stream())

                try:
                    iterator = iter(stream_result)
                except TypeError:
                    final_text = response_to_text(stream_result)
                    return sanitize_text(final_text, max_chars=10000), False

                for chunk in iterator:
                    ingest_chunk(chunk)
                return sanitize_text(accumulated, max_chars=10000), emitted


def download_model_httpx(
    url: str,
    dest: Path,
    *,
    expected_sha: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> str:
    import hashlib

    if httpx is None:
        detail = f" Import error: {HTTPX_IMPORT_ERROR}" if HTTPX_IMPORT_ERROR else ""
        raise RuntimeError("httpx is required to download the local Gemma model." + detail)

    dest.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with httpx.stream("GET", url, follow_redirects=True, timeout=NETWORK_TIMEOUT) as response:
        response.raise_for_status()
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        tmp = dest.with_suffix(dest.suffix + f".download.{uuid.uuid4().hex}")
        try:
            with tmp.open("wb") as handle:
                for chunk in response.iter_bytes(chunk_size=1024 * 256):
                    if not chunk:
                        break
                    handle.write(chunk)
                    digest.update(chunk)
                    done += len(chunk)
                    if progress_callback:
                        progress_callback(done, total)
            tmp.replace(dest)
        finally:
            safe_cleanup([tmp])
    sha = digest.hexdigest()
    if expected_sha and sha.lower() != expected_sha.lower():
        safe_cleanup([dest])
        raise ValueError(f"Downloaded model SHA mismatch. Expected {expected_sha}, got {sha}.")
    return sha


def download_and_encrypt_model(key: bytes, reporter: Optional[Callable[[str, Any], None]] = None) -> str:
    paths = require_paths()
    plain_temp = _tmp_path("gemma_download", ".litertlm")
    encrypted_temp = _tmp_path("gemma_sealed", ".litertlm.aes")
    try:
        if reporter:
            reporter("status", "Downloading Gemma 4 into a temporary vault...")

        def on_progress(done: int, total: int) -> None:
            if reporter and total:
                reporter("progress", done / total)
            if reporter:
                reporter(
                    "status",
                    f"Downloading model... {human_size(done)} of {human_size(total) if total else 'unknown'}",
                )

        sha = download_model_httpx(
            MODEL_REPO + MODEL_FILE,
            plain_temp,
            expected_sha=EXPECTED_HASH,
            progress_callback=on_progress,
        )
        if reporter:
            reporter("status", "Encrypting and sealing the model...")
        encrypt_file(plain_temp, encrypted_temp, key)
        encrypted_temp.replace(paths.encrypted_model_path)
        _set_owner_only_permissions(paths.encrypted_model_path)
        safe_cleanup([paths.plain_model_path])
        if reporter:
            reporter("progress", 1.0)
            reporter("status", "Gemma 4 is ready for offline use.")
        return sha
    finally:
        safe_cleanup([plain_temp, encrypted_temp])


def verify_model_hash(key: bytes) -> Tuple[str, bool]:
    with unlocked_model_path(key) as model_path:
        sha = sha256_file(model_path)
    return sha, sha.lower() == EXPECTED_HASH.lower()


def selected_or_matching_med_id(data: Dict[str, Any], payload_name: str, selected_med_id: Optional[str]) -> Optional[str]:
    meds = list(data.get("meds") or [])
    if selected_med_id and any(str(item.get("id")) == selected_med_id for item in meds):
        return selected_med_id
    lowered = payload_name.strip().lower()
    for item in meds:
        if sanitize_text(item.get("name"), max_chars=120).lower() == lowered:
            return str(item.get("id"))
    return None


def normalized_med_name(value: Any) -> str:
    return sanitize_text(value or "", max_chars=120).strip().lower()


def should_create_new_med_entry(existing_med: Optional[Dict[str, Any]], form_name: str) -> bool:
    if existing_med is None:
        return True
    next_name = normalized_med_name(form_name)
    current_name = normalized_med_name(existing_med.get("name") or "")
    return bool(next_name and current_name and next_name != current_name)


def medication_archived_ts(med: Optional[Dict[str, Any]]) -> float:
    return max(0.0, safe_float((med or {}).get("archived_ts")))


def medication_is_archived(med: Optional[Dict[str, Any]]) -> bool:
    return medication_archived_ts(med) > 0.0


def active_medications(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [med for med in list(data.get("meds") or []) if isinstance(med, dict) and not medication_is_archived(med)]


def archived_medications(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    archived = [med for med in list(data.get("med_archives") or []) if isinstance(med, dict)]
    archived.extend(
        med
        for med in list(data.get("meds") or [])
        if isinstance(med, dict) and medication_is_archived(med)
    )
    return archived


def all_stored_medications(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return active_medications(data) + archived_medications(data)


def medication_archive_label(med: Dict[str, Any]) -> str:
    archived_ts = medication_archived_ts(med)
    if archived_ts > 0.0:
        archived_day = datetime.fromtimestamp(archived_ts).date().isoformat()
        return f"Completed on {archived_day}"
    return "Completed medication"


def build_dashboard_med_picker_map(data: Dict[str, Any], now_ts: Optional[float] = None) -> Dict[str, str]:
    now = now_ts or time.time()
    option_map: Dict[str, str] = {"Choose medication": ""}
    used_labels = {"Choose medication"}

    active = sorted(
        active_medications(data),
        key=lambda med: (
            0 if medication_due_status(med, now)["overdue"] else 1 if medication_due_status(med, now)["due_now"] else 2,
            medication_due_status(med, now)["next_ts"] or float("inf"),
            sanitize_text(med.get("name"), max_chars=120).lower(),
        ),
    )
    archived = sorted(
        archived_medications(data),
        key=lambda med: (
            -medication_archived_ts(med),
            -last_effective_taken_ts(med),
            sanitize_text(med.get("name"), max_chars=120).lower(),
        ),
    )

    def add_option(prefix: str, med: Dict[str, Any], suffix: str = "") -> None:
        med_id = sanitize_text(med.get("id") or "", max_chars=32)
        if not med_id:
            return
        base = f"{prefix} | {sanitize_text(med.get('name') or 'Medication', max_chars=120)}"
        if suffix:
            base += f" | {suffix}"
        label = base
        if label in used_labels:
            label = f"{base} | {med_id[:4]}"
        used_labels.add(label)
        option_map[label] = med_id

    for med in active:
        add_option("Current", med)
    for med in archived:
        archived_ts = medication_archived_ts(med)
        suffix = datetime.fromtimestamp(archived_ts).date().isoformat() if archived_ts > 0.0 else "history"
        add_option("Completed", med, suffix=suffix)
    return option_map


def medication_history_records(
    med: Dict[str, Any],
    *,
    collapse_probable_duplicates: bool = True,
    duplicate_window_seconds: float = DOSE_HISTORY_DUPLICATE_WINDOW_SECONDS,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for raw_index, row in enumerate(med.get("history", []) or []):
        timestamp = 0.0
        dose_mg = 0.0
        scheduled_ts = 0.0
        slot_key = ""
        if isinstance(row, dict):
            timestamp = safe_float(row.get("timestamp") or row.get("taken_ts") or 0.0)
            dose_mg = max(0.0, safe_float(row.get("dose_mg") or row.get("amount_mg") or row.get("dose") or 0.0))
            scheduled_ts = safe_float(row.get("scheduled_ts") or 0.0)
            slot_key = sanitize_text(row.get("slot_key") or "", max_chars=64)
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            timestamp = safe_float(row[0])
            dose_mg = max(0.0, safe_float(row[1]))
            scheduled_ts = safe_float(row[2]) if len(row) >= 3 else 0.0
            slot_key = sanitize_text(row[3] if len(row) >= 4 else "", max_chars=64)
        if timestamp <= 0.0 or dose_mg <= 0.0:
            continue
        records.append(
            {
                "timestamp": timestamp,
                "dose_mg": dose_mg,
                "scheduled_ts": max(0.0, scheduled_ts),
                "slot_key": slot_key,
                "raw_index": raw_index,
            }
        )
    records.sort(key=lambda item: (safe_float(item.get("timestamp")), safe_float(item.get("scheduled_ts")), int(item.get("raw_index", 0))))
    if not collapse_probable_duplicates:
        return records
    normalized: List[Dict[str, Any]] = []
    for record in records:
        if normalized:
            prev = normalized[-1]
            same_dose = abs(safe_float(prev.get("dose_mg")) - safe_float(record.get("dose_mg"))) <= 1e-6
            same_slot = False
            prev_key = sanitize_text(prev.get("slot_key") or "", max_chars=64)
            next_key = sanitize_text(record.get("slot_key") or "", max_chars=64)
            if prev_key and next_key and prev_key == next_key:
                same_slot = True
            else:
                prev_scheduled = safe_float(prev.get("scheduled_ts"))
                next_scheduled = safe_float(record.get("scheduled_ts"))
                if prev_scheduled > 0.0 and next_scheduled > 0.0 and abs(prev_scheduled - next_scheduled) <= 60.0:
                    same_slot = True
            if same_dose and same_slot:
                continue
            if (
                same_dose
                and not prev_key
                and not next_key
                and (safe_float(record.get("timestamp")) - safe_float(prev.get("timestamp"))) <= duplicate_window_seconds
            ):
                continue
        normalized.append(record)
    return normalized


def medication_history_rows(
    med: Dict[str, Any],
    *,
    collapse_probable_duplicates: bool = True,
    duplicate_window_seconds: float = DOSE_HISTORY_DUPLICATE_WINDOW_SECONDS,
) -> List[Tuple[float, float]]:
    return [
        (safe_float(record.get("timestamp")), max(0.0, safe_float(record.get("dose_mg"))))
        for record in medication_history_records(
            med,
            collapse_probable_duplicates=collapse_probable_duplicates,
            duplicate_window_seconds=duplicate_window_seconds,
        )
    ]


def last_effective_taken_ts(med: Dict[str, Any]) -> float:
    rows = medication_history_rows(med)
    if rows:
        return rows[-1][0]
    return safe_float(med.get("last_taken_ts"))


def recent_duplicate_log_ts(med: Dict[str, Any], dose_mg: float, now_ts: float) -> Optional[float]:
    dose_value = max(0.0, dose_mg)
    if dose_value <= 0:
        return None
    records = medication_history_records(med, collapse_probable_duplicates=False)
    if not records:
        return None
    last_record = records[-1]
    last_ts = safe_float(last_record.get("timestamp"))
    last_mg = max(0.0, safe_float(last_record.get("dose_mg")))
    if abs(last_mg - dose_value) > 1e-6:
        return None
    if 0.0 <= (now_ts - last_ts) <= DOSE_RELOG_GUARD_SECONDS:
        return last_ts
    return None


def append_medication_history_entry(
    med: Dict[str, Any],
    timestamp: float,
    dose_mg: float,
    *,
    scheduled_ts: float = 0.0,
    slot_key: str = "",
) -> None:
    entry = [safe_float(timestamp), max(0.0, safe_float(dose_mg))]
    clean_scheduled = max(0.0, safe_float(scheduled_ts))
    clean_slot_key = sanitize_text(slot_key or "", max_chars=64)
    if clean_scheduled > 0.0 or clean_slot_key:
        entry.extend([clean_scheduled, clean_slot_key])
    med["history"] = list(med.get("history") or []) + [entry]
    med["history"] = med["history"][-240:]
    med["last_taken_ts"] = last_effective_taken_ts(med)


def matching_medication_history_entry_for_slot(med: Dict[str, Any], slot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    slot_key = sanitize_text(slot.get("slot_key") or "", max_chars=64)
    scheduled_ts = max(0.0, safe_float(slot.get("scheduled_ts")))
    tolerance = max(60.0, medication_slot_match_tolerance_seconds(med))
    records = medication_history_records(med, collapse_probable_duplicates=False)
    if not records:
        return None
    if slot_key:
        for record in reversed(records):
            if sanitize_text(record.get("slot_key") or "", max_chars=64) == slot_key:
                return record
    if scheduled_ts > 0.0:
        for record in reversed(records):
            record_scheduled = max(0.0, safe_float(record.get("scheduled_ts")))
            if record_scheduled > 0.0 and abs(record_scheduled - scheduled_ts) <= 60.0:
                return record
    # Only fall back to fuzzy timestamp matching for legacy rows that do not
    # carry a stable slot key or scheduled timestamp.
    if not slot_key and scheduled_ts > 0.0:
        for record in reversed(records):
            if sanitize_text(record.get("slot_key") or "", max_chars=64):
                continue
            if max(0.0, safe_float(record.get("scheduled_ts"))) > 0.0:
                continue
            if abs(safe_float(record.get("timestamp")) - scheduled_ts) <= tolerance:
                return record
    return None


def remove_medication_history_entry_for_slot(med: Dict[str, Any], slot: Dict[str, Any]) -> bool:
    match = matching_medication_history_entry_for_slot(med, slot)
    if match is None:
        return False
    raw_history = list(med.get("history") or [])
    raw_index = int(match.get("raw_index", -1))
    if raw_index < 0 or raw_index >= len(raw_history):
        return False
    del raw_history[raw_index]
    med["history"] = raw_history[-240:]
    med["last_taken_ts"] = last_effective_taken_ts(med)
    return True


def total_taken_last_24h(med: Dict[str, Any], now_ts: float) -> float:
    cutoff = now_ts - 24 * 3600.0
    total = 0.0
    for ts, mg in medication_history_rows(med):
        if ts >= cutoff:
            total += mg
    return total


def parse_clock_minutes(value: Any) -> Optional[int]:
    text = sanitize_text(value, max_chars=40).lower().replace(".", "")
    if not text:
        return None
    if text == "noon":
        return 12 * 60
    if text == "midnight":
        return 0
    match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*([ap]m)?", text)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    meridiem = match.group(3)
    if minute > 59:
        return None
    if meridiem:
        if hour < 1 or hour > 12:
            return None
        hour %= 12
        if meridiem == "pm":
            hour += 12
    elif hour > 23:
        return None
    return (hour * 60 + minute) % 1440


def extract_clock_minutes(value: Any) -> Optional[int]:
    text = sanitize_text(value, max_chars=80).lower().replace(".", "")
    if not text:
        return None
    exact = parse_clock_minutes(text)
    if exact is not None:
        return exact
    match = re.search(r"(?<!\d)(\d{1,2})(?::(\d{2}))?\s*([ap]m)?\b", text)
    if not match:
        return None
    return parse_clock_minutes(match.group(0))


def format_clock_minutes(minutes: int) -> str:
    normalized = int(minutes) % 1440
    hour_24 = normalized // 60
    minute = normalized % 60
    suffix = "AM" if hour_24 < 12 else "PM"
    hour_12 = hour_24 % 12 or 12
    return f"{hour_12}:{minute:02d} {suffix}"


def time_bucket_label(minutes: int) -> str:
    hour = (int(minutes) % 1440) // 60
    if 5 <= hour < 10:
        return "Breakfast"
    if 10 <= hour < 12:
        return "Daytime"
    if 12 <= hour < 13:
        return "Mid day"
    if 13 <= hour < 15:
        return "Lunch"
    if 17 <= hour < 21:
        return "Dinner"
    return "Nighttime"


def _normalize_slot_templates(raw_slots: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
    results: List[Tuple[str, int]] = []
    seen_minutes = set()
    used_labels = set()
    for raw_label, raw_minutes in sorted(raw_slots, key=lambda item: (int(item[1]) % 1440, sanitize_text(item[0], max_chars=40).lower())):
        minutes = int(raw_minutes) % 1440
        if minutes in seen_minutes:
            continue
        seen_minutes.add(minutes)
        label = sanitize_text(raw_label or time_bucket_label(minutes), max_chars=40) or time_bucket_label(minutes)
        candidate = label
        index = 2
        while candidate in used_labels:
            candidate = f"{label} {index}"
            index += 1
        used_labels.add(candidate)
        results.append((candidate, minutes))
    return results[:8]


def infer_named_dose_slots(text: str) -> List[Tuple[str, int]]:
    lowered = sanitize_text(text, max_chars=500).lower()
    if not lowered:
        return []
    aliases = {
        "breakfast": "Breakfast",
        "morning": "Breakfast",
        "daytime": "Daytime",
        "mid day": "Mid day",
        "midday": "Mid day",
        "noon": "Mid day",
        "lunch": "Lunch",
        "dinner": "Dinner",
        "supper": "Dinner",
        "evening": "Dinner",
        "nighttime": "Nighttime",
        "bedtime": "Nighttime",
        "night": "Nighttime",
    }
    found = []
    for label, minutes in NAMED_DOSE_PRESETS:
        for alias, target in aliases.items():
            if target == label and alias in lowered:
                found.append((label, minutes))
                break
    return _normalize_slot_templates(found)


def parse_custom_dose_times_text(text: str) -> List[Tuple[str, int]]:
    clean = sanitize_text(text, max_chars=600)
    if not clean:
        return []
    aliases = {
        "breakfast": "Breakfast",
        "morning": "Breakfast",
        "daytime": "Daytime",
        "mid day": "Mid day",
        "midday": "Mid day",
        "noon": "Mid day",
        "lunch": "Lunch",
        "dinner": "Dinner",
        "supper": "Dinner",
        "evening": "Dinner",
        "nighttime": "Nighttime",
        "bedtime": "Nighttime",
        "night": "Nighttime",
    }
    raw_slots: List[Tuple[str, int]] = []
    for segment in [part.strip() for part in re.split(r"[\n,;]+", clean) if part.strip()]:
        lowered = segment.lower()
        label_guess = ""
        for alias, mapped_label in aliases.items():
            if alias in lowered:
                label_guess = mapped_label
                break
        minutes = extract_clock_minutes(segment)
        if minutes is None and label_guess:
            minutes = NAMED_DOSE_PRESET_MAP.get(label_guess.lower())
        if minutes is None:
            continue
        label_text = sanitize_text(
            re.sub(r"(?i)(?<!\d)\d{1,2}(?::\d{2})?\s*([ap]m)?\b", "", segment).strip(" -"),
            max_chars=40,
        )
        label = label_guess or label_text or time_bucket_label(minutes)
        raw_slots.append((label, minutes))
    return _normalize_slot_templates(raw_slots)


def planned_daily_dose_count(med: Dict[str, Any]) -> int:
    dose = max(0.0, safe_float(med.get("dose_mg")))
    interval = max(0.0, safe_float(med.get("interval_hours")))
    max_daily = max(0.0, safe_float(med.get("max_daily_mg")))
    counts = []
    if interval > 0:
        counts.append(max(1, int(math.ceil(24.0 / interval - 1e-9))))
    if dose > 0 and max_daily > 0:
        counts.append(max(1, int(math.floor(max_daily / dose + 1e-9))))
    if not counts:
        return 0
    return max(1, min(counts))


def _limit_slot_templates_to_daily_max(med: Dict[str, Any], slots: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
    if not slots:
        return []
    dose = max(0.0, safe_float(med.get("dose_mg")))
    max_daily = max(0.0, safe_float(med.get("max_daily_mg")))
    if dose <= 0.0 or max_daily <= 0.0:
        return slots
    allowed_count = max(1, int(math.floor(max_daily / dose + 1e-9)))
    return list(slots[:allowed_count])


def default_first_dose_minutes(med: Dict[str, Any]) -> int:
    schedule_text = sanitize_text(med.get("schedule_text") or "", max_chars=300)
    inferred = infer_named_dose_slots(schedule_text)
    if inferred:
        return inferred[0][1]
    interval = max(0.0, safe_float(med.get("interval_hours")))
    if 0.0 < interval <= 8.0:
        return 6 * 60
    return 8 * 60


def resolved_medication_slot_templates(med: Dict[str, Any]) -> List[Tuple[str, int]]:
    custom_slots = parse_custom_dose_times_text(sanitize_text(med.get("custom_times_text") or "", max_chars=600))
    if custom_slots:
        return _limit_slot_templates_to_daily_max(med, custom_slots)
    inferred_slots = infer_named_dose_slots(sanitize_text(med.get("schedule_text") or "", max_chars=500))
    if inferred_slots:
        return _limit_slot_templates_to_daily_max(med, inferred_slots)
    interval = max(0.0, safe_float(med.get("interval_hours")))
    count = planned_daily_dose_count(med)
    if interval <= 0 or count <= 0:
        return []
    anchor = parse_clock_minutes(med.get("first_dose_time")) or default_first_dose_minutes(med)
    raw_slots = []
    for index in range(count):
        minutes = int(round(anchor + index * interval * 60.0)) % 1440
        raw_slots.append((time_bucket_label(minutes), minutes))
    return _limit_slot_templates_to_daily_max(med, _normalize_slot_templates(raw_slots))


def clock_minutes_to_timestamp(target_day: date, minutes: int) -> float:
    normalized = int(minutes) % 1440
    hour = normalized // 60
    minute = normalized % 60
    return datetime.combine(target_day, dt_time(hour=hour, minute=minute)).timestamp()


def medication_slot_key(target_day: date, index: int, label: str, minutes: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", sanitize_text(label or "", max_chars=40).lower()).strip("-")
    if not slug:
        slug = f"slot-{int(index)}"
    return f"{target_day.isoformat()}::{int(minutes) % 1440:04d}::{slug}"


def medication_slot_match_tolerance_seconds(med: Dict[str, Any]) -> float:
    interval = max(0.0, safe_float(med.get("interval_hours")))
    if interval > 0:
        return max(45.0 * 60.0, min(3.0 * 3600.0, interval * 3600.0 * 0.45))
    return 2.0 * 3600.0


def medication_due_lead_seconds(med: Dict[str, Any]) -> float:
    interval = max(0.0, safe_float(med.get("interval_hours")))
    if interval > 0:
        return max(15.0 * 60.0, min(45.0 * 60.0, interval * 3600.0 * 0.15))
    return 30.0 * 60.0


def medication_miss_grace_seconds(med: Dict[str, Any]) -> float:
    interval = max(0.0, safe_float(med.get("interval_hours")))
    if interval > 0:
        return max(45.0 * 60.0, min(2.0 * 3600.0, interval * 3600.0 * 0.25))
    return 60.0 * 60.0


def build_medication_daily_slots(
    med: Dict[str, Any],
    target_day: date,
    now_ts: Optional[float] = None,
) -> List[Dict[str, Any]]:
    if medication_is_archived(med):
        return []
    templates = resolved_medication_slot_templates(med)
    if not templates:
        return []
    now = now_ts or time.time()
    slots = [
        {
            "slot_key": medication_slot_key(target_day, index, label, minutes),
            "index": index,
            "label": label,
            "minutes": minutes,
            "time_text": format_clock_minutes(minutes),
            "scheduled_ts": clock_minutes_to_timestamp(target_day, minutes),
        }
        for index, (label, minutes) in enumerate(templates)
    ]
    created_ts = safe_float(med.get("created_ts") or 0.0)
    if created_ts > 0:
        slots = [slot for slot in slots if safe_float(slot.get("scheduled_ts")) >= created_ts]
    if not slots:
        return []
    tolerance = medication_slot_match_tolerance_seconds(med)
    day_start = clock_minutes_to_timestamp(target_day, 0)
    day_end = day_start + 24.0 * 3600.0
    history_records = medication_history_records(med, collapse_probable_duplicates=False)
    used_rows = set()
    for slot in slots:
        best_match = None
        slot_key = sanitize_text(slot.get("slot_key") or "", max_chars=64)
        slot_scheduled_ts = safe_float(slot.get("scheduled_ts"))
        if slot_key:
            for record in history_records:
                raw_index = int(record.get("raw_index", -1))
                if raw_index in used_rows:
                    continue
                if sanitize_text(record.get("slot_key") or "", max_chars=64) != slot_key:
                    continue
                best_match = (0.0, raw_index, safe_float(record.get("timestamp")), max(0.0, safe_float(record.get("dose_mg"))), record)
                break
        if best_match is None and slot_scheduled_ts > 0.0:
            for record in history_records:
                raw_index = int(record.get("raw_index", -1))
                if raw_index in used_rows:
                    continue
                record_scheduled_ts = max(0.0, safe_float(record.get("scheduled_ts")))
                if record_scheduled_ts <= 0.0 or abs(record_scheduled_ts - slot_scheduled_ts) > 60.0:
                    continue
                gap = abs(safe_float(record.get("timestamp")) - slot_scheduled_ts)
                if best_match is None or gap < best_match[0]:
                    best_match = (
                        gap,
                        raw_index,
                        safe_float(record.get("timestamp")),
                        max(0.0, safe_float(record.get("dose_mg"))),
                        record,
                    )
        if best_match is None and not slot_key and slot_scheduled_ts <= 0.0:
            for record in history_records:
                raw_index = int(record.get("raw_index", -1))
                ts = safe_float(record.get("timestamp"))
                amount = max(0.0, safe_float(record.get("dose_mg")))
                if raw_index in used_rows or amount <= 0:
                    continue
                if sanitize_text(record.get("slot_key") or "", max_chars=64):
                    continue
                if max(0.0, safe_float(record.get("scheduled_ts"))) > 0.0:
                    continue
                if not ((day_start - tolerance) <= ts < (day_end + tolerance)):
                    continue
                gap = abs(ts - slot_scheduled_ts)
                if gap > tolerance:
                    continue
                if best_match is None or gap < best_match[0]:
                    best_match = (gap, raw_index, ts, amount, record)
        if best_match is not None:
            _, row_index, taken_ts, taken_amount, record = best_match
            used_rows.add(row_index)
            slot["taken_ts"] = taken_ts
            slot["taken_amount"] = taken_amount
            slot["history_raw_index"] = row_index
            slot["logged_scheduled_ts"] = max(0.0, safe_float(record.get("scheduled_ts")))

    due_lead = medication_due_lead_seconds(med)
    miss_grace = medication_miss_grace_seconds(med)
    for slot in slots:
        scheduled_ts = slot["scheduled_ts"]
        if slot.get("taken_ts"):
            slot["status"] = "taken"
            taken_text = time.strftime("%I:%M %p", time.localtime(slot["taken_ts"])).lstrip("0")
            delta = safe_float(slot.get("taken_ts")) - scheduled_ts
            if delta >= 30.0 * 60.0:
                slot["status_text"] = f"Taken {taken_text} ({format_duration(delta)} late)"
            elif delta <= -30.0 * 60.0:
                slot["status_text"] = f"Taken {taken_text} ({format_duration(abs(delta))} early)"
            else:
                slot["status_text"] = f"Taken {taken_text}"
            continue
        if now < scheduled_ts - due_lead:
            slot["status"] = "upcoming"
            slot["status_text"] = format_relative_due(scheduled_ts, now)
            continue
        if now <= scheduled_ts + miss_grace:
            slot["status"] = "due"
            slot["status_text"] = "Due now"
            continue
        slot["status"] = "missed"
        slot["status_text"] = f"Missed {format_duration(now - scheduled_ts)} ago"
    return slots


def build_dashboard_daily_checklist_entries(
    meds: List[Dict[str, Any]],
    target_day: date,
    now_ts: Optional[float] = None,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for med in meds:
        med_name = sanitize_text(med.get("name") or "Medication", max_chars=120)
        dose_mg = max(0.0, safe_float(med.get("dose_mg")))
        dose_text = f"{int(dose_mg) if dose_mg.is_integer() else dose_mg:g} mg" if dose_mg > 0 else "Dose not set"
        for slot in build_medication_daily_slots(med, target_day, now_ts):
            entry = dict(slot)
            entry["med_id"] = str(med.get("id"))
            entry["med_name"] = med_name
            entry["dose_text"] = dose_text
            rows.append(entry)
    rows.sort(
        key=lambda item: (
            safe_float(item.get("scheduled_ts")) or float("inf"),
            sanitize_text(item.get("med_name") or "", max_chars=120).lower(),
            sanitize_text(item.get("label") or "", max_chars=40).lower(),
        )
    )
    return rows


def next_unchecked_medication_slot(med: Dict[str, Any], now_ts: Optional[float] = None) -> Optional[Dict[str, Any]]:
    if medication_is_archived(med):
        return None
    now = now_ts or time.time()
    today = datetime.fromtimestamp(now).date()
    for day_offset in range(0, 3):
        slots = build_medication_daily_slots(med, today + timedelta(days=day_offset), now)
        for slot in slots:
            if slot.get("status") != "taken":
                return slot
    return None


def next_due_timestamp(med: Dict[str, Any]) -> Optional[float]:
    slot = next_unchecked_medication_slot(med, time.time())
    if slot is not None:
        return safe_float(slot.get("scheduled_ts"))
    interval_hours = max(0.0, safe_float(med.get("interval_hours")))
    last_taken_ts = last_effective_taken_ts(med)
    if interval_hours <= 0:
        return None
    if last_taken_ts <= 0:
        return time.time()
    return last_taken_ts + interval_hours * 3600.0


def medication_due_status(med: Dict[str, Any], now_ts: Optional[float] = None) -> Dict[str, Any]:
    now = now_ts or time.time()
    if medication_is_archived(med):
        return {
            "state": "Completed",
            "text": medication_archive_label(med),
            "next_ts": None,
            "due_now": False,
            "overdue": False,
        }
    slot = next_unchecked_medication_slot(med, now)
    if slot is not None:
        if slot.get("status") == "missed":
            return {
                "state": "Missed",
                "text": f"{slot['label']} missed {format_duration(now - safe_float(slot['scheduled_ts']))} ago",
                "next_ts": safe_float(slot["scheduled_ts"]),
                "due_now": True,
                "overdue": True,
                "slot": slot,
            }
        if slot.get("status") == "due":
            return {
                "state": "Due",
                "text": f"{slot['label']} due now",
                "next_ts": safe_float(slot["scheduled_ts"]),
                "due_now": True,
                "overdue": False,
                "slot": slot,
            }
        return {
            "state": "Scheduled",
            "text": f"{slot['label']} {format_relative_due(safe_float(slot['scheduled_ts']), now)}",
            "next_ts": safe_float(slot["scheduled_ts"]),
            "due_now": False,
            "overdue": False,
            "slot": slot,
        }
    interval_hours = max(0.0, safe_float(med.get("interval_hours")))
    last_taken_ts = last_effective_taken_ts(med)
    next_ts = next_due_timestamp(med)
    if interval_hours <= 0:
        return {"state": "Flexible", "text": "Flexible schedule", "next_ts": None, "due_now": False, "overdue": False}
    if last_taken_ts <= 0:
        return {"state": "Ready", "text": "No dose logged yet", "next_ts": next_ts, "due_now": True, "overdue": False}
    delta = (next_ts or now) - now
    if delta <= -3600:
        return {"state": "Overdue", "text": format_relative_due(next_ts, now), "next_ts": next_ts, "due_now": True, "overdue": True}
    if delta <= 0:
        return {"state": "Due", "text": "Due now", "next_ts": next_ts, "due_now": True, "overdue": False}
    return {"state": "Scheduled", "text": format_relative_due(next_ts, now), "next_ts": next_ts, "due_now": False, "overdue": False}


def medication_card_line(med: Dict[str, Any], now_ts: Optional[float] = None) -> str:
    now = now_ts or time.time()
    if medication_is_archived(med):
        history_count = len(medication_history_records(med))
        last_taken = format_timestamp(last_effective_taken_ts(med))
        return f"{medication_archive_label(med)} | Last taken {last_taken} | {history_count} logged dose(s)"
    status = medication_due_status(med, now)
    dose = max(0.0, safe_float(med.get("dose_mg")))
    interval = max(0.0, safe_float(med.get("interval_hours")))
    daily = total_taken_last_24h(med, now)
    dose_text = f"{int(dose) if dose.is_integer() else dose:g} mg"
    interval_text = f"every {int(interval) if interval.is_integer() else interval:g}h" if interval > 0 else "flex schedule"
    max_daily = max(0.0, safe_float(med.get("max_daily_mg")))
    daily_text = f"{daily:g}/{max_daily:g} mg last 24h" if max_daily > 0 else f"{daily:g} mg last 24h"
    return f"{dose_text} | {interval_text} | {status['text']} | {daily_text}"


def build_timeline_text(meds: List[Dict[str, Any]], now_ts: Optional[float] = None) -> str:
    if not meds:
        return "No medications yet. Add one manually or import a bottle photo."
    now = now_ts or time.time()
    ranked = sorted(
        meds,
        key=lambda med: (
            0 if medication_due_status(med, now)["overdue"] else 1 if medication_due_status(med, now)["due_now"] else 2,
            medication_due_status(med, now)["next_ts"] or float("inf"),
            sanitize_text(med.get("name"), max_chars=120).lower(),
        ),
    )
    lines = []
    for index, med in enumerate(ranked[:6], start=1):
        status = medication_due_status(med, now)
        lines.append(f"{index}. {sanitize_text(med.get('name'), max_chars=120)} | {status['text']}")
    return "\n".join(lines)


def build_med_history_text(med: Optional[Dict[str, Any]]) -> str:
    if not med:
        return "Select a medication from the dashboard focus menu or Medication List to see dosage history."
    records = medication_history_records(med)
    if not records:
        if medication_is_archived(med):
            return medication_archive_label(med) + "\nNo doses were logged before this medication was completed."
        return "No doses logged for this medication yet."
    lines = []
    if medication_is_archived(med):
        lines.append(medication_archive_label(med))
    for record in reversed(records[-8:]):
        lines.append(f"{format_timestamp(safe_float(record.get('timestamp')))} • {safe_float(record.get('dose_mg')):g} mg")
    return "\n".join(lines)




def build_recent_activity_text(data: Dict[str, Any], *, limit: int = 24) -> str:
    rows: List[Tuple[float, str]] = []

    for med in all_stored_medications(data):
        med_name = sanitize_text(med.get("name") or "Medication", max_chars=120)
        for record in medication_history_records(med):
            ts = safe_float(record.get("timestamp"))
            dose = safe_float(record.get("dose_mg"))
            if ts > 0:
                rows.append((ts, f"{format_timestamp(ts)} • Medication • {med_name} • {dose:g} mg"))
        archived_ts = safe_float(med.get("archived_ts") or 0.0)
        if archived_ts > 0:
            rows.append((archived_ts, f"{format_timestamp(archived_ts)} • Medication completed • {med_name}"))

    hygiene = dict(data.get("dental_hygiene") or dental_hygiene_defaults())
    for label, ts_key in (("Brushed", "last_brush_ts"), ("Flossed", "last_floss_ts"), ("Rinsed", "last_rinse_ts")):
        ts = safe_float(hygiene.get(ts_key) or 0.0)
        if ts > 0:
            rows.append((ts, f"{format_timestamp(ts)} • Dental • {label}"))
    for item in list(hygiene.get("history") or []):
        ts = safe_float(item.get("timestamp") or 0.0)
        if ts > 0:
            rating = sanitize_text(item.get("rating") or "Hygiene review", max_chars=80)
            score = safe_float(item.get("score") or 0.0)
            score_text = f" • {score:.0f}/100" if score > 0 else ""
            rows.append((ts, f"{format_timestamp(ts)} • Dental scan • {rating}{score_text}"))

    dental_recovery = dict(data.get("dental_recovery") or dental_recovery_defaults())
    for item in list(dental_recovery.get("daily_logs") or []):
        ts = safe_float(item.get("timestamp") or 0.0)
        if ts > 0:
            status = sanitize_text(item.get("status") or "Recovery photo review", max_chars=80)
            day = max(0, int(safe_float(item.get("day_number") or 0)))
            day_text = f" day {day}" if day else ""
            rows.append((ts, f"{format_timestamp(ts)} • Dental recovery{day_text} • {status}"))

    exercise = dict(data.get("exercise") or exercise_defaults())
    for item in list(exercise.get("history") or []):
        ts = safe_float(item.get("timestamp") or 0.0)
        if ts > 0:
            habit = sanitize_text(item.get("habit") or "movement", max_chars=40).title()
            minutes = safe_float(item.get("minutes") or 0.0)
            rows.append((ts, f"{format_timestamp(ts)} • Exercise • {habit} • {minutes:g} min"))

    recovery = dict(data.get("recovery_support") or recovery_support_defaults())
    for item in list(recovery.get("history") or []):
        ts = safe_float(item.get("timestamp") or 0.0)
        if ts > 0:
            item_type = sanitize_text(item.get("type") or "checkin", max_chars=40).replace("_", " ").title()
            label = sanitize_text(item.get("label") or item_type, max_chars=80)
            streak = safe_float(item.get("streak_days") or -1)
            streak_text = f" • {int(streak)} days clean" if streak >= 0 else ""
            rows.append((ts, f"{format_timestamp(ts)} • Recovery • {label}{streak_text}"))

    for item in list(data.get("vision_imports") or []):
        ts = safe_float(item.get("timestamp") or 0.0)
        if ts > 0:
            med_id = sanitize_text(item.get("med_id") or "", max_chars=32)
            med = next((m for m in all_stored_medications(data) if str(m.get("id")) == med_id), None)
            med_name = sanitize_text(med.get("name") if med else "Bottle import", max_chars=120)
            rows.append((ts, f"{format_timestamp(ts)} • Vision scan • {med_name}"))

    if not rows:
        return "No activity logged yet. Medication doses, dental actions, exercise, recovery check-ins, and vision scans will appear here."
    rows.sort(key=lambda item: item[0], reverse=True)
    return "\n".join(text for _ts, text in rows[:max(1, limit)])


def build_medication_schedule_text(
    med: Optional[Dict[str, Any]],
    now_ts: Optional[float] = None,
    *,
    target_day: Optional[date] = None,
) -> str:
    if not med:
        return "Select a medication to see today's planned doses."
    if medication_is_archived(med):
        return (
            f"{medication_archive_label(med)}.\n"
            "This medication is no longer part of the current regimen, so it stays visible for history only."
        )
    now = now_ts or time.time()
    active_day = target_day or datetime.fromtimestamp(now).date()
    slots = build_medication_daily_slots(med, active_day, now)
    if not slots:
        next_slot = next_unchecked_medication_slot(med, now)
        if next_slot is not None:
            return f"Next planned slot: {next_slot['label']} {next_slot['time_text']} | {next_slot['status_text']}"
        return "No daily time plan yet. Add custom times or save an interval to generate suggested times."
    lines = []
    for slot in slots:
        if slot.get("status") == "taken":
            marker = "[x]"
        elif slot.get("status") == "missed":
            marker = "[X]"
        else:
            marker = "[ ]"
        lines.append(f"{marker} {slot['label']} {slot['time_text']} | {slot['status_text']}")
    return "\n".join(lines)


def build_medication_nudge_text(med: Optional[Dict[str, Any]], now_ts: Optional[float] = None) -> str:
    if not med:
        return "Select a medication to see the next gentle reminder."
    if medication_is_archived(med):
        med_name = sanitize_text(med.get("name") or "This medication", max_chars=120)
        return f"Gentle nudge: {med_name} is completed and kept visible for history."
    now = now_ts or time.time()
    slots = build_medication_daily_slots(med, datetime.fromtimestamp(now).date(), now)
    if not slots:
        next_slot = next_unchecked_medication_slot(med, now)
        if next_slot is not None:
            med_name = sanitize_text(med.get("name") or "This medication", max_chars=120)
            return f"Gentle nudge: {med_name} next planned dose is {next_slot['label']} at {next_slot['time_text']}."
        return "Add custom times or save an interval to let MedSafe build a dose plan."
    missed = [slot for slot in slots if slot.get("status") == "missed"]
    due = [slot for slot in slots if slot.get("status") == "due"]
    upcoming = [slot for slot in slots if slot.get("status") == "upcoming"]
    taken = [slot for slot in slots if slot.get("status") == "taken"]
    med_name = sanitize_text(med.get("name") or "This medication", max_chars=120)
    if missed:
        slot = missed[0]
        return f"Gentle nudge: {med_name} missed {slot['label']} {format_duration(now - safe_float(slot['scheduled_ts']))} ago."
    if due:
        slot = due[0]
        return f"Gentle nudge: {med_name} {slot['label']} dose is due now."
    if upcoming:
        slot = upcoming[0]
        return f"Gentle nudge: {med_name} {slot['label']} dose is planned for {slot['time_text']}."
    return f"All planned doses for {med_name} are checked off today ({len(taken)} completed)."


def dose_safety_level(med: Dict[str, Any], dose_mg: float, now_ts: float) -> Tuple[str, str]:
    dose_value = max(0.0, dose_mg)
    interval_hours = max(0.0, safe_float(med.get("interval_hours")))
    max_daily = max(0.0, safe_float(med.get("max_daily_mg")))
    last_taken = last_effective_taken_ts(med)
    minutes_since = (now_ts - last_taken) / 60.0 if last_taken > 0 else 1e9
    taken_last_24h = total_taken_last_24h(med, now_ts)
    projected = taken_last_24h + dose_value
    ratio = (projected / max_daily) if max_daily > 0 else 0.0
    way_too_soon = interval_hours > 0 and minutes_since < interval_hours * 60.0 * 0.50
    too_soon = interval_hours > 0 and minutes_since < interval_hours * 60.0 * 0.85
    next_slot = next_unchecked_medication_slot(med, now_ts)

    if dose_value <= 0:
        return "High", "Dose is missing or invalid. Enter a valid mg value before logging."
    if max_daily > 0 and projected > max_daily + 1e-6:
        return "High", f"Unsafe: this would exceed the stored 24h limit ({projected:g}/{max_daily:g} mg in the last 24h)."
    if way_too_soon:
        return "High", f"Unsafe: this is much earlier than the stored {interval_hours:g}h interval."
    if too_soon:
        return "Medium", f"Caution: this is earlier than the stored {interval_hours:g}h interval."
    if max_daily > 0 and abs(projected - max_daily) <= 1e-6:
        return "Low", f"On schedule. This dose reaches the stored 24h limit at {projected:g} mg."
    if max_daily > 0 and ratio >= 0.90:
        return "Medium", f"Caution: close to the 24h limit ({projected:g}/{max_daily:g} mg in the last 24h after this dose)."
    if interval_hours <= 0 and max_daily <= 0 and next_slot is None:
        return "Medium", "Schedule has no interval or daily limit stored, so this stays a caution check."
    if next_slot is not None and next_slot.get("status") == "upcoming":
        early_by = safe_float(next_slot.get("scheduled_ts")) - now_ts
        if early_by > medication_due_lead_seconds(med):
            return "Low", f"Stored limits look okay. The next planned dose window is {next_slot['label']} at {next_slot['time_text']}."
    if next_slot is not None and next_slot.get("status") == "missed":
        return "Low", f"Okay to log now if the bottle directions still fit. Missed slot: {next_slot['label']}."
    if next_slot is not None and next_slot.get("status") == "due":
        return "Low", f"Looks on schedule for {next_slot['label']}. Projected 24h total after this dose: {projected:g} mg."
    return "Low", f"Looks on schedule. Projected 24h total after this dose: {projected:g} mg."


def build_dose_safety_model_context(
    med: Dict[str, Any],
    dose_mg: float,
    now_ts: float,
    *,
    source_label: str = "dose",
) -> Dict[str, Any]:
    dose_value = max(0.0, dose_mg)
    med_name = sanitize_text(med.get("name") or "Medication", max_chars=120)
    interval_hours = max(0.0, safe_float(med.get("interval_hours")))
    max_daily = max(0.0, safe_float(med.get("max_daily_mg")))
    last_taken = last_effective_taken_ts(med)
    minutes_since = (now_ts - last_taken) / 60.0 if last_taken > 0 else -1.0
    taken_last_24h = total_taken_last_24h(med, now_ts)
    projected = taken_last_24h + dose_value
    duplicate_ts = recent_duplicate_log_ts(med, dose_value, now_ts)
    due_status = medication_due_status(med, now_ts)
    next_slot = due_status.get("slot") or next_unchecked_medication_slot(med, now_ts)
    deterministic_level, deterministic_message = dose_safety_level(med, dose_value, now_ts)
    schedule_preview = sanitize_text(build_medication_schedule_text(med, now_ts).replace("\n", " | "), max_chars=420)
    history_preview = sanitize_text(build_med_history_text(med).replace("\n", " | "), max_chars=360)
    context_lines = [
        f"medication={med_name}",
        f"event={sanitize_text(source_label, max_chars=40)}",
        f"standard_dose_mg={max(0.0, safe_float(med.get('dose_mg'))):g}",
        f"candidate_dose_mg={dose_value:g}",
        f"interval_hours={interval_hours:g}",
        f"max_daily_mg={max_daily:g}",
        f"taken_last_24h_mg={taken_last_24h:g}",
        f"projected_last_24h_mg={projected:g}",
        f"last_taken={format_timestamp(last_taken)}",
        f"minutes_since_last_taken={minutes_since:.1f}" if minutes_since >= 0 else "minutes_since_last_taken=unknown",
        f"next_due_state={due_status.get('state', '')}",
        f"next_due_text={sanitize_text(due_status.get('text') or '', max_chars=160)}",
        f"next_slot_label={sanitize_text((next_slot or {}).get('label') or 'none', max_chars=40)}",
        f"next_slot_time={sanitize_text((next_slot or {}).get('time_text') or 'none', max_chars=20)}",
        f"next_slot_status={sanitize_text((next_slot or {}).get('status') or 'none', max_chars=20)}",
        f"duplicate_guard={'yes' if duplicate_ts is not None else 'no'}",
        f"schedule_text={sanitize_text(med.get('schedule_text') or '', max_chars=320) or 'none'}",
        f"custom_times={sanitize_text(med.get('custom_times_text') or '', max_chars=240) or 'none'}",
        f"daily_plan={schedule_preview or 'none'}",
        f"recent_history={history_preview or 'none'}",
        f"deterministic_label={deterministic_level}",
        f"deterministic_message={sanitize_text(deterministic_message, max_chars=220)}",
    ]
    return {
        "med_name": med_name,
        "dose_value": dose_value,
        "interval_hours": interval_hours,
        "max_daily": max_daily,
        "taken_last_24h": taken_last_24h,
        "projected": projected,
        "last_taken": last_taken,
        "minutes_since": minutes_since,
        "due_status": due_status,
        "next_slot": next_slot,
        "duplicate_ts": duplicate_ts,
        "deterministic_level": deterministic_level,
        "deterministic_message": deterministic_message,
        "context_text": "\n".join(context_lines),
    }


def build_dose_safety_dashboard_message(
    med: Dict[str, Any],
    action: str,
    now_ts: float,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    details = context or build_dose_safety_model_context(med, max(0.0, safe_float(med.get("dose_mg"))), now_ts)
    med_name = sanitize_text(med.get("name") or "Medication", max_chars=120)
    pieces = [f"{med_name}: {action}."]
    if details["max_daily"] > 0:
        pieces.append(f"{details['projected']:g}/{details['max_daily']:g} mg projected in the last 24h.")
    else:
        pieces.append(f"{details['projected']:g} mg projected in the last 24h.")
    if details["interval_hours"] > 0 and details["minutes_since"] >= 0:
        pieces.append(f"{details['minutes_since']:.0f} minutes since the last logged dose; stored interval {details['interval_hours']:g}h.")
    if details.get("duplicate_ts") is not None:
        pieces.append("A matching recent dose log was detected.")
    next_slot = details.get("next_slot")
    if next_slot:
        pieces.append(
            f"Next planned slot: {sanitize_text(next_slot.get('label') or 'dose', max_chars=40)} {sanitize_text(next_slot.get('time_text') or '', max_chars=20)}."
        )
    elif details.get("due_status"):
        pieces.append(sanitize_text(details["due_status"].get("text") or "", max_chars=120) + ".")
    return " ".join(piece for piece in pieces if piece).strip()


def medication_safety_snapshot(
    med: Dict[str, Any],
    now_ts: float,
    *,
    source_label: str = "dashboard",
) -> Dict[str, Any]:
    dose_value = max(0.0, safe_float(med.get("dose_mg")))
    med_name = sanitize_text(med.get("name") or "Medication", max_chars=120)
    interval_hours = max(0.0, safe_float(med.get("interval_hours")))
    max_daily = max(0.0, safe_float(med.get("max_daily_mg")))
    taken_last_24h = total_taken_last_24h(med, now_ts)
    last_taken = last_effective_taken_ts(med)
    due_status = medication_due_status(med, now_ts)
    next_slot = due_status.get("slot") or next_unchecked_medication_slot(med, now_ts)
    if dose_value <= 0.0:
        action = "Caution"
        message = f"{med_name}: Caution. Save a dose amount before reviewing this medication's schedule safety."
        return {
            "med_id": sanitize_text(med.get("id") or "", max_chars=32),
            "med_name": med_name,
            "dose_value": dose_value,
            "action": action,
            "display": f"Dose safety: {action}",
            "message": message,
            "context": None,
        }
    if max_daily > 0.0 and taken_last_24h > max_daily + 1e-6:
        action = "Unsafe"
        message = f"{med_name}: Unsafe. Logged total already exceeds the stored 24h limit ({taken_last_24h:g}/{max_daily:g} mg)."
    elif interval_hours <= 0.0 and max_daily <= 0.0 and next_slot is None:
        action = "Caution"
        message = f"{med_name}: Caution. The stored plan is missing interval and daily-limit structure."
    elif max_daily > 0.0 and taken_last_24h >= max_daily - 1e-6:
        action = "Caution"
        message = f"{med_name}: Caution. The logged total is already at the stored 24h limit ({taken_last_24h:g}/{max_daily:g} mg)."
    elif max_daily > 0.0 and (taken_last_24h / max_daily) >= 0.9:
        action = "Caution"
        message = f"{med_name}: Caution. The plan is close to the stored 24h limit ({taken_last_24h:g}/{max_daily:g} mg logged)."
    elif due_status.get("overdue"):
        action = "Caution"
        message = f"{med_name}: Caution. {sanitize_text(due_status.get('text') or 'A planned dose is overdue.', max_chars=180)}."
    else:
        action = "Safe"
        if next_slot:
            message = (
                f"{med_name}: Safe. The stored plan looks on track. "
                f"Next planned slot: {sanitize_text(next_slot.get('label') or 'dose', max_chars=40)} "
                f"{sanitize_text(next_slot.get('time_text') or '', max_chars=20)}."
            )
        elif due_status.get("text"):
            message = f"{med_name}: Safe. {sanitize_text(due_status.get('text') or '', max_chars=180)}."
        else:
            message = f"{med_name}: Safe. The stored schedule looks internally consistent."
    context = {
        "interval_hours": interval_hours,
        "max_daily": max_daily,
        "taken_last_24h": taken_last_24h,
        "last_taken": last_taken,
        "due_status": due_status,
        "next_slot": next_slot,
        "deterministic_level": action,
        "deterministic_message": message,
        "context_text": "\n".join(
            [
                f"medication={med_name}",
                f"event={sanitize_text(source_label, max_chars=40)}",
                f"dose_mg={dose_value:g}",
                f"interval_hours={interval_hours:g}",
                f"max_daily_mg={max_daily:g}",
                f"taken_last_24h_mg={taken_last_24h:g}",
                f"last_taken={format_timestamp(last_taken)}",
                f"next_due_state={sanitize_text(due_status.get('state') or '', max_chars=20)}",
                f"next_due_text={sanitize_text(due_status.get('text') or '', max_chars=160)}",
                f"next_slot_label={sanitize_text((next_slot or {}).get('label') or 'none', max_chars=40)}",
                f"next_slot_time={sanitize_text((next_slot or {}).get('time_text') or 'none', max_chars=20)}",
                f"schedule_text={sanitize_text(med.get('schedule_text') or '', max_chars=320) or 'none'}",
                f"custom_times={sanitize_text(med.get('custom_times_text') or '', max_chars=240) or 'none'}",
            ]
        ),
    }
    return {
        "med_id": sanitize_text(med.get("id") or "", max_chars=32),
        "med_name": med_name,
        "dose_value": dose_value,
        "action": action,
        "display": f"Dose safety: {action}",
        "message": sanitize_text(message, max_chars=320),
        "context": context,
    }


def build_per_med_safety_text(meds: List[Dict[str, Any]], now_ts: float) -> str:
    if not meds:
        return "No medications saved yet."
    rows = []
    for med in meds:
        snapshot = medication_safety_snapshot(med, now_ts)
        line = sanitize_text(snapshot.get("message") or "", max_chars=260)
        rows.append(line or f"{sanitize_text(med.get('name') or 'Medication', max_chars=120)}: awaiting schedule review.")
    return "\n".join(rows[:8])


def regimen_signature(meds: List[Dict[str, Any]]) -> str:
    parts = []
    for med in sorted(list(meds or []), key=lambda item: sanitize_text(item.get("id") or "", max_chars=32)):
        history = medication_history_records(med, collapse_probable_duplicates=False)
        last_record = history[-1] if history else {}
        parts.append(
            "|".join(
                [
                    sanitize_text(med.get("id") or "", max_chars=32),
                    sanitize_text(med.get("name") or "", max_chars=120),
                    f"{max(0.0, safe_float(med.get('dose_mg'))):g}",
                    f"{max(0.0, safe_float(med.get('interval_hours'))):g}",
                    f"{max(0.0, safe_float(med.get('max_daily_mg'))):g}",
                    f"{safe_float(last_effective_taken_ts(med)):.3f}",
                    str(len(history)),
                    sanitize_text(last_record.get("slot_key") or "", max_chars=64),
                ]
            )
        )
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def build_regimen_safety_context(meds: List[Dict[str, Any]], now_ts: float) -> Dict[str, Any]:
    snapshots = [medication_safety_snapshot(med, now_ts, source_label="regimen") for med in meds]
    action_ranks = {"Safe": 0, "Caution": 1, "Unsafe": 2}
    top_action = "Safe"
    for snapshot in snapshots:
        if action_ranks.get(snapshot.get("action") or "Caution", 1) > action_ranks.get(top_action, 0):
            top_action = snapshot.get("action") or top_action
    due_now = 0
    missed = 0
    grouped_times: Dict[str, List[str]] = {}
    lines: List[str] = []
    safe_overlap_groups = 0
    for med, snapshot in zip(meds, snapshots):
        status = medication_due_status(med, now_ts)
        slot = status.get("slot") or {}
        if status.get("due_now") and not status.get("overdue"):
            due_now += 1
        if status.get("overdue"):
            missed += 1
        time_key = sanitize_text(slot.get("time_text") or "", max_chars=20)
        if time_key:
            grouped_times.setdefault(time_key, []).append(sanitize_text(med.get("name") or "Medication", max_chars=120))
        lines.append(
            "med={name}; action={action}; due={due}; next={next_text}; last24h={last24h:g}; interval={interval:g}; max_daily={max_daily:g}; directions={directions}".format(
                name=sanitize_text(med.get("name") or "Medication", max_chars=120),
                action=snapshot.get("action") or "Caution",
                due=sanitize_text(status.get("state") or "", max_chars=20),
                next_text=sanitize_text(status.get("text") or "", max_chars=160),
                last24h=total_taken_last_24h(med, now_ts),
                interval=max(0.0, safe_float(med.get("interval_hours"))),
                max_daily=max(0.0, safe_float(med.get("max_daily_mg"))),
                directions=sanitize_text(med.get("schedule_text") or "none", max_chars=240),
            )
        )
    overlapping = sorted(
        [
            f"{time_text}: {', '.join(names[:4])}"
            for time_text, names in grouped_times.items()
            if len(names) > 1
        ]
    )
    for names in grouped_times.values():
        if len(names) > 1:
            safe_overlap_groups += 1
    context_text = "\n".join(
        [
            f"med_count={len(meds)}",
            f"due_now_count={due_now}",
            f"missed_count={missed}",
            f"overlapping_slot_groups={'; '.join(overlapping) if overlapping else 'none'}",
            "per_med:",
            *lines,
        ]
    )
    if top_action == "Unsafe":
        message = "At least one medication schedule is already outside its stored limits, so the combined plan needs review before another dose is logged."
    elif top_action == "Caution":
        message = "At least one medication schedule already needs review on its own, so the combined plan stays on caution until that schedule is clarified."
    elif due_now >= 3:
        message = f"Combined plan caution. {due_now} medications land in the same current window, so do a quick double-check before logging."
        top_action = "Caution"
    elif safe_overlap_groups:
        message = f"Combined plan looks stable. Shared planned windows are expected here ({'; '.join(overlapping[:2])}) and do not count as a caution by themselves."
    else:
        message = f"Combined plan looks stable across {len(meds)} medication schedules."
    return {
        "snapshots": snapshots,
        "action": top_action,
        "message": sanitize_text(message, max_chars=320),
        "context_text": sanitize_text(context_text, max_chars=5000),
        "signature": regimen_signature(meds),
    }


def assess_regimen_safety_with_llm(
    key: bytes,
    meds: List[Dict[str, Any]],
    now_ts: float,
    settings: Dict[str, Any],
) -> Dict[str, Any]:
    context = build_regimen_safety_context(meds, now_ts)
    system_text = (
        "You are MedSafe Regimen Safety Judge, a private local schedule-integration checker running on-device.\n"
        "Assess the combined medication plan only from the supplied schedule facts.\n"
        "Do not invent diagnoses, lab values, allergies, pharmacology, or clinician-only interaction claims.\n"
        "Shared planned dose windows across different medications are normal and are not a caution by themselves.\n"
        "Only escalate when the stored facts show an actual schedule conflict, a missing structure problem, or a medication that is already unsafe on its own.\n"
        "Return exactly one action tag and one short summary tag."
    )
    prompt = (
        "Review the full medication regimen below as one integrated schedule.\n"
        "Judge the whole plan, not a single dose.\n"
        "Facts:\n"
        f"{context['context_text']}\n"
        "Rules:\n"
        "- Use SAFE when the listed schedules look internally consistent together.\n"
        "- Do not treat different medications sharing the same planned time window as a caution by itself.\n"
        "- Use CAUTION only when the stored directions are unclear, several meds create a genuinely crowded current window, or a medication already needs review on its own.\n"
        "- Use UNSAFE when one or more schedules are already unsafe from their stored interval/max-daily rules.\n"
        "- Mirror the deterministic context when it is clearly SAFE or UNSAFE.\n"
        "- Do not output JSON.\n"
        "- Return exactly two lines:\n"
        "[action]SAFE or CAUTION or UNSAFE[/action]\n"
        "[summary]one short regimen-level summary[/summary]\n"
    )
    raw = litert_chat_blocking(
        key,
        prompt,
        system_text=system_text,
        native_image_input=False,
        inference_backend=settings.get("inference_backend", "Auto"),
    )
    action = extract_action_tag(raw, normalize_dose_action_text(context.get("action"), "Caution"))
    summary = extract_tagged_block(raw, "summary", context.get("message") or "Combined regimen review updated.")
    return {
        "action": action,
        "display": f"All-meds safety: {action}",
        "message": sanitize_text(summary, max_chars=320),
        "raw": sanitize_text(raw, max_chars=400),
        "signature": context.get("signature") or "",
        "context_message": context.get("message") or "",
    }


def assess_all_medications_with_llm(
    key: bytes,
    meds: List[Dict[str, Any]],
    now_ts: float,
    settings: Dict[str, Any],
    *,
    reason: str = "",
) -> Dict[str, Any]:
    signature = regimen_signature(meds)
    per_med_results: List[Dict[str, Any]] = []
    for med in meds:
        med_name = sanitize_text(med.get("name") or "Medication", max_chars=120)
        try:
            result = assess_medication_plan_with_llm(key, med, now_ts, settings)
        except Exception as exc:
            snapshot = medication_safety_snapshot(med, now_ts, source_label="auto safety scan")
            result = {
                "action": snapshot.get("action") or "Caution",
                "display": snapshot.get("display") or "Dose safety",
                "message": sanitize_text(snapshot.get("message") or f"{med_name}: schedule review updated.", max_chars=320)
                + f" Local model unavailable: {sanitize_text(str(exc), max_chars=140)}",
                "raw": "",
                "deterministic_level": sanitize_text(snapshot.get("action") or "", max_chars=40),
                "deterministic_message": sanitize_text(snapshot.get("message") or "", max_chars=260),
            }
        per_med_results.append(
            {
                "timestamp": now_ts,
                "med_id": sanitize_text(med.get("id") or "", max_chars=32),
                "med_name": med_name,
                "action": normalize_dose_action_text(result.get("action") or "", "Caution"),
                "display": sanitize_text(result.get("display") or "Dose safety", max_chars=160),
                "message": sanitize_text(result.get("message") or "", max_chars=420),
                "raw": sanitize_text(result.get("raw") or "", max_chars=400),
                "deterministic_level": sanitize_text(result.get("deterministic_level") or "", max_chars=40),
                "deterministic_message": sanitize_text(result.get("deterministic_message") or "", max_chars=260),
            }
        )
    try:
        regimen = assess_regimen_safety_with_llm(key, meds, now_ts, settings)
    except Exception as exc:
        context = build_regimen_safety_context(meds, now_ts)
        regimen = {
            "action": normalize_dose_action_text(context.get("action") or "", "Caution"),
            "display": f"All-meds safety: {normalize_dose_action_text(context.get('action') or '', 'Caution')}",
            "message": sanitize_text(context.get("message") or "Combined regimen review updated.", max_chars=320)
            + f" Local model unavailable: {sanitize_text(str(exc), max_chars=140)}",
            "raw": "",
            "signature": signature,
            "context_message": sanitize_text(context.get("message") or "", max_chars=260),
        }
    return {
        "timestamp": now_ts,
        "signature": signature,
        "pending": False,
        "reason": sanitize_text(reason, max_chars=160),
        "per_med": per_med_results,
        "regimen": {
            "action": normalize_dose_action_text(regimen.get("action") or "", "Caution"),
            "display": sanitize_text(regimen.get("display") or "All-meds safety", max_chars=160),
            "message": sanitize_text(regimen.get("message") or "", max_chars=420),
            "raw": sanitize_text(regimen.get("raw") or "", max_chars=400),
            "signature": sanitize_text(regimen.get("signature") or signature, max_chars=120),
        },
    }


def effective_safety_reviews_state(
    safety_reviews: Optional[Dict[str, Any]],
    meds: List[Dict[str, Any]],
    now_ts: float,
) -> Dict[str, Any]:
    stored = dict(safety_reviews or {})
    signature = regimen_signature(meds)
    if stored and sanitize_text(stored.get("signature") or "", max_chars=120) == signature:
        return stored
    regimen_context = build_regimen_safety_context(meds, now_ts)
    per_med = []
    for med in meds:
        snapshot = medication_safety_snapshot(med, now_ts, source_label="dashboard summary")
        per_med.append(
            {
                "timestamp": now_ts,
                "med_id": sanitize_text(med.get("id") or "", max_chars=32),
                "med_name": sanitize_text(med.get("name") or "Medication", max_chars=120),
                "action": normalize_dose_action_text(snapshot.get("action") or "", "Caution"),
                "display": sanitize_text(snapshot.get("display") or "Dose safety", max_chars=160),
                "message": sanitize_text(snapshot.get("message") or "", max_chars=420),
                "raw": "",
                "deterministic_level": sanitize_text(snapshot.get("action") or "", max_chars=40),
                "deterministic_message": sanitize_text(snapshot.get("message") or "", max_chars=260),
            }
        )
    return {
        "timestamp": now_ts,
        "signature": signature,
        "pending": False,
        "reason": "",
        "per_med": per_med,
        "regimen": {
            "action": normalize_dose_action_text(regimen_context.get("action") or "", "Caution"),
            "display": f"All-meds safety: {normalize_dose_action_text(regimen_context.get('action') or '', 'Caution')}",
            "message": sanitize_text(regimen_context.get("message") or "Combined regimen review ready.", max_chars=420),
            "raw": "",
            "signature": signature,
        },
    }


def build_dashboard_safety_summary_text(state: Dict[str, Any], meds: List[Dict[str, Any]]) -> str:
    regimen = dict(state.get("regimen") or {})
    pending = bool(state.get("pending", False))
    per_med = list(state.get("per_med") or [])
    action = normalize_dose_action_text(regimen.get("action") or "", "Caution")
    med_count = len(meds)
    safe_count = len([item for item in per_med if normalize_dose_action_text(item.get("action") or "", "") == "Safe"])
    caution_count = len([item for item in per_med if normalize_dose_action_text(item.get("action") or "", "") == "Caution"])
    unsafe_count = len([item for item in per_med if normalize_dose_action_text(item.get("action") or "", "") == "Unsafe"])
    summary = sanitize_text(regimen.get("message") or "", max_chars=320)
    if pending:
        reason = sanitize_text(state.get("reason") or "recent medication changes", max_chars=120)
        return f"Scanning {med_count} medication plan(s) after {reason}."
    counts = f"Safe: {safe_count} | Caution: {caution_count} | Unsafe: {unsafe_count}"
    if summary:
        return f"{counts}\n{summary}"
    return f"{counts}\nOverall regimen review: {action}."


def build_safety_tab_per_med_text(state: Dict[str, Any], meds: List[Dict[str, Any]]) -> str:
    per_med = list(state.get("per_med") or [])
    if not meds:
        return "No medications saved yet."
    if not per_med:
        return "Safety results will appear here after the first scan."
    lines = []
    for item in per_med:
        med_name = sanitize_text(item.get("med_name") or "Medication", max_chars=120)
        action = normalize_dose_action_text(item.get("action") or "", "Caution")
        message = sanitize_text(item.get("message") or "", max_chars=280)
        lines.append(f"{med_name} | {action}\n{message}")
    return "\n\n".join(lines[:12])


def assess_medication_plan_with_llm(
    key: bytes,
    med: Dict[str, Any],
    now_ts: float,
    settings: Dict[str, Any],
) -> Dict[str, Any]:
    snapshot = medication_safety_snapshot(med, now_ts, source_label="manual plan check")
    context = dict(snapshot.get("context") or {})
    med_name = sanitize_text(snapshot.get("med_name") or med.get("name") or "Medication", max_chars=120)
    system_text = (
        "You are MedSafe Medication Plan Safety Judge, running privately on-device.\n"
        "Assess the stored schedule for one medication as a plan snapshot.\n"
        "Do not judge whether the user should take another immediate dose right now unless the supplied facts say that is the plan.\n"
        "Do not invent pharmacology, allergies, diagnoses, organ status, or clinician-only interaction claims.\n"
        "Return one action tag and one short summary tag."
    )
    prompt = (
        "Review this one medication schedule and its recent logged history.\n"
        "Judge whether the stored plan itself looks SAFE, needs CAUTION, or is UNSAFE.\n"
        "Facts:\n"
        f"{sanitize_text(context.get('context_text') or '', max_chars=5000)}\n"
        "Rules:\n"
        "- Use SAFE when the stored plan and logged history look internally consistent.\n"
        "- Use CAUTION when the schedule is overdue, close to the daily limit, or missing structure.\n"
        "- Use UNSAFE only when the stored logged total already exceeds the daily limit or the stored facts are clearly contradictory.\n"
        "- If the deterministic plan review is SAFE, do not escalate it to UNSAFE.\n"
        "- Return exactly two lines:\n"
        "[action]SAFE or CAUTION or UNSAFE[/action]\n"
        "[summary]one short medication-plan summary[/summary]\n"
        f"Medication under review: {med_name}.\n"
    )
    raw = litert_chat_blocking(
        key,
        prompt,
        system_text=system_text,
        native_image_input=False,
        inference_backend=settings.get("inference_backend", "Auto"),
    )
    deterministic_action = normalize_dose_action_text(snapshot.get("action") or "Caution", "Caution")
    requested_action = extract_action_tag(raw, deterministic_action)
    if deterministic_action == "Unsafe":
        action = "Unsafe"
    elif deterministic_action == "Safe":
        action = "Safe"
    else:
        action = normalize_dose_action_text(requested_action, deterministic_action)
    summary = extract_tagged_block(raw, "summary", sanitize_text(snapshot.get("message") or "", max_chars=320))
    return {
        "action": action,
        "display": f"Dose safety AI: {action}",
        "message": sanitize_text(summary, max_chars=320),
        "raw": sanitize_text(raw, max_chars=400),
        "deterministic_level": sanitize_text(snapshot.get("action") or "", max_chars=40),
        "deterministic_message": sanitize_text(snapshot.get("message") or "", max_chars=260),
    }


def medication_plan_process_worker(
    result_queue: Any,
    key: bytes,
    med: Dict[str, Any],
    now_ts: float,
    settings: Dict[str, Any],
) -> None:
    try:
        result_queue.put(
            {
                "ok": True,
                "result": assess_medication_plan_with_llm(
                    key,
                    med,
                    now_ts,
                    settings,
                ),
            }
        )
    except Exception as exc:
        result_queue.put({"ok": False, "error": sanitize_text(str(exc), max_chars=240)})


def assess_dose_safety_with_llm(
    key: bytes,
    med: Dict[str, Any],
    dose_mg: float,
    now_ts: float,
    settings: Dict[str, Any],
    *,
    source_label: str = "dose",
) -> Dict[str, Any]:
    context = build_dose_safety_model_context(med, dose_mg, now_ts, source_label=source_label)
    quantum_packet = build_quantum_risk_packet("medication_dose_safety", context["context_text"])
    med_name = sanitize_text(med.get("name") or "Medication", max_chars=120)
    system_text = (
        "You are MedSafe Dose Safety Judge, a private local schedule-check model running entirely on the user's device.\n"
        "You are not a clinician.\n"
        "Assess only the immediate schedule safety of logging one dose right now using the supplied stored facts.\n"
        "Never invent age, weight, diagnoses, allergies, organ function, interactions, or clinician-only guidance.\n"
        "Use the quantum risk packet as a tie-breaker only after the numeric schedule facts are checked.\n"
        "Return exactly one tagged action and nothing else."
    )
    prompt = (
        "Evaluate whether logging the candidate dose right now looks SAFE, needs CAUTION, or is UNSAFE.\n"
        f"{quantum_packet['prompt_block']}\n"
        "Facts:\n"
        f"{context['context_text']}\n"
        "Decision rules:\n"
        "- Use SAFE only when the stored numbers and plan support logging the dose now.\n"
        "- Use CAUTION when the timing is a little early, close to the stored daily limit, or important schedule details are missing.\n"
        "- Use UNSAFE when the projected last-24-hour total exceeds the stored max_daily_mg, the stored interval is clearly violated, or a recent duplicate log is indicated.\n"
        "- If deterministic_label is High, you should normally answer UNSAFE.\n"
        "- If deterministic_label is Medium and the schedule facts are incomplete or close to a limit, answer CAUTION.\n"
        "- If deterministic_label is Low and the stored facts are internally consistent, answer SAFE.\n"
        "- If the only issue is that the next planned slot is later but the stored interval and daily-limit facts are otherwise okay, answer SAFE.\n"
        "- Do not explain. Do not hedge. Do not output JSON.\n"
        "- Return exactly one line in this format: [action]SAFE[/action] or [action]CAUTION[/action] or [action]UNSAFE[/action]\n"
        f"Medication under review: {med_name}.\n"
    )
    raw = litert_chat_blocking(
        key,
        prompt,
        system_text=system_text,
        native_image_input=False,
        inference_backend=settings.get("inference_backend", "Auto"),
    )
    fallback_action = normalize_dose_action_text(context["deterministic_level"])
    action = resolve_dose_action_from_context(extract_action_tag(raw, fallback_action), context)
    quantum_line = ""
    if action != "Safe":
        quantum_line = f" Quantum prior {quantum_packet['risk_level']} {quantum_packet['risk_score']:.0f}/100."
    return {
        "action": action,
        "display": f"Dose safety AI: {action}",
        "message": build_dose_safety_dashboard_message(med, action, now_ts, context) + quantum_line,
        "raw": sanitize_text(raw, max_chars=400),
        "prompt_block": quantum_packet["prompt_block"],
        "quantum_summary": quantum_packet["risk_summary"],
        "quantum_level": quantum_packet["risk_level"],
        "quantum_score": quantum_packet["risk_score"],
        "deterministic_level": context["deterministic_level"],
        "deterministic_message": context["deterministic_message"],
    }


def dose_safety_process_worker(
    result_queue: Any,
    key: bytes,
    med: Dict[str, Any],
    dose_mg: float,
    now_ts: float,
    settings: Dict[str, Any],
    source_label: str,
) -> None:
    try:
        result_queue.put(
            {
                "ok": True,
                "result": assess_dose_safety_with_llm(
                    key,
                    med,
                    dose_mg,
                    now_ts,
                    settings,
                    source_label=source_label,
                ),
            }
        )
    except Exception as exc:
        result_queue.put({"ok": False, "error": sanitize_text(str(exc), max_chars=240)})


def all_meds_safety_process_worker(
    result_queue: Any,
    key: bytes,
    meds: List[Dict[str, Any]],
    now_ts: float,
    settings: Dict[str, Any],
    reason: str,
) -> None:
    try:
        result_queue.put(
            {
                "ok": True,
                "result": assess_all_medications_with_llm(
                    key,
                    meds,
                    now_ts,
                    settings,
                    reason=reason,
                ),
            }
        )
    except Exception as exc:
        result_queue.put({"ok": False, "error": sanitize_text(str(exc), max_chars=240)})


def assistant_request_process_worker(
    result_queue: Any,
    key: bytes,
    data: Dict[str, Any],
    prompt: str,
    selected_med_id: Optional[str],
    settings: Dict[str, Any],
    mode: str,
) -> None:
    try:
        streamed = False

        def emit_delta(delta: str) -> None:
            nonlocal streamed
            clean = sanitize_stream_delta(delta, max_chars=2000)
            if not clean:
                return
            streamed = True
            result_queue.put({"ok": True, "delta": clean})

        reply = run_assistant_request(
            key,
            data,
            prompt,
            selected_med_id,
            settings,
            mode=mode,
            on_delta=emit_delta,
        )
        result_queue.put(
            {
                "ok": True,
                "reply": sanitize_text(
                    reply,
                    max_chars=10000,
                ),
                "streamed": streamed,
            }
        )
    except Exception as exc:
        result_queue.put({"ok": False, "error": sanitize_text(str(exc), max_chars=240)})


def habit_due_status(last_ts: float, interval_hours: float, now_ts: Optional[float] = None) -> Dict[str, Any]:
    now = now_ts or time.time()
    interval_seconds = max(1.0, interval_hours) * 3600.0
    if last_ts <= 0:
        return {"state": "Ready", "text": "Ready now", "due_now": True, "overdue": False}
    target = last_ts + interval_seconds
    delta = target - now
    if delta <= -3600:
        return {"state": "Overdue", "text": format_relative_due(target, now), "due_now": True, "overdue": True}
    if delta <= 0:
        return {"state": "Due", "text": "Due now", "due_now": True, "overdue": False}
    return {"state": "Scheduled", "text": format_relative_due(target, now), "due_now": False, "overdue": False}


def dental_rating_from_score(score: float) -> str:
    if score >= 88:
        return "Excellent"
    if score >= 72:
        return "Good"
    if score >= 55:
        return "Needs polish"
    return "Needs attention"


def parse_date_string(raw: str) -> Optional[date]:
    text = sanitize_text(raw, max_chars=20)
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def days_since_date_string(raw: str) -> Optional[int]:
    parsed = parse_date_string(raw)
    if not parsed:
        return None
    return max(0, (date.today() - parsed).days)


def build_dental_hygiene_history_text(state: Dict[str, Any]) -> str:
    rows = list(state.get("history") or [])
    if not rows:
        return "No dental hygiene photo reviews yet."
    lines = []
    for item in rows[-3:][::-1]:
        risk_score = max(0.0, min(100.0, safe_float(item.get("risk_score"))))
        risk_level = normalized_risk_level_text(item.get("risk_level") or "", risk_score)
        risk_suffix = f" • risk {risk_level} {risk_score:.0f}/100" if risk_score > 0 else ""
        lines.append(
            "{when} • {score:.0f}/100 • {rating}{risk}".format(
                when=format_timestamp(safe_float(item.get("timestamp"))),
                score=max(0.0, min(100.0, safe_float(item.get("score")))),
                rating=sanitize_text(item.get("rating") or "Review", max_chars=80),
                risk=risk_suffix,
            )
        )
    return "\n".join(lines)


def build_recovery_history_text(state: Dict[str, Any]) -> str:
    rows = list(state.get("daily_logs") or [])
    if not rows:
        return "No recovery photo check-ins yet."
    lines = []
    for item in rows[-3:][::-1]:
        score = max(0.0, min(100.0, safe_float(item.get("score"))))
        risk_score = max(0.0, min(100.0, safe_float(item.get("risk_score"))))
        risk_level = normalized_risk_level_text(item.get("risk_level") or "", risk_score)
        risk_suffix = f" • risk {risk_level} {risk_score:.0f}/100" if risk_score > 0 else ""
        if score > 0:
            lines.append(
                "Day {day} • {status} • {score:.0f}/100{risk} • {when}".format(
                    day=max(0, int(safe_float(item.get("day_number") or 0))),
                    status=sanitize_text(item.get("status") or "Review", max_chars=80),
                    score=score,
                    risk=risk_suffix,
                    when=format_timestamp(safe_float(item.get("timestamp"))),
                )
            )
        else:
            lines.append(
                "Day {day} • {status}{risk} • {when}".format(
                    day=max(0, int(safe_float(item.get("day_number") or 0))),
                    status=sanitize_text(item.get("status") or "Review", max_chars=80),
                    risk=risk_suffix,
                    when=format_timestamp(safe_float(item.get("timestamp"))),
                )
            )
    return "\n".join(lines)


def score_change_text(rows: List[Dict[str, Any]], key: str = "score") -> str:
    if not rows:
        return "Take a first AI review to start the trend."
    if len(rows) < 2:
        return "First AI review saved."
    latest = max(0.0, min(100.0, safe_float(rows[-1].get(key))))
    previous = max(0.0, min(100.0, safe_float(rows[-2].get(key))))
    delta = latest - previous
    if abs(delta) < 2.0:
        return "Holding steady versus the last review."
    direction = "up" if delta > 0 else "down"
    return f"{abs(delta):.0f} points {direction} versus the last review."


def score_palette(score: float) -> Tuple[float, float, float, float]:
    if score >= 80:
        return (0.58, 0.96, 0.77, 1)
    if score >= 55:
        return (1.00, 0.84, 0.46, 1)
    return (1.00, 0.62, 0.68, 1)


def habit_palette(status: Dict[str, Any]) -> Tuple[Tuple[float, float, float, float], Tuple[float, float, float, float]]:
    if status.get("overdue"):
        return (1.00, 0.69, 0.74, 1), (1.00, 0.84, 0.87, 1)
    if status.get("due_now"):
        return (1.00, 0.86, 0.50, 1), (1.00, 0.93, 0.74, 1)
    return (0.68, 0.98, 0.84, 1), (0.82, 0.96, 0.91, 1)


def build_dental_overview(
    hygiene: Dict[str, Any],
    recovery: Dict[str, Any],
    now_ts: Optional[float] = None,
) -> Tuple[str, str]:
    now = now_ts or time.time()
    habits = [
        ("Brush", habit_due_status(safe_float(hygiene.get("last_brush_ts")), safe_float(hygiene.get("brush_interval_hours")) or 12.0, now)),
        ("Floss", habit_due_status(safe_float(hygiene.get("last_floss_ts")), safe_float(hygiene.get("floss_interval_hours")) or 24.0, now)),
        ("Rinse", habit_due_status(safe_float(hygiene.get("last_rinse_ts")), safe_float(hygiene.get("rinse_interval_hours")) or 24.0, now)),
    ]
    urgent = next((item for item in habits if item[1].get("overdue")), None)
    if urgent is None:
        urgent = next((item for item in habits if item[1].get("due_now")), None)
    if urgent is None:
        urgent = habits[0]

    latest_rating = sanitize_text(hygiene.get("latest_rating") or "", max_chars=80)
    latest_score = max(0.0, min(100.0, safe_float(hygiene.get("latest_score"))))
    rating_text = f"Latest hygiene review: {latest_rating} ({latest_score:.0f}/100)." if latest_rating else "No hygiene photo review saved yet."

    recovery_enabled = bool(recovery.get("enabled"))
    if recovery_enabled:
        day_count = days_since_date_string(str(recovery.get("procedure_date") or ""))
        day_text = f"day {day_count + 1}" if day_count is not None else "an unknown day"
        recovery_line = (
            f"Recovery mode is active for {sanitize_text(recovery.get('procedure_type') or 'dental work', max_chars=80)} on {day_text}."
        )
    else:
        recovery_line = "Recovery mode is off right now."

    if urgent[1].get("overdue"):
        title = f"{urgent[0]} is overdue"
    elif urgent[1].get("due_now"):
        title = f"{urgent[0]} is ready now"
    elif latest_rating:
        title = f"{latest_rating} hygiene rhythm"
    else:
        title = "Dental studio ready"

    body = f"{urgent[0]}: {urgent[1]['text']}. {rating_text} {recovery_line}"
    return title, body


def build_exercise_daily_totals(state: Dict[str, Any], now_ts: Optional[float] = None) -> Dict[str, float]:
    now = now_ts or time.time()
    today = datetime.fromtimestamp(now).date()
    day_start = datetime.combine(today, dt_time.min).timestamp()
    totals = {"walk": 0.0, "light": 0.0, "stretch": 0.0}
    for item in list(state.get("history") or []):
        habit_name = sanitize_text(item.get("habit") or "", max_chars=16).lower()
        if habit_name not in totals:
            continue
        if safe_float(item.get("timestamp")) >= day_start:
            totals[habit_name] += max(0.0, safe_float(item.get("minutes")))
    return totals


def build_exercise_history_text(state: Dict[str, Any]) -> str:
    rows = list(state.get("history") or [])
    if not rows:
        return "No movement sessions logged yet."
    labels = {"walk": "Walk", "light": "Light Exercise", "stretch": "Stretch"}
    lines = []
    for item in rows[-5:][::-1]:
        habit_name = sanitize_text(item.get("habit") or "", max_chars=16).lower()
        lines.append(
            "{when} • {habit} • {minutes:g} min".format(
                when=format_timestamp(safe_float(item.get("timestamp"))),
                habit=labels.get(habit_name, "Movement"),
                minutes=max(0.0, safe_float(item.get("minutes"))),
            )
        )
    return "\n".join(lines)


def build_exercise_overview(
    state: Dict[str, Any],
    now_ts: Optional[float] = None,
) -> Tuple[str, str]:
    now = now_ts or time.time()
    habits = [
        ("Walk", habit_due_status(safe_float(state.get("last_walk_ts")), safe_float(state.get("walk_interval_hours")) or 4.0, now)),
        ("Light exercise", habit_due_status(safe_float(state.get("last_light_ts")), safe_float(state.get("light_interval_hours")) or 8.0, now)),
        ("Stretch", habit_due_status(safe_float(state.get("last_stretch_ts")), safe_float(state.get("stretch_interval_hours")) or 2.0, now)),
    ]
    urgent = next((item for item in habits if item[1].get("overdue")), None)
    if urgent is None:
        urgent = next((item for item in habits if item[1].get("due_now")), None)
    if urgent is None:
        urgent = habits[0]

    totals = build_exercise_daily_totals(state, now)
    walk_goal = max(1.0, safe_float(state.get("daily_walk_goal_minutes")) or 30.0)
    light_goal = max(1.0, safe_float(state.get("daily_light_goal_minutes")) or 20.0)
    stretch_goal = max(1.0, safe_float(state.get("daily_stretch_goal_minutes")) or 10.0)
    progress_line = (
        f"Today's movement: walk {totals['walk']:.0f}/{walk_goal:.0f} min, "
        f"light {totals['light']:.0f}/{light_goal:.0f} min, "
        f"stretch {totals['stretch']:.0f}/{stretch_goal:.0f} min."
    )
    notes_text = sanitize_text(state.get("notes") or "", max_chars=220)
    notes_line = f" Focus note: {notes_text}" if notes_text else ""

    if urgent[1].get("overdue"):
        title = f"{urgent[0]} reminder overdue"
    elif urgent[1].get("due_now"):
        title = f"{urgent[0]} reminder ready now"
    else:
        title = "Movement rhythm on track"

    body = f"{urgent[0]}: {urgent[1]['text']}. {progress_line}{notes_line}"
    return title, body


def recovery_anchor_date(state: Dict[str, Any]) -> Optional[date]:
    clean_start = parse_date_string(str(state.get("clean_start_date") or ""))
    if clean_start is not None:
        return clean_start
    candidates: List[date] = []
    relapse_date = parse_date_string(str(state.get("last_relapse_date") or ""))
    if relapse_date is not None:
        candidates.append(relapse_date)
    for item in list(state.get("history") or []):
        if sanitize_text(item.get("type") or "", max_chars=20).lower() != "relapse":
            continue
        event_day = datetime.fromtimestamp(safe_float(item.get("timestamp"))).date()
        candidates.append(event_day)
    if not candidates:
        return None
    return max(candidates)


def recovery_clean_days(state: Dict[str, Any], today: Optional[date] = None) -> int:
    anchor_date = recovery_anchor_date(state)
    if anchor_date is None:
        return 0
    anchor = today or date.today()
    if anchor < anchor_date:
        return 0
    return (anchor - anchor_date).days + 1


def recovery_checked_in_today(state: Dict[str, Any], now_ts: Optional[float] = None) -> bool:
    now = now_ts or time.time()
    today = datetime.fromtimestamp(now).date()
    for item in reversed(list(state.get("history") or [])):
        if sanitize_text(item.get("type") or "", max_chars=20).lower() != "checkin":
            continue
        if datetime.fromtimestamp(safe_float(item.get("timestamp"))).date() == today:
            return True
    return False


def recovery_next_milestone(days_clean: int) -> Optional[Tuple[int, int, str]]:
    for milestone in RECOVERY_SUPPORT_MILESTONES:
        if milestone[0] > days_clean:
            return milestone
    return None


def apply_recovery_support_progress(
    state: Dict[str, Any],
    *,
    now_ts: Optional[float] = None,
    award_checkin_points: bool = False,
) -> Tuple[Dict[str, Any], List[str]]:
    updated = dict(state)
    now = now_ts or time.time()
    current_days = recovery_clean_days(updated, datetime.fromtimestamp(now).date())
    updated["best_streak_days"] = max(max(0, int(safe_float(updated.get("best_streak_days") or 0))), current_days)
    updated["cycle"] = max(1, int(safe_float(updated.get("cycle") or 1)))
    claimed = {
        sanitize_text(item, max_chars=24)
        for item in list(updated.get("milestones_claimed") or [])
        if sanitize_text(item, max_chars=24)
    }
    history = list(updated.get("history") or [])
    points = max(0, int(safe_float(updated.get("points") or 0)))
    rewards: List[str] = []
    for milestone_days, bonus_points, label in RECOVERY_SUPPORT_MILESTONES:
        claim_key = f"{updated['cycle']}:{milestone_days}"
        if current_days >= milestone_days and claim_key not in claimed:
            claimed.add(claim_key)
            points += bonus_points
            rewards.append(f"{label} unlocked (+{bonus_points} points)")
            history.append(
                {
                    "timestamp": now,
                    "type": "milestone",
                    "note": "",
                    "streak_days": milestone_days,
                    "points_delta": bonus_points,
                    "label": label,
                }
            )
    if award_checkin_points:
        points += 2
        rewards.append("Daily check-in (+2 points)")
    updated["points"] = points
    updated["milestones_claimed"] = sorted(claimed)[-96:]
    updated["history"] = history[-240:]
    return updated, rewards


def build_recovery_support_summary(state: Dict[str, Any], now_ts: Optional[float] = None) -> Tuple[str, str]:
    now = now_ts or time.time()
    days_clean = recovery_clean_days(state, datetime.fromtimestamp(now).date())
    best_streak = max(days_clean, max(0, int(safe_float(state.get("best_streak_days") or 0))))
    relapse_count = max(0, int(safe_float(state.get("relapse_count") or 0)))
    points = max(0, int(safe_float(state.get("points") or 0)))
    goal_name = sanitize_text(state.get("goal_name") or "Recovery", max_chars=120)
    next_milestone = recovery_next_milestone(days_clean)
    last_checkin = safe_float(state.get("latest_checkin_ts"))
    latest_note = sanitize_text(state.get("latest_note") or "", max_chars=220)
    latest_mood = max(0.0, min(10.0, safe_float(state.get("latest_mood") or 0.0)))
    latest_craving = max(0.0, min(10.0, safe_float(state.get("latest_craving") or 0.0)))
    reminder_time = sanitize_text(state.get("reminder_time") or recovery_support_defaults()["reminder_time"], max_chars=20)
    due = recovery_support_due_status(state, now)
    recent_events = list(state.get("history") or [])[-4:][::-1]
    if days_clean <= 0:
        title = f"{goal_name} planner ready"
    elif relapse_count == 0 and days_clean >= 30:
        title = f"{goal_name} streak building strong"
    else:
        title = f"{goal_name} day {days_clean}"
    lines = [
        f"Current clean streak: {days_clean} day{'s' if days_clean != 1 else ''}.",
        f"Best streak: {best_streak} day{'s' if best_streak != 1 else ''}.",
        f"Relapses logged: {relapse_count}.",
        f"Support points: {points}.",
    ]
    if next_milestone is not None:
        lines.append(f"Next milestone: day {next_milestone[0]} for +{next_milestone[1]} points.")
    else:
        lines.append("Top milestone unlocked. Keep protecting the streak one day at a time.")
    lines.append(f"Check-in reminder: {reminder_time}. {sanitize_text(due.get('text') or '', max_chars=140)}")
    if last_checkin > 0:
        lines.append(f"Latest check-in: {format_timestamp(last_checkin)}.")
    if last_checkin > 0:
        lines.append(f"Mood {latest_mood:.0f}/10. Craving {latest_craving:.0f}/10.")
    if latest_note:
        lines.append(f"Latest note: {latest_note}")
    if recent_events:
        event_lines = []
        for item in recent_events:
            event_type = sanitize_text(item.get("type") or "", max_chars=20).lower()
            if event_type == "milestone":
                event_lines.append(
                    f"{format_timestamp(safe_float(item.get('timestamp')))} • milestone • {sanitize_text(item.get('label') or '', max_chars=80)}"
                )
            elif event_type == "relapse":
                event_lines.append(
                    f"{format_timestamp(safe_float(item.get('timestamp')))} • relapse reset • {sanitize_text(item.get('note') or 'fresh start logged', max_chars=120)}"
                )
            else:
                event_lines.append(
                    f"{format_timestamp(safe_float(item.get('timestamp')))} • check-in • {sanitize_text(item.get('note') or 'steady work', max_chars=120)}"
                )
        lines.append("Recent progress: " + " | ".join(event_lines))
    return title, " ".join(lines)


def build_recovery_badges_text(state: Dict[str, Any]) -> str:
    milestone_rows = [
        item
        for item in list(state.get("history") or [])
        if sanitize_text(item.get("type") or "", max_chars=20).lower() == "milestone"
    ]
    if not milestone_rows:
        return "No milestone badges unlocked yet. Your first rewards appear as the streak grows."
    lines = []
    for item in milestone_rows[-8:][::-1]:
        label = sanitize_text(item.get("label") or "Milestone", max_chars=120)
        points = int(safe_float(item.get("points_delta") or 0))
        streak_days = max(0, int(safe_float(item.get("streak_days") or 0)))
        lines.append(f"{label} • day {streak_days} • +{points} pts • {format_timestamp(safe_float(item.get('timestamp')))}")
    return "\n".join(lines)


def recovery_support_due_status(state: Dict[str, Any], now_ts: Optional[float] = None) -> Dict[str, Any]:
    now = now_ts or time.time()
    if not bool(state.get("enabled")):
        return {"state": "Off", "text": "Recovery check-ins are off.", "due_now": False, "overdue": False}
    reminder_minutes = parse_clock_minutes(state.get("reminder_time") or "") or (20 * 60)
    today = datetime.fromtimestamp(now).date()
    target_ts = clock_minutes_to_timestamp(today, reminder_minutes)
    checked_in = recovery_checked_in_today(state, now)
    if checked_in:
        return {"state": "Done", "text": "Today's recovery check-in is complete.", "due_now": False, "overdue": False}
    if now < target_ts:
        return {"state": "Scheduled", "text": f"Recovery check-in {format_relative_due(target_ts, now)}.", "due_now": False, "overdue": False}
    if now <= target_ts + 3.0 * 3600.0:
        return {"state": "Due", "text": "Recovery check-in is due now.", "due_now": True, "overdue": False}
    return {"state": "Overdue", "text": f"Recovery check-in {format_duration(now - target_ts)} overdue.", "due_now": True, "overdue": True}


def build_recovery_support_nudge_text(state: Dict[str, Any], now_ts: Optional[float] = None) -> str:
    now = now_ts or time.time()
    if not bool(state.get("enabled")):
        return ""
    goal_name = sanitize_text(state.get("goal_name") or "Recovery", max_chars=120)
    due = recovery_support_due_status(state, now)
    latest_craving = max(0.0, min(10.0, safe_float(state.get("latest_craving") or 0.0)))
    latest_mood = max(0.0, min(10.0, safe_float(state.get("latest_mood") or 0.0)))
    days_clean = recovery_clean_days(state, datetime.fromtimestamp(now).date())
    next_milestone = recovery_next_milestone(days_clean)
    if latest_craving >= 7.0:
        return (
            f"Gentle nudge: {goal_name} protection mode. You logged craving {latest_craving:.0f}/10. "
            f"Open the coping plan and protect the next 20 minutes."
        )
    if due.get("overdue"):
        return f"Gentle nudge: {goal_name} check-in is overdue. Protect the streak with a quick honest note."
    if due.get("due_now"):
        return f"Gentle nudge: {goal_name} check-in is due now. One check-in keeps the streak visible."
    if latest_mood <= 3.0 and safe_float(state.get("latest_checkin_ts")) > 0:
        return (
            f"Gentle nudge: mood has been low ({latest_mood:.0f}/10). Use Therapy or Recovery Coach mode for a grounded reset."
        )
    if next_milestone is not None:
        days_left = max(0, next_milestone[0] - days_clean)
        return f"Gentle nudge: {goal_name} is {days_left} day{'s' if days_left != 1 else ''} from the next milestone."
    return f"Gentle nudge: {goal_name} streak is active. Keep the next small win simple."


def build_dashboard_nudge_text(
    med: Optional[Dict[str, Any]],
    recovery_support: Dict[str, Any],
    now_ts: Optional[float] = None,
) -> str:
    now = now_ts or time.time()
    med_text = build_medication_nudge_text(med, now) if med is not None else ""
    recovery_text = build_recovery_support_nudge_text(recovery_support, now)
    if med_text and recovery_text:
        return med_text + "\n\n" + recovery_text
    return med_text or recovery_text or "Gentle nudge: choose a medication or recovery plan to see the next reminder."


def _flow_score_label(score: float) -> str:
    if score >= 88:
        return "excellent"
    if score >= 74:
        return "strong"
    if score >= 58:
        return "useful"
    return "optional"


def _flow_clamp(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def build_flow_simulation_report(
    data: Dict[str, Any],
    settings: Dict[str, Any],
    *,
    selected_med_id: str = "",
    now_ts: Optional[float] = None,
    model_ready: bool = False,
    password_enabled: bool = False,
) -> Tuple[str, str]:
    now = now_ts or time.time()
    meds = list(active_medications(data))
    archived = list(archived_medications(data))
    selected = next((med for med in all_stored_medications(data) if str(med.get("id")) == selected_med_id), None)
    statuses = [medication_due_status(med, now) for med in meds]
    due_count = len([status for status in statuses if status.get("due_now") and not status.get("overdue")])
    overdue_count = len([status for status in statuses if status.get("overdue")])
    safety_state = effective_safety_reviews_state(data.get("safety_reviews"), meds, now)
    safety_pending = bool(safety_state.get("pending", False))
    safety_timestamp = safe_float(safety_state.get("timestamp") or 0.0)
    safety_age_hours = ((now - safety_timestamp) / 3600.0) if safety_timestamp > 0 else 999.0
    hygiene = dict(data.get("dental_hygiene") or dental_hygiene_defaults())
    dental_due = any(
        bool(
            habit_due_status(
                safe_float(hygiene.get(last_key)),
                safe_float(hygiene.get(interval_key)) or default_interval,
                now,
            ).get("due_now")
        )
        for last_key, interval_key, default_interval in (
            ("last_brush_ts", "brush_interval_hours", 12.0),
            ("last_floss_ts", "floss_interval_hours", 24.0),
            ("last_rinse_ts", "rinse_interval_hours", 24.0),
        )
    )
    exercise = dict(data.get("exercise") or exercise_defaults())
    movement_due = any(
        bool(
            habit_due_status(
                safe_float(exercise.get(last_key)),
                safe_float(exercise.get(interval_key)) or default_interval,
                now,
            ).get("due_now")
        )
        for last_key, interval_key, default_interval in (
            ("last_walk_ts", "walk_interval_hours", 4.0),
            ("last_light_ts", "light_interval_hours", 8.0),
            ("last_stretch_ts", "stretch_interval_hours", 2.0),
        )
    )
    recovery = dict(data.get("recovery_support") or recovery_support_defaults())
    recovery_due = recovery_support_due_status(recovery, now)
    assistant_count = len(list(data.get("assistant_history") or []))
    vision_count = len(list(data.get("vision_imports") or []))
    text_scale = TEXT_SIZE_SCALE_MAP.get(normalize_setting_choice(settings.get("text_size"), TEXT_SIZE_OPTIONS, "Default"), 1.0)
    native_image = bool(settings.get("enable_native_image_input", True))

    rows: List[Dict[str, Any]] = []
    for index, current_step in enumerate(HELP_FLOW_STEPS[:-1]):
        next_step = HELP_FLOW_STEPS[index + 1]
        edge = f"{current_step[0]}->{next_step[0]}"
        usefulness = 60.0 + index * 1.2
        beauty = 72.0
        seamless = 68.0
        backend = 70.0
        reason = f"{current_step[2]} into {next_step[2]} keeps the care loop moving."

        if edge == "A->B":
            usefulness += 22.0 if not meds else 6.0 + min(12.0, float(due_count + overdue_count) * 4.0)
            seamless += 8.0 if selected is not None else 4.0
            reason = "Best when the day needs a clean regimen source before anything else."
        elif edge == "B->C":
            usefulness += 20.0 if meds else 4.0
            seamless += 12.0 if meds else -8.0
            backend += 8.0
            reason = "A saved regimen becomes a visible checklist instead of memory work."
        elif edge == "C->D":
            usefulness += min(24.0, float(due_count + overdue_count) * 8.0)
            backend += 10.0
            reason = "Checklist changes are safest when schedule rules and all-meds review stay close."
        elif edge == "D->E":
            usefulness += 16.0 if (not meds or safety_pending or safety_age_hours > 24.0) else 4.0
            seamless += 8.0 if model_ready and native_image else -6.0
            backend += 10.0 if model_ready else -10.0
            reason = "Photo import helps most when label context can clarify uncertain medication details."
        elif edge == "E->F":
            usefulness += 12.0 if dental_due else 5.0
            beauty += 8.0
            seamless += 6.0 if vision_count else 2.0
            reason = "Visual review and dental routines share the same inspect, save, and continue rhythm."
        elif edge == "F->G":
            usefulness += 14.0 if dental_due or movement_due else 5.0
            beauty += 6.0
            seamless += 7.0
            reason = "Dental and movement cards are quick habit loops with similar log-and-refresh behavior."
        elif edge == "G->H":
            usefulness += 16.0 if movement_due or recovery.get("enabled") else 6.0
            beauty += 7.0
            seamless += 8.0
            reason = "Movement logging pairs well with recovery momentum and low-friction check-ins."
        elif edge == "H->I":
            usefulness += 18.0 if recovery.get("enabled") or bool(recovery_due.get("due_now")) else 7.0
            seamless += 8.0 if assistant_count else 4.0
            backend += 8.0 if model_ready else -8.0
            reason = "Chat has better context after plans, streaks, and check-ins are saved."
        elif edge == "I->J":
            usefulness += 13.0 if not model_ready or text_scale != 1.0 else 6.0
            seamless += 10.0
            backend += 12.0
            reason = "Runtime and accessibility tuning remove friction after the support loop is understood."
        elif edge == "J->K":
            usefulness += 18.0 if password_enabled else 10.0
            beauty += 4.0
            seamless += 7.0
            backend += 12.0
            reason = "Security is clearest when the next launch policy is visible before closing."

        total = (
            _flow_clamp(usefulness) * 0.38
            + _flow_clamp(beauty) * 0.22
            + _flow_clamp(seamless) * 0.25
            + _flow_clamp(backend) * 0.15
        )
        rows.append(
            {
                "edge": edge,
                "from": current_step[2],
                "to": next_step[2],
                "usefulness": _flow_clamp(usefulness),
                "beauty": _flow_clamp(beauty),
                "seamless": _flow_clamp(seamless),
                "backend": _flow_clamp(backend),
                "total": _flow_clamp(total),
                "reason": reason,
            }
        )

    rows.sort(key=lambda item: item["total"], reverse=True)
    best = rows[0]
    snapshot = (
        f"Best next path: {best['edge']} | {_flow_score_label(best['total']).title()} "
        f"({best['total']:.0f}/100)\n"
        f"{best['from']} -> {best['to']}\n"
        f"{best['reason']}"
    )
    comparison_lines = [
        "A-K path simulation compares usefulness, visual clarity, handoff smoothness, and backend readiness.",
        f"Current state: {len(meds)} active meds, {len(archived)} completed meds, {due_count} due, {overdue_count} missed.",
        "",
    ]
    for row in sorted(rows, key=lambda item: item["edge"]):
        comparison_lines.append(
            f"{row['edge']} {row['from']} -> {row['to']}: {row['total']:.0f}/100 "
            f"({row['usefulness']:.0f} useful, {row['beauty']:.0f} clear, "
            f"{row['seamless']:.0f} seamless, {row['backend']:.0f} backend)"
        )
        comparison_lines.append(f"  {row['reason']}")
    return snapshot, "\n".join(comparison_lines)


def build_help_feature_text(topic: str = "") -> str:
    clean_topic = sanitize_text(topic, max_chars=80).lower()
    if clean_topic:
        for title, body in HELP_FEATURE_GUIDE:
            if clean_topic == title.lower():
                return f"{title}\n{body}"
    lines = ["MedSafe feature guide"]
    lines.extend(f"{title}: {body}" for title, body in HELP_FEATURE_GUIDE)
    return "\n\n".join(lines)


def build_recovery_support_context(state: Dict[str, Any], now_ts: Optional[float] = None) -> str:
    now = now_ts or time.time()
    title, summary = build_recovery_support_summary(state, now)
    days_clean = recovery_clean_days(state, datetime.fromtimestamp(now).date())
    next_milestone = recovery_next_milestone(days_clean)
    due = recovery_support_due_status(state, now)
    next_text = (
        f"day {next_milestone[0]} (+{next_milestone[1]} pts)"
        if next_milestone is not None
        else "top milestone already reached"
    )
    return "\n".join(
        [
            "Recovery support:",
            f"- enabled={'yes' if state.get('enabled') else 'no'} goal={sanitize_text(state.get('goal_name') or 'Recovery', max_chars=120)}",
            f"- clean_start={sanitize_text(state.get('clean_start_date') or 'unset', max_chars=20)} current_streak_days={days_clean}",
            f"- best_streak_days={max(0, int(safe_float(state.get('best_streak_days') or 0)))} relapse_count={max(0, int(safe_float(state.get('relapse_count') or 0)))}",
            f"- points={max(0, int(safe_float(state.get('points') or 0)))} next_milestone={next_text}",
            f"- reminder_time={sanitize_text(state.get('reminder_time') or '8:00 PM', max_chars=20)} due_status={sanitize_text(due.get('text') or '', max_chars=140)}",
            f"- latest_mood={max(0.0, min(10.0, safe_float(state.get('latest_mood') or 0.0))):.0f}/10 latest_craving={max(0.0, min(10.0, safe_float(state.get('latest_craving') or 0.0))):.0f}/10",
            f"- motivation={sanitize_text(state.get('motivation') or 'none', max_chars=220)}",
            f"- coping_plan={sanitize_text(state.get('coping_plan') or 'none', max_chars=260)}",
            f"- summary={sanitize_text(title + '. ' + summary, max_chars=420)}",
        ]
    )


def build_schedule_context(data: Dict[str, Any], selected_med_id: Optional[str]) -> str:
    meds = active_medications(data)
    archived = archived_medications(data)
    now = time.time()
    lines = ["Local health schedule context:"]
    if meds:
        for med in meds:
            status = medication_due_status(med, now)
            schedule_preview = sanitize_text(build_medication_schedule_text(med, now).replace("\n", " | "), max_chars=260)
            last_24h = total_taken_last_24h(med, now)
            marker = " [selected]" if str(med.get("id")) == selected_med_id else ""
            lines.append(
                "- {name}{marker}: dose={dose:g}mg interval={interval:g}h max_daily={max_daily:g}mg "
                "last_taken={last_taken} last_24h_total={last_24h:g}mg next_due={next_due} plan={plan} notes={notes}".format(
                    name=sanitize_text(med.get("name"), max_chars=120),
                    marker=marker,
                    dose=max(0.0, safe_float(med.get("dose_mg"))),
                    interval=max(0.0, safe_float(med.get("interval_hours"))),
                    max_daily=max(0.0, safe_float(med.get("max_daily_mg"))),
                    last_taken=format_timestamp(last_effective_taken_ts(med)),
                    last_24h=last_24h,
                    next_due=status["text"],
                    plan=schedule_preview or "no daily plan",
                    notes=sanitize_text(med.get("notes") or "none", max_chars=180) or "none",
                )
            )
    else:
        lines.append("- No current medications are stored yet.")
    if archived:
        lines.append("")
        lines.append("Completed medications kept for history:")
        for med in archived[:6]:
            marker = " [selected]" if str(med.get("id")) == selected_med_id else ""
            lines.append(
                "- {name}{marker}: archived={archived} last_taken={last_taken} total_logs={log_count} notes={notes}".format(
                    name=sanitize_text(med.get("name"), max_chars=120),
                    marker=marker,
                    archived=medication_archive_label(med),
                    last_taken=format_timestamp(last_effective_taken_ts(med)),
                    log_count=len(medication_history_records(med)),
                    notes=sanitize_text(med.get("notes") or "none", max_chars=180) or "none",
                )
            )

    hygiene = data.get("dental_hygiene") or dental_hygiene_defaults()
    lines.append("")
    lines.append("Dental hygiene:")
    lines.append(
        "- brush={brush} floss={floss} rinse={rinse} latest_rating={rating} latest_score={score:g} latest_risk={risk} latest_summary={summary}".format(
            brush=habit_due_status(safe_float(hygiene.get("last_brush_ts")), safe_float(hygiene.get("brush_interval_hours")) or 12.0, now)["text"],
            floss=habit_due_status(safe_float(hygiene.get("last_floss_ts")), safe_float(hygiene.get("floss_interval_hours")) or 24.0, now)["text"],
            rinse=habit_due_status(safe_float(hygiene.get("last_rinse_ts")), safe_float(hygiene.get("rinse_interval_hours")) or 24.0, now)["text"],
            rating=sanitize_text(hygiene.get("latest_rating") or "not rated", max_chars=80),
            score=max(0.0, safe_float(hygiene.get("latest_score"))),
            risk=(
                f"{normalized_risk_level_text(hygiene.get('latest_risk_level') or '', safe_float(hygiene.get('latest_risk_score')))}"
                f":{max(0.0, safe_float(hygiene.get('latest_risk_score'))):.0f}"
            ),
            summary=sanitize_text(hygiene.get("latest_summary") or "no photo review yet", max_chars=180),
        )
    )

    recovery = data.get("dental_recovery") or dental_recovery_defaults()
    lines.append("")
    lines.append("Dental recovery:")
    if recovery.get("enabled"):
        lines.append(
            "- procedure={procedure} date={when} latest_status={status} latest_score={score:g} latest_risk={risk} symptoms={symptoms}".format(
                procedure=sanitize_text(recovery.get("procedure_type") or "unknown", max_chars=120),
                when=sanitize_text(recovery.get("procedure_date") or "unknown", max_chars=20),
                status=sanitize_text(recovery.get("latest_status") or "awaiting photo check-in", max_chars=140),
                score=max(0.0, safe_float(recovery.get("latest_score"))),
                risk=(
                    f"{normalized_risk_level_text(recovery.get('latest_risk_level') or '', safe_float(recovery.get('latest_risk_score')))}"
                    f":{max(0.0, safe_float(recovery.get('latest_risk_score'))):.0f}"
                ),
                symptoms=sanitize_text(recovery.get("symptom_notes") or "none", max_chars=180),
            )
        )
    else:
        lines.append("- recovery mode not enabled")

    exercise = data.get("exercise") or exercise_defaults()
    exercise_title, exercise_body = build_exercise_overview(exercise, now)
    lines.append("")
    lines.append("Movement:")
    lines.append(f"- {sanitize_text(exercise_title, max_chars=120)} | {sanitize_text(exercise_body, max_chars=320)}")

    recovery_support = data.get("recovery_support") or recovery_support_defaults()
    lines.append("")
    lines.append(build_recovery_support_context(recovery_support, now))

    latest_imports = list(data.get("vision_imports") or [])
    if latest_imports:
        latest_import = latest_imports[-1]
        lines.append("")
        lines.append(
            "- latest bottle import: {summary} review_risk={risk} note={note}".format(
                summary=sanitize_text(latest_import.get("summary") or "schedule imported", max_chars=180),
                risk=(
                    f"{normalized_risk_level_text(latest_import.get('risk_level') or '', safe_float(latest_import.get('risk_score')))}"
                    f":{max(0.0, safe_float(latest_import.get('risk_score'))):.0f}"
                ),
                note=sanitize_text(latest_import.get("risk_summary") or "none", max_chars=180),
            )
        )
    return "\n".join(lines)


def estimate_context_tokens(value: Any) -> int:
    """Fast local token estimate for the small on-device context window."""
    text = sanitize_text(value, max_chars=120000)
    if not text:
        return 0
    # A conservative mixed heuristic: words catch prose, chars catch dense JSON/paths.
    word_count = len(re.findall(r"\S+", text))
    char_count = len(text)
    return max(1, int(max(word_count * 1.35, char_count / 3.8)))


def assistant_context_memory_defaults() -> Dict[str, Any]:
    return {
        "summary": "",
        "summary_updated_ts": 0.0,
        "compaction_count": 0,
        "last_compacted_message_count": 0,
        "window_token_limit": ASSISTANT_CONTEXT_TOKEN_LIMIT,
        "target_tokens": ASSISTANT_CONTEXT_TARGET_TOKENS,
        "recent_turns": ASSISTANT_CONTEXT_RECENT_TURNS,
    }


def normalize_assistant_context_memory(raw: Any) -> Dict[str, Any]:
    base = assistant_context_memory_defaults()
    if not isinstance(raw, dict):
        return base
    base["summary"] = sanitize_text(raw.get("summary") or "", max_chars=ASSISTANT_SUMMARY_MAX_CHARS)
    base["summary_updated_ts"] = safe_float(raw.get("summary_updated_ts") or 0.0)
    base["compaction_count"] = max(0, int(safe_float(raw.get("compaction_count") or 0)))
    base["last_compacted_message_count"] = max(0, int(safe_float(raw.get("last_compacted_message_count") or 0)))
    base["window_token_limit"] = max(1200, int(safe_float(raw.get("window_token_limit") or ASSISTANT_CONTEXT_TOKEN_LIMIT)))
    base["target_tokens"] = max(1000, min(base["window_token_limit"], int(safe_float(raw.get("target_tokens") or ASSISTANT_CONTEXT_TARGET_TOKENS))))
    base["recent_turns"] = max(4, min(14, int(safe_float(raw.get("recent_turns") or ASSISTANT_CONTEXT_RECENT_TURNS))))
    return base


def format_chat_turn_for_context(item: Dict[str, Any], *, max_chars: int = 420) -> str:
    role = "User" if item.get("role") == "user" else "Assistant"
    mode = normalize_assistant_mode(item.get("mode") or "General")
    mode_suffix = "" if mode == "General" else f" [{mode}]"
    timestamp = safe_float(item.get("timestamp") or 0.0)
    when = format_timestamp(timestamp) if timestamp else "unknown time"
    return f"{role}{mode_suffix} ({when}): {sanitize_text(item.get('content') or '', max_chars=max_chars)}"


def build_deterministic_compaction_summary(
    prior_summary: str,
    old_messages: List[Dict[str, Any]],
    *,
    max_chars: int = ASSISTANT_SUMMARY_MAX_CHARS,
) -> str:
    """Local compactor for old chat turns; avoids spending an extra model call."""
    prior = sanitize_text(prior_summary, max_chars=max_chars)
    if not old_messages:
        return prior
    user_lines: List[str] = []
    assistant_lines: List[str] = []
    decisions: List[str] = []
    safety: List[str] = []
    prefs: List[str] = []
    keywords = (
        "med", "dose", "mg", "interval", "schedule", "missed", "dental", "tooth", "gum", "brush", "floss",
        "recovery", "craving", "relapse", "streak", "exercise", "walk", "stretch", "preference", "setting",
        "text size", "compact", "summary", "context", "token", "persistent",
    )
    safety_keywords = ("unsafe", "warning", "urgent", "overdose", "self-harm", "suicide", "emergency", "call", "limit", "too soon")
    pref_keywords = ("like", "prefer", "don't", "remove", "keep", "setting", "text size", "spacing", "compact")
    for item in old_messages:
        content = sanitize_text(item.get("content") or "", max_chars=900)
        if not content:
            continue
        lowered = content.lower()
        line = format_chat_turn_for_context(item, max_chars=360)
        if item.get("role") == "user":
            if any(token in lowered for token in keywords):
                user_lines.append(line)
            if any(token in lowered for token in pref_keywords):
                prefs.append(line)
        else:
            if any(token in lowered for token in ("done", "changed", "updated", "saved", "removed", "added", "set", "compact")):
                decisions.append(line)
            elif any(token in lowered for token in keywords):
                assistant_lines.append(line)
        if any(token in lowered for token in safety_keywords):
            safety.append(line)

    sections: List[str] = []
    if prior:
        sections.append("Existing rolling memory:\n" + prior)
    sections.append("Compaction policy:\n" + ASSISTANT_COMPACTION_PROMPT)
    if prefs:
        sections.append("User preferences and UI/app instructions preserved:\n" + "\n".join(prefs[-8:]))
    if user_lines:
        sections.append("Important older user context:\n" + "\n".join(user_lines[-10:]))
    if decisions:
        sections.append("Decisions/changes already made:\n" + "\n".join(decisions[-10:]))
    if assistant_lines:
        sections.append("Useful older assistant context:\n" + "\n".join(assistant_lines[-6:]))
    if safety:
        sections.append("Safety boundaries or warnings to preserve:\n" + "\n".join(safety[-6:]))
    summary = "\n\n".join(sections).strip()
    if len(summary) > max_chars:
        summary = summary[-max_chars:].lstrip()
        first_break = summary.find("\n")
        if first_break > 0:
            summary = summary[first_break + 1 :].lstrip()
        summary = "[Older rolling memory trimmed to fit window.]\n" + summary
    return sanitize_text(summary, max_chars=max_chars)


def compact_assistant_history_if_needed(data: Dict[str, Any], *, force: bool = False) -> Tuple[Dict[str, Any], bool]:
    history = list(data.get("assistant_history") or [])
    memory = normalize_assistant_context_memory(data.get("assistant_context_memory") or {})
    if not history:
        data["assistant_context_memory"] = memory
        return data, False
    history_tokens = estimate_context_tokens("\n".join(format_chat_turn_for_context(item, max_chars=900) for item in history))
    trigger = force or len(history) > ASSISTANT_CONTEXT_MAX_MESSAGES or history_tokens > ASSISTANT_CONTEXT_COMPACT_TRIGGER_TOKENS
    if not trigger:
        data["assistant_context_memory"] = memory
        return data, False
    recent_count = int(memory.get("recent_turns") or ASSISTANT_CONTEXT_RECENT_TURNS)
    recent_count = max(4, min(14, recent_count))
    if len(history) <= recent_count:
        data["assistant_context_memory"] = memory
        return data, False
    old_messages = history[:-recent_count]
    recent_messages = history[-recent_count:]
    memory["summary"] = build_deterministic_compaction_summary(memory.get("summary") or "", old_messages)
    memory["summary_updated_ts"] = time.time()
    memory["compaction_count"] = int(memory.get("compaction_count") or 0) + 1
    memory["last_compacted_message_count"] = len(old_messages)
    memory["recent_turns"] = recent_count
    data["assistant_context_memory"] = memory
    data["assistant_history"] = recent_messages
    return data, True


def build_recent_assistant_context(history: List[Dict[str, Any]], memory: Optional[Dict[str, Any]] = None, *, token_budget: int = 900) -> str:
    memory = normalize_assistant_context_memory(memory or {})
    lines: List[str] = []
    summary = sanitize_text(memory.get("summary") or "", max_chars=ASSISTANT_SUMMARY_MAX_CHARS)
    if summary:
        lines.append("Rolling compacted chat memory:")
        lines.append(summary)
    if history:
        lines.append("Recent sliding-window chat turns:")
        # Add newest turns first within budget, then reverse for natural order.
        picked: List[str] = []
        used = estimate_context_tokens("\n".join(lines))
        for item in reversed(history):
            line = format_chat_turn_for_context(item, max_chars=320)
            cost = estimate_context_tokens(line)
            if picked and used + cost > max(220, token_budget):
                break
            picked.append(line)
            used += cost
        lines.extend(reversed(picked))
    if not lines:
        return "No prior assistant messages."
    return "\n".join(lines)


def build_context_window_report(data: Dict[str, Any], prompt: str = "") -> str:
    history = list(data.get("assistant_history") or [])
    memory = normalize_assistant_context_memory(data.get("assistant_context_memory") or {})
    chat_context = build_recent_assistant_context(history, memory, token_budget=1200)
    schedule_context = build_schedule_context(data, None)
    prompt_tokens = estimate_context_tokens(prompt)
    chat_tokens = estimate_context_tokens(chat_context)
    schedule_tokens = estimate_context_tokens(schedule_context)
    total = prompt_tokens + chat_tokens + schedule_tokens
    limit = int(memory.get("window_token_limit") or ASSISTANT_CONTEXT_TOKEN_LIMIT)
    return "\n".join(
        [
            f"Context window: ~{total}/{limit} tokens used before model overhead.",
            f"Vault/schedule context: ~{schedule_tokens} tokens",
            f"Rolling chat memory: ~{estimate_context_tokens(memory.get('summary') or '')} tokens",
            f"Recent chat window: {len(history)} messages, ~{chat_tokens} tokens",
            f"Compactions run: {int(memory.get('compaction_count') or 0)}",
            f"Last compacted: {format_timestamp(safe_float(memory.get('summary_updated_ts') or 0.0)) if memory.get('summary_updated_ts') else 'Not yet'}",
            "Window policy: keep latest turns verbatim, compact older turns, reserve room for the next reply.",
        ]
    )

def workflow_surface_hint(tab_name: str) -> str:
    clean = sanitize_text(tab_name, max_chars=80)
    hints = {
        "Dashboard": "",
        "Medications": "Medications: select an entry to edit, or start a new one and confirm dose, interval, max daily amount, and timing.",
        "Safety": "Safety: run an all-meds scan after regimen changes, then review any caution before logging.",
        "Pill Bottle Scanner": "Pill Bottle Scanner: import bottle photos as draft context, then manually confirm the label details before saving.",
        "Dental": "Dental: log habits, review photos when useful, and keep recovery notes close to the actual timeline.",
        "Exercise": "Exercise: use small movement logs and intervals to keep recovery-friendly routines visible.",
        "Recovery": "Recovery: check mood and craving, protect the next 24 hours, and update the coping plan when patterns change.",
        "Chat": "Chat: pick a mode, use a quick prompt when stuck, and use the context preview to see what the reply will emphasize.",
        "Help": "Help: open the best path or choose a feature topic when the next workflow is unclear.",
        "Settings": "Settings: confirm model readiness, backend, text size, checklist undo, and startup password policy.",
    }
    return hints.get(clean, "MedSafe: choose the workflow that matches the next concrete action.")


def assistant_prompt_health(prompt: str, mode: str) -> Dict[str, str]:
    clean_prompt = sanitize_text(prompt, max_chars=1600)
    active_mode = normalize_assistant_mode(mode)
    lowered = clean_prompt.lower()
    targets = []
    if any(token in lowered for token in ("dose", "med", "pill", "mg", "schedule", "missed", "late")):
        targets.append("meds")
    if any(token in lowered for token in ("tooth", "teeth", "dental", "gum", "brush", "floss", "rinse")):
        targets.append("dental")
    if any(token in lowered for token in ("walk", "exercise", "stretch", "movement")):
        targets.append("movement")
    if any(token in lowered for token in ("craving", "streak", "relapse", "recovery", "urge", "trigger")):
        targets.append("recovery")
    if any(token in lowered for token in ("feel", "anxious", "sad", "overwhelmed", "therapy", "cope")):
        targets.append("support")
    if not targets:
        targets.append("vault")

    if len(clean_prompt) < 12:
        clarity = "too short"
        suggestion = "Add the situation, timeframe, or desired outcome."
    elif clean_prompt.endswith("?") or any(token in lowered for token in ("summarize", "check", "draft", "plan", "what next")):
        clarity = "clear"
        suggestion = "Ready to send."
    else:
        clarity = "usable"
        suggestion = "A direct question or timeframe would sharpen the answer."
    if active_mode == "Therapy":
        stance = "reflective"
    elif active_mode == "Recovery Coach":
        stance = "momentum"
    else:
        stance = "practical"
    return {
        "clarity": clarity,
        "targets": ", ".join(targets),
        "stance": stance,
        "suggestion": suggestion,
    }


def run_assistant_request(
    key: bytes,
    data: Dict[str, Any],
    prompt: str,
    selected_med_id: Optional[str],
    settings: Dict[str, Any],
    mode: str = "General",
    on_delta: Optional[Callable[[str], None]] = None,
) -> str:
    active_mode = normalize_assistant_mode(mode)
    if active_mode == "Therapy":
        system_text = (
            "You are MedSafe Therapy Companion, a private local reflective support assistant running entirely on the user's device.\n"
            "Be warm, calm, validating, collaborative, and nonjudgmental.\n"
            "Use reflective listening, grounding ideas, gentle CBT-style reframes, motivational interviewing, journaling prompts, and practical coping steps.\n"
            "Keep the tone trauma-informed, shame-free, and emotionally steady. Avoid absolutist language and avoid pretending certainty about the user's life.\n"
            "Use this support rhythm internally: stabilize emotion, name the pressure, reflect patterns, offer one grounding tool, offer one small next action, and close with encouragement.\n"
            "Prefer one or two grounded interventions over long lectures. Mirror the user's feelings and needs in plain language when it helps them feel understood.\n"
            "Use only the context provided from the encrypted vault and the user's message.\n"
            "You are not a licensed therapist, you do not diagnose, and you do not replace professional care.\n"
            "If the user mentions self-harm, overdose, suicidal intent, or immediate danger, urge immediate human help and emergency support clearly.\n"
            "Prefer short supportive paragraphs followed by a few concrete next steps when helpful."
        )
        final_instruction = (
            "Respond like a supportive therapist-style coach. Validate first, then offer 2-4 grounded next steps, reflection questions, or coping tools. When useful, include short sections named Reflect, Ground, and Next Step, and close with a compassionate check-in question."
        )
    elif active_mode == "Recovery Coach":
        system_text = (
            "You are MedSafe Recovery Coach, a private local relapse-prevention and recovery-support assistant running entirely on the user's device.\n"
            "Be encouraging, direct, shame-free, and practical.\n"
            "Use the stored clean-streak, relapse, milestone, points, and coping-plan context as the backbone of your response.\n"
            "Use the stored reminder time, latest mood and craving, and milestone progress when those details are relevant.\n"
            "Help the user protect the next 24 hours with concrete strategies such as urge surfing, trigger interruption, distraction plans, reaching out, and environment changes.\n"
            "Treat craving spikes, low mood, anniversaries, and slip risk as immediate planning problems, not identity failures.\n"
            "If the user reports a slip or relapse, treat it as data, help them restart without shame, and focus on the smallest stabilizing next actions.\n"
            "When the user feels shaky, structure the reply around: protect the next 10 minutes, the next hour, and tonight.\n"
            "Celebrate progress without sounding fake or childish.\n"
            "You are not a clinician, sponsor, detox program, or emergency service.\n"
            "If the user describes overdose risk, dangerous withdrawal, or immediate safety risk, tell them to seek urgent human help right away.\n"
            "Keep replies actionable and structured around recovery momentum."
        )
        final_instruction = (
            "Respond like a recovery therapist-coach. Reference the streak, points, mood, craving, reminder timing, or milestone context when relevant. Keep the structure practical, protect momentum, and end with a short action ladder for the next 10 minutes, next hour, and today."
        )
    else:
        system_text = (
            "You are MedSafe, a private local health scheduling assistant running entirely on the user's device.\n"
            "Use only the medication, dental hygiene, recovery, movement, and recovery-support facts in the provided context and the user's request.\n"
            "You are not a clinician and cannot verify interactions, diagnoses, allergies, organ function, or procedure complications.\n"
            "When the user asks whether a dose looks okay, ground the answer in the stored dose amount, interval, planned times, and last-24-hour total from the context.\n"
            "Use High only when the stored numbers clearly show a timing or 24-hour-limit problem, Medium when timing is a little early or key details are missing, and Low when the stored schedule supports the dose.\n"
            "Do not keep repeating that something is unsafe unless the provided numbers clearly support that conclusion.\n"
            "Be concise, practical, and clear when uncertainty exists."
        )
        final_instruction = "Answer directly, then include Today, Watch-outs, and Next action when those sections help the user move faster."
    quantum_context = build_assistant_quantum_context(data, selected_med_id, prompt, active_mode)
    system_text = (
        system_text
        + "\nThe provided _quantum:state, RGB, and psutil values are private local context-routing metadata only. "
        "Use them to choose emphasis, ordering, caution tone, and retrieval focus; never present them as medical evidence, diagnosis, certainty, or a reason to act."
    )
    data, _compacted = compact_assistant_history_if_needed(dict(data), force=False)
    memory = normalize_assistant_context_memory(data.get("assistant_context_memory") or {})
    prompt_block = f"User request: {sanitize_text(prompt, max_chars=1200)}"
    fixed_tokens = estimate_context_tokens(prompt_block + "\n" + final_instruction + "\n" + quantum_context.get("assistant_prompt_block", ""))
    target_tokens = int(memory.get("target_tokens") or ASSISTANT_CONTEXT_TARGET_TOKENS)
    remaining = max(700, target_tokens - fixed_tokens)
    schedule_budget = max(450, int(remaining * 0.58))
    chat_budget = max(300, remaining - schedule_budget)
    schedule_context = build_schedule_context(data, selected_med_id)
    if estimate_context_tokens(schedule_context) > schedule_budget:
        schedule_context = sanitize_text(schedule_context, max_chars=max(1800, schedule_budget * 4)) + "\n[Schedule context trimmed to protect the 4k-token window.]"
    recent_context = build_recent_assistant_context(
        list(data.get("assistant_history") or []),
        memory,
        token_budget=chat_budget,
    )
    user_text = "\n\n".join(
        [
            f"Assistant mode: {active_mode}",
            f"Context budget: target~{target_tokens} tokens, schedule_budget~{schedule_budget}, chat_budget~{chat_budget}. Sliding-window compaction is active.",
            schedule_context,
            recent_context,
            quantum_context.get("assistant_prompt_block", ""),
            prompt_block,
            final_instruction,
        ]
    )
    inference_backend = settings.get("inference_backend", "Auto")
    if on_delta is not None:
        reply, _streamed = litert_chat_streaming(
            key,
            user_text,
            system_text=system_text,
            native_image_input=False,
            inference_backend=inference_backend,
            on_delta=on_delta,
        )
        return reply

    return litert_chat_blocking(
        key,
        user_text,
        system_text=system_text,
        native_image_input=False,
        inference_backend=inference_backend,
    )


def extract_json_object(text: str) -> Dict[str, Any]:
    candidate = sanitize_text(text, max_chars=12000)
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        candidate = candidate.replace("json\n", "", 1).strip()
    try:
        loaded = json.loads(candidate)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        pass
    match = JSON_BLOCK_RE.search(candidate)
    if not match:
        return {}
    try:
        loaded = json.loads(match.group(0))
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        return {}


def normalize_photo_payload(raw_payload: Dict[str, Any], image_name: str, risk_packet: Dict[str, Any]) -> Dict[str, Any]:
    name = sanitize_text(
        raw_payload.get("name")
        or raw_payload.get("medication_name")
        or raw_payload.get("medicine")
        or "",
        max_chars=140,
    )
    schedule_text = sanitize_text(
        raw_payload.get("schedule_text") or raw_payload.get("directions") or raw_payload.get("label_schedule") or "",
        max_chars=240,
    )
    notes = sanitize_text(
        raw_payload.get("notes") or raw_payload.get("warnings") or raw_payload.get("caution") or "",
        max_chars=500,
    )
    source_text = " ".join(part for part in (name, schedule_text, notes) if part)
    dose_mg = max(0.0, safe_float(raw_payload.get("dose_mg") or raw_payload.get("strength_mg") or 0.0))
    if dose_mg <= 0:
        dose_mg = mg_from_text(source_text)
    interval_hours = max(0.0, safe_float(raw_payload.get("interval_hours") or 0.0))
    if interval_hours <= 0:
        interval_hours = infer_interval_from_text(source_text)
    max_daily_mg = max(0.0, safe_float(raw_payload.get("max_daily_mg") or 0.0))
    if max_daily_mg <= 0:
        max_daily_mg = infer_max_daily_mg(source_text, dose_mg)
    confidence = safe_float(raw_payload.get("confidence") or raw_payload.get("score") or 0.0)
    if confidence > 1.0 and confidence <= 100.0:
        confidence /= 100.0
    confidence = max(0.0, min(1.0, confidence))
    if not name:
        raise ValueError("The model could not confidently read a medication name from that photo.")
    if not schedule_text:
        schedule_text = "Imported from bottle photo. Review directions before relying on it."
    risk_fields = resolve_medication_review_risk(
        normalize_risk_fields(raw_payload, {"risk_score": 0.0, "risk_level": "", "risk_summary": ""}),
        name=name,
        dose_mg=dose_mg,
        interval_hours=interval_hours,
        max_daily_mg=max_daily_mg,
        schedule_text=schedule_text,
        notes=notes,
        confidence=confidence,
    )
    return {
        "name": name,
        "dose_mg": dose_mg,
        "interval_hours": interval_hours,
        "max_daily_mg": max_daily_mg,
        "schedule_text": schedule_text,
        "notes": notes,
        "confidence": confidence,
        "source": "vision",
        "source_photo": sanitize_text(image_name, max_chars=180),
        "risk_score": risk_fields["risk_score"],
        "risk_level": risk_fields["risk_level"],
        "risk_summary": risk_fields["risk_summary"],
    }


def resolve_medication_review_risk(
    provided: Dict[str, Any],
    *,
    name: str,
    dose_mg: float,
    interval_hours: float,
    max_daily_mg: float,
    schedule_text: str,
    notes: str,
    confidence: float,
) -> Dict[str, Any]:
    issues: List[str] = []
    derived_score = 0.0
    clarity_text = " ".join((schedule_text, notes, sanitize_text(provided.get("risk_summary") or "", max_chars=260))).lower()
    has_named_slots = bool(infer_named_dose_slots(schedule_text))
    mentions_daily_limit = any(
        phrase in clarity_text
        for phrase in ("24 hour", "24-hour", "24hr", "24 hr", "max", "maximum", "do not exceed", "not more than", "no more than")
    )

    if any(token in clarity_text for token in ("blur", "blurry", "unclear", "cut off", "cropped", "partial", "hidden", "illegible", "conflict", "confusing")):
        derived_score += 35.0
        issues.append("parts of the label may be hard to read")
    if not name:
        derived_score += 45.0
        issues.append("the medication name was unclear")
    if dose_mg <= 0:
        derived_score += 20.0
        issues.append("dose strength needs a manual check")
    if not schedule_text:
        derived_score += 25.0
        issues.append("directions were not clearly extracted")
    if interval_hours <= 0 and not has_named_slots:
        derived_score += 15.0
        issues.append("timing directions still need manual review")
    if max_daily_mg <= 0 and mentions_daily_limit:
        derived_score += 20.0
        issues.append("the 24-hour limit may not have been read correctly")
    if confidence <= 0.0:
        derived_score += 20.0
        issues.append("model confidence was unavailable")
    elif confidence < 0.55:
        derived_score += 40.0
        issues.append("the extraction confidence was low")
    elif confidence < 0.75:
        derived_score += 15.0
        issues.append("some fields may still need a manual re-check")

    explicit_score = max(0.0, min(100.0, safe_float(provided.get("risk_score"))))
    explicit_level = sanitize_text(provided.get("risk_level") or "", max_chars=24)
    explicit_summary = sanitize_text(provided.get("risk_summary") or "", max_chars=260)
    if explicit_level == "Low":
        explicit_score = max(explicit_score, 18.0)
    elif explicit_level == "Medium":
        explicit_score = max(explicit_score, 55.0)
    elif explicit_level == "High":
        explicit_score = max(explicit_score, 80.0)

    if explicit_score > 0:
        derived_score = max(derived_score, explicit_score)
    elif not issues:
        derived_score = 18.0 if confidence >= 0.85 and name and (dose_mg > 0 or schedule_text) else 35.0

    derived_score = max(0.0, min(100.0, derived_score))
    level = risk_level_from_score(derived_score)
    if not explicit_summary:
        if issues:
            explicit_summary = sanitize_text("; ".join(issues[:2]).capitalize() + ".", max_chars=260)
        elif level == "Low":
            explicit_summary = "Visible label details looked consistent, but compare the saved schedule with the bottle once before relying on it."
        else:
            explicit_summary = "Review the bottle directions manually before relying on this imported schedule."

    return {
        "risk_score": derived_score,
        "risk_level": level,
        "risk_summary": explicit_summary,
    }


def analyze_medication_image(key: bytes, image_path: Path, settings: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    risk_packet = build_quantum_risk_packet(
        "medication_label",
        "medicine bottle import review for visible label text and schedule extraction",
    )
    system_text = (
        "You are a medication label extraction assistant.\n"
        "Read only visible label text from the provided medicine bottle or box image.\n"
        "Do not fill in dose timing or safety limits from general medical knowledge.\n"
        "Use only visible text from the image.\n"
        "If text is blurry, cut off, or conflicting, keep unclear numeric fields as 0 and raise the review risk instead of guessing.\n"
        "Return raw JSON only.\n"
        "If something is unclear, keep the field conservative instead of inventing details."
    )
    prompt = (
        "Extract the medication schedule from this image.\n"
        "Return JSON with exactly these keys:\n"
        "{"
        '"name":"",'
        '"dose_mg":0,'
        '"interval_hours":0,'
        '"max_daily_mg":0,'
        '"schedule_text":"",'
        '"notes":"",'
        '"confidence":0,'
        '"risk_score":0,'
        '"risk_level":"",'
        '"risk_summary":""'
        "}\n"
        "Rules:\n"
        "- Use numbers only for numeric fields.\n"
        "- Use 0 when the label does not clearly show a value.\n"
        "- If the label says a range like every 4-6 hours, use the minimum interval.\n"
        "- If the label says no more than 4 doses in 24 hours and the dose strength is visible, convert that to max_daily_mg.\n"
        "- Put PRN, take-with-food, tablet-count, or warning notes into notes.\n"
        "- risk_score is 0-100 for how cautiously the user should manually review this extraction before relying on it.\n"
        "- Base the risk only on label clarity and extraction completeness, not on whether the medication itself is dangerous.\n"
        "- Low means the name and key schedule details are clearly visible and internally consistent.\n"
        "- Medium means at least one important field needed partial reading, inference, or a manual re-check.\n"
        "- High means the name, dose, interval, or 24-hour limit is blurry, cut off, conflicting, or missing.\n"
        "- risk_level must be exactly Low, Medium, or High.\n"
        "- risk_summary should be one short sentence about what needs verification.\n"
        "- Never output markdown fences or commentary."
    )
    raw = litert_chat_blocking(
        key,
        prompt,
        system_text=system_text,
        image_path=str(validate_image_path(image_path)),
        native_image_input=bool(settings.get("enable_native_image_input", True)),
        inference_backend=settings.get("inference_backend", "Auto"),
    )
    payload = normalize_photo_payload(extract_json_object(raw), image_path.name, risk_packet)
    return payload, raw


def merge_notes(existing: str, incoming: str) -> str:
    clean_existing = sanitize_text(existing, max_chars=500)
    clean_incoming = sanitize_text(incoming, max_chars=500)
    if not clean_existing:
        return clean_incoming
    if not clean_incoming or clean_incoming in clean_existing:
        return clean_existing
    return f"{clean_existing}\n{clean_incoming}"


def apply_vision_payload(
    data: Dict[str, Any],
    payload: Dict[str, Any],
    *,
    selected_med_id: Optional[str] = None,
) -> Tuple[Dict[str, Any], str, bool]:
    updated = ensure_vault_shape(data)
    meds = list(updated.get("meds") or [])
    target_id = selected_or_matching_med_id(updated, payload["name"], selected_med_id)
    created = False
    med_id = target_id or uuid.uuid4().hex[:12]
    for med in meds:
        if str(med.get("id")) != med_id:
            continue
        med["name"] = payload["name"]
        if payload["dose_mg"] > 0:
            med["dose_mg"] = payload["dose_mg"]
        if payload["interval_hours"] > 0:
            med["interval_hours"] = payload["interval_hours"]
        if payload["max_daily_mg"] > 0:
            med["max_daily_mg"] = payload["max_daily_mg"]
        med["schedule_text"] = payload["schedule_text"] or med.get("schedule_text", "")
        med["notes"] = merge_notes(str(med.get("notes") or ""), payload.get("notes", ""))
        med["source"] = "vision"
        med["source_photo"] = payload.get("source_photo", "")
        break
    else:
        created = True
        meds.append(
            {
                "id": med_id,
                "name": payload["name"],
                "dose_mg": max(0.0, safe_float(payload.get("dose_mg"))),
                "interval_hours": max(0.0, safe_float(payload.get("interval_hours"))),
                "max_daily_mg": max(0.0, safe_float(payload.get("max_daily_mg"))),
                "created_ts": time.time(),
                "first_dose_time": "",
                "custom_times_text": "",
                "schedule_text": payload.get("schedule_text", ""),
                "notes": payload.get("notes", ""),
                "source": "vision",
                "source_photo": payload.get("source_photo", ""),
                "last_taken_ts": 0.0,
                "history": [],
            }
        )
    updated["meds"] = meds
    updated["vision_imports"] = list(updated.get("vision_imports") or []) + [
        {
            "timestamp": time.time(),
            "image_name": payload.get("source_photo", ""),
            "med_id": med_id,
            "summary": "{name} | {dose:g}mg | every {interval:g}h".format(
                name=payload["name"],
                dose=max(0.0, safe_float(payload.get("dose_mg"))),
                interval=max(0.0, safe_float(payload.get("interval_hours"))),
            ),
            "risk_score": max(0.0, min(100.0, safe_float(payload.get("risk_score")))),
            "risk_level": normalized_risk_level_text(payload.get("risk_level") or "", safe_float(payload.get("risk_score"))),
            "risk_summary": sanitize_text(payload.get("risk_summary") or "", max_chars=260),
        }
    ]
    updated["vision_imports"] = updated["vision_imports"][-16:]
    return updated, med_id, created


def normalize_dental_hygiene_payload(
    raw_payload: Dict[str, Any],
    image_name: str,
    risk_packet: Dict[str, Any],
) -> Dict[str, Any]:
    score = safe_float(raw_payload.get("hygiene_score") or raw_payload.get("score") or 0.0)
    if 0.0 < score <= 1.0:
        score *= 100.0
    score = max(0.0, min(100.0, score))
    rating = sanitize_text(raw_payload.get("rating") or raw_payload.get("grade") or "", max_chars=80)
    if not rating:
        rating = dental_rating_from_score(score)
    summary = sanitize_text(
        raw_payload.get("visible_signs") or raw_payload.get("summary") or raw_payload.get("findings") or "",
        max_chars=500,
    )
    suggestions = sanitize_text(
        raw_payload.get("suggestions") or raw_payload.get("care_suggestions") or raw_payload.get("advice") or "",
        max_chars=700,
    )
    warning_flags = sanitize_text(
        raw_payload.get("warning_flags") or raw_payload.get("red_flags") or "",
        max_chars=400,
    )
    confidence = safe_float(raw_payload.get("confidence") or raw_payload.get("score_confidence") or 0.0)
    if confidence > 1.0 and confidence <= 100.0:
        confidence /= 100.0
    confidence = max(0.0, min(1.0, confidence))
    risk_fields = normalize_risk_fields(raw_payload, risk_packet)
    return {
        "score": score,
        "rating": rating,
        "summary": summary or "Review the photo manually; the model did not provide a clear hygiene summary.",
        "suggestions": suggestions or "Brush gently for two minutes, floss carefully, and stay consistent with your routine.",
        "warning_flags": warning_flags,
        "confidence": confidence,
        "source_photo": sanitize_text(image_name, max_chars=180),
        "risk_score": risk_fields["risk_score"],
        "risk_level": risk_fields["risk_level"],
        "risk_summary": risk_fields["risk_summary"],
    }


def analyze_dental_hygiene_image(key: bytes, image_path: Path, settings: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    risk_packet = build_quantum_risk_packet(
        "dental_hygiene",
        "teeth and mouth hygiene photo review with visible-cleanliness scoring",
    )
    system_text = (
        "You are a dental hygiene photo reviewer.\n"
        "Use only visible evidence from the image.\n"
        "Do not diagnose disease or claim certainty.\n"
        "Give general hygiene coaching, not medical treatment advice.\n"
        "Use the provided quantum risk simulation as a conservative follow-up prior only.\n"
        "Visible image evidence is more important than the prior.\n"
        "Return raw JSON only."
    )
    prompt = (
        "Review this mouth or teeth photo and rate visible dental hygiene.\n"
        f"{risk_packet['prompt_block']}\n"
        "Return JSON with exactly these keys:\n"
        "{"
        '"hygiene_score":0,'
        '"rating":"",'
        '"visible_signs":"",'
        '"suggestions":"",'
        '"warning_flags":"",'
        '"confidence":0,'
        '"risk_score":0,'
        '"risk_level":"",'
        '"risk_summary":""'
        "}\n"
        "Rules:\n"
        "- hygiene_score is 0-100 based only on visible cleanliness and gum appearance.\n"
        "- warning_flags should mention only clearly visible concerns or 'none'.\n"
        "- suggestions should be gentle hygiene coaching, not diagnosis.\n"
        "- risk_score is 0-100 for how strongly the visible photo suggests closer follow-up or extra care, not diagnosis.\n"
        "- risk_level must be exactly Low, Medium, or High.\n"
        "- risk_summary should be one short sentence about the caution level.\n"
        "- never output markdown fences or extra commentary."
    )
    raw = litert_chat_blocking(
        key,
        prompt,
        system_text=system_text,
        image_path=str(validate_image_path(image_path)),
        native_image_input=bool(settings.get("enable_native_image_input", True)),
        inference_backend=settings.get("inference_backend", "Auto"),
    )
    return normalize_dental_hygiene_payload(extract_json_object(raw), image_path.name, risk_packet), raw


def apply_dental_hygiene_payload(data: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    updated = ensure_vault_shape(data)
    hygiene = dict(updated.get("dental_hygiene") or dental_hygiene_defaults())
    hygiene["latest_score"] = payload["score"]
    hygiene["latest_rating"] = payload["rating"]
    hygiene["latest_summary"] = payload["summary"]
    hygiene["latest_suggestions"] = payload["suggestions"]
    hygiene["latest_warning_flags"] = payload["warning_flags"]
    hygiene["latest_risk_score"] = payload["risk_score"]
    hygiene["latest_risk_level"] = payload["risk_level"]
    hygiene["latest_risk_summary"] = payload["risk_summary"]
    hygiene["latest_photo"] = payload["source_photo"]
    hygiene["latest_timestamp"] = time.time()
    hygiene["history"] = list(hygiene.get("history") or []) + [
        {
            "timestamp": hygiene["latest_timestamp"],
            "image_name": payload["source_photo"],
            "score": payload["score"],
            "rating": payload["rating"],
            "summary": payload["summary"],
            "suggestions": payload["suggestions"],
            "warning_flags": payload["warning_flags"],
            "confidence": payload["confidence"],
            "risk_score": payload["risk_score"],
            "risk_level": payload["risk_level"],
            "risk_summary": payload["risk_summary"],
        }
    ]
    hygiene["history"] = hygiene["history"][-20:]
    updated["dental_hygiene"] = hygiene
    return updated


def normalize_dental_recovery_payload(
    raw_payload: Dict[str, Any],
    image_name: str,
    recovery_state: Dict[str, Any],
    risk_packet: Dict[str, Any],
) -> Dict[str, Any]:
    score = safe_float(raw_payload.get("recovery_score") or raw_payload.get("healing_score") or 0.0)
    if 0.0 < score <= 1.0:
        score *= 100.0
    score = max(0.0, min(100.0, score))
    status = sanitize_text(
        raw_payload.get("status") or raw_payload.get("healing_status") or raw_payload.get("rating") or "",
        max_chars=120,
    )
    summary = sanitize_text(
        raw_payload.get("healing_summary") or raw_payload.get("summary") or raw_payload.get("visible_signs") or "",
        max_chars=700,
    )
    advice = sanitize_text(
        raw_payload.get("care_suggestions") or raw_payload.get("advice") or raw_payload.get("care_advice") or "",
        max_chars=900,
    )
    warning_flags = sanitize_text(
        raw_payload.get("warning_flags") or raw_payload.get("red_flags") or raw_payload.get("urgent_flags") or "",
        max_chars=420,
    )
    confidence = safe_float(raw_payload.get("confidence") or 0.0)
    if confidence > 1.0 and confidence <= 100.0:
        confidence /= 100.0
    confidence = max(0.0, min(1.0, confidence))
    risk_fields = normalize_risk_fields(raw_payload, risk_packet)
    day_number = (days_since_date_string(str(recovery_state.get("procedure_date") or "")) or 0) + 1
    if not status:
        if score >= 80:
            status = "Looks steady"
        elif score >= 55:
            status = "Monitor closely"
        elif score > 0:
            status = "Needs dentist review"
        else:
            status = "Needs manual review"
    return {
        "score": score,
        "status": status,
        "summary": summary or "Review the photo manually; the model did not provide a clear healing summary.",
        "advice": advice or "Follow your dentist's aftercare directions and reach out if symptoms feel worse instead of better.",
        "warning_flags": warning_flags,
        "confidence": confidence,
        "day_number": day_number,
        "source_photo": sanitize_text(image_name, max_chars=180),
        "risk_score": risk_fields["risk_score"],
        "risk_level": risk_fields["risk_level"],
        "risk_summary": risk_fields["risk_summary"],
    }


def analyze_dental_recovery_image(
    key: bytes,
    image_path: Path,
    settings: Dict[str, Any],
    recovery_state: Dict[str, Any],
) -> Tuple[Dict[str, Any], str]:
    days_since = days_since_date_string(str(recovery_state.get("procedure_date") or ""))
    day_text = f"day {days_since + 1}" if days_since is not None else "an unknown day"
    risk_packet = build_quantum_risk_packet(
        "dental_recovery",
        "\n".join(
            [
                sanitize_text(recovery_state.get("procedure_type") or "unknown procedure", max_chars=120),
                sanitize_text(recovery_state.get("procedure_date") or "unknown date", max_chars=20),
                sanitize_text(recovery_state.get("symptom_notes") or "no symptom notes", max_chars=400),
                sanitize_text(recovery_state.get("care_notes") or "no care notes", max_chars=400),
            ]
        ),
    )
    system_text = (
        "You are a dental recovery photo reviewer.\n"
        "Use only visible evidence plus the provided procedure context.\n"
        "Do not diagnose or replace a dentist.\n"
        "Give general, conservative aftercare suggestions and clearly call out warning signs that deserve professional follow-up.\n"
        "Use the provided quantum risk simulation as a conservative follow-up prior only.\n"
        "Visible evidence and the user's recovery notes are more important than the prior.\n"
        "Return raw JSON only."
    )
    prompt = (
        "Review this dental recovery photo.\n"
        f"Procedure type: {sanitize_text(recovery_state.get('procedure_type') or 'unknown', max_chars=120)}\n"
        f"Procedure date: {sanitize_text(recovery_state.get('procedure_date') or 'unknown', max_chars=20)}\n"
        f"Days since procedure: {days_since if days_since is not None else 'unknown'}\n"
        f"Symptom notes: {sanitize_text(recovery_state.get('symptom_notes') or 'none', max_chars=300)}\n"
        f"Care notes: {sanitize_text(recovery_state.get('care_notes') or 'none', max_chars=300)}\n\n"
        f"{risk_packet['prompt_block']}\n"
        "Return JSON with exactly these keys:\n"
        "{"
        '"recovery_score":0,'
        '"status":"",'
        '"healing_summary":"",'
        '"care_suggestions":"",'
        '"warning_flags":"",'
        '"confidence":0,'
        '"risk_score":0,'
        '"risk_level":"",'
        '"risk_summary":""'
        "}\n"
        "Rules:\n"
        f"- evaluate only what is visible for {day_text}.\n"
        "- care_suggestions must stay general and conservative.\n"
        "- warning_flags should mention swelling, discharge, worsening redness, or other signs that should be checked by a dentist if clearly visible or consistent with the notes.\n"
        "- risk_score is 0-100 for how strongly the image and notes suggest closer follow-up or dentist contact, not diagnosis.\n"
        "- risk_level must be exactly Low, Medium, or High.\n"
        "- risk_summary should be one short sentence about the caution level.\n"
        "- never output markdown fences or extra commentary."
    )
    raw = litert_chat_blocking(
        key,
        prompt,
        system_text=system_text,
        image_path=str(validate_image_path(image_path)),
        native_image_input=bool(settings.get("enable_native_image_input", True)),
        inference_backend=settings.get("inference_backend", "Auto"),
    )
    return normalize_dental_recovery_payload(extract_json_object(raw), image_path.name, recovery_state, risk_packet), raw


def apply_dental_recovery_payload(data: Dict[str, Any], payload: Dict[str, Any], recovery_state: Dict[str, Any]) -> Dict[str, Any]:
    updated = ensure_vault_shape(data)
    recovery = dict(updated.get("dental_recovery") or dental_recovery_defaults())
    recovery["enabled"] = True
    recovery["procedure_type"] = sanitize_text(recovery_state.get("procedure_type") or recovery.get("procedure_type") or "", max_chars=120)
    recovery["procedure_date"] = sanitize_text(recovery_state.get("procedure_date") or recovery.get("procedure_date") or "", max_chars=20)
    recovery["symptom_notes"] = sanitize_text(recovery_state.get("symptom_notes") or recovery.get("symptom_notes") or "", max_chars=600)
    recovery["care_notes"] = sanitize_text(recovery_state.get("care_notes") or recovery.get("care_notes") or "", max_chars=600)
    recovery["latest_score"] = payload["score"]
    recovery["latest_status"] = payload["status"]
    recovery["latest_summary"] = payload["summary"]
    recovery["latest_advice"] = payload["advice"]
    recovery["latest_warning_flags"] = payload["warning_flags"]
    recovery["latest_risk_score"] = payload["risk_score"]
    recovery["latest_risk_level"] = payload["risk_level"]
    recovery["latest_risk_summary"] = payload["risk_summary"]
    recovery["latest_photo"] = payload["source_photo"]
    recovery["latest_timestamp"] = time.time()
    recovery["daily_logs"] = list(recovery.get("daily_logs") or []) + [
        {
            "timestamp": recovery["latest_timestamp"],
            "image_name": payload["source_photo"],
            "day_number": payload["day_number"],
            "score": payload["score"],
            "status": payload["status"],
            "summary": payload["summary"],
            "advice": payload["advice"],
            "warning_flags": payload["warning_flags"],
            "confidence": payload["confidence"],
            "risk_score": payload["risk_score"],
            "risk_level": payload["risk_level"],
            "risk_summary": payload["risk_summary"],
        }
    ]
    recovery["daily_logs"] = recovery["daily_logs"][-30:]
    updated["dental_recovery"] = recovery
    return updated


def warning_text_needs_attention(text: str) -> bool:
    lowered = sanitize_text(text, max_chars=300).lower()
    if not lowered or lowered in {"none", "none.", "none clearly visible", "no obvious warning flags"}:
        return False
    return any(token in lowered for token in ("warning", "urgent", "call", "dentist", "swelling", "pus", "bleeding", "infection", "review"))


class BackgroundGradient(Widget):
    top_color = ListProperty([0.08, 0.11, 0.10, 1])
    bottom_color = ListProperty([0.03, 0.04, 0.07, 1])
    steps = NumericProperty(40)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, top_color=self._redraw, bottom_color=self._redraw, steps=self._redraw)

    def _redraw(self, *_args):
        self.canvas.before.clear()
        x, y = self.pos
        width, height = self.size
        steps = max(8, int(self.steps))
        with self.canvas.before:
            for index in range(steps):
                ratio = index / max(1, steps - 1)
                r = self.top_color[0] + (self.bottom_color[0] - self.top_color[0]) * ratio
                g = self.top_color[1] + (self.bottom_color[1] - self.top_color[1]) * ratio
                b = self.top_color[2] + (self.bottom_color[2] - self.top_color[2]) * ratio
                a = self.top_color[3] + (self.bottom_color[3] - self.top_color[3]) * ratio
                Color(r, g, b, a)
                Rectangle(pos=(x, y + (height * index / steps)), size=(width, height / steps + 1))


class GlassCard(Widget):
    radius = NumericProperty(dp(24))
    fill = ListProperty([1, 1, 1, 0.055])
    border = ListProperty([1, 1, 1, 0.14])
    highlight = ListProperty([1, 1, 1, 0.07])
    shine_x = NumericProperty(0.0)
    shine_alpha = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            pos=self._redraw,
            size=self._redraw,
            radius=self._redraw,
            fill=self._redraw,
            border=self._redraw,
            highlight=self._redraw,
            shine_x=self._redraw,
            shine_alpha=self._redraw,
        )
        Clock.schedule_once(lambda _dt: self._start_animation(), 0.2)

    def _start_animation(self):
        self.shine_x = -0.3
        self.shine_alpha = 0.0
        loop = (
            (Animation(shine_alpha=0.18, duration=0.35, t="out_quad") & Animation(shine_x=1.25, duration=1.0, t="out_cubic"))
            + Animation(shine_alpha=0.0, duration=0.35, t="out_quad")
        )
        loop.repeat = True
        loop.start(self)

    def _redraw(self, *_args):
        self.canvas.clear()
        x, y = self.pos
        width, height = self.size
        radius = float(self.radius)
        with self.canvas:
            Color(0, 0, 0, 0.18)
            RoundedRectangle(pos=(x, y - dp(2)), size=(width, height + dp(3)), radius=[radius])
            Color(*self.fill)
            RoundedRectangle(pos=(x, y), size=(width, height), radius=[radius])
            Color(*self.highlight)
            RoundedRectangle(pos=(x + dp(1), y + height * 0.55), size=(width - dp(2), height * 0.45), radius=[radius])
            Color(*self.border)
            Line(rounded_rectangle=[x, y, width, height, radius], width=dp(1.1))
            if self.shine_alpha > 0.001:
                Color(1, 1, 1, self.shine_alpha)
                Rectangle(pos=(x + width * self.shine_x, y), size=(width * 0.18, height))


class GradientButton(MDRaisedButton):
    start_color = ListProperty([0.15, 0.70, 0.48, 1])
    end_color = ListProperty([0.18, 0.45, 0.95, 1])
    border_color = ListProperty([1, 1, 1, 0.14])
    border_width = NumericProperty(dp(1.0))
    radius = NumericProperty(dp(18))
    steps = NumericProperty(24)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0, 0, 0, 0)
        self.elevation = 0
        self.bind(
            pos=self._redraw,
            size=self._redraw,
            start_color=self._redraw,
            end_color=self._redraw,
            border_color=self._redraw,
            border_width=self._redraw,
            radius=self._redraw,
            steps=self._redraw,
        )
        Clock.schedule_once(lambda _dt: self._redraw(), 0)

    def _build_gradient_texture(self) -> Texture:
        steps = max(2, int(self.steps))
        buffer = bytearray()
        for index in range(steps):
            ratio = index / max(1, steps - 1)
            r = self.start_color[0] + (self.end_color[0] - self.start_color[0]) * ratio
            g = self.start_color[1] + (self.end_color[1] - self.start_color[1]) * ratio
            b = self.start_color[2] + (self.end_color[2] - self.start_color[2]) * ratio
            a = self.start_color[3] + (self.end_color[3] - self.start_color[3]) * ratio
            buffer.extend([int(255 * r), int(255 * g), int(255 * b), int(255 * a)])
        texture = Texture.create(size=(1, steps), colorfmt="rgba")
        texture.blit_buffer(bytes(buffer), colorfmt="rgba", bufferfmt="ubyte")
        texture.wrap = "repeat"
        texture.mag_filter = "linear"
        texture.min_filter = "linear"
        return texture

    def _redraw(self, *_args):
        self.canvas.before.clear()
        if self.width <= 0 or self.height <= 0:
            return
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius],
                texture=self._build_gradient_texture(),
            )
            Color(*self.border_color)
            Line(rounded_rectangle=[self.x, self.y, self.width, self.height, self.radius], width=self.border_width)


class DoseWheel(Widget):
    value = NumericProperty(0.5)
    level = StringProperty("MEDIUM")
    sweep = NumericProperty(0.0)
    glow = NumericProperty(0.25)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, value=self._redraw, level=self._redraw, sweep=self._redraw, glow=self._redraw)
        Clock.schedule_once(lambda _dt: self._start_animation(), 0.05)

    def _start_animation(self):
        sweep = Animation(sweep=1.0, duration=2.1, t="linear")
        sweep.repeat = True
        sweep.start(self)
        glow = Animation(glow=0.42, duration=0.9, t="in_out_quad") + Animation(glow=0.22, duration=0.9, t="in_out_quad")
        glow.repeat = True
        glow.start(self)

    def set_level(self, level: str):
        text = sanitize_text(level, max_chars=16).upper()
        if text.startswith("LOW"):
            target = 0.0
            self.level = "LOW"
        elif text.startswith("HIGH"):
            target = 1.0
            self.level = "HIGH"
        else:
            target = 0.5
            self.level = "MEDIUM"
        Animation.cancel_all(self, "value")
        Animation(value=target, duration=0.45, t="out_cubic").start(self)

    def _level_color(self) -> Tuple[float, float, float]:
        if self.level == "LOW":
            return (0.12, 0.90, 0.48)
        if self.level == "HIGH":
            return (0.98, 0.26, 0.34)
        return (0.98, 0.78, 0.24)

    def _redraw(self, *_args):
        self.canvas.clear()
        center_x, center_y = self.center
        radius = min(self.width, self.height) * 0.41
        thickness = max(dp(12), radius * 0.16)
        active = self._level_color()
        angle = -135.0 + 270.0 * float(self.value)
        angle_rad = math.radians(angle)
        sweep_angle = -135.0 + 270.0 * float(self.sweep)
        segments = [
            ("LOW", (0.12, 0.85, 0.45), -135.0, -45.0),
            ("MED", (0.98, 0.78, 0.24), -45.0, 45.0),
            ("HIGH", (0.98, 0.26, 0.34), 45.0, 135.0),
        ]
        with self.canvas:
            Color(1, 1, 1, 0.04)
            Line(circle=(center_x, center_y, radius + dp(10), -140, 140), width=dp(1.2))
            Color(0.08, 0.10, 0.14, 0.65)
            Line(circle=(center_x, center_y, radius, -140, 140), width=thickness, cap="round")
            for name, rgb, start, end in segments:
                boost = 1.0 + (0.85 * float(self.glow) if (self.level == "MEDIUM" and name == "MED") or self.level == name else 0.0)
                for spread in range(5, 0, -1):
                    Color(rgb[0], rgb[1], rgb[2], (0.05 + 0.03 * spread) * boost)
                    Line(circle=(center_x, center_y, radius, start + 3, end - 3), width=thickness + dp(2.4 * spread), cap="round")
                Color(rgb[0], rgb[1], rgb[2], 0.78)
                Line(circle=(center_x, center_y, radius, start + 3, end - 3), width=thickness, cap="round")
            Color(active[0], active[1], active[2], 0.25 + 0.18 * float(self.glow))
            Line(circle=(center_x, center_y, radius, sweep_angle - 8, sweep_angle + 8), width=thickness + dp(6), cap="round")
            needle_x = center_x + math.cos(angle_rad) * (radius * 0.92)
            needle_y = center_y + math.sin(angle_rad) * (radius * 0.92)
            Color(active[0], active[1], active[2], 0.18 + 0.18 * float(self.glow))
            Line(points=[center_x, center_y, needle_x, needle_y], width=max(dp(3.2), thickness * 0.16), cap="round")
            Color(0.97, 0.98, 0.99, 0.98)
            Line(points=[center_x, center_y, needle_x, needle_y], width=max(dp(2), thickness * 0.10), cap="round")
            Color(0.06, 0.08, 0.10, 0.9)
            RoundedRectangle(pos=(center_x - dp(12), center_y - dp(12)), size=(dp(24), dp(24)), radius=[dp(12)])
            Color(1, 1, 1, 0.18)
            Line(rounded_rectangle=[center_x - dp(18), center_y - dp(18), dp(36), dp(36), dp(18)], width=dp(1.0))


KV = r"""
<BackgroundGradient>:
    size_hint: 1, 1
<GlassCard>:
    size_hint: 1, None
<GradientButton>:
    text_color: 0.98, 0.99, 1, 1
<DoseWheel>:
    size_hint: None, None

MDScreen:
    BackgroundGradient:
        top_color: 0.08, 0.11, 0.10, 1
        bottom_color: 0.03, 0.04, 0.07, 1

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "MedSafe"
            md_bg_color: 0.04, 0.06, 0.08, 0.98
            specific_text_color: 0.95, 0.98, 0.99, 1
            left_action_items: [["heart-pulse", lambda x: None]]
            right_action_items: [["refresh", lambda x: app.refresh_from_disk()]]

        MDLabel:
            id: status_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.78, 0.88, 0.85, 1
            halign: "center"
            size_hint_y: None
            height: "28dp"

        MDBottomNavigation:
            id: bottom_nav
            panel_color: 0.05, 0.07, 0.09, 0.98

            MDBottomNavigationItem:
                name: "today"
                text: "Today"
                icon: "clock-outline"

                ScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "12dp"
                        padding: "12dp"
                        size_hint_y: None
                        height: self.minimum_height

                        FloatLayout:
                            size_hint_y: None
                            height: "330dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(28)
                                fill: 1, 1, 1, 0.055
                                border: 0.65, 0.98, 0.82, 0.16
                                highlight: 1, 1, 1, 0.08

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "12dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Dose Safety Pulse"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    font_style: "H6"
                                    size_hint_y: None
                                    height: "30dp"

                                MDLabel:
                                    id: dashboard_selection
                                    text: "Select a medication to log doses."
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    size_hint_y: None
                                    height: "24dp"

                                MDBoxLayout:
                                    spacing: "10dp"
                                    size_hint_y: None
                                    height: "182dp"

                                    DoseWheel:
                                        id: dose_wheel
                                        size: "190dp", "190dp"

                                    MDBoxLayout:
                                        orientation: "vertical"
                                        spacing: "8dp"

                                        MDLabel:
                                            id: dashboard_risk_title
                                            text: "Awaiting check"
                                            theme_text_color: "Custom"
                                            text_color: 0.96, 0.99, 0.98, 1
                                            bold: True
                                            font_style: "H5"
                                            size_hint_y: None
                                            height: "38dp"

                                        MDLabel:
                                            id: dashboard_risk_caption
                                            text: "Log a selected dose to score timing and daily totals."
                                            theme_text_color: "Custom"
                                            text_color: 0.79, 0.88, 0.86, 1
                                            text_size: self.width, None
                                            size_hint_y: None
                                            height: self.texture_size[1]

                                        MDLabel:
                                            text: "Due now"
                                            theme_text_color: "Custom"
                                            text_color: 0.67, 0.80, 0.78, 1
                                            size_hint_y: None
                                            height: "20dp"

                                        MDLabel:
                                            id: today_due_count
                                            text: "0 meds"
                                            theme_text_color: "Custom"
                                            text_color: 0.96, 0.99, 0.98, 1
                                            bold: True
                                            size_hint_y: None
                                            height: "28dp"

                                        MDLabel:
                                            text: "Next dose"
                                            theme_text_color: "Custom"
                                            text_color: 0.67, 0.80, 0.78, 1
                                            size_hint_y: None
                                            height: "20dp"

                                        MDLabel:
                                            id: today_next_due
                                            text: "No schedule yet"
                                            theme_text_color: "Custom"
                                            text_color: 0.96, 0.99, 0.98, 1
                                            bold: True
                                            text_size: self.width, None
                                            size_hint_y: None
                                            height: self.texture_size[1]

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Log Selected Dose"
                                        on_release: app.on_log_dose()

                                    GradientButton:
                                        text: "Take Bottle Photo"
                                        start_color: 0.18, 0.56, 0.94, 1
                                        end_color: 0.12, 0.35, 0.68, 1
                                        on_release: app.on_take_bottle_photo()

                                    GradientButton:
                                        text: "Refresh"
                                        start_color: 0.19, 0.79, 0.58, 1
                                        end_color: 0.12, 0.46, 0.34, 1
                                        on_release: app.refresh_from_disk()

                                MDLabel:
                                    id: dashboard_model_state
                                    text: "Model: not downloaded yet"
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    size_hint_y: None
                                    height: "24dp"

                        FloatLayout:
                            size_hint_y: None
                            height: "250dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(24)
                                fill: 1, 1, 1, 0.05
                                border: 1, 1, 1, 0.11
                                highlight: 1, 1, 1, 0.06

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Schedule Lineup"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    size_hint_y: None
                                    height: "28dp"

                                MDLabel:
                                    id: today_timeline
                                    text: "No medications yet."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                        FloatLayout:
                            size_hint_y: None
                            height: "250dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(24)
                                fill: 1, 1, 1, 0.05
                                border: 1, 1, 1, 0.11
                                highlight: 1, 1, 1, 0.06

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Selected Medication"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    size_hint_y: None
                                    height: "28dp"

                                MDLabel:
                                    id: selected_med_summary
                                    text: "No medication selected."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: selected_med_history
                                    text: "Select a medication to see recent logs."
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

            MDBottomNavigationItem:
                name: "schedule"
                text: "Schedule"
                icon: "format-list-bulleted-square"

                ScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "12dp"
                        padding: "12dp"
                        size_hint_y: None
                        height: self.minimum_height

                        FloatLayout:
                            size_hint_y: None
                            height: "540dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(28)
                                fill: 1, 1, 1, 0.055
                                border: 1, 1, 1, 0.12
                                highlight: 1, 1, 1, 0.07

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Medication Editor"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    font_style: "H6"
                                    size_hint_y: None
                                    height: "30dp"

                                MDLabel:
                                    id: form_selection
                                    text: "Creating a new medication"
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    size_hint_y: None
                                    height: "24dp"

                                MDTextField:
                                    id: med_name
                                    hint_text: "Medication name"
                                    mode: "fill"
                                    fill_color: 1, 1, 1, 0.06

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "82dp"

                                    MDTextField:
                                        id: dose_mg
                                        hint_text: "Dose (mg)"
                                        mode: "fill"
                                        input_filter: "float"
                                        fill_color: 1, 1, 1, 0.06

                                    MDTextField:
                                        id: interval_h
                                        hint_text: "Interval (hours)"
                                        mode: "fill"
                                        input_filter: "float"
                                        fill_color: 1, 1, 1, 0.06

                                    MDTextField:
                                        id: max_daily
                                        hint_text: "Max daily (mg)"
                                        mode: "fill"
                                        input_filter: "float"
                                        fill_color: 1, 1, 1, 0.06

                                MDTextField:
                                    id: schedule_text
                                    hint_text: "Bottle directions or reminder note"
                                    mode: "fill"
                                    multiline: True
                                    fill_color: 1, 1, 1, 0.06

                                MDTextField:
                                    id: med_notes
                                    hint_text: "Notes"
                                    mode: "fill"
                                    multiline: True
                                    fill_color: 1, 1, 1, 0.06

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Save / Update"
                                        on_release: app.on_save_med()

                                    GradientButton:
                                        text: "New"
                                        start_color: 0.18, 0.56, 0.94, 1
                                        end_color: 0.12, 0.35, 0.68, 1
                                        on_release: app.on_new_med()

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Log Dose Now"
                                        start_color: 0.19, 0.79, 0.58, 1
                                        end_color: 0.12, 0.46, 0.34, 1
                                        on_release: app.on_log_dose()

                                    GradientButton:
                                        text: "Delete"
                                        start_color: 0.94, 0.42, 0.38, 1
                                        end_color: 0.71, 0.21, 0.22, 1
                                        on_release: app.on_delete_med()

                                MDLabel:
                                    id: form_schedule_preview
                                    text: "Saved schedules appear below."
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                        FloatLayout:
                            size_hint_y: None
                            height: "360dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(24)
                                fill: 1, 1, 1, 0.05
                                border: 1, 1, 1, 0.11
                                highlight: 1, 1, 1, 0.06

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Saved Medications"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    size_hint_y: None
                                    height: "28dp"

                                ScrollView:
                                    do_scroll_x: False

                                    MDList:
                                        id: med_list

            MDBottomNavigationItem:
                name: "vision"
                text: "Scanner"
                icon: "camera-outline"

                ScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "12dp"
                        padding: "12dp"
                        size_hint_y: None
                        height: self.minimum_height

                        FloatLayout:
                            size_hint_y: None
                            height: "300dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(28)
                                fill: 1, 1, 1, 0.055
                                border: 0.60, 0.79, 1.0, 0.16
                                highlight: 1, 1, 1, 0.08

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Bottle Photo Import"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    font_style: "H6"
                                    size_hint_y: None
                                    height: "30dp"

                                MDLabel:
                                    text: "Take a picture of a medicine bottle or choose an existing image. Gemma 4 will read the visible directions and add or update a schedule entry."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: vision_status
                                    text: "Ready for a bottle photo."
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: vision_last_file
                                    text: "Last image: none"
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    size_hint_y: None
                                    height: "24dp"

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Take Bottle Photo"
                                        start_color: 0.18, 0.56, 0.94, 1
                                        end_color: 0.12, 0.35, 0.68, 1
                                        on_release: app.on_take_bottle_photo()

                                    GradientButton:
                                        text: "Use Existing Photo"
                                        start_color: 0.19, 0.79, 0.58, 1
                                        end_color: 0.12, 0.46, 0.34, 1
                                        on_release: app.on_pick_bottle_photo()

                        FloatLayout:
                            size_hint_y: None
                            height: "330dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(24)
                                fill: 1, 1, 1, 0.05
                                border: 1, 1, 1, 0.11
                                highlight: 1, 1, 1, 0.06

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Latest Import"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    size_hint_y: None
                                    height: "28dp"

                                MDLabel:
                                    id: vision_result
                                    text: "No bottle photo processed yet."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

            MDBottomNavigationItem:
                name: "dental"
                text: "Dental"
                icon: "tooth-outline"

                ScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "12dp"
                        padding: "12dp"
                        size_hint_y: None
                        height: self.minimum_height

                        FloatLayout:
                            size_hint_y: None
                            height: "540dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(28)
                                fill: 1, 1, 1, 0.055
                                border: 0.88, 0.90, 0.42, 0.18
                                highlight: 1, 1, 1, 0.08

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Oral Care Studio"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    font_style: "H6"
                                    size_hint_y: None
                                    height: "30dp"

                                MDLabel:
                                    text: "A private LiteRT-LM dental dashboard for reminders, photo reviews, and recovery journaling."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: dental_overview_title
                                    text: "Dental studio ready"
                                    theme_text_color: "Custom"
                                    text_color: 0.98, 0.99, 1, 1
                                    bold: True
                                    font_style: "H5"
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: dental_overview_body
                                    text: "Keep the daily rhythm steady, use the vision coach when you want a check-in, and switch on recovery mode after dental work."
                                    theme_text_color: "Custom"
                                    text_color: 0.78, 0.88, 0.86, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                GridLayout:
                                    cols: 3
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "122dp"

                                    FloatLayout:
                                        GlassCard:
                                            pos: self.parent.pos
                                            size: self.parent.size
                                            radius: dp(22)
                                            fill: 1, 1, 1, 0.05
                                            border: 0.98, 0.83, 0.44, 0.20
                                            highlight: 1, 1, 1, 0.06

                                        MDBoxLayout:
                                            orientation: "vertical"
                                            padding: "14dp"
                                            spacing: "8dp"
                                            pos: self.parent.pos
                                            size: self.parent.size

                                            MDLabel:
                                                text: "Brush"
                                                theme_text_color: "Custom"
                                                text_color: 0.78, 0.88, 0.86, 1
                                                size_hint_y: None
                                                height: "22dp"

                                            MDLabel:
                                                id: dental_brush_status
                                                text: "Ready now"
                                                theme_text_color: "Custom"
                                                text_color: 1.00, 0.86, 0.50, 1
                                                bold: True
                                                size_hint_y: None
                                                height: "28dp"

                                            MDLabel:
                                                id: dental_brush_caption
                                                text: "Every 12h"
                                                theme_text_color: "Custom"
                                                text_color: 1.00, 0.93, 0.74, 1
                                                text_size: self.width, None
                                                size_hint_y: None
                                                height: self.texture_size[1]

                                    FloatLayout:
                                        GlassCard:
                                            pos: self.parent.pos
                                            size: self.parent.size
                                            radius: dp(22)
                                            fill: 1, 1, 1, 0.05
                                            border: 0.60, 0.84, 1.0, 0.20
                                            highlight: 1, 1, 1, 0.06

                                        MDBoxLayout:
                                            orientation: "vertical"
                                            padding: "14dp"
                                            spacing: "8dp"
                                            pos: self.parent.pos
                                            size: self.parent.size

                                            MDLabel:
                                                text: "Floss"
                                                theme_text_color: "Custom"
                                                text_color: 0.78, 0.88, 0.86, 1
                                                size_hint_y: None
                                                height: "22dp"

                                            MDLabel:
                                                id: dental_floss_status
                                                text: "Ready now"
                                                theme_text_color: "Custom"
                                                text_color: 0.70, 0.98, 0.84, 1
                                                bold: True
                                                size_hint_y: None
                                                height: "28dp"

                                            MDLabel:
                                                id: dental_floss_caption
                                                text: "Every 24h"
                                                theme_text_color: "Custom"
                                                text_color: 0.82, 0.96, 0.91, 1
                                                text_size: self.width, None
                                                size_hint_y: None
                                                height: self.texture_size[1]

                                    FloatLayout:
                                        GlassCard:
                                            pos: self.parent.pos
                                            size: self.parent.size
                                            radius: dp(22)
                                            fill: 1, 1, 1, 0.05
                                            border: 0.52, 0.94, 0.76, 0.20
                                            highlight: 1, 1, 1, 0.06

                                        MDBoxLayout:
                                            orientation: "vertical"
                                            padding: "14dp"
                                            spacing: "8dp"
                                            pos: self.parent.pos
                                            size: self.parent.size

                                            MDLabel:
                                                text: "Rinse"
                                                theme_text_color: "Custom"
                                                text_color: 0.78, 0.88, 0.86, 1
                                                size_hint_y: None
                                                height: "22dp"

                                            MDLabel:
                                                id: dental_rinse_status
                                                text: "Ready now"
                                                theme_text_color: "Custom"
                                                text_color: 0.70, 0.98, 0.84, 1
                                                bold: True
                                                size_hint_y: None
                                                height: "28dp"

                                            MDLabel:
                                                id: dental_rinse_caption
                                                text: "Every 24h"
                                                theme_text_color: "Custom"
                                                text_color: 0.82, 0.96, 0.91, 1
                                                text_size: self.width, None
                                                size_hint_y: None
                                                height: self.texture_size[1]

                                MDLabel:
                                    text: "Reminder rhythm (hours between routines)"
                                    theme_text_color: "Custom"
                                    text_color: 0.78, 0.88, 0.86, 1
                                    size_hint_y: None
                                    height: "22dp"

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "82dp"

                                    MDTextField:
                                        id: dental_brush_interval
                                        hint_text: "Brush"
                                        helper_text: "hours"
                                        helper_text_mode: "persistent"
                                        mode: "fill"
                                        input_filter: "float"
                                        fill_color: 1, 1, 1, 0.06

                                    MDTextField:
                                        id: dental_floss_interval
                                        hint_text: "Floss"
                                        helper_text: "hours"
                                        helper_text_mode: "persistent"
                                        mode: "fill"
                                        input_filter: "float"
                                        fill_color: 1, 1, 1, 0.06

                                    MDTextField:
                                        id: dental_rinse_interval
                                        hint_text: "Rinse"
                                        helper_text: "hours"
                                        helper_text_mode: "persistent"
                                        mode: "fill"
                                        input_filter: "float"
                                        fill_color: 1, 1, 1, 0.06

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Save Reminder Rhythm"
                                        start_color: 0.98, 0.83, 0.44, 1
                                        end_color: 0.78, 0.56, 0.14, 1
                                        on_release: app.on_save_dental_intervals()

                                    GradientButton:
                                        text: "Reset Defaults"
                                        start_color: 0.34, 0.60, 0.98, 1
                                        end_color: 0.18, 0.36, 0.70, 1
                                        on_release: app.on_reset_dental_intervals()

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Log Brush"
                                        start_color: 0.93, 0.76, 0.22, 1
                                        end_color: 0.78, 0.55, 0.12, 1
                                        on_release: app.on_log_dental_habit("brush")

                                    GradientButton:
                                        text: "Log Floss"
                                        start_color: 0.30, 0.76, 0.95, 1
                                        end_color: 0.16, 0.46, 0.78, 1
                                        on_release: app.on_log_dental_habit("floss")

                                    GradientButton:
                                        text: "Log Rinse"
                                        start_color: 0.20, 0.82, 0.60, 1
                                        end_color: 0.12, 0.50, 0.36, 1
                                        on_release: app.on_log_dental_habit("rinse")

                        FloatLayout:
                            size_hint_y: None
                            height: "430dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(24)
                                fill: 1, 1, 1, 0.05
                                border: 0.75, 0.88, 1.0, 0.16
                                highlight: 1, 1, 1, 0.06

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Smile Vision Coach"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    size_hint_y: None
                                    height: "28dp"

                                MDLabel:
                                    text: "Use a front-facing mouth photo to get a private cleanliness rating, visible-sign summary, and gentle suggestions."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: dental_hygiene_status
                                    text: "Ready for a teeth photo."
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: dental_hygiene_photo
                                    text: "Last hygiene photo: none"
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    size_hint_y: None
                                    height: "24dp"

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Take Teeth Photo"
                                        start_color: 0.30, 0.76, 0.95, 1
                                        end_color: 0.16, 0.46, 0.78, 1
                                        on_release: app.on_take_dental_hygiene_photo()

                                    GradientButton:
                                        text: "Use Existing Photo"
                                        start_color: 0.20, 0.82, 0.60, 1
                                        end_color: 0.12, 0.50, 0.36, 1
                                        on_release: app.on_pick_dental_hygiene_photo()

                                MDLabel:
                                    id: dental_hygiene_rating
                                    text: "No hygiene rating yet."
                                    theme_text_color: "Custom"
                                    text_color: 0.96, 0.99, 0.98, 1
                                    bold: True
                                    size_hint_y: None
                                    height: "26dp"

                                MDLabel:
                                    id: dental_hygiene_trend
                                    text: "Trend: take two AI reviews over time to compare your hygiene rhythm."
                                    theme_text_color: "Custom"
                                    text_color: 0.78, 0.88, 0.86, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: dental_hygiene_summary
                                    text: "Take a photo for a cleanliness score, visible-sign review, and gentle brushing/flossing suggestions."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                        FloatLayout:
                            size_hint_y: None
                            height: "720dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(24)
                                fill: 1, 1, 1, 0.05
                                border: 1.0, 0.72, 0.82, 0.16
                                highlight: 1, 1, 1, 0.06

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Recovery Journal"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    size_hint_y: None
                                    height: "28dp"

                                MDLabel:
                                    text: "For extractions, crowns, fillings, caps, implants, and similar dental work, save context once and then run daily photo check-ins."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: recovery_mode_status
                                    text: "Recovery mode is off."
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: recovery_snapshot
                                    text: "Set a procedure type and date to start a daily recovery journal."
                                    theme_text_color: "Custom"
                                    text_color: 0.78, 0.88, 0.86, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDTextField:
                                    id: recovery_procedure_type
                                    hint_text: "Procedure type (extraction, crown, filling, implant, cap)"
                                    mode: "fill"
                                    fill_color: 1, 1, 1, 0.06

                                MDTextField:
                                    id: recovery_procedure_date
                                    hint_text: "Procedure date (YYYY-MM-DD)"
                                    mode: "fill"
                                    fill_color: 1, 1, 1, 0.06

                                MDTextField:
                                    id: recovery_symptom_notes
                                    hint_text: "Symptom notes (pain, swelling, sensitivity, bleeding)"
                                    mode: "fill"
                                    multiline: True
                                    fill_color: 1, 1, 1, 0.06

                                MDTextField:
                                    id: recovery_care_notes
                                    hint_text: "Dentist instructions or recovery notes"
                                    mode: "fill"
                                    multiline: True
                                    fill_color: 1, 1, 1, 0.06

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Save Recovery Mode"
                                        start_color: 1.00, 0.62, 0.52, 1
                                        end_color: 0.83, 0.34, 0.37, 1
                                        on_release: app.on_save_recovery_mode()

                                    GradientButton:
                                        text: "Pause Recovery"
                                        start_color: 0.38, 0.44, 0.74, 1
                                        end_color: 0.24, 0.28, 0.54, 1
                                        on_release: app.on_pause_recovery_mode()

                                MDLabel:
                                    id: recovery_last_photo
                                    text: "Last recovery photo: none"
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    size_hint_y: None
                                    height: "24dp"

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Take Recovery Photo"
                                        start_color: 1.00, 0.62, 0.52, 1
                                        end_color: 0.83, 0.34, 0.37, 1
                                        on_release: app.on_take_recovery_photo()

                                    GradientButton:
                                        text: "Use Existing Photo"
                                        start_color: 0.38, 0.44, 0.74, 1
                                        end_color: 0.24, 0.28, 0.54, 1
                                        on_release: app.on_pick_recovery_photo()

                                MDLabel:
                                    id: recovery_result
                                    text: "Recovery suggestions here stay general and should never replace your dentist's instructions."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

            MDBottomNavigationItem:
                name: "assistant"
                text: "Chat"
                icon: "chat-processing-outline"

                ScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "12dp"
                        padding: "12dp"
                        size_hint_y: None
                        height: self.minimum_height

                        FloatLayout:
                            size_hint_y: None
                            height: "560dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(28)
                                fill: 1, 1, 1, 0.055
                                border: 1, 1, 1, 0.12
                                highlight: 1, 1, 1, 0.07

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Local Gemma Chat"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    font_style: "H6"
                                    size_hint_y: None
                                    height: "30dp"

                                MDLabel:
                                    text: "Ask about upcoming doses, schedule consistency, dental hygiene reminders, or recovery check-ins already stored in the encrypted vault."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                ScrollView:
                                    do_scroll_x: False

                                    MDLabel:
                                        id: assistant_history
                                        text: "No assistant messages yet."
                                        theme_text_color: "Custom"
                                        text_color: 0.82, 0.90, 0.88, 1
                                        text_size: self.width, None
                                        valign: "top"
                                        size_hint_y: None
                                        height: self.texture_size[1]

                                MDTextField:
                                    id: assistant_input
                                    hint_text: "Ask MedSafe about this schedule"
                                    mode: "fill"
                                    multiline: True
                                    fill_color: 1, 1, 1, 0.06

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Send"
                                        on_release: app.on_assistant_send()

                                    GradientButton:
                                        text: "Clear Chat"
                                        start_color: 0.94, 0.42, 0.38, 1
                                        end_color: 0.71, 0.21, 0.22, 1
                                        on_release: app.on_assistant_clear()

            MDBottomNavigationItem:
                name: "model"
                text: "Model"
                icon: "download-circle-outline"

                ScrollView:
                    do_scroll_x: False

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: "12dp"
                        padding: "12dp"
                        size_hint_y: None
                        height: self.minimum_height

                        FloatLayout:
                            size_hint_y: None
                            height: "360dp"

                            GlassCard:
                                pos: self.parent.pos
                                size: self.parent.size
                                radius: dp(28)
                                fill: 1, 1, 1, 0.055
                                border: 1, 1, 1, 0.12
                                highlight: 1, 1, 1, 0.07

                            MDBoxLayout:
                                orientation: "vertical"
                                padding: "16dp"
                                spacing: "10dp"
                                pos: self.parent.pos
                                size: self.parent.size

                                MDLabel:
                                    text: "Gemma 4 Runtime"
                                    theme_text_color: "Custom"
                                    text_color: 0.95, 0.99, 0.97, 1
                                    bold: True
                                    font_style: "H6"
                                    size_hint_y: None
                                    height: "30dp"

                                MDLabel:
                                    id: model_status
                                    text: "No model downloaded yet."
                                    theme_text_color: "Custom"
                                    text_color: 0.82, 0.90, 0.88, 1
                                    text_size: self.width, None
                                    size_hint_y: None
                                    height: self.texture_size[1]

                                MDLabel:
                                    id: model_backend_label
                                    text: "Backend: Auto"
                                    theme_text_color: "Custom"
                                    text_color: 0.67, 0.80, 0.78, 1
                                    size_hint_y: None
                                    height: "24dp"

                                MDProgressBar:
                                    id: model_progress
                                    value: 0
                                    max: 100
                                    type: "determinate"

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Download & Seal"
                                        on_release: app.on_model_download()

                                    GradientButton:
                                        text: "Verify SHA"
                                        start_color: 0.18, 0.56, 0.94, 1
                                        end_color: 0.12, 0.35, 0.68, 1
                                        on_release: app.on_model_verify()

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Cycle Backend"
                                        start_color: 0.19, 0.79, 0.58, 1
                                        end_color: 0.12, 0.46, 0.34, 1
                                        on_release: app.on_cycle_backend()

                                    GradientButton:
                                        text: "Toggle Image Input"
                                        start_color: 0.94, 0.65, 0.30, 1
                                        end_color: 0.72, 0.44, 0.16, 1
                                        on_release: app.on_toggle_native_image_input()

                                MDBoxLayout:
                                    spacing: "8dp"
                                    size_hint_y: None
                                    height: "46dp"

                                    GradientButton:
                                        text: "Delete Plain Cache"
                                        start_color: 0.94, 0.42, 0.38, 1
                                        end_color: 0.71, 0.21, 0.22, 1
                                        on_release: app.on_delete_plain_model()

                                    GradientButton:
                                        text: "Refresh"
                                        start_color: 0.18, 0.56, 0.94, 1
                                        end_color: 0.12, 0.35, 0.68, 1
                                        on_release: app.refresh_model_status()
"""


class MedSafeApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.paths: Optional[AppPaths] = None
        self.vault: Optional[EncryptedVault] = None
        self.settings_data: Dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.data_cache: Dict[str, Any] = vault_defaults()
        self.vault_write_blocked_reason = ""
        self.selected_med_id: Optional[str] = None
        self.last_form_med_id: Optional[str] = None
        self.last_check_level = "Medium"
        self.last_check_display = "Awaiting check"
        self.last_check_message = "Log a selected dose to score timing and daily totals."
        self.dialog: Optional[MDDialog] = None

    def build(self):
        self.title = "MedSafe"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "BlueGray"

        storage_root = Path(getattr(self, "user_data_dir", "") or ".medsafe_data")
        self.paths = set_app_paths(storage_root)
        self.vault = EncryptedVault(self.paths)
        self.settings_data = load_settings(self.paths)

        root = Builder.load_string(KV)
        self._request_runtime_permissions()
        Clock.schedule_once(lambda _dt: self.refresh_from_disk(), 0.05)
        Clock.schedule_interval(lambda _dt: self.refresh_time_sensitive_labels(), 60.0)
        return root

    def _request_runtime_permissions(self) -> None:
        if not request_permissions or not Permission:
            return
        wanted = []
        for name in ("CAMERA", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE", "POST_NOTIFICATIONS"):
            if hasattr(Permission, name):
                wanted.append(getattr(Permission, name))
        if wanted:
            try:
                request_permissions(wanted)
            except Exception:
                pass

    def on_stop(self):
        self.dialog = None

    def set_status(self, text: str) -> None:
        if self.root:
            self.root.ids.status_label.text = sanitize_text(text, max_chars=220)

    def show_dialog(self, title: str, text: str) -> None:
        if self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass
        self.dialog = MDDialog(
            title=sanitize_text(title, max_chars=80),
            text=sanitize_text(text, max_chars=3000),
            buttons=[MDFlatButton(text="OK", on_release=lambda *_args: self.dialog.dismiss() if self.dialog else None)],
        )
        self.dialog.open()

    def set_field_text(self, widget_id: str, value: str, *, force: bool = False) -> None:
        if not self.root:
            return
        widget = self.root.ids.get(widget_id)
        if widget is None:
            return
        next_text = sanitize_text(value, max_chars=4000)
        if force or not bool(getattr(widget, "focus", False)):
            if getattr(widget, "text", None) != next_text:
                widget.text = next_text

    def refresh_from_disk(self) -> None:
        if not self.vault:
            return
        self.data_cache = ensure_vault_shape(self.vault.load())
        if self.selected_med_id and not self.current_selected_med():
            self.selected_med_id = None
        if not self.selected_med_id and self.data_cache.get("meds"):
            sorted_meds = sorted(
                list(self.data_cache.get("meds") or []),
                key=lambda med: (
                    0 if medication_due_status(med)["overdue"] else 1 if medication_due_status(med)["due_now"] else 2,
                    medication_due_status(med)["next_ts"] or float("inf"),
                ),
            )
            self.selected_med_id = str(sorted_meds[0].get("id"))
        self.refresh_ui()

    def refresh_time_sensitive_labels(self) -> None:
        self.refresh_dashboard()
        self.refresh_med_list()
        self.refresh_dental_ui()

    def refresh_ui(self) -> None:
        self.refresh_dashboard()
        self.refresh_med_list()
        self.refresh_form()
        self.refresh_assistant_history()
        self.refresh_model_status()
        self.refresh_vision_summary()
        self.refresh_dental_ui()

    def save_data(self) -> None:
        if self.vault:
            self.vault.save(self.data_cache)

    def current_selected_med(self) -> Optional[Dict[str, Any]]:
        for med in all_stored_medications(self.data_cache):
            if str(med.get("id")) == self.selected_med_id:
                return med
        return None

    def med_by_id(self, med_id: str) -> Optional[Dict[str, Any]]:
        target = sanitize_text(med_id, max_chars=32)
        for med in self.data_cache.get("meds", []) or []:
            if str(med.get("id")) == target:
                return med
        return None

    def _render_daily_checklist(self, med: Optional[Dict[str, Any]], now: float) -> None:
        frame = self.ids.daily_checklist_frame
        for child in frame.winfo_children():
            child.destroy()
        frame.grid_columnconfigure(0, weight=1)
        if not med:
            ctk.CTkLabel(
                frame,
                text="Select a medication to build today's checklist.",
                anchor="w",
                justify="left",
                wraplength=500,
                text_color=DESKTOP_MUTED,
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return
        slots = build_medication_daily_slots(med, datetime.fromtimestamp(now).date(), now)
        if not slots:
            next_slot = next_unchecked_medication_slot(med, now)
            message = "Add custom times or save an interval to generate a daily checklist."
            if next_slot is not None:
                message = f"No remaining slots today. Next planned dose: {next_slot['label']} {next_slot['time_text']}."
            ctk.CTkLabel(
                frame,
                text=message,
                anchor="w",
                justify="left",
                wraplength=500,
                text_color=DESKTOP_MUTED,
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return
        for row_index, slot in enumerate(slots):
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.grid(row=row_index, column=0, sticky="ew", padx=8, pady=4)
            row.grid_columnconfigure(1, weight=1)

            checkbox = ctk.CTkCheckBox(
                row,
                text=f"{slot['label']} • {slot['time_text']}",
                fg_color=DESKTOP_ACCENT,
                hover_color="#0d6b63",
                border_color=DESKTOP_BORDER,
                text_color=DESKTOP_TEXT,
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            checkbox.grid(row=0, column=0, sticky="w", padx=(4, 10))
            if slot.get("status") == "taken":
                checkbox.select()
                checkbox.configure(state="disabled")
            elif slot.get("status") == "missed":
                checkbox.deselect()
                checkbox.configure(state="disabled")
            else:
                checkbox.deselect()
                checkbox.configure(
                    command=lambda med_id=str(med.get("id")), slot_label=str(slot.get("label")): self.on_checklist_take_dose(med_id, slot_label)
                )

            if slot.get("status") == "missed":
                status_color = DESKTOP_DANGER
                status_text = f"X {slot['status_text']}"
            elif slot.get("status") == "due":
                status_color = DESKTOP_WARNING
                status_text = f"! {slot['status_text']}"
            elif slot.get("status") == "taken":
                status_color = DESKTOP_SUCCESS
                status_text = slot["status_text"]
            else:
                status_color = DESKTOP_MUTED
                status_text = slot["status_text"]

            ctk.CTkLabel(
                row,
                text=status_text,
                anchor="w",
                justify="left",
                wraplength=260,
                text_color=status_color,
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=1, sticky="ew")

            if slot.get("status") == "missed":
                self._button(
                    row,
                    text="Take Now",
                    command=lambda med_id=str(med.get("id")), slot_label=str(slot.get("label")): self.on_checklist_take_dose(med_id, slot_label),
                    tone="warning",
                ).grid(row=0, column=2, sticky="e", padx=(10, 0))

    def _log_dose_for_med(
        self,
        med: Dict[str, Any],
        *,
        source_label: str = "dose",
        log_timestamp: Optional[float] = None,
        scheduled_ts: float = 0.0,
        slot_key: str = "",
        enforce_safety: bool = True,
    ) -> None:
        dose_value = max(0.0, safe_float(self.ids.dose_mg.text) or safe_float(med.get("dose_mg")))
        now = time.time()
        effective_timestamp = safe_float(log_timestamp) if log_timestamp is not None else now
        assessment_timestamp = effective_timestamp if effective_timestamp > 0.0 else now
        slot_info = {
            "slot_key": sanitize_text(slot_key or "", max_chars=64),
            "scheduled_ts": max(0.0, safe_float(scheduled_ts)),
        }
        existing_slot_record = matching_medication_history_entry_for_slot(med, slot_info) if (slot_info["slot_key"] or slot_info["scheduled_ts"] > 0.0) else None
        if existing_slot_record is not None:
            self.last_check_level = "Medium"
            self.last_check_display = "Already checked"
            self.last_check_message = f"{source_label or 'Dose'} was already recorded for this checklist slot."
            self.refresh_ui()
            self.set_status(self.last_check_message)
            self.start_dose_safety_assessment(med, dose_value, source_label=f"{source_label} duplicate")
            return
        duplicate_ts = None
        if not slot_info["slot_key"] and slot_info["scheduled_ts"] <= 0.0:
            duplicate_ts = recent_duplicate_log_ts(med, dose_value, now)
        if duplicate_ts is not None:
            self.start_dose_safety_assessment(med, dose_value, source_label=f"{source_label} duplicate")
            return
        label, message = dose_safety_level(med, dose_value, now)
        source_suffix = f" Logged for {source_label}." if source_label else ""
        self.last_check_level = label
        self.last_check_display = label
        self.last_check_message = message + (source_suffix if label != "High" else "")
        if label == "High":
            self.refresh_ui()
            self.set_status(message)
            if enforce_safety:
                self.show_dialog("High Safety Flag", message)
                self.start_dose_safety_assessment(med, dose_value, source_label=f"{source_label} blocked")
                return
            self.last_check_message = message + " Checklist slot marked anyway."
        original_med = self.clone_med_snapshot(med)
        append_medication_history_entry(
            med,
            effective_timestamp,
            dose_value,
            scheduled_ts=slot_info["scheduled_ts"],
            slot_key=slot_info["slot_key"],
        )
        if dose_value > 0:
            med["dose_mg"] = dose_value
        assessment_med = original_med
        if not self.save_data():
            med.clear()
            med.update(original_med)
            self.refresh_ui()
            return
        self.refresh_ui()
        self.set_status(self.last_check_message)
        self.start_dose_safety_assessment(assessment_med, dose_value, source_label=source_label)

    def on_checklist_take_dose(self, med_id: str, slot_label: str) -> None:
        self.selected_med_id = med_id
        med = self.current_selected_med()
        if not med:
            return
        self._log_dose_for_med(med, source_label=slot_label)

    def refresh_dashboard(self) -> None:
        now = time.time()
        meds = list(self.data_cache.get("meds") or [])
        med_statuses = [(medication_due_status(med, now), med) for med in meds]
        due_now = [med for status, med in med_statuses if status["due_now"] and not status["overdue"]]
        overdue = [med for status, med in med_statuses if status["overdue"]]
        next_due_items = [
            (status["next_ts"], med)
            for status, med in med_statuses
            if status["next_ts"] is not None
        ]
        next_due_items.sort(key=lambda item: item[0] or float("inf"))
        next_due_text = "Nothing scheduled yet"
        if next_due_items:
            next_due_ts, med = next_due_items[0]
            next_due_text = f"{sanitize_text(med.get('name'), max_chars=120)} • {format_relative_due(next_due_ts, now)}"

        selected = self.current_selected_med()
        selection_text = "Select a medication to log doses."
        summary_text = "No medication selected."
        if selected:
            status = medication_due_status(selected, now)
            selection_text = f"Focused med: {sanitize_text(selected.get('name'), max_chars=120)}"
            summary_text = (
                f"{sanitize_text(selected.get('name'), max_chars=120)}\n"
                f"{medication_card_line(selected, now)}\n"
                f"Last taken: {format_timestamp(last_effective_taken_ts(selected))}\n"
                f"Directions: {sanitize_text(selected.get('schedule_text') or 'No bottle directions saved yet.', max_chars=260)}"
            )

        self.root.ids.dose_wheel.set_level(self.last_check_level)
        self.root.ids.dashboard_risk_title.text = self.last_check_display
        self.root.ids.dashboard_risk_caption.text = self.last_check_message
        self.root.ids.today_due_count.text = f"{len(due_now)} due • {len(overdue)} overdue"
        self.root.ids.today_next_due.text = next_due_text
        self.root.ids.today_timeline.text = build_timeline_text(meds, now)
        self.root.ids.dashboard_selection.text = selection_text
        self.root.ids.selected_med_summary.text = summary_text
        self.root.ids.selected_med_history.text = build_med_history_text(selected)

    def refresh_med_list(self) -> None:
        med_list = self.root.ids.med_list
        med_list.clear_widgets()
        meds = list(self.data_cache.get("meds") or [])
        now = time.time()
        for med in sorted(
            meds,
            key=lambda item: (
                0 if medication_due_status(item, now)["overdue"] else 1 if medication_due_status(item, now)["due_now"] else 2,
                medication_due_status(item, now)["next_ts"] or float("inf"),
                sanitize_text(item.get("name"), max_chars=120).lower(),
            ),
        ):
            title = sanitize_text(med.get("name"), max_chars=120)
            prefix = "Selected • " if str(med.get("id")) == self.selected_med_id else ""
            item = TwoLineListItem(
                text=prefix + title,
                secondary_text=medication_card_line(med, now),
                on_release=lambda _widget, med_id=str(med.get("id")): self.select_med(med_id),
            )
            med_list.add_widget(item)

    def refresh_form(self) -> None:
        med = self.current_selected_med()
        if not med:
            self.last_form_med_id = None
            self.root.ids.form_selection.text = "Creating a new medication"
            self.root.ids.form_schedule_preview.text = "Saved schedules appear below."
            return
        med_id = str(med.get("id"))
        force_sync = med_id != self.last_form_med_id
        self.root.ids.form_selection.text = f"Editing: {sanitize_text(med.get('name'), max_chars=120)}"
        self.set_field_text("med_name", sanitize_text(med.get("name") or "", max_chars=120), force=force_sync)
        self.set_field_text("dose_mg", f"{safe_float(med.get('dose_mg')):g}" if safe_float(med.get("dose_mg")) else "", force=force_sync)
        self.set_field_text("interval_h", f"{safe_float(med.get('interval_hours')):g}" if safe_float(med.get("interval_hours")) else "", force=force_sync)
        self.set_field_text("max_daily", f"{safe_float(med.get('max_daily_mg')):g}" if safe_float(med.get("max_daily_mg")) else "", force=force_sync)
        self.set_field_text("schedule_text", sanitize_text(med.get("schedule_text") or "", max_chars=240), force=force_sync)
        self.set_field_text("med_notes", sanitize_text(med.get("notes") or "", max_chars=500), force=force_sync)
        self.root.ids.form_schedule_preview.text = medication_card_line(med)
        self.last_form_med_id = med_id

    def refresh_assistant_history(self) -> None:
        history = list(self.data_cache.get("assistant_history") or [])
        if not history:
            self.root.ids.assistant_history.text = "No assistant messages yet."
            return
        lines = []
        for item in history[-12:]:
            speaker = "You" if item.get("role") == "user" else "MedSafe"
            lines.append(f"{speaker}\n{sanitize_text(item.get('content') or '', max_chars=1200)}")
        self.root.ids.assistant_history.text = "\n\n".join(lines)

    def refresh_vision_summary(self) -> None:
        imports = list(self.data_cache.get("vision_imports") or [])
        if not imports:
            self.root.ids.vision_result.text = "No bottle photo processed yet."
            return
        latest = imports[-1]
        risk_score = max(0.0, min(100.0, safe_float(latest.get("risk_score"))))
        risk_level = normalized_risk_level_text(latest.get("risk_level") or "", risk_score)
        risk_summary = sanitize_text(latest.get("risk_summary") or "", max_chars=220)
        lines = [
            f"Imported from: {sanitize_text(latest.get('image_name') or 'photo', max_chars=120)}",
            sanitize_text(latest.get("summary") or "Schedule imported.", max_chars=300),
        ]
        if risk_score > 0 or risk_summary:
            lines.append(f"Review risk: {risk_level} • {risk_score:.0f}/100")
            if risk_summary:
                lines.append(f"Risk note: {risk_summary}")
        lines.append(format_timestamp(safe_float(latest.get("timestamp"))))
        self.root.ids.vision_result.text = "\n".join(lines)

    def refresh_dental_ui(self) -> None:
        now = time.time()
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        brush = habit_due_status(safe_float(hygiene.get("last_brush_ts")), safe_float(hygiene.get("brush_interval_hours")) or 12.0, now)
        floss = habit_due_status(safe_float(hygiene.get("last_floss_ts")), safe_float(hygiene.get("floss_interval_hours")) or 24.0, now)
        rinse = habit_due_status(safe_float(hygiene.get("last_rinse_ts")), safe_float(hygiene.get("rinse_interval_hours")) or 24.0, now)
        overview_title, overview_body = build_dental_overview(
            hygiene,
            dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults()),
            now,
        )
        self.root.ids.dental_overview_title.text = overview_title
        self.root.ids.dental_overview_body.text = overview_body
        for prefix, status, interval in (
            ("brush", brush, safe_float(hygiene.get("brush_interval_hours")) or 12.0),
            ("floss", floss, safe_float(hygiene.get("floss_interval_hours")) or 24.0),
            ("rinse", rinse, safe_float(hygiene.get("rinse_interval_hours")) or 24.0),
        ):
            title_color, caption_color = habit_palette(status)
            self.root.ids[f"dental_{prefix}_status"].text = status["state"]
            self.root.ids[f"dental_{prefix}_status"].text_color = title_color
            self.root.ids[f"dental_{prefix}_caption"].text = f"{status['text']} • every {interval:g}h"
            self.root.ids[f"dental_{prefix}_caption"].text_color = caption_color
        self.set_field_text("dental_brush_interval", f"{safe_float(hygiene.get('brush_interval_hours')):g}")
        self.set_field_text("dental_floss_interval", f"{safe_float(hygiene.get('floss_interval_hours')):g}")
        self.set_field_text("dental_rinse_interval", f"{safe_float(hygiene.get('rinse_interval_hours')):g}")
        self.root.ids.dental_hygiene_photo.text = f"Last hygiene photo: {sanitize_text(hygiene.get('latest_photo') or 'none', max_chars=120)}"
        if hygiene.get("latest_rating"):
            rating_color = score_palette(safe_float(hygiene.get("latest_score")))
            hygiene_history = list(hygiene.get("history") or [])
            latest_hygiene_review = hygiene_history[-1] if hygiene_history else {}
            self.root.ids.dental_hygiene_rating.text = (
                f"{sanitize_text(hygiene.get('latest_rating') or '', max_chars=80)} • {safe_float(hygiene.get('latest_score')):.0f}/100"
            )
            self.root.ids.dental_hygiene_rating.text_color = rating_color
            warning = sanitize_text(hygiene.get("latest_warning_flags") or "None flagged", max_chars=220)
            confidence = max(0.0, min(1.0, safe_float(latest_hygiene_review.get("confidence"))))
            risk_score = max(0.0, min(100.0, safe_float(hygiene.get("latest_risk_score"))))
            risk_level = normalized_risk_level_text(hygiene.get("latest_risk_level") or "", risk_score)
            risk_summary = sanitize_text(hygiene.get("latest_risk_summary") or "", max_chars=220)
            trend_text = f"Trend: {score_change_text(hygiene_history)} AI confidence {confidence:.2f}."
            if risk_score > 0 or risk_summary:
                trend_text += f" Risk: {risk_level} {risk_score:.0f}/100."
            self.root.ids.dental_hygiene_trend.text = trend_text
            summary_lines = [
                sanitize_text(hygiene.get("latest_summary") or "", max_chars=280),
                f"Suggestions: {sanitize_text(hygiene.get('latest_suggestions') or '', max_chars=320)}",
            ]
            if risk_score > 0 or risk_summary:
                summary_lines.append(
                    f"Risk: {risk_level} • {risk_score:.0f}/100 • "
                    f"{risk_summary or 'Use the photo and your symptoms together before acting.'}"
                )
            summary_lines.extend(
                [
                    f"Warnings: {warning}",
                    build_dental_hygiene_history_text(hygiene),
                ]
            )
            self.root.ids.dental_hygiene_summary.text = "\n".join(summary_lines)
        else:
            self.root.ids.dental_hygiene_rating.text = "No hygiene rating yet."
            self.root.ids.dental_hygiene_rating.text_color = (0.96, 0.99, 0.98, 1)
            self.root.ids.dental_hygiene_trend.text = "Trend: take two AI reviews over time to compare your hygiene rhythm."
            self.root.ids.dental_hygiene_summary.text = "Take a photo for a cleanliness score, visible-sign review, and gentle brushing/flossing suggestions."
        if hygiene.get("latest_timestamp") and hygiene.get("latest_rating"):
            self.root.ids.dental_hygiene_status.text = (
                f"Latest review: {sanitize_text(hygiene.get('latest_rating') or '', max_chars=80)} • "
                f"{format_timestamp(safe_float(hygiene.get('latest_timestamp')))}"
            )
        else:
            self.root.ids.dental_hygiene_status.text = "Ready for a teeth photo."

        recovery = dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults())
        self.set_field_text("recovery_procedure_type", sanitize_text(recovery.get("procedure_type") or "", max_chars=120))
        self.set_field_text("recovery_procedure_date", sanitize_text(recovery.get("procedure_date") or "", max_chars=20))
        self.set_field_text("recovery_symptom_notes", sanitize_text(recovery.get("symptom_notes") or "", max_chars=600))
        self.set_field_text("recovery_care_notes", sanitize_text(recovery.get("care_notes") or "", max_chars=600))
        self.root.ids.recovery_last_photo.text = f"Last recovery photo: {sanitize_text(recovery.get('latest_photo') or 'none', max_chars=120)}"
        day_count = days_since_date_string(str(recovery.get("procedure_date") or ""))
        if recovery.get("enabled"):
            day_text = f"Day {day_count + 1}" if day_count is not None else "Day unknown"
            self.root.ids.recovery_mode_status.text = (
                f"{sanitize_text(recovery.get('procedure_type') or 'Recovery mode', max_chars=120)} • {day_text}"
            )
            self.root.ids.recovery_mode_status.text_color = score_palette(safe_float(recovery.get("latest_score") or 70.0))
            score_hint = f" Latest AI recovery score: {safe_float(recovery.get('latest_score')):.0f}/100." if safe_float(recovery.get("latest_score")) else ""
            self.root.ids.recovery_snapshot.text = (
                f"Daily journal active. {score_change_text(list(recovery.get('daily_logs') or []))}{score_hint}"
            )
        else:
            self.root.ids.recovery_mode_status.text = "Recovery mode is off."
            self.root.ids.recovery_mode_status.text_color = (0.67, 0.80, 0.78, 1)
            self.root.ids.recovery_snapshot.text = "Set a procedure type and date to start a daily recovery journal."
        if recovery.get("latest_status"):
            recovery_logs = list(recovery.get("daily_logs") or [])
            latest_recovery_log = recovery_logs[-1] if recovery_logs else {}
            warning = sanitize_text(recovery.get("latest_warning_flags") or "None flagged", max_chars=260)
            confidence = max(0.0, min(1.0, safe_float(latest_recovery_log.get("confidence"))))
            risk_score = max(0.0, min(100.0, safe_float(recovery.get("latest_risk_score"))))
            risk_level = normalized_risk_level_text(recovery.get("latest_risk_level") or "", risk_score)
            risk_summary = sanitize_text(recovery.get("latest_risk_summary") or "", max_chars=240)
            result_lines = [
                f"{sanitize_text(recovery.get('latest_status') or '', max_chars=120)} • {safe_float(recovery.get('latest_score')):.0f}/100",
                sanitize_text(recovery.get("latest_summary") or "", max_chars=320),
                f"Suggestions: {sanitize_text(recovery.get('latest_advice') or '', max_chars=360)}",
            ]
            if risk_score > 0 or risk_summary:
                result_lines.append(
                    f"Risk: {risk_level} • {risk_score:.0f}/100 • "
                    f"{risk_summary or 'Use the image and symptoms together before deciding next steps.'}"
                )
            result_lines.extend(
                [
                    f"Warnings: {warning}",
                    f"AI confidence: {confidence:.2f}",
                    build_recovery_history_text(recovery),
                ]
            )
            self.root.ids.recovery_result.text = "\n".join(result_lines)
        else:
            self.root.ids.recovery_result.text = "Recovery suggestions here stay general and should never replace your dentist's instructions."

    def model_state_summary(self) -> str:
        if not self.paths:
            return "Storage not ready."
        plain_exists = self.paths.plain_model_path.exists()
        encrypted_exists = self.paths.encrypted_model_path.exists()
        encrypted_size = human_size(self.paths.encrypted_model_path.stat().st_size) if encrypted_exists else "0B"
        plain_size = human_size(self.paths.plain_model_path.stat().st_size) if plain_exists else "0B"
        if encrypted_exists and not plain_exists:
            verdict = "Ready for local assistant and safety checks."
        elif encrypted_exists and plain_exists:
            verdict = "Ready, but plain model cache is still present."
        else:
            verdict = "Model not installed. Download and seal Gemma to enable local assistant checks."
        return (
            f"{verdict}\n"
            f"Encrypted model: {'yes' if encrypted_exists else 'no'} ({encrypted_size})\n"
            f"Plain copy: {'yes' if plain_exists else 'no'} ({plain_size})\n"
            f"Model file: {MODEL_FILE}"
        )

    def refresh_model_status(self) -> None:
        settings = load_settings(self.paths) if self.paths else dict(DEFAULT_SETTINGS)
        self.settings_data = settings
        backend = settings.get("inference_backend", "Auto")
        auto_selected = settings.get("auto_selected_inference_backend", "")
        if backend != "Auto":
            backend_note = backend
        else:
            auto_hint = auto_selected
            if not auto_hint:
                try:
                    auto_hint = choose_auto_inference_backend_name()
                except Exception:
                    auto_hint = "pending"
            backend_note = f"Auto ({auto_hint})"
        image_state = "on" if settings.get("enable_native_image_input", True) else "off"
        self.root.ids.model_status.text = self.model_state_summary()
        self.root.ids.model_backend_label.text = f"Backend: {backend_note} • Native image input: {image_state}"
        self.root.ids.dashboard_model_state.text = f"Model: {'ready' if self.paths and self.paths.encrypted_model_path.exists() else 'not downloaded'} • Image input {image_state}"

    def reset_form_fields(self) -> None:
        self.root.ids.med_name.text = ""
        self.root.ids.dose_mg.text = ""
        self.root.ids.interval_h.text = ""
        self.root.ids.max_daily.text = ""
        self.root.ids.schedule_text.text = ""
        self.root.ids.med_notes.text = ""
        self.root.ids.form_selection.text = "Creating a new medication"
        self.root.ids.form_schedule_preview.text = "Saved schedules appear below."

    def select_med(self, med_id: str) -> None:
        self.selected_med_id = med_id
        self.refresh_ui()

    def on_dashboard_med_select(self, label: str) -> None:
        med_id = sanitize_text(self.dashboard_med_option_map.get(label) or "", max_chars=32)
        self.selected_med_id = med_id or None
        self.refresh_ui()

    def on_new_med(self) -> None:
        self.selected_med_id = None
        self.last_form_med_id = None
        self.reset_form_fields()
        self.set_status("Ready to add a new medication.")
        self.refresh_ui()

    def on_save_med(self) -> None:
        name = sanitize_text(self.root.ids.med_name.text, max_chars=120)
        if not name:
            self.set_status("Enter a medication name first.")
            return
        dose_mg = max(0.0, safe_float(self.root.ids.dose_mg.text))
        interval_hours = max(0.0, safe_float(self.root.ids.interval_h.text))
        max_daily_mg = max(0.0, safe_float(self.root.ids.max_daily.text))
        schedule_text = sanitize_text(self.root.ids.schedule_text.text, max_chars=240)
        notes = sanitize_text(self.root.ids.med_notes.text, max_chars=500)

        meds = list(self.data_cache.get("meds") or [])
        selected_med = self.current_selected_med()
        created_new = should_create_new_med_entry(selected_med, name)
        created_from_name_change = selected_med is not None and created_new
        med = selected_med
        if created_new:
            med = {
                "id": uuid.uuid4().hex[:12],
                "name": name,
                "dose_mg": dose_mg,
                "interval_hours": interval_hours,
                "max_daily_mg": max_daily_mg,
                "schedule_text": schedule_text,
                "notes": notes,
                "source": "manual",
                "source_photo": "",
                "last_taken_ts": 0.0,
                "history": [],
            }
            meds.append(med)
            self.selected_med_id = med["id"]
        else:
            med["name"] = name
            med["dose_mg"] = dose_mg
            med["interval_hours"] = interval_hours
            med["max_daily_mg"] = max_daily_mg
            med["schedule_text"] = schedule_text
            med["notes"] = notes

        self.data_cache["meds"] = meds
        saved = self.save_data()
        self.last_check_level = "Medium"
        self.last_check_display = "Schedule saved"
        self.last_check_message = f"{name} was saved to the encrypted schedule vault."
        if created_new:
            self.selected_med_id = None
            self.last_form_med_id = None
            self.reset_form_fields()
        self.refresh_ui()
        if saved:
            self.trigger_safety_scan("medication save", announce=False)
        if created_new:
            if created_from_name_change:
                self.set_status(f"Saved {name} as a new medication. Ready to add another medication.")
            else:
                self.set_status(f"Saved {name}. Ready to add another medication.")
        else:
            self.set_status(f"Saved {name}.")
        self.start_dose_safety_assessment(med, max(dose_mg, max(0.0, safe_float(med.get("dose_mg")))), source_label="schedule update")

    def on_delete_med(self) -> None:
        med = self.current_selected_med()
        if not med:
            self.set_status("Select a medication first.")
            return
        name = sanitize_text(med.get("name"), max_chars=120)
        self.data_cache["meds"] = [item for item in self.data_cache.get("meds", []) or [] if str(item.get("id")) != self.selected_med_id]
        self.selected_med_id = None
        saved = self.save_data()
        self.reset_form_fields()
        self.last_check_level = "Medium"
        self.last_check_display = "Medication removed"
        self.last_check_message = f"{name} was removed from the local schedule."
        self.refresh_ui()
        if saved:
            self.trigger_safety_scan("medication removal", announce=False)
        self.set_status(f"Deleted {name}.")

    def on_log_dose(self) -> None:
        med = self.current_selected_med()
        if not med:
            self.set_status("Select a medication before logging a dose.")
            return
        dose_value = max(0.0, safe_float(self.root.ids.dose_mg.text) or safe_float(med.get("dose_mg")))
        now = time.time()
        duplicate_ts = recent_duplicate_log_ts(med, dose_value, now)
        if duplicate_ts is not None:
            self.last_check_level = "Medium"
            self.last_check_display = "Already logged"
            self.last_check_message = f"A matching dose was already logged {format_duration(now - duplicate_ts)} ago. It was not added again."
            self.refresh_ui()
            self.set_status(self.last_check_message)
            return
        label, message = dose_safety_level(med, dose_value, now)
        self.last_check_level = label
        self.last_check_display = label
        self.last_check_message = message
        if label == "High":
            self.refresh_ui()
            self.set_status(message)
            self.show_dialog("High Safety Flag", message)
            return
        med["history"] = list(med.get("history") or []) + [[now, dose_value]]
        med["history"] = med["history"][-240:]
        med["last_taken_ts"] = now
        if dose_value > 0:
            med["dose_mg"] = dose_value
        self.save_data()
        self.refresh_ui()
        self.set_status(message)

    def on_log_dental_habit(self, habit: str) -> None:
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        now = time.time()
        habit_key = {
            "brush": "last_brush_ts",
            "floss": "last_floss_ts",
            "rinse": "last_rinse_ts",
        }.get(habit)
        if not habit_key:
            return
        hygiene[habit_key] = now
        self.data_cache["dental_hygiene"] = hygiene
        self.save_data()
        self.refresh_dental_ui()
        self.set_status(f"Logged dental {habit} routine.")

    def on_save_dental_intervals(self) -> None:
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        values = {
            "brush_interval_hours": max(1.0, safe_float(self.root.ids.dental_brush_interval.text) or safe_float(hygiene.get("brush_interval_hours")) or 12.0),
            "floss_interval_hours": max(1.0, safe_float(self.root.ids.dental_floss_interval.text) or safe_float(hygiene.get("floss_interval_hours")) or 24.0),
            "rinse_interval_hours": max(1.0, safe_float(self.root.ids.dental_rinse_interval.text) or safe_float(hygiene.get("rinse_interval_hours")) or 24.0),
        }
        hygiene.update(values)
        self.data_cache["dental_hygiene"] = hygiene
        self.save_data()
        self.set_field_text("dental_brush_interval", f"{values['brush_interval_hours']:g}", force=True)
        self.set_field_text("dental_floss_interval", f"{values['floss_interval_hours']:g}", force=True)
        self.set_field_text("dental_rinse_interval", f"{values['rinse_interval_hours']:g}", force=True)
        self.refresh_dental_ui()
        self.set_status("Dental reminder rhythm saved.")

    def on_reset_dental_intervals(self) -> None:
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        defaults = dental_hygiene_defaults()
        hygiene["brush_interval_hours"] = defaults["brush_interval_hours"]
        hygiene["floss_interval_hours"] = defaults["floss_interval_hours"]
        hygiene["rinse_interval_hours"] = defaults["rinse_interval_hours"]
        self.data_cache["dental_hygiene"] = hygiene
        self.save_data()
        self.set_field_text("dental_brush_interval", f"{defaults['brush_interval_hours']:g}", force=True)
        self.set_field_text("dental_floss_interval", f"{defaults['floss_interval_hours']:g}", force=True)
        self.set_field_text("dental_rinse_interval", f"{defaults['rinse_interval_hours']:g}", force=True)
        self.refresh_dental_ui()
        self.set_status("Dental reminder rhythm reset to defaults.")

    def recovery_state_from_form(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "procedure_type": sanitize_text(self.root.ids.recovery_procedure_type.text, max_chars=120),
            "procedure_date": sanitize_text(self.root.ids.recovery_procedure_date.text, max_chars=20),
            "symptom_notes": sanitize_text(self.root.ids.recovery_symptom_notes.text, max_chars=600),
            "care_notes": sanitize_text(self.root.ids.recovery_care_notes.text, max_chars=600),
        }

    def on_save_recovery_mode(self) -> None:
        recovery = dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults())
        form_state = self.recovery_state_from_form()
        if not form_state["procedure_type"]:
            self.set_status("Enter the dental procedure before enabling recovery mode.")
            return
        if form_state["procedure_date"] and parse_date_string(form_state["procedure_date"]) is None:
            self.set_status("Use YYYY-MM-DD for the procedure date.")
            return
        recovery.update(form_state)
        self.data_cache["dental_recovery"] = recovery
        self.save_data()
        self.refresh_dental_ui()
        self.set_status("Dental recovery mode saved.")

    def on_pause_recovery_mode(self) -> None:
        recovery = dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults())
        recovery["enabled"] = False
        self.data_cache["dental_recovery"] = recovery
        self.save_data()
        self.refresh_dental_ui()
        self.set_status("Dental recovery mode paused.")

    def _capture_photo(
        self,
        prefix: str,
        opening_status: str,
        on_ready: Callable[[Path], None],
        on_failure: Callable[[str], None],
    ) -> None:
        if not self.paths:
            return
        if plyer_camera is None:
            on_failure("Camera support is unavailable on this platform. Use an existing photo on a device build.")
            return
        target = self.paths.media_dir / f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
        self.set_status(opening_status)

        def on_complete(path_text: str) -> None:
            if not path_text:
                Clock.schedule_once(lambda _dt: on_failure("Camera did not return a saved image."), 0)
                return
            Clock.schedule_once(lambda _dt: on_ready(Path(path_text)), 0)

        try:
            plyer_camera.take_picture(filename=str(target), on_complete=on_complete)
        except Exception as exc:
            on_failure(str(exc))

    def _pick_photo(
        self,
        choose_status: str,
        on_ready: Callable[[Path], None],
        on_failure: Callable[[str], None],
    ) -> None:
        if plyer_filechooser is None:
            on_failure("File chooser support is unavailable on this platform.")
            return
        self.set_status(choose_status)

        def on_selection(selection: List[str]) -> None:
            if not selection:
                Clock.schedule_once(lambda _dt: self.set_status("Photo selection cancelled."), 0)
                return
            Clock.schedule_once(lambda _dt: on_ready(Path(selection[0])), 0)

        try:
            plyer_filechooser.open_file(
                on_selection=on_selection,
                filters=[("Images", "*.jpg;*.jpeg;*.png;*.webp")],
            )
        except Exception as exc:
            on_failure(str(exc))

    def append_assistant_message(self, role: str, content: str) -> None:
        history = list(self.data_cache.get("assistant_history") or [])
        history.append({"role": role, "content": sanitize_text(content, max_chars=3000), "timestamp": time.time()})
        self.data_cache["assistant_history"] = history[-ASSISTANT_CONTEXT_MAX_MESSAGES:]
        self.save_data()
        self.refresh_assistant_history()

    def on_assistant_send(self) -> None:
        prompt = sanitize_text(self.root.ids.assistant_input.text, max_chars=1600)
        if not prompt:
            return
        if not self.vault:
            return
        self.root.ids.assistant_input.text = ""
        self.append_assistant_message("user", prompt)
        self.set_status("Thinking with Gemma 4...")

        snapshot = ensure_vault_shape(json.loads(json.dumps(self.data_cache)))
        settings = dict(self.settings_data)
        key = self.vault.get_or_create_key()

        def worker():
            try:
                reply = run_assistant_request(key, snapshot, prompt, self.selected_med_id, settings)
            except Exception as exc:
                reply = f"Chat unavailable: {exc}"
            Clock.schedule_once(lambda _dt: self._assistant_done(reply), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _assistant_done(self, reply: str) -> None:
        self.append_assistant_message("assistant", reply)
        self.set_status("Chat reply ready.")

    def on_assistant_clear(self) -> None:
        self.data_cache["assistant_history"] = []
        self.save_data()
        self.refresh_assistant_history()
        self.set_status("Chat cleared.")

    def _start_image_analysis(self, image_path: Path) -> None:
        if not self.vault:
            return
        self.root.ids.vision_last_file.text = f"Last image: {image_path.name}"
        self.root.ids.vision_status.text = "Reading bottle photo with Gemma 4..."
        self.set_status("Importing medication from photo...")
        key = self.vault.get_or_create_key()
        settings = dict(self.settings_data)

        def worker():
            try:
                payload, raw = analyze_medication_image(key, image_path, settings)
                updated, med_id, created = apply_vision_payload(self.data_cache, payload, selected_med_id=self.selected_med_id)
                Clock.schedule_once(lambda _dt: self._vision_done(updated, med_id, payload, created, raw), 0)
            except Exception as exc:
                Clock.schedule_once(lambda _dt: self._vision_failed(str(exc)), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _vision_done(self, updated: Dict[str, Any], med_id: str, payload: Dict[str, Any], created: bool, raw: str) -> None:
        self.data_cache = ensure_vault_shape(updated)
        self.selected_med_id = med_id
        saved = self.save_data()
        action = "Added" if created else "Updated"
        confidence = payload.get("confidence", 0.0)
        self.root.ids.vision_status.text = f"{action} {payload['name']} from the bottle photo."
        self.root.ids.vision_result.text = (
            f"{action} {payload['name']}\n"
            f"Dose: {payload['dose_mg']:g} mg\n"
            f"Interval: {payload['interval_hours']:g} hours\n"
            f"Max daily: {payload['max_daily_mg']:g} mg\n"
            f"Directions: {payload['schedule_text']}\n"
            f"Notes: {payload['notes'] or 'None'}\n"
            f"Review risk: {payload['risk_level']} • {payload['risk_score']:.0f}/100\n"
            f"Risk note: {payload['risk_summary'] or 'Review the label manually before relying on the import.'}\n"
            f"Confidence: {confidence:.2f}\n"
            f"Model raw: {sanitize_text(raw, max_chars=420)}"
        )
        self.last_check_level = payload["risk_level"]
        self.last_check_display = f"Bottle review risk: {payload['risk_level']}"
        self.last_check_message = payload["risk_summary"] or f"{payload['name']} was saved from the bottle photo."
        self.refresh_ui()
        if saved:
            self.trigger_safety_scan("bottle import", announce=False)
        self.set_status(f"{action} {payload['name']} from the bottle photo.")
        if payload["risk_level"] == "High":
            self.show_dialog(
                "Bottle Photo Needs Review",
                "The quantum-assisted bottle import marked this photo as high review risk.\n\n"
                + sanitize_text(payload.get("risk_summary") or "", max_chars=320),
            )

    def _vision_failed(self, message: str) -> None:
        self.root.ids.vision_status.text = f"Import failed: {sanitize_text(message, max_chars=200)}"
        self.set_status("Bottle photo import failed.")
        self.show_dialog("Bottle Photo Import Failed", message)

    def on_take_bottle_photo(self) -> None:
        self.root.ids.vision_status.text = "Opening camera..."
        self._capture_photo(
            "pill",
            "Opening camera for bottle photo...",
            self._start_image_analysis,
            self._vision_failed,
        )

    def on_pick_bottle_photo(self) -> None:
        self.root.ids.vision_status.text = "Waiting for image selection..."
        self._pick_photo(
            "Choose a medicine bottle photo...",
            self._start_image_analysis,
            self._vision_failed,
        )

    def _dental_hygiene_failed(self, message: str) -> None:
        self.root.ids.dental_hygiene_status.text = f"Review failed: {sanitize_text(message, max_chars=220)}"
        self.set_status("Dental hygiene review failed.")
        self.show_dialog("Dental Hygiene Review Failed", message)

    def _start_dental_hygiene_analysis(self, image_path: Path) -> None:
        if not self.vault:
            return
        self.root.ids.dental_hygiene_photo.text = f"Last hygiene photo: {image_path.name}"
        self.root.ids.dental_hygiene_status.text = "Reviewing hygiene photo with Gemma 4..."
        self.set_status("Reviewing dental hygiene photo...")
        key = self.vault.get_or_create_key()
        settings = dict(self.settings_data)

        def worker():
            try:
                payload, raw = analyze_dental_hygiene_image(key, image_path, settings)
                updated = apply_dental_hygiene_payload(self.data_cache, payload)
                Clock.schedule_once(lambda _dt: self._dental_hygiene_done(updated, payload, raw), 0)
            except Exception as exc:
                Clock.schedule_once(lambda _dt: self._dental_hygiene_failed(str(exc)), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _dental_hygiene_done(self, updated: Dict[str, Any], payload: Dict[str, Any], raw: str) -> None:
        self.data_cache = ensure_vault_shape(updated)
        self.save_data()
        _ = raw
        self.last_check_level = payload["risk_level"]
        self.last_check_display = f"Dental hygiene risk: {payload['risk_level']}"
        self.last_check_message = payload["risk_summary"] or f"{payload['rating']} hygiene rating saved in the encrypted dental journal."
        self.refresh_dental_ui()
        self.set_status("Dental hygiene review saved.")
        if payload["risk_level"] == "High" or warning_text_needs_attention(payload.get("warning_flags", "")):
            self.show_dialog(
                "Dental Hygiene Attention Flag",
                "The vision review noticed something worth checking more closely.\n\n"
                + sanitize_text(
                    payload.get("risk_summary") or payload.get("warning_flags") or "",
                    max_chars=320,
                ),
            )

    def on_take_dental_hygiene_photo(self) -> None:
        self.root.ids.dental_hygiene_status.text = "Opening camera..."
        self._capture_photo(
            "dental_hygiene",
            "Opening camera for a dental hygiene photo...",
            self._start_dental_hygiene_analysis,
            self._dental_hygiene_failed,
        )

    def on_pick_dental_hygiene_photo(self) -> None:
        self.root.ids.dental_hygiene_status.text = "Waiting for image selection..."
        self._pick_photo(
            "Choose a teeth or mouth photo...",
            self._start_dental_hygiene_analysis,
            self._dental_hygiene_failed,
        )

    def _recovery_failed(self, message: str) -> None:
        self.root.ids.recovery_mode_status.text = f"Review failed: {sanitize_text(message, max_chars=220)}"
        self.set_status("Dental recovery review failed.")
        self.show_dialog("Dental Recovery Review Failed", message)

    def _start_recovery_analysis(self, image_path: Path) -> None:
        if not self.vault:
            return
        recovery_state = self.recovery_state_from_form()
        if not recovery_state["procedure_type"]:
            self._recovery_failed("Enter the procedure type before running recovery mode.")
            return
        if recovery_state["procedure_date"] and parse_date_string(recovery_state["procedure_date"]) is None:
            self._recovery_failed("Use YYYY-MM-DD for the procedure date before running recovery mode.")
            return
        self.root.ids.recovery_last_photo.text = f"Last recovery photo: {image_path.name}"
        self.root.ids.recovery_mode_status.text = "Reviewing recovery photo with Gemma 4..."
        self.set_status("Reviewing dental recovery photo...")
        key = self.vault.get_or_create_key()
        settings = dict(self.settings_data)

        def worker():
            try:
                payload, raw = analyze_dental_recovery_image(key, image_path, settings, recovery_state)
                updated = apply_dental_recovery_payload(self.data_cache, payload, recovery_state)
                Clock.schedule_once(lambda _dt: self._recovery_done(updated, payload, raw), 0)
            except Exception as exc:
                Clock.schedule_once(lambda _dt: self._recovery_failed(str(exc)), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _recovery_done(self, updated: Dict[str, Any], payload: Dict[str, Any], raw: str) -> None:
        self.data_cache = ensure_vault_shape(updated)
        self.save_data()
        _ = raw
        self.last_check_level = payload["risk_level"]
        self.last_check_display = f"Recovery risk: {payload['risk_level']}"
        self.last_check_message = payload["risk_summary"] or (
            "General aftercare suggestions were saved. This is not a diagnosis and does not replace your dentist."
        )
        self.refresh_dental_ui()
        self.set_status("Dental recovery review saved.")
        if payload["risk_level"] == "High" or warning_text_needs_attention(payload.get("warning_flags", "")):
            self.show_dialog(
                "Dental Recovery Attention Flag",
                "The vision review noticed a recovery warning that may deserve a dentist check.\n\n"
                + sanitize_text(
                    payload.get("risk_summary") or payload.get("warning_flags") or "",
                    max_chars=320,
                ),
            )

    def on_take_recovery_photo(self) -> None:
        self.root.ids.recovery_mode_status.text = "Opening camera..."
        self._capture_photo(
            "dental_recovery",
            "Opening camera for a dental recovery check-in...",
            self._start_recovery_analysis,
            self._recovery_failed,
        )

    def on_pick_recovery_photo(self) -> None:
        self.root.ids.recovery_mode_status.text = "Waiting for image selection..."
        self._pick_photo(
            "Choose a recovery check-in photo...",
            self._start_recovery_analysis,
            self._recovery_failed,
        )

    def _run_model_task(self, worker: Callable[[], Any], on_done: Callable[[Any], None], failure_title: str) -> None:
        def runner():
            try:
                result = worker()
                Clock.schedule_once(lambda _dt: on_done(result), 0)
            except Exception as exc:
                Clock.schedule_once(lambda _dt: self._model_task_failed(failure_title, str(exc)), 0)

        threading.Thread(target=runner, daemon=True).start()

    def _model_task_failed(self, title: str, message: str) -> None:
        self.root.ids.model_progress.value = 0
        self.set_status(message)
        self.show_dialog(title, message)
        self.refresh_model_status()

    def on_model_download(self) -> None:
        if not self.vault:
            return
        self.root.ids.model_progress.value = 0
        self.set_status("Downloading Gemma 4...")
        key = self.vault.get_or_create_key()

        def worker():
            def reporter(kind: str, payload: Any) -> None:
                if kind == "progress":
                    Clock.schedule_once(lambda _dt, value=float(payload): setattr(self.root.ids.model_progress, "value", int(value * 100)), 0)
                elif kind == "status":
                    Clock.schedule_once(lambda _dt, value=sanitize_text(payload, max_chars=180): self.set_status(value), 0)

            return download_and_encrypt_model(key, reporter)

        self._run_model_task(worker, self._model_download_done, "Model Download Failed")

    def _model_download_done(self, sha: str) -> None:
        self.root.ids.model_progress.value = 100
        self.set_status("Gemma 4 downloaded and sealed.")
        self.refresh_model_status()
        self.show_dialog("Gemma 4 Ready", f"Model sealed successfully.\nSHA-256: {sha}")

    def on_model_verify(self) -> None:
        if not self.vault:
            return
        self.root.ids.model_progress.value = 15
        self.set_status("Verifying model hash...")
        key = self.vault.get_or_create_key()
        self._run_model_task(lambda: verify_model_hash(key), self._model_verify_done, "Model Verification Failed")

    def _model_verify_done(self, result: Tuple[str, bool]) -> None:
        sha, okay = result
        self.root.ids.model_progress.value = 100 if okay else 0
        self.set_status("Model hash verified." if okay else "Model hash mismatch.")
        self.refresh_model_status()
        self.show_dialog("Model Verification", f"SHA-256: {sha}\nMatches expected hash: {'yes' if okay else 'no'}")

    def on_cycle_backend(self) -> None:
        current = self.settings_data.get("inference_backend", "Auto")
        options = list(INFERENCE_BACKEND_OPTIONS)
        current_index = options.index(current) if current in options else 0
        next_value = options[(current_index + 1) % len(options)]
        save_settings({"inference_backend": next_value}, self.paths)
        self.settings_data = load_settings(self.paths)
        self.refresh_model_status()
        self.set_status(f"Inference backend set to {next_value}.")

    def on_toggle_native_image_input(self) -> None:
        enabled = not bool(self.settings_data.get("enable_native_image_input", True))
        save_settings({"enable_native_image_input": enabled}, self.paths)
        self.settings_data = load_settings(self.paths)
        self.refresh_model_status()
        self.set_status(f"Native image input {'enabled' if enabled else 'disabled'}.")

    def on_delete_plain_model(self) -> None:
        if not self.paths:
            return
        safe_cleanup([self.paths.plain_model_path])
        self.root.ids.model_progress.value = 0
        self.refresh_model_status()
        self.set_status("Deleted any leftover plaintext model copy.")


DESKTOP_BG = "#0d141b"
DESKTOP_SURFACE = "#13202a"
DESKTOP_SURFACE_ALT = "#182633"
DESKTOP_BORDER = "#243343"
DESKTOP_TEXT = "#edf3f1"
DESKTOP_MUTED = "#97abb1"
DESKTOP_ACCENT = "#11837a"
DESKTOP_SUCCESS = "#3fb980"
DESKTOP_WARNING = "#efb54a"
DESKTOP_DANGER = "#d9646d"


def _desktop_hex(color: Union[str, Tuple[float, float, float, float], List[float]]) -> str:
    if isinstance(color, str):
        return color
    if isinstance(color, (tuple, list)) and len(color) >= 3:
        red = max(0, min(255, int(round(float(color[0]) * 255.0))))
        green = max(0, min(255, int(round(float(color[1]) * 255.0))))
        blue = max(0, min(255, int(round(float(color[2]) * 255.0))))
        return f"#{red:02x}{green:02x}{blue:02x}"
    return DESKTOP_TEXT


class DesktopIdMap(dict):
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


class DesktopWidgetAdapter:
    def __init__(self, widget: Any, *focus_targets: Any):
        self.widget = widget
        self.focus_targets = tuple(target for target in (widget,) + focus_targets if target is not None)

    @property
    def focus(self) -> bool:
        focused = self.widget.focus_get()
        while focused is not None:
            if focused in self.focus_targets:
                return True
            focused = getattr(focused, "master", None)
        return False


class DesktopLabelAdapter(DesktopWidgetAdapter):
    @property
    def text(self) -> str:
        return str(self.widget.cget("text"))

    @text.setter
    def text(self, value: str) -> None:
        self.widget.configure(text=sanitize_text(value, max_chars=4000))

    @property
    def text_color(self) -> str:
        return str(self.widget.cget("text_color"))

    @text_color.setter
    def text_color(self, value: Union[str, Tuple[float, float, float, float], List[float]]) -> None:
        self.widget.configure(text_color=_desktop_hex(value))


class DesktopEntryAdapter(DesktopWidgetAdapter):
    def __init__(self, widget: Any):
        super().__init__(widget, getattr(widget, "_entry", None))

    @property
    def text(self) -> str:
        return str(self.widget.get())

    @text.setter
    def text(self, value: str) -> None:
        self.widget.delete(0, tk.END)
        clean = sanitize_text(value, max_chars=4000)
        if clean:
            self.widget.insert(0, clean)


class DesktopTextboxAdapter(DesktopWidgetAdapter):
    def __init__(self, widget: Any, *, readonly: bool = False):
        super().__init__(widget, getattr(widget, "_textbox", None))
        self.readonly = readonly

    def _set_state(self, state: str) -> None:
        try:
            self.widget.configure(state=state)
        except Exception:
            pass

    @property
    def text(self) -> str:
        return str(self.widget.get("1.0", "end-1c"))

    @text.setter
    def text(self, value: str) -> None:
        if self.readonly:
            self._set_state("normal")
        self.widget.delete("1.0", tk.END)
        clean = sanitize_text(value, max_chars=12000)
        if clean:
            self.widget.insert("1.0", clean)
        if self.readonly:
            self._set_state("disabled")


class DesktopProgressAdapter:
    def __init__(self, widget: Any):
        self.widget = widget
        self._value = 0.0

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: Union[int, float]) -> None:
        self._value = max(0.0, min(100.0, float(value)))
        self.widget.set(self._value / 100.0)


class DesktopRiskBadgeAdapter(DesktopLabelAdapter):
    def set_level(self, level: str) -> None:
        normalized = sanitize_text(level, max_chars=24).lower()
        if normalized.startswith("assess") or normalized.startswith("check") or normalized.startswith("pending"):
            label = "Checking"
            fg = "#6a7e94"
        elif normalized.startswith("safe") or normalized.startswith("low"):
            label = "Safe" if normalized.startswith("safe") else "Low"
            fg = DESKTOP_SUCCESS
        elif normalized.startswith("unsafe") or normalized.startswith("high"):
            label = "Unsafe" if normalized.startswith("unsafe") else "High"
            fg = DESKTOP_DANGER
        elif normalized.startswith("caution"):
            label = "Caution"
            fg = DESKTOP_WARNING
        else:
            label = "Medium"
            fg = DESKTOP_WARNING
        self.widget.configure(text=f"Safety {label}", fg_color=fg, text_color="#08110f")


@dataclass
class DesktopListItem:
    text: str
    secondary_text: str
    on_release: Callable[[Any], None]


class DesktopListAdapter:
    def __init__(self, frame: Any):
        self.frame = frame
        self.frame.grid_columnconfigure(0, weight=1)
        self._row = 0

    def clear_widgets(self) -> None:
        for child in self.frame.winfo_children():
            child.destroy()
        self._row = 0

    def add_section(self, title: str) -> None:
        label = ctk.CTkLabel(
            self.frame,
            text=sanitize_text(title, max_chars=120),
            anchor="w",
            justify="left",
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        label.grid(row=self._row, column=0, sticky="ew", padx=4, pady=(6 if self._row else 0, 8))
        self._row += 1

    def add_widget(self, item: DesktopListItem) -> None:
        card = ctk.CTkFrame(
            self.frame,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
        )
        card.grid(row=self._row, column=0, sticky="ew", pady=(0, 8))
        card.grid_columnconfigure(0, weight=1)

        button = ctk.CTkButton(
            card,
            text=sanitize_text(item.text, max_chars=180),
            command=lambda callback=item.on_release: callback(None),
            anchor="w",
            fg_color="transparent",
            hover_color="#223443",
            text_color=DESKTOP_TEXT,
            corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=36,
        )
        button.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 2))

        subtitle = ctk.CTkLabel(
            card,
            text=sanitize_text(item.secondary_text, max_chars=280),
            anchor="w",
            justify="left",
            wraplength=420,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        )
        subtitle.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        self._row += 1


class DesktopMedSafeApp:
    def __init__(self) -> None:
        self.window: Optional[Any] = None
        self.root = SimpleNamespace(ids=DesktopIdMap())
        self.ids = self.root.ids
        self.paths: Optional[AppPaths] = None
        self.vault: Optional[EncryptedVault] = None
        self.settings_data: Dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.data_cache: Dict[str, Any] = vault_defaults()
        self.vault_write_blocked_reason = ""
        self.selected_med_id: Optional[str] = None
        self.last_form_med_id: Optional[str] = None
        self.last_check_level = "Medium"
        self.last_check_display = "Awaiting check"
        self.last_check_message = "Log a selected dose to score timing and daily totals."
        self.main_ui_started = False
        self.refresh_timer_started = False
        self.dose_ai_request_id = 0
        self.dose_ai_process: Optional[Any] = None
        self.dose_ai_queue: Optional[Any] = None
        self.safety_scan_process: Optional[Any] = None
        self.safety_scan_queue: Optional[Any] = None
        self.assistant_process: Optional[Any] = None
        self.assistant_queue: Optional[Any] = None
        self.assistant_request_pending = False
        self.assistant_request_id = 0
        self.assistant_history_dirty = False
        self.assistant_context_refresh_request_id = 0
        self.assistant_quick_prompt_buttons = {}
        self.assistant_context_visible = True
        self.assistant_chat_font_delta = 2
        self.assistant_reply_streaming = False
        self.assistant_stream_request_id = 0
        self.assistant_stream_text = ""
        self.assistant_stream_index = 0
        self.assistant_stream_message_index = -1
        self.background_save_request_id = 0
        self.assistant_mode = "General"
        self.help_selected_topic = ""
        self.unlock_popup: Optional[Any] = None
        self.setup_password_var: Optional[tk.BooleanVar] = None
        self.setup_download_model_var: Optional[tk.BooleanVar] = None
        self.startup_password_lock_var: Optional[tk.BooleanVar] = None
        self.allow_checklist_uncheck_var: Optional[tk.BooleanVar] = None
        self.recovery_enabled_var: Optional[tk.BooleanVar] = None
        self.checklist_target_date_text = date.today().isoformat()
        self.startup_temp_cleanup_message = ""
        self.regimen_check_review: Dict[str, Any] = {}
        self.safety_scan_request_id = 0
        self.dashboard_med_option_map: Dict[str, str] = {"Choose medication": ""}
        self.dashboard_best_action_target = "Dashboard"

    def build(self) -> None:
        if ctk is None:
            detail = f" ({CUSTOMTKINTER_IMPORT_ERROR})" if CUSTOMTKINTER_IMPORT_ERROR else ""
            raise RuntimeError(f"customtkinter is required for the {desktop_platform_name()} desktop build" + detail)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")

        self.window = ctk.CTk()
        self.window.title("MedSafe Desktop")
        screen_width = max(960, int(self.window.winfo_screenwidth() or 1280))
        screen_height = max(720, int(self.window.winfo_screenheight() or 800))
        window_width = min(1440, max(960, screen_width - 80))
        window_height = min(920, max(680, screen_height - 120))
        origin_x = max(0, (screen_width - window_width) // 2)
        origin_y = max(0, (screen_height - window_height) // 3)
        self.window.geometry(f"{window_width}x{window_height}+{origin_x}+{origin_y}")
        self.window.minsize(min(window_width, 960), min(window_height, 680))
        self.window.configure(fg_color=DESKTOP_BG)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.report_callback_exception = self._report_callback_exception

        self.paths = set_app_paths(default_storage_root())
        reclaimed_bytes, removed_count = cleanup_stale_temp_files(self.paths)
        if removed_count > 0:
            self.startup_temp_cleanup_message = (
                f"Cleaned up {removed_count} stale temp file{'s' if removed_count != 1 else ''} "
                f"({human_size(reclaimed_bytes)}) from the local MedSafe temp folder."
            )
        self.vault = EncryptedVault(self.paths)
        self.settings_data = load_settings(self.paths)
        self.assistant_chat_font_delta = max(-6, min(10, int(self.settings_data.get("assistant_chat_font_delta", 2))))
        self.apply_text_size_setting(self.settings_data.get("text_size"))
        if self.vault:
            self.vault.clear_cached_key()
        key_status = self.vault.key_status() if self.vault else "missing"
        if self.vault and key_status == "invalid":
            self._build_blocked_startup(
                "Invalid Vault Key",
                "The local vault key file is unreadable or malformed. MedSafe blocked startup to avoid corrupting or overwriting encrypted data.",
            )
            return
        if self.paths and self.vault and key_status == "missing" and self.paths.vault_path.exists():
            self._build_blocked_startup(
                "Missing Vault Key",
                "The encrypted medication vault exists, but its local key file is missing. MedSafe blocked startup to avoid opening or overwriting protected data.",
            )
            return
        if self.paths and self.vault and existing_app_install(self.paths) and not self.settings_data.get("setup_complete", False):
            save_settings(
                {
                    "setup_complete": True,
                    "startup_password_enabled": self.vault.is_key_protected()
                    or bool(self.settings_data.get("startup_password_enabled", False)),
                },
                self.paths,
            )
            self.settings_data = load_settings(self.paths)

        if self._startup_gate_required():
            if self.vault and self.vault.is_key_protected() and not bool(self.settings_data.get("startup_password_enabled", True)) and self.paths is not None:
                save_settings({"startup_password_enabled": True}, self.paths)
                self.settings_data = load_settings(self.paths)
            self._build_startup_gate()
            return
        if not self.settings_data.get("setup_complete", False):
            self._build_first_boot_flow()
            return
        self._enter_main_app()

    def run(self) -> None:
        self.build()
        if self.window is not None:
            try:
                self.window.mainloop()
            except KeyboardInterrupt:
                self.on_close()

    def _report_callback_exception(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        try:
            is_keyboard_interrupt = bool(exc_type and issubclass(exc_type, KeyboardInterrupt))
        except Exception:
            is_keyboard_interrupt = False
        if is_keyboard_interrupt:
            self.on_close()
            return
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def on_close(self) -> None:
        if self.assistant_history_dirty:
            try:
                self.save_data()
            except Exception:
                pass
        self._close_unlock_popup()
        self._cleanup_dose_safety_process(terminate=True)
        self._cleanup_safety_scan_process(terminate=True)
        self._cleanup_assistant_process(terminate=True)
        if self.vault is not None:
            self.vault.clear_cached_key()
        if self.window is not None:
            self.window.destroy()
            self.window = None

    def run_on_ui_thread(self, callback: Callable[..., Any], *args: Any, delay_ms: int = 0) -> None:
        if self.window is None:
            return
        self.window.after(max(0, int(delay_ms)), lambda: callback(*args))

    def schedule_interval(self, callback: Callable[[], None], seconds: float) -> None:
        if self.window is None:
            return
        interval_ms = max(1000, int(seconds * 1000))

        def runner() -> None:
            if self.window is None:
                return
            callback()
            self.window.after(interval_ms, runner)

        self.window.after(interval_ms, runner)

    def clone_med_snapshot(self, med: Dict[str, Any]) -> Dict[str, Any]:
        return json.loads(json.dumps(med))

    def clone_data_snapshot(self) -> Dict[str, Any]:
        return ensure_vault_shape(json.loads(json.dumps(self.data_cache)))

    def save_data_async(self, snapshot: Optional[Dict[str, Any]] = None) -> None:
        if not self.vault:
            return
        if self.vault_write_blocked_reason:
            self.assistant_history_dirty = True
            if self.main_ui_started:
                self.set_status(self.vault_write_blocked_reason)
            return
        self.assistant_history_dirty = False
        self.background_save_request_id += 1
        request_id = self.background_save_request_id
        prepared_snapshot = ensure_vault_shape(json.loads(json.dumps(snapshot if snapshot is not None else self.data_cache)))

        def worker() -> None:
            if request_id != self.background_save_request_id or not self.vault:
                return
            try:
                self.vault.save(prepared_snapshot)
            except Exception as exc:
                self.assistant_history_dirty = True
                self.run_on_ui_thread(self._handle_save_error, str(exc), False)
                return

        threading.Thread(target=worker, daemon=True).start()

    def persist_data_async(self) -> None:
        self.save_data_async()

    def apply_text_size_setting(self, text_size: Optional[str] = None) -> None:
        choice = normalize_setting_choice(text_size or self.settings_data.get("text_size"), TEXT_SIZE_OPTIONS, "Default")
        self.settings_data["text_size"] = choice
        if ctk is None:
            return
        try:
            ctk.set_widget_scaling(TEXT_SIZE_SCALE_MAP.get(choice, 1.0))
        except Exception:
            pass

    def _handle_save_error(self, message: str, show_dialog: bool = True) -> None:
        clean = sanitize_text(message, max_chars=260)
        if self.main_ui_started:
            self.set_status(clean)
        if show_dialog and self.window is not None:
            self.show_dialog("Save Failed", clean)

    def _cleanup_dose_safety_process(self, *, terminate: bool = False) -> None:
        process = self.dose_ai_process
        queue_obj = self.dose_ai_queue
        self.dose_ai_process = None
        self.dose_ai_queue = None
        if process is not None:
            try:
                if terminate and process.is_alive():
                    process.terminate()
            except Exception:
                pass
            try:
                process.join(timeout=0.2)
            except Exception:
                pass
        if queue_obj is not None:
            try:
                queue_obj.close()
            except Exception:
                pass
            try:
                queue_obj.join_thread()
            except Exception:
                pass

    def _cleanup_safety_scan_process(self, *, terminate: bool = False) -> None:
        process = self.safety_scan_process
        queue_obj = self.safety_scan_queue
        self.safety_scan_process = None
        self.safety_scan_queue = None
        if process is not None:
            try:
                if terminate and process.is_alive():
                    process.terminate()
            except Exception:
                pass
            try:
                process.join(timeout=0.2)
            except Exception:
                pass
        if queue_obj is not None:
            try:
                queue_obj.close()
            except Exception:
                pass
            try:
                queue_obj.join_thread()
            except Exception:
                pass

    def _cleanup_assistant_process(self, *, terminate: bool = False) -> None:
        process = self.assistant_process
        queue_obj = self.assistant_queue
        self.assistant_process = None
        self.assistant_queue = None
        if process is not None:
            try:
                if terminate and process.is_alive():
                    process.terminate()
            except Exception:
                pass
            try:
                process.join(timeout=0.2)
            except Exception:
                pass
        if queue_obj is not None:
            try:
                queue_obj.close()
            except Exception:
                pass
            try:
                queue_obj.join_thread()
            except Exception:
                pass

    def _saved_dose_safety_review(
        self,
        med: Dict[str, Any],
        dose_value: float,
        source_label: str,
        *,
        action: str,
        display: str,
        message: str,
        raw: str = "",
        quantum_level: str = "",
        quantum_score: float = 0.0,
        deterministic_level: str = "",
        deterministic_message: str = "",
    ) -> Dict[str, Any]:
        review = dose_safety_review_defaults()
        review.update(
            {
                "timestamp": time.time(),
                "med_id": sanitize_text(med.get("id") or "", max_chars=32),
                "med_name": sanitize_text(med.get("name") or "Medication", max_chars=120),
                "dose_mg": max(0.0, safe_float(dose_value)),
                "source_label": sanitize_text(source_label, max_chars=60),
                "action": normalize_dose_action_text(action, ""),
                "display": sanitize_text(display, max_chars=160),
                "message": sanitize_text(message, max_chars=420),
                "raw": sanitize_text(raw, max_chars=400),
                "quantum_level": sanitize_text(quantum_level, max_chars=40),
                "quantum_score": max(0.0, min(100.0, safe_float(quantum_score))),
                "deterministic_level": sanitize_text(deterministic_level, max_chars=40),
                "deterministic_message": sanitize_text(deterministic_message, max_chars=260),
            }
        )
        return review

    def _restore_saved_dose_safety_review(self) -> None:
        review = dict(self.data_cache.get("dose_safety_review") or {})
        if safe_float(review.get("timestamp")) <= 0:
            return
        action = normalize_dose_action_text(review.get("action") or "", "")
        if action:
            self.last_check_level = action
        display = sanitize_text(review.get("display") or "", max_chars=160)
        message = sanitize_text(review.get("message") or "", max_chars=420)
        if display:
            self.last_check_display = display
        if message:
            self.last_check_message = message

    def start_dose_safety_assessment(self, med: Dict[str, Any], dose_value: float, *, source_label: str = "dose") -> None:
        med_snapshot = self.clone_med_snapshot(med)
        now_ts = time.time()
        self.dose_ai_request_id += 1
        request_id = self.dose_ai_request_id
        med_name = sanitize_text(med_snapshot.get("name") or "Medication", max_chars=120)
        self._cleanup_dose_safety_process(terminate=True)
        self.last_check_level = "Assessing"
        self.last_check_display = "Dose safety AI"
        self.last_check_message = f"Assessing {med_name} with the local model..."
        self.refresh_dashboard()
        if not self.vault:
            self.run_on_ui_thread(
                self._dose_safety_assessment_failed,
                request_id,
                med_snapshot,
                dose_value,
                now_ts,
                f"{source_label}: vault unavailable",
            )
            return
        settings = dict(self.settings_data)

        def launcher() -> None:
            try:
                if not self.vault:
                    raise RuntimeError("Dose safety vault unavailable.")
                key = self.vault.get_or_create_key()
                ctx = mp.get_context("spawn")
                result_queue = ctx.Queue()
                process = ctx.Process(
                    target=medication_plan_process_worker,
                    args=(result_queue, key, med_snapshot, now_ts, settings),
                    daemon=True,
                )
                process.start()
                self.run_on_ui_thread(
                    self._dose_safety_process_started,
                    request_id,
                    process,
                    result_queue,
                    med_snapshot,
                    dose_value,
                    now_ts,
                    source_label,
                )
            except Exception as exc:
                self.run_on_ui_thread(self._dose_safety_assessment_failed, request_id, med_snapshot, dose_value, now_ts, str(exc))

        threading.Thread(target=launcher, daemon=True).start()

    def _dose_safety_process_started(
        self,
        request_id: int,
        process: Any,
        result_queue: Any,
        med: Dict[str, Any],
        dose_value: float,
        now_ts: float,
        source_label: str,
    ) -> None:
        if request_id != self.dose_ai_request_id:
            try:
                if process.is_alive():
                    process.terminate()
            except Exception:
                pass
            try:
                result_queue.close()
            except Exception:
                pass
            return
        self.dose_ai_process = process
        self.dose_ai_queue = result_queue
        self.run_on_ui_thread(self._poll_dose_safety_process, request_id, med, dose_value, now_ts, source_label, delay_ms=120)

    def _poll_dose_safety_process(
        self,
        request_id: int,
        med: Dict[str, Any],
        dose_value: float,
        now_ts: float,
        source_label: str,
    ) -> None:
        if request_id != self.dose_ai_request_id:
            self._cleanup_dose_safety_process(terminate=True)
            return
        process = self.dose_ai_process
        result_queue = self.dose_ai_queue
        if process is None or result_queue is None:
            self._dose_safety_assessment_failed(request_id, med, dose_value, now_ts, "Dose safety worker did not start.")
            return
        try:
            payload = result_queue.get_nowait()
        except queue.Empty:
            try:
                alive = process.is_alive()
            except Exception:
                alive = False
            if alive:
                self.run_on_ui_thread(self._poll_dose_safety_process, request_id, med, dose_value, now_ts, source_label, delay_ms=120)
            else:
                self._cleanup_dose_safety_process(terminate=False)
                self._dose_safety_assessment_failed(request_id, med, dose_value, now_ts, "Dose safety worker ended unexpectedly.")
            return
        self._cleanup_dose_safety_process(terminate=False)
        if payload.get("ok"):
            self._dose_safety_assessment_done(request_id, med, dose_value, source_label, dict(payload.get("result") or {}))
        else:
            self._dose_safety_assessment_failed(
                request_id,
                med,
                dose_value,
                now_ts,
                sanitize_text(payload.get("error") or "Dose safety worker failed.", max_chars=240),
            )

    def _dose_safety_assessment_done(
        self,
        request_id: int,
        med: Dict[str, Any],
        dose_value: float,
        source_label: str,
        result: Dict[str, Any],
    ) -> None:
        if request_id != self.dose_ai_request_id:
            return
        self.last_check_level = result.get("action") or "Caution"
        self.last_check_display = sanitize_text(result.get("display") or "Dose safety AI", max_chars=160)
        self.last_check_message = sanitize_text(result.get("message") or "Dose safety review updated.", max_chars=420)
        self.data_cache["dose_safety_review"] = self._saved_dose_safety_review(
            med,
            dose_value,
            source_label,
            action=result.get("action") or "",
            display=self.last_check_display,
            message=self.last_check_message,
            raw=result.get("raw") or "",
            quantum_level=result.get("quantum_level") or "",
            quantum_score=safe_float(result.get("quantum_score") or 0.0),
            deterministic_level=result.get("deterministic_level") or "",
            deterministic_message=result.get("deterministic_message") or "",
        )
        self.save_data_async()
        self.refresh_dashboard()
        self.set_status(self.last_check_message)

    def _dose_safety_assessment_failed(self, request_id: int, med: Dict[str, Any], dose_value: float, now_ts: float, error_text: str) -> None:
        if request_id != self.dose_ai_request_id:
            return
        snapshot = medication_safety_snapshot(med, now_ts, source_label="manual plan check")
        action = normalize_dose_action_text(snapshot.get("action") or "Caution")
        self.last_check_level = action
        self.last_check_display = f"Dose safety AI: {action}"
        fallback_message = sanitize_text(snapshot.get("message") or "Stored schedule review updated.", max_chars=320)
        if error_text:
            fallback_message += " Local model unavailable, so this used the stored schedule rules."
        self.last_check_message = sanitize_text(fallback_message, max_chars=420)
        self.data_cache["dose_safety_review"] = self._saved_dose_safety_review(
            med,
            dose_value,
            "fallback",
            action=action,
            display=self.last_check_display,
            message=self.last_check_message,
            deterministic_level=sanitize_text(snapshot.get("action") or "", max_chars=40),
            deterministic_message=sanitize_text(snapshot.get("message") or "", max_chars=260),
        )
        self.save_data_async()
        self.refresh_dashboard()
        self.set_status(self.last_check_message)

    def _safety_scan_process_started(self, request_id: int, process: Any, result_queue: Any, announce: bool = False) -> None:
        if request_id != self.safety_scan_request_id:
            try:
                if process.is_alive():
                    process.terminate()
            except Exception:
                pass
            try:
                result_queue.close()
            except Exception:
                pass
            return
        self.safety_scan_process = process
        self.safety_scan_queue = result_queue
        self.run_on_ui_thread(self._poll_safety_scan_process, request_id, announce, delay_ms=140)

    def _poll_safety_scan_process(self, request_id: int, announce: bool = False) -> None:
        if request_id != self.safety_scan_request_id:
            self._cleanup_safety_scan_process(terminate=True)
            return
        process = self.safety_scan_process
        result_queue = self.safety_scan_queue
        if process is None or result_queue is None:
            self._safety_scan_failed(request_id, "Safety scan worker did not start.", announce)
            return
        try:
            payload = result_queue.get_nowait()
        except queue.Empty:
            try:
                alive = process.is_alive()
            except Exception:
                alive = False
            if alive:
                self.run_on_ui_thread(self._poll_safety_scan_process, request_id, announce, delay_ms=140)
            else:
                self._cleanup_safety_scan_process(terminate=False)
                self._safety_scan_failed(request_id, "Safety scan worker ended unexpectedly.", announce)
            return
        self._cleanup_safety_scan_process(terminate=False)
        if payload.get("ok"):
            self._safety_scan_done(request_id, dict(payload.get("result") or {}), announce)
        else:
            self._safety_scan_failed(
                request_id,
                sanitize_text(payload.get("error") or "Safety scan worker failed.", max_chars=240),
                announce,
            )

    def _register(self, name: str, adapter: Any) -> Any:
        self.ids[name] = adapter
        return adapter

    def _card(self, parent: Any) -> Any:
        return ctk.CTkFrame(
            parent,
            fg_color=DESKTOP_SURFACE,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=18,
        )

    def _readonly_box(self, parent: Any, *, height: int) -> DesktopTextboxAdapter:
        widget = ctk.CTkTextbox(
            parent,
            height=height,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
            wrap="word",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=13),
        )
        widget.configure(state="disabled")
        return DesktopTextboxAdapter(widget, readonly=True)

    def _edit_box(self, parent: Any, *, height: int) -> DesktopTextboxAdapter:
        widget = ctk.CTkTextbox(
            parent,
            height=height,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
            wrap="word",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=13),
        )
        return DesktopTextboxAdapter(widget, readonly=False)

    def _entry(self, parent: Any, *, placeholder: str) -> DesktopEntryAdapter:
        widget = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            fg_color=DESKTOP_SURFACE_ALT,
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
            corner_radius=12,
            height=38,
        )
        return DesktopEntryAdapter(widget)

    def _password_entry(self, parent: Any, *, placeholder: str) -> DesktopEntryAdapter:
        widget = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            show="*",
            fg_color=DESKTOP_SURFACE_ALT,
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
            corner_radius=12,
            height=42,
        )
        return DesktopEntryAdapter(widget)

    def _label(self, parent: Any, *, text: str, bold: bool = False, muted: bool = False, wrap: int = 0) -> DesktopLabelAdapter:
        widget = ctk.CTkLabel(
            parent,
            text=text,
            anchor="w",
            justify="left",
            wraplength=wrap,
            text_color=DESKTOP_MUTED if muted else DESKTOP_TEXT,
            font=ctk.CTkFont(size=14, weight="bold" if bold else "normal"),
        )
        return DesktopLabelAdapter(widget)

    def _button(self, parent: Any, *, text: str, command: Callable[[], None], tone: str = "accent") -> Any:
        fg_map = {
            "accent": DESKTOP_ACCENT,
            "secondary": "#2f4656",
            "neutral": "#314455",
            "danger": DESKTOP_DANGER,
            "warning": "#b8801f",
        }
        hover_map = {
            "accent": "#0d6b63",
            "secondary": "#3f5c70",
            "neutral": "#42586c",
            "danger": "#b84e58",
            "warning": "#936513",
        }
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=fg_map.get(tone, DESKTOP_ACCENT),
            hover_color=hover_map.get(tone, "#0d6b63"),
            corner_radius=12,
            height=38,
            text_color=DESKTOP_TEXT,
        )

    def _reset_ids(self) -> None:
        self.root = SimpleNamespace(ids=DesktopIdMap())
        self.ids = self.root.ids

    def _clear_window_content(self) -> None:
        if self.window is None:
            return
        for child in self.window.winfo_children():
            child.destroy()
        self._reset_ids()
        self.window.grid_columnconfigure(0, weight=1)

    def _set_start_screen_status(self, widget_id: str, text: str) -> None:
        label = self.ids.get(widget_id)
        if label is not None:
            label.text = sanitize_text(text, max_chars=260)

    def _save_security_settings(self) -> None:
        if not self.paths or not self.vault:
            return
        save_settings(
            {
                "setup_complete": True,
                "startup_password_enabled": self.vault.is_key_protected(),
            },
            self.paths,
        )
        self.settings_data = load_settings(self.paths)

    def _sync_setup_password_fields(self) -> None:
        enabled = bool(self.setup_password_var.get()) if self.setup_password_var is not None else False
        for widget_id in ("setup_password", "setup_password_confirm"):
            widget = self.ids.get(widget_id)
            if widget is None:
                continue
            if not enabled:
                try:
                    widget.widget.configure(state="normal")
                except Exception:
                    pass
                widget.text = ""
            try:
                widget.widget.configure(state="normal" if enabled else "disabled")
            except Exception:
                pass

    def _startup_gate_required(self) -> bool:
        if not self.vault:
            return False
        key_status = self.vault.key_status()
        if key_status == "protected":
            return True
        return key_status in {"raw", "missing"} and bool(self.settings_data.get("startup_password_enabled", False))

    def _startup_gate_satisfied(self) -> bool:
        if not self._startup_gate_required() or not self.vault:
            return True
        return self.vault.key_status() == "protected" and self.vault.is_unlocked()

    def _build_startup_gate(self) -> None:
        if not self.vault:
            return
        if self.vault.key_status() == "protected":
            self.vault.clear_cached_key()
            self._build_unlock_flow()
            return
        self._build_startup_password_repair_flow()

    def _build_first_boot_flow(self) -> None:
        if self.window is None:
            return
        self._clear_window_content()
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)

        shell = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        shell.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)
        shell.grid_columnconfigure(0, weight=1)

        hero = self._card(shell)
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        hero.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            hero,
            text="Welcome to MedSafe Desktop",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(22, 8))
        ctk.CTkLabel(
            hero,
            text=(
                "Let's set up your encrypted medication vault, startup protection, and optional offline Gemma runtime "
                "before you land in the main dashboard."
            ),
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 8))
        ctk.CTkLabel(
            hero,
            text=f"Vault location: {self.paths.root if self.paths else default_storage_root()}",
            anchor="w",
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="w", padx=22, pady=(0, 22))

        security = self._card(shell)
        security.grid(row=1, column=0, sticky="ew", pady=12)
        security.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(
            security,
            text="Startup Security",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(22, 8))
        ctk.CTkLabel(
            security,
            text=(
                "If you enable a startup password, MedSafe wraps the local encryption key and asks for it "
                "before opening your vault on future launches."
            ),
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=22, pady=(0, 12))

        self.setup_password_var = tk.BooleanVar(value=False)
        password_toggle = ctk.CTkCheckBox(
            security,
            text="Require a startup password when opening MedSafe",
            variable=self.setup_password_var,
            onvalue=True,
            offvalue=False,
            command=self._sync_setup_password_fields,
            fg_color=DESKTOP_ACCENT,
            hover_color="#0d6b63",
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        password_toggle.grid(row=2, column=0, columnspan=2, sticky="w", padx=22, pady=(0, 14))

        password_entry = self._password_entry(security, placeholder="Create startup password")
        password_entry.widget.grid(row=3, column=0, sticky="ew", padx=(22, 10), pady=(0, 12))
        self._register("setup_password", password_entry)

        confirm_entry = self._password_entry(security, placeholder="Confirm startup password")
        confirm_entry.widget.grid(row=3, column=1, sticky="ew", padx=(10, 22), pady=(0, 12))
        self._register("setup_password_confirm", confirm_entry)

        security_status = self._label(
            security,
            text="You can skip the password now and add or rotate security later from the Settings tab.",
            muted=True,
            wrap=980,
        )
        security_status.widget.grid(row=4, column=0, columnspan=2, sticky="ew", padx=22, pady=(0, 22))
        self._register("setup_status_label", security_status)

        runtime = self._card(shell)
        runtime.grid(row=2, column=0, sticky="ew", pady=12)
        runtime.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            runtime,
            text="Offline Gemma Runtime",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(22, 8))
        ctk.CTkLabel(
            runtime,
            text=(
                "You can download and seal the local LLM during setup so bottle-photo review and assistant tools "
                "are ready right away, or skip it and do it later."
            ),
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 12))
        self.setup_download_model_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            runtime,
            text="Download Gemma 4 now after setup completes",
            variable=self.setup_download_model_var,
            onvalue=True,
            offvalue=False,
            fg_color=DESKTOP_ACCENT,
            hover_color="#0d6b63",
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=2, column=0, sticky="w", padx=22, pady=(0, 10))
        ctk.CTkLabel(
            runtime,
            text="The model stays sealed on disk and can still be verified or re-downloaded later from the Settings tab.",
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 22))

        actions = ctk.CTkFrame(shell, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        actions.grid_columnconfigure((0, 1), weight=1)
        self._button(actions, text="Create Secure Vault", command=self._complete_first_boot).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        self._button(actions, text="Open With Defaults", command=lambda: self._complete_first_boot(force_skip_password=True), tone="neutral").grid(
            row=0, column=1, sticky="ew", padx=(8, 0)
        )

        self._sync_setup_password_fields()

    def _complete_first_boot(self, force_skip_password: bool = False) -> None:
        if not self.vault:
            return
        use_password = bool(self.setup_password_var.get()) if self.setup_password_var is not None else False
        if force_skip_password:
            use_password = False
        try:
            if use_password:
                password = sanitize_text(self.ids.setup_password.text, max_chars=256)
                confirm = sanitize_text(self.ids.setup_password_confirm.text, max_chars=256)
                if len(password) < 6:
                    self._set_start_screen_status("setup_status_label", "Choose a startup password with at least 6 characters.")
                    return
                if password != confirm:
                    self._set_start_screen_status("setup_status_label", "Startup password and confirmation do not match yet.")
                    return
                self.vault.get_or_create_key(password=password)
            else:
                self.vault.get_or_create_key()
            self._save_security_settings()
            download_now = bool(self.setup_download_model_var.get()) if self.setup_download_model_var is not None else False
            self._enter_main_app(start_model_download=download_now)
            self.set_status(
                "Setup complete. Starting Gemma 4 download..." if download_now else "Setup complete. Your local vault is ready."
            )
        except Exception as exc:
            self._set_start_screen_status("setup_status_label", str(exc))

    def _build_unlock_flow(self) -> None:
        if self.window is None:
            return
        self._clear_window_content()
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)

        shell = ctk.CTkFrame(self.window, fg_color="transparent")
        shell.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        card = self._card(shell)
        card.grid(row=0, column=0, sticky="n", pady=40)
        card.grid_columnconfigure(0, weight=1)
        card.configure(width=720)

        ctk.CTkLabel(
            card,
            text="MedSafe Is Locked",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            card,
            text=(
                "Startup password is required for this launch. Unlock to open your encrypted medication data, "
                "assistant history, and sealed model tools for this session."
            ),
            anchor="w",
            justify="left",
            wraplength=620,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        ctk.CTkLabel(
            card,
            text=f"Vault location: {self.paths.root if self.paths else default_storage_root()}",
            anchor="w",
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(0, 18))

        locked_status = self._label(
            card,
            text="The app asks once per launch while startup password is enabled in Settings.",
            muted=True,
            wrap=620,
        )
        locked_status.widget.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))
        self._register("unlock_status_label", locked_status)

        self._button(card, text="Enter Startup Password", command=self._show_unlock_popup).grid(
            row=4, column=0, sticky="ew", padx=24, pady=(0, 24)
        )
        self.run_on_ui_thread(self._show_unlock_popup, delay_ms=80)

    def _build_startup_password_repair_flow(self) -> None:
        if self.window is None:
            return
        self._clear_window_content()
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=0)

        shell = ctk.CTkFrame(self.window, fg_color="transparent")
        shell.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        card = self._card(shell)
        card.grid(row=0, column=0, sticky="n", pady=40)
        card.grid_columnconfigure(0, weight=1)
        card.configure(width=720)

        ctk.CTkLabel(
            card,
            text="Startup Protection Needs Repair",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            card,
            text=(
                "Settings require a startup password, but the local key is not password-wrapped. "
                "Set a startup password before MedSafe opens the encrypted vault for this session."
            ),
            anchor="w",
            justify="left",
            wraplength=620,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        ctk.CTkLabel(
            card,
            text=f"Vault location: {self.paths.root if self.paths else default_storage_root()}",
            anchor="w",
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(0, 18))
        status = self._label(
            card,
            text="The dashboard stays closed until startup protection is repaired.",
            muted=True,
            wrap=620,
        )
        status.widget.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))
        self._register("startup_repair_status_label", status)
        self._button(card, text="Set Startup Password", command=self._show_startup_password_repair_popup).grid(
            row=4, column=0, sticky="ew", padx=24, pady=(0, 24)
        )
        self.run_on_ui_thread(self._show_startup_password_repair_popup, delay_ms=80)

    def _drop_popup_topmost(self, popup: Any) -> None:
        try:
            popup.attributes("-topmost", False)
        except Exception:
            pass

    def _show_unlock_popup(self) -> None:
        if self.window is None:
            return
        if self.unlock_popup is not None:
            try:
                self.unlock_popup.lift()
                self.unlock_popup.focus_force()
                return
            except Exception:
                self.unlock_popup = None

        popup = ctk.CTkToplevel(self.window)
        self.unlock_popup = popup
        popup.title("Unlock MedSafe")
        popup.configure(fg_color=DESKTOP_BG)
        popup.resizable(False, False)
        popup.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            popup.transient(self.window)
        except Exception:
            pass

        width = 560
        height = 340
        try:
            root_x = int(self.window.winfo_rootx())
            root_y = int(self.window.winfo_rooty())
            root_w = int(self.window.winfo_width())
            root_h = int(self.window.winfo_height())
            x = root_x + max(0, (root_w - width) // 2)
            y = root_y + max(0, (root_h - height) // 3)
            popup.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            popup.geometry(f"{width}x{height}")
        try:
            popup.lift()
            popup.focus_force()
            popup.attributes("-topmost", True)
            popup.after(450, lambda: self._drop_popup_topmost(popup))
        except Exception:
            pass
        try:
            popup.grab_set()
        except Exception:
            pass

        popup.grid_columnconfigure(0, weight=1)
        card = self._card(popup)
        card.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Unlock MedSafe",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))
        ctk.CTkLabel(
            card,
            text="Enter the startup password once for this app launch.",
            anchor="w",
            justify="left",
            wraplength=480,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 14))

        unlock_entry = self._password_entry(card, placeholder="Startup password")
        unlock_entry.widget.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 12))
        self._register("unlock_password", unlock_entry)
        try:
            unlock_entry.widget.bind("<Return>", lambda _event: (self._unlock_startup_password(), "break")[1])
        except Exception:
            pass

        unlock_status = self._label(
            card,
            text="Your local vault stays closed until this password unlocks the session.",
            muted=True,
            wrap=480,
        )
        unlock_status.widget.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 14))
        self._register("unlock_status_label", unlock_status)

        unlock_buttons = ctk.CTkFrame(card, fg_color="transparent")
        unlock_buttons.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        unlock_buttons.grid_columnconfigure((0, 1), weight=1)
        self._button(unlock_buttons, text="Unlock And Open Dashboard", command=self._unlock_startup_password).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        self._button(unlock_buttons, text="Exit", command=self.on_close, tone="neutral").grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )
        try:
            popup.after(120, lambda: unlock_entry.widget.focus_set())
        except Exception:
            pass

    def _show_startup_password_repair_popup(self) -> None:
        if self.window is None:
            return
        if self.unlock_popup is not None:
            try:
                self.unlock_popup.lift()
                self.unlock_popup.focus_force()
                return
            except Exception:
                self.unlock_popup = None

        popup = ctk.CTkToplevel(self.window)
        self.unlock_popup = popup
        popup.title("Set Startup Password")
        popup.configure(fg_color=DESKTOP_BG)
        popup.resizable(False, False)
        popup.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            popup.transient(self.window)
        except Exception:
            pass

        width = 600
        height = 410
        try:
            root_x = int(self.window.winfo_rootx())
            root_y = int(self.window.winfo_rooty())
            root_w = int(self.window.winfo_width())
            root_h = int(self.window.winfo_height())
            x = root_x + max(0, (root_w - width) // 2)
            y = root_y + max(0, (root_h - height) // 3)
            popup.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            popup.geometry(f"{width}x{height}")
        try:
            popup.lift()
            popup.focus_force()
            popup.attributes("-topmost", True)
            popup.after(450, lambda: self._drop_popup_topmost(popup))
        except Exception:
            pass
        try:
            popup.grab_set()
        except Exception:
            pass

        popup.grid_columnconfigure(0, weight=1)
        card = self._card(popup)
        card.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text="Set Startup Password",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 8))
        ctk.CTkLabel(
            card,
            text="MedSafe will wrap the local vault key before opening the dashboard.",
            anchor="w",
            justify="left",
            wraplength=520,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 14))

        password_entry = self._password_entry(card, placeholder="Create startup password")
        password_entry.widget.grid(row=2, column=0, sticky="ew", padx=(20, 8), pady=(0, 12))
        self._register("startup_repair_password", password_entry)
        confirm_entry = self._password_entry(card, placeholder="Confirm startup password")
        confirm_entry.widget.grid(row=2, column=1, sticky="ew", padx=(8, 20), pady=(0, 12))
        self._register("startup_repair_password_confirm", confirm_entry)
        for entry in (password_entry, confirm_entry):
            try:
                entry.widget.bind("<Return>", lambda _event: (self._repair_startup_password_and_open(), "break")[1])
            except Exception:
                pass

        repair_status = self._label(
            card,
            text="Use at least 6 characters. The vault stays closed until this is saved.",
            muted=True,
            wrap=520,
        )
        repair_status.widget.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 14))
        self._register("startup_repair_status_label", repair_status)

        repair_buttons = ctk.CTkFrame(card, fg_color="transparent")
        repair_buttons.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        repair_buttons.grid_columnconfigure((0, 1), weight=1)
        self._button(repair_buttons, text="Save Password And Open", command=self._repair_startup_password_and_open).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        self._button(repair_buttons, text="Exit", command=self.on_close, tone="neutral").grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )
        try:
            popup.after(120, lambda: password_entry.widget.focus_set())
        except Exception:
            pass

    def _close_unlock_popup(self) -> None:
        popup = self.unlock_popup
        self.unlock_popup = None
        if popup is None:
            return
        try:
            popup.grab_release()
        except Exception:
            pass
        try:
            popup.destroy()
        except Exception:
            pass

    def _unlock_startup_password(self) -> None:
        if not self.vault:
            return
        password = sanitize_text(self.ids.unlock_password.text, max_chars=256)
        if not password:
            self._set_start_screen_status("unlock_status_label", "Enter the startup password to unlock this vault.")
            return
        try:
            self.vault.get_or_create_key(password=password, allow_create=False)
            self._save_security_settings()
            self._close_unlock_popup()
            self._enter_main_app()
        except Exception:
            self.ids.unlock_password.text = ""
            self._set_start_screen_status("unlock_status_label", "That password did not unlock the encrypted vault. Please try again.")

    def _repair_startup_password_and_open(self) -> None:
        if not self.vault:
            return
        password = sanitize_text(getattr(self.ids.get("startup_repair_password"), "text", ""), max_chars=256)
        confirm = sanitize_text(getattr(self.ids.get("startup_repair_password_confirm"), "text", ""), max_chars=256)
        if len(password) < 6:
            self._set_start_screen_status("startup_repair_status_label", "Choose a startup password with at least 6 characters.")
            return
        if password != confirm:
            self._set_start_screen_status("startup_repair_status_label", "Startup password and confirmation do not match yet.")
            return
        try:
            if self.vault.key_status() not in {"raw", "missing"}:
                self._close_unlock_popup()
                self._build_startup_gate()
                return
            self.vault.enable_password(password)
            self._save_security_settings()
            self._close_unlock_popup()
            self._enter_main_app()
            self.set_status("Startup password repaired and vault unlocked for this session.")
        except Exception:
            if "startup_repair_password" in self.ids:
                self.ids.startup_repair_password.text = ""
            if "startup_repair_password_confirm" in self.ids:
                self.ids.startup_repair_password_confirm.text = ""
            self._set_start_screen_status("startup_repair_status_label", "Could not wrap the vault key. Please try again.")

    def _enter_main_app(self, *, start_model_download: bool = False) -> None:
        if self.window is None:
            return
        if not self._startup_gate_satisfied():
            self._build_startup_gate()
            return
        self._clear_window_content()
        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=1)
        self._build_layout()
        self.main_ui_started = True
        self.refresh_from_disk()
        if hasattr(self, "sync_text_size_widgets"):
            try:
                self.sync_text_size_widgets()
            except Exception:
                pass
        if self.startup_temp_cleanup_message:
            self.set_status(self.startup_temp_cleanup_message)
            self.startup_temp_cleanup_message = ""
        if not self.refresh_timer_started:
            self.schedule_interval(self.refresh_time_sensitive_labels, 60.0)
            self.refresh_timer_started = True
        if start_model_download:
            self.run_on_ui_thread(self.on_model_download, delay_ms=250)

    def _prompt_password(self, title: str, prompt: str) -> Optional[str]:
        if self.window is None:
            return None
        value = simpledialog.askstring(title, prompt, parent=self.window, show="*")
        if value is None:
            return None
        return sanitize_text(value, max_chars=256)

    def _prompt_new_password(self, title: str) -> Optional[str]:
        first = self._prompt_password(title, "Enter the new startup password:")
        if first is None:
            return None
        second = self._prompt_password(title, "Confirm the new startup password:")
        if second is None:
            return None
        if len(first) < 6:
            self.show_dialog("Password Too Short", "Use at least 6 characters for the startup password.")
            return None
        if first != second:
            self.show_dialog("Password Mismatch", "The startup password confirmation did not match.")
            return None
        return first

    def _prompt_current_password_if_needed(self, title: str) -> Optional[str]:
        if not self.vault or not self.vault.is_key_protected():
            return None
        return self._prompt_password(title, "Enter the current startup password:")

    def _build_blocked_startup(self, title: str, message: str) -> None:
        if self.window is None:
            raise RuntimeError(message)
        frame = ctk.CTkFrame(self.window, fg_color=DESKTOP_SURFACE, corner_radius=18)
        frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=title, text_color=DESKTOP_DANGER, font=ctk.CTkFont(size=26, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=24, pady=(24, 12)
        )
        ctk.CTkLabel(frame, text=message, text_color=DESKTOP_TEXT, justify="left", wraplength=860).grid(
            row=1, column=0, sticky="ew", padx=24, pady=(0, 18)
        )
        self._button(frame, text="Close", command=self.on_close, tone="warning").grid(row=2, column=0, sticky="w", padx=24, pady=(0, 24))

    def _build_layout(self) -> None:
        if self.window is None:
            return

        header = self._card(self.window)
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(8, 4))
        header.grid_columnconfigure(0, weight=1)

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="ew", padx=18, pady=(8, 10))
        title_block.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_block,
            text="MedSafe Desktop",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        try:
            self.window.bind("<Control-k>", lambda _event: (self.show_command_palette(), "break")[1])
            self.window.bind("<Control-K>", lambda _event: (self.show_command_palette(), "break")[1])
        except Exception:
            pass

        tabview = ctk.CTkTabview(
            self.window,
            fg_color=DESKTOP_SURFACE,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=18,
            segmented_button_fg_color=DESKTOP_SURFACE_ALT,
            segmented_button_selected_color=DESKTOP_ACCENT,
            segmented_button_selected_hover_color="#0d6b63",
            segmented_button_unselected_color="#314455",
            segmented_button_unselected_hover_color="#223443",
            text_color=DESKTOP_TEXT,
            text_color_disabled=DESKTOP_MUTED,
        )
        tabview.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        try:
            tabview.configure(
                segmented_button_fg_color=DESKTOP_SURFACE_ALT,
                segmented_button_selected_color=DESKTOP_ACCENT,
                segmented_button_selected_hover_color="#0d6b63",
                segmented_button_unselected_color="#314455",
                segmented_button_unselected_hover_color="#223443",
                text_color=DESKTOP_TEXT,
                text_color_disabled=DESKTOP_MUTED,
            )
        except Exception:
            pass

        self.ids["main_tabs"] = tabview

        for tab_name in ("Dashboard", "Medications", "Safety", "Pill Bottle Scanner", "Dental", "Exercise", "Recovery", "Chat", "Help", "Settings"):
            tabview.add(tab_name)

        self._build_dashboard_tab(tabview.tab("Dashboard"))
        self._build_medications_tab(tabview.tab("Medications"))
        self._build_safety_tab(tabview.tab("Safety"))
        self._build_vision_tab(tabview.tab("Pill Bottle Scanner"))
        self._build_dental_tab(tabview.tab("Dental"))
        self._build_exercise_tab(tabview.tab("Exercise"))
        self._build_recovery_tab(tabview.tab("Recovery"))
        self._build_assistant_tab(tabview.tab("Chat"))
        self._build_help_tab(tabview.tab("Help"))
        self._build_model_tab(tabview.tab("Settings"))

    def _build_dashboard_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure((0, 1), weight=1)

        left = ctk.CTkFrame(scroll, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=14)
        left.grid_columnconfigure(0, weight=1)

        compass_card = self._card(left)
        compass_card.grid(row=0, column=0, sticky="nsew", pady=(0, 7))
        compass_card.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(
            compass_card,
            text="Care Compass",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 8))
        compass_action = self._label(
            compass_card,
            text="Your best next step will appear here.",
            muted=True,
            wrap=520,
        )
        compass_action.widget.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))
        self._register("care_compass_action", compass_action)
        for row, (left_id, left_title, right_id, right_title) in enumerate(
            (
                ("care_compass_meds", "Meds", "care_compass_safety", "Safety"),
                ("care_compass_routines", "Routines", "care_compass_days_clean", "Days Clean"),
            ),
            start=2,
        ):
            for column, widget_id, title in ((0, left_id, left_title), (1, right_id, right_title)):
                tile = ctk.CTkFrame(
                    compass_card,
                    fg_color=DESKTOP_SURFACE_ALT,
                    border_width=1,
                    border_color=DESKTOP_BORDER,
                    corner_radius=12,
                )
                tile.grid(row=row, column=column, sticky="ew", padx=(18 if column == 0 else 6, 6 if column == 0 else 18), pady=(0, 8))
                tile.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    tile,
                    text=title,
                    anchor="w",
                    text_color=DESKTOP_MUTED,
                    font=ctk.CTkFont(size=12, weight="bold"),
                ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
                value_label = self._label(tile, text="Ready", bold=True, wrap=220)
                value_label.widget.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
                self._register(widget_id, value_label)
        # Removed dashboard action button; the checklist and activity feed are the primary actions now.

        risk_card = self._card(left)
        risk_card.grid(row=1, column=0, sticky="nsew", pady=7)
        risk_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            risk_card,
            text="Dose Safety",
            anchor="w",
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        risk_badge_widget = ctk.CTkLabel(
            risk_card,
            text="Safety Medium",
            fg_color=DESKTOP_WARNING,
            text_color="#08110f",
            corner_radius=18,
            width=170,
            height=44,
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        risk_badge_widget.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))
        self._register("dose_wheel", DesktopRiskBadgeAdapter(risk_badge_widget))

        risk_title = self._label(risk_card, text="Awaiting check", bold=True, wrap=420)
        risk_title.widget.grid(row=2, column=0, sticky="ew", padx=18)
        self._register("dashboard_risk_title", risk_title)

        risk_caption = self._label(
            risk_card,
            text="Log a selected dose to score timing and daily totals.",
            muted=True,
            wrap=420,
        )
        risk_caption.widget.grid(row=3, column=0, sticky="ew", padx=18, pady=(8, 12))
        self._register("dashboard_risk_caption", risk_caption)
        risk_buttons = ctk.CTkFrame(risk_card, fg_color="transparent")
        risk_buttons.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 12))
        risk_buttons.grid_columnconfigure((0, 1), weight=1)
        self._button(
            risk_buttons,
            text="Run Focused Safety Check",
            command=self.on_run_safety_check,
            tone="neutral",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(
            risk_buttons,
            text="Run All-Meds Check",
            command=self.on_run_all_meds_safety_check,
            tone="warning",
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(risk_card, text="All-Meds Integration", anchor="w", text_color=DESKTOP_MUTED).grid(
            row=5, column=0, sticky="w", padx=18
        )
        regimen_box = self._readonly_box(risk_card, height=92)
        regimen_box.widget.grid(row=6, column=0, sticky="nsew", padx=18, pady=(6, 18))
        self._register("dashboard_regimen_safety", regimen_box)

        summary_card = self._card(left)
        summary_card.grid(row=2, column=0, sticky="nsew", pady=7)
        summary_card.grid_columnconfigure(0, weight=1)

        today_due = self._label(summary_card, text="0 due", bold=True, wrap=420)
        today_due.widget.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 6))
        self._register("today_due_count", today_due)

        today_next = self._label(summary_card, text="Nothing scheduled yet", muted=True, wrap=420)
        today_next.widget.grid(row=1, column=0, sticky="ew", padx=18)
        self._register("today_next_due", today_next)

        model_state = self._label(summary_card, text="Model: not downloaded", muted=True, wrap=420)
        model_state.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 18))
        self._register("dashboard_model_state", model_state)
        ctk.CTkLabel(summary_card, text="Per-Med Safety", anchor="w", text_color=DESKTOP_MUTED).grid(
            row=3, column=0, sticky="w", padx=18
        )
        per_med_safety = self._readonly_box(summary_card, height=145)
        per_med_safety.widget.grid(row=4, column=0, sticky="nsew", padx=18, pady=(6, 18))
        self._register("dashboard_med_safety", per_med_safety)

        nudge_card = self._card(left)
        nudge_card.grid(row=3, column=0, sticky="nsew", pady=(7, 0))
        nudge_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(nudge_card, text="Gentle Nudge", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        nudge_box = self._readonly_box(nudge_card, height=150)
        nudge_box.widget.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self._register("dashboard_nudge", nudge_box)
        # Removed best-path simulation box from the dashboard nudge card.

        right = ctk.CTkFrame(scroll, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=14)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=2)
        right.grid_rowconfigure(3, weight=1)

        timeline_card = self._card(right)
        timeline_card.grid(row=0, column=0, sticky="nsew", pady=(0, 7))
        timeline_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(timeline_card, text="Today's Timeline", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        timeline_box = self._readonly_box(timeline_card, height=150)
        timeline_box.widget.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self._register("today_timeline", timeline_box)

        selection_card = self._card(right)
        selection_card.grid(row=1, column=0, sticky="nsew", pady=7)
        selection_card.grid_columnconfigure(0, weight=1)
        dashboard_selection = self._label(selection_card, text="Choose a medication from Dashboard focus.", bold=True, wrap=520)
        dashboard_selection.widget.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        self._register("dashboard_selection", dashboard_selection)
        picker_row = ctk.CTkFrame(selection_card, fg_color="transparent")
        picker_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        picker_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(picker_row, text="Dashboard focus", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 12))
        dashboard_picker = ctk.CTkOptionMenu(
            picker_row,
            values=["Choose medication"],
            command=self.on_dashboard_med_select,
            fg_color=DESKTOP_SURFACE_ALT,
            button_color=DESKTOP_ACCENT,
            button_hover_color="#0d6b63",
            dropdown_fg_color=DESKTOP_SURFACE_ALT,
            dropdown_hover_color="#223443",
            dropdown_text_color=DESKTOP_TEXT,
            text_color=DESKTOP_TEXT,
            corner_radius=12,
        )
        dashboard_picker.grid(row=0, column=1, sticky="ew")
        try:
            dashboard_picker.set("Choose medication")
        except Exception:
            pass
        self.ids["dashboard_med_picker"] = dashboard_picker
        dashboard_focus_hint = self._label(
            selection_card,
            text="Current regimen and completed history both appear in the focus picker.",
            muted=True,
            wrap=520,
        )
        dashboard_focus_hint.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        self._register("dashboard_focus_hint", dashboard_focus_hint)
        selected_summary = self._readonly_box(selection_card, height=135)
        selected_summary.widget.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self._register("selected_med_summary", selected_summary)
        # Dashboard dose-plan preview removed to keep the daily checklist higher on screen.

        checklist_card = self._card(right)
        checklist_card.grid(row=2, column=0, sticky="nsew", pady=7)
        checklist_card.grid_columnconfigure(0, weight=1)
        checklist_card.grid_columnconfigure(1, weight=0)
        ctk.CTkLabel(checklist_card, text="Meds Daily Checklist", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        checklist_date_label = self._label(checklist_card, text="Today", bold=True, wrap=220)
        checklist_date_label.widget.grid(row=0, column=1, sticky="e", padx=18, pady=(18, 10))
        self._register("daily_checklist_date_label", checklist_date_label)
        checklist_controls = ctk.CTkFrame(checklist_card, fg_color="transparent")
        checklist_controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8))
        checklist_controls.grid_columnconfigure(0, weight=1)
        checklist_date = self._entry(checklist_controls, placeholder="YYYY-MM-DD")
        checklist_date.widget.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._register("daily_checklist_date", checklist_date)
        try:
            checklist_date.widget.bind("<Return>", lambda _event: (self.on_checklist_date_go(), "break")[1])
        except Exception:
            pass
        self._button(checklist_controls, text="Prev", command=self.on_checklist_date_prev, tone="neutral").grid(row=0, column=1, sticky="ew", padx=4)
        self._button(checklist_controls, text="Today", command=self.on_checklist_date_today, tone="neutral").grid(row=0, column=2, sticky="ew", padx=4)
        self._button(checklist_controls, text="Next", command=self.on_checklist_date_next, tone="neutral").grid(row=0, column=3, sticky="ew", padx=4)
        self._button(checklist_controls, text="Go", command=self.on_checklist_date_go, tone="neutral").grid(row=0, column=4, sticky="ew", padx=(4, 0))
        checklist_hint = self._label(
            checklist_card,
            text="Use the date picker to review earlier checklists. Check a slot when you take it; missed slots can be reconciled or taken now.",
            muted=True,
            wrap=520,
        )
        checklist_hint.widget.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))
        self._register("daily_checklist_hint", checklist_hint)
        checklist_frame = ctk.CTkScrollableFrame(
            checklist_card,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
            height=210,
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        checklist_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=18, pady=(0, 18))
        checklist_frame.grid_columnconfigure(0, weight=1)
        self._register("daily_checklist_frame", checklist_frame)

        history_card = self._card(right)
        history_card.grid(row=3, column=0, sticky="nsew", pady=(7, 0))
        history_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(history_card, text="Recent Activity", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        history_box = self._readonly_box(history_card, height=260)
        history_box.widget.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self._register("selected_med_history", history_box)

    def _build_medications_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Use a fixed two-column shell instead of putting the whole tab inside one
        # giant scroll area. Each pane owns its own scrollbar, so the medication
        # editor stretches to the available screen height and the action buttons
        # stay reachable without wasting blank space at the bottom.
        shell = ctk.CTkFrame(tab, fg_color="transparent")
        shell.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_columnconfigure(1, weight=2)
        shell.grid_rowconfigure(0, weight=1)

        list_card = self._card(shell)
        list_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7), pady=0)
        list_card.grid_rowconfigure(2, weight=1)
        list_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(list_card, text="Medication List", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        med_list_summary = self._label(
            list_card,
            text="Current regimen entries and completed medication history stay visible here.",
            muted=True,
            wrap=420,
        )
        med_list_summary.widget.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        self._register("med_list_summary", med_list_summary)
        med_list_frame = ctk.CTkScrollableFrame(
            list_card,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
            height=620,
        )
        med_list_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self._register("med_list", DesktopListAdapter(med_list_frame))

        form_card = ctk.CTkScrollableFrame(
            shell,
            fg_color=DESKTOP_SURFACE,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=18,
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        form_card.grid(row=0, column=1, sticky="nsew", padx=(7, 0), pady=0)
        form_card.grid_columnconfigure((0, 1, 2), weight=1)

        form_selection = self._label(form_card, text="Creating a new medication", bold=True, wrap=720)
        form_selection.widget.grid(row=0, column=0, columnspan=3, sticky="ew", padx=18, pady=(18, 10))
        self._register("form_selection", form_selection)

        ctk.CTkLabel(form_card, text="Medication name", anchor="w", text_color=DESKTOP_MUTED).grid(row=1, column=0, columnspan=3, sticky="w", padx=18)
        med_name = self._entry(form_card, placeholder="Medication name")
        med_name.widget.grid(row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(6, 12))
        self._register("med_name", med_name)

        ctk.CTkLabel(form_card, text="Dose (mg)", anchor="w", text_color=DESKTOP_MUTED).grid(row=3, column=0, sticky="w", padx=(18, 8))
        ctk.CTkLabel(form_card, text="Interval (hours)", anchor="w", text_color=DESKTOP_MUTED).grid(row=3, column=1, sticky="w", padx=8)
        ctk.CTkLabel(form_card, text="Max daily (mg)", anchor="w", text_color=DESKTOP_MUTED).grid(row=3, column=2, sticky="w", padx=(8, 18))
        dose_mg = self._entry(form_card, placeholder="Dose mg")
        interval_h = self._entry(form_card, placeholder="Interval h")
        max_daily = self._entry(form_card, placeholder="Max daily mg")
        dose_mg.widget.grid(row=4, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        interval_h.widget.grid(row=4, column=1, sticky="ew", padx=8, pady=(6, 12))
        max_daily.widget.grid(row=4, column=2, sticky="ew", padx=(8, 18), pady=(6, 12))
        self._register("dose_mg", dose_mg)
        self._register("interval_h", interval_h)
        self._register("max_daily", max_daily)

        ctk.CTkLabel(form_card, text="First planned dose time (HH:MM)", anchor="w", text_color=DESKTOP_MUTED).grid(row=5, column=0, sticky="w", padx=(18, 8))
        ctk.CTkLabel(form_card, text="Optional custom daily dose times", anchor="w", text_color=DESKTOP_MUTED).grid(row=5, column=1, columnspan=2, sticky="w", padx=(8, 18))
        first_dose_time = self._entry(form_card, placeholder="06:00 or 08:00")
        first_dose_time.widget.grid(row=6, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        self._register("first_dose_time", first_dose_time)
        custom_times = self._edit_box(form_card, height=100)
        custom_times.widget.grid(row=6, column=1, columnspan=2, sticky="ew", padx=(8, 18), pady=(6, 12))
        self._register("custom_times_text", custom_times)

        planner_hint = self._label(
            form_card,
            text="Examples: Breakfast, Lunch, Dinner or Breakfast 08:00, Mid day 12:00, Nighttime 21:00. Leave blank for automatic interval-based times.",
            muted=True,
            wrap=720,
        )
        planner_hint.widget.grid(row=7, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 12))

        ctk.CTkLabel(form_card, text="Bottle directions", anchor="w", text_color=DESKTOP_MUTED).grid(row=8, column=0, columnspan=3, sticky="w", padx=18)
        schedule_text = self._edit_box(form_card, height=110)
        schedule_text.widget.grid(row=9, column=0, columnspan=3, sticky="ew", padx=18, pady=(6, 12))
        self._register("schedule_text", schedule_text)

        ctk.CTkLabel(form_card, text="Notes", anchor="w", text_color=DESKTOP_MUTED).grid(row=10, column=0, columnspan=3, sticky="w", padx=18)
        med_notes = self._edit_box(form_card, height=120)
        med_notes.widget.grid(row=11, column=0, columnspan=3, sticky="ew", padx=18, pady=(6, 12))
        self._register("med_notes", med_notes)

        ctk.CTkLabel(form_card, text="Saved schedule preview", anchor="w", text_color=DESKTOP_MUTED).grid(row=12, column=0, columnspan=3, sticky="w", padx=18)
        preview = self._readonly_box(form_card, height=130)
        preview.widget.grid(row=13, column=0, columnspan=3, sticky="ew", padx=18, pady=(6, 12))
        self._register("form_schedule_preview", preview)

        buttons = ctk.CTkFrame(form_card, fg_color="transparent")
        buttons.grid(row=14, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 18))
        buttons.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._button(buttons, text="New", command=self.on_new_med, tone="neutral").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(buttons, text="Save", command=self.on_save_med).grid(row=0, column=1, sticky="ew", padx=6)
        self._button(buttons, text="Complete / Archive", command=self.on_delete_med, tone="danger").grid(row=0, column=2, sticky="ew", padx=6)
        self._button(buttons, text="Run Safety Check", command=self.on_run_safety_check, tone="neutral").grid(row=0, column=3, sticky="ew", padx=6)
        self._button(buttons, text="Log Dose", command=self.on_log_dose, tone="warning").grid(row=0, column=4, sticky="ew", padx=(6, 0))
        form_hint = self._label(
            form_card,
            text="Completing a medication removes it from the current regimen and keeps its dose history in the encrypted vault.",
            muted=True,
            wrap=720,
        )
        form_hint.widget.grid(row=15, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 18))
        self._register("med_form_hint", form_hint)

    def _build_vision_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        scroll.grid_columnconfigure(0, weight=1)

        card = self._card(scroll)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Pill Bottle Scanner", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        vision_last = self._label(card, text="Last image: none", muted=True, wrap=980)
        vision_last.widget.grid(row=1, column=0, sticky="ew", padx=18)
        self._register("vision_last_file", vision_last)
        vision_status = self._label(card, text="Ready to review a medication bottle photo.", muted=True, wrap=980)
        vision_status.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 12))
        self._register("vision_status", vision_status)

        button_row = ctk.CTkFrame(card, fg_color="transparent")
        button_row.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 12))
        button_row.grid_columnconfigure((0, 1), weight=1)
        self._button(button_row, text="Choose Bottle Photo", command=self.on_pick_bottle_photo).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(button_row, text="Import From Computer", command=self.on_take_bottle_photo, tone="neutral").grid(row=0, column=1, sticky="ew", padx=(6, 0))

        vision_result = self._readonly_box(card, height=420)
        vision_result.widget.grid(row=4, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self._register("vision_result", vision_result)

    def _build_dental_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        scroll.grid_columnconfigure(0, weight=1)

        overview = self._card(scroll)
        overview.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        overview.grid_columnconfigure(0, weight=1)
        overview_title = self._label(overview, text="Dental studio ready", bold=True, wrap=980)
        overview_title.widget.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        self._register("dental_overview_title", overview_title)
        overview_body = self._label(
            overview,
            text="Brush, floss, rinse, and AI hygiene reviews all stay local.",
            muted=True,
            wrap=980,
        )
        overview_body.widget.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        self._register("dental_overview_body", overview_body)

        habits = self._card(scroll)
        habits.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        habits.grid_columnconfigure((0, 1, 2), weight=1)
        for column, (prefix, title, command) in enumerate(
            (
                ("brush", "Brush", lambda: self.on_log_dental_habit("brush")),
                ("floss", "Floss", lambda: self.on_log_dental_habit("floss")),
                ("rinse", "Rinse", lambda: self.on_log_dental_habit("rinse")),
            )
        ):
            habit_card = ctk.CTkFrame(habits, fg_color=DESKTOP_SURFACE_ALT, border_width=1, border_color=DESKTOP_BORDER, corner_radius=14)
            habit_card.grid(row=0, column=column, sticky="nsew", padx=(18 if column == 0 else 8, 18 if column == 2 else 8), pady=18)
            habit_card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(habit_card, text=title, anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=17, weight="bold")).grid(
                row=0, column=0, sticky="w", padx=14, pady=(14, 6)
            )
            status = self._label(habit_card, text="Ready", bold=True, wrap=240)
            status.widget.grid(row=1, column=0, sticky="ew", padx=14)
            self._register(f"dental_{prefix}_status", status)
            caption = self._label(habit_card, text="Ready now", muted=True, wrap=240)
            caption.widget.grid(row=2, column=0, sticky="ew", padx=14, pady=(6, 12))
            self._register(f"dental_{prefix}_caption", caption)
            self._button(habit_card, text=f"Log {title}", command=command, tone="neutral").grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))

        intervals = self._card(scroll)
        intervals.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        intervals.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(intervals, text="Brush interval (h)", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=0, sticky="w", padx=(18, 8), pady=(18, 0))
        ctk.CTkLabel(intervals, text="Floss interval (h)", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=1, sticky="w", padx=8, pady=(18, 0))
        ctk.CTkLabel(intervals, text="Rinse interval (h)", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=2, sticky="w", padx=(8, 18), pady=(18, 0))
        brush_interval = self._entry(intervals, placeholder="Brush interval h")
        floss_interval = self._entry(intervals, placeholder="Floss interval h")
        rinse_interval = self._entry(intervals, placeholder="Rinse interval h")
        brush_interval.widget.grid(row=1, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        floss_interval.widget.grid(row=1, column=1, sticky="ew", padx=8, pady=(6, 12))
        rinse_interval.widget.grid(row=1, column=2, sticky="ew", padx=(8, 18), pady=(6, 12))
        self._register("dental_brush_interval", brush_interval)
        self._register("dental_floss_interval", floss_interval)
        self._register("dental_rinse_interval", rinse_interval)
        interval_buttons = ctk.CTkFrame(intervals, fg_color="transparent")
        interval_buttons.grid(row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 18))
        interval_buttons.grid_columnconfigure((0, 1), weight=1)
        self._button(interval_buttons, text="Save Rhythm", command=self.on_save_dental_intervals).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(interval_buttons, text="Reset Defaults", command=self.on_reset_dental_intervals, tone="neutral").grid(row=0, column=1, sticky="ew", padx=(6, 0))

        hygiene = self._card(scroll)
        hygiene.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        hygiene.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hygiene, text="Hygiene Review", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        hygiene_photo = self._label(hygiene, text="Last hygiene photo: none", muted=True, wrap=980)
        hygiene_photo.widget.grid(row=1, column=0, sticky="ew", padx=18)
        self._register("dental_hygiene_photo", hygiene_photo)
        hygiene_rating = self._label(hygiene, text="No hygiene rating yet.", bold=True, wrap=980)
        hygiene_rating.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 0))
        self._register("dental_hygiene_rating", hygiene_rating)
        hygiene_status = self._label(hygiene, text="Ready for a teeth photo.", muted=True, wrap=980)
        hygiene_status.widget.grid(row=3, column=0, sticky="ew", padx=18, pady=(8, 0))
        self._register("dental_hygiene_status", hygiene_status)
        hygiene_trend = self._label(
            hygiene,
            text="Trend: take two AI reviews over time to compare your hygiene rhythm.",
            muted=True,
            wrap=980,
        )
        hygiene_trend.widget.grid(row=4, column=0, sticky="ew", padx=18, pady=(8, 12))
        self._register("dental_hygiene_trend", hygiene_trend)
        hygiene_buttons = ctk.CTkFrame(hygiene, fg_color="transparent")
        hygiene_buttons.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 12))
        hygiene_buttons.grid_columnconfigure((0, 1), weight=1)
        self._button(hygiene_buttons, text="Choose Hygiene Photo", command=self.on_pick_dental_hygiene_photo).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(hygiene_buttons, text="Import From Computer", command=self.on_take_dental_hygiene_photo, tone="neutral").grid(row=0, column=1, sticky="ew", padx=(6, 0))
        hygiene_summary = self._readonly_box(hygiene, height=220)
        hygiene_summary.widget.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 18))
        self._register("dental_hygiene_summary", hygiene_summary)

        recovery = self._card(scroll)
        recovery.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        recovery.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(recovery, text="Recovery Mode", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 10)
        )
        recovery_mode = self._label(recovery, text="Recovery mode is off.", bold=True, wrap=980)
        recovery_mode.widget.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18)
        self._register("recovery_mode_status", recovery_mode)
        recovery_snapshot = self._label(
            recovery,
            text="Set a procedure type and date to start a daily recovery journal.",
            muted=True,
            wrap=980,
        )
        recovery_snapshot.widget.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(8, 12))
        self._register("recovery_snapshot", recovery_snapshot)
        ctk.CTkLabel(recovery, text="Procedure type", anchor="w", text_color=DESKTOP_MUTED).grid(row=3, column=0, sticky="w", padx=(18, 8))
        ctk.CTkLabel(recovery, text="Procedure date (YYYY-MM-DD)", anchor="w", text_color=DESKTOP_MUTED).grid(row=3, column=1, sticky="w", padx=(8, 18))
        procedure_type = self._entry(recovery, placeholder="Procedure type")
        procedure_date = self._entry(recovery, placeholder="YYYY-MM-DD")
        procedure_type.widget.grid(row=4, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        procedure_date.widget.grid(row=4, column=1, sticky="ew", padx=(8, 18), pady=(6, 12))
        self._register("recovery_procedure_type", procedure_type)
        self._register("recovery_procedure_date", procedure_date)
        ctk.CTkLabel(recovery, text="Symptom notes", anchor="w", text_color=DESKTOP_MUTED).grid(row=5, column=0, sticky="w", padx=(18, 8))
        ctk.CTkLabel(recovery, text="Aftercare notes", anchor="w", text_color=DESKTOP_MUTED).grid(row=5, column=1, sticky="w", padx=(8, 18))
        symptom_notes = self._edit_box(recovery, height=120)
        care_notes = self._edit_box(recovery, height=120)
        symptom_notes.widget.grid(row=6, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        care_notes.widget.grid(row=6, column=1, sticky="ew", padx=(8, 18), pady=(6, 12))
        self._register("recovery_symptom_notes", symptom_notes)
        self._register("recovery_care_notes", care_notes)
        recovery_buttons = ctk.CTkFrame(recovery, fg_color="transparent")
        recovery_buttons.grid(row=7, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))
        recovery_buttons.grid_columnconfigure((0, 1, 2), weight=1)
        self._button(recovery_buttons, text="Save Recovery", command=self.on_save_recovery_mode, tone="warning").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(recovery_buttons, text="Pause Recovery", command=self.on_pause_recovery_mode, tone="neutral").grid(row=0, column=1, sticky="ew", padx=6)
        self._button(recovery_buttons, text="Choose Recovery Photo", command=self.on_pick_recovery_photo).grid(row=0, column=2, sticky="ew", padx=(6, 0))
        recovery_last = self._label(recovery, text="Last recovery photo: none", muted=True, wrap=980)
        recovery_last.widget.grid(row=8, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8))
        self._register("recovery_last_photo", recovery_last)
        recovery_result = self._readonly_box(recovery, height=240)
        recovery_result.widget.grid(row=9, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))
        self._register("recovery_result", recovery_result)

    def _build_assistant_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        shell = ctk.CTkFrame(tab, fg_color="transparent")
        shell.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        body = ctk.CTkFrame(shell, fg_color="transparent")
        body.grid(row=0, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=0, minsize=330)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        self.ids["assistant_body"] = body

        context_panel = ctk.CTkScrollableFrame(
            body,
            fg_color=DESKTOP_SURFACE,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=18,
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        context_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        context_panel.grid_columnconfigure(0, weight=1)
        self.ids["assistant_context_sidebar"] = context_panel

        ctk.CTkLabel(
            context_panel,
            text="Context",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))
        ctk.CTkLabel(
            context_panel,
            text="Mode, prompt shortcuts, and local vault preview live here so the conversation can breathe.",
            anchor="w",
            justify="left",
            wraplength=275,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        mode_row = ctk.CTkFrame(context_panel, fg_color="transparent")
        mode_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        mode_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(mode_row, text="Mode", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=0, sticky="w", pady=(0, 6))
        mode_menu = ctk.CTkOptionMenu(
            mode_row,
            values=["General", "Therapy", "Recovery Coach"],
            command=self.on_assistant_mode_change,
            fg_color=DESKTOP_SURFACE_ALT,
            button_color=DESKTOP_ACCENT,
            button_hover_color="#0d6b63",
            dropdown_fg_color=DESKTOP_SURFACE_ALT,
            dropdown_hover_color="#223443",
            dropdown_text_color=DESKTOP_TEXT,
            text_color=DESKTOP_TEXT,
            corner_radius=12,
        )
        mode_menu.grid(row=1, column=0, sticky="ew")
        try:
            mode_menu.set(self.assistant_mode)
        except Exception:
            pass
        self.ids["assistant_mode_menu"] = mode_menu
        mode_hint = self._label(
            context_panel,
            text="General mode focuses on schedule, wellness, dental, and practical vault guidance.",
            muted=True,
            wrap=280,
        )
        mode_hint.widget.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))
        self._register("assistant_mode_hint", mode_hint)

        ctk.CTkLabel(context_panel, text="Quick Prompts", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=4, column=0, sticky="w", padx=16, pady=(0, 8)
        )
        quick_prompts = ctk.CTkFrame(context_panel, fg_color="transparent")
        quick_prompts.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 12))
        quick_prompts.grid_columnconfigure((0, 1), weight=1)
        prompt_buttons = [
            ("Summarize Today", "Summarize my medication, dental, movement, and recovery plan for today. Start with what matters most."),
            ("What Next?", "What is the most useful next action based on my current MedSafe vault context?"),
            ("Check Routine", "Check my current routine for timing gaps, missing details, and anything I should verify before acting."),
            ("Draft Questions", "Draft clear questions I can bring to a clinician, dentist, therapist, sponsor, or support person based on my current context."),
        ]
        self.assistant_quick_prompt_buttons: Dict[str, Any] = {}
        for index, (label, prompt_text) in enumerate(prompt_buttons):
            button = self._button(
                quick_prompts,
                text=label,
                command=lambda text=prompt_text, label=label: self.on_assistant_quick_prompt(text, label=label),
                tone="secondary",
            )
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=(0 if index % 2 == 0 else 5, 0), pady=(0, 8))
            self.assistant_quick_prompt_buttons[label] = button

        prompt_lens = self._label(
            context_panel,
            text="Prompt lens: direct local RAG context, schedule-aware, and safety-bounded.",
            muted=True,
            wrap=280,
        )
        prompt_lens.widget.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 10))
        self._register("assistant_prompt_lens", prompt_lens)
        quantum_panel = self._readonly_box(context_panel, height=210)
        quantum_panel.widget.grid(row=7, column=0, sticky="ew", padx=16, pady=(0, 10))
        self._register("assistant_quantum_state", quantum_panel)

        ctk.CTkLabel(context_panel, text="Context Window", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=8, column=0, sticky="w", padx=16, pady=(0, 8)
        )
        context_report = self._readonly_box(context_panel, height=142)
        context_report.widget.grid(row=9, column=0, sticky="ew", padx=16, pady=(0, 10))
        self._register("assistant_context_window_report", context_report)
        compact_button = self._button(
            context_panel,
            text="Compact Memory Now",
            command=self.on_assistant_compact_memory,
            tone="secondary",
        )
        compact_button.grid(row=10, column=0, sticky="ew", padx=16, pady=(0, 16))
        self.ids["assistant_compact_button"] = compact_button

        chat_card = self._card(body)
        chat_card.grid(row=0, column=1, sticky="nsew", pady=0)
        chat_card.grid_columnconfigure(0, weight=1)
        chat_card.grid_rowconfigure(2, weight=1)
        self.ids["assistant_chat_card"] = chat_card

        chat_header = ctk.CTkFrame(chat_card, fg_color="transparent")
        chat_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
        chat_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            chat_header,
            text="Conversation",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        loading_badge = ctk.CTkLabel(
            chat_header,
            text="Ready",
            fg_color="#20313e",
            text_color=DESKTOP_MUTED,
            corner_radius=16,
            height=30,
            width=150,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        loading_badge.grid(row=0, column=1, sticky="e")
        self.ids["assistant_loading_badge"] = loading_badge
        loading_bar = ctk.CTkProgressBar(chat_card, progress_color=DESKTOP_ACCENT, fg_color="#21303c", height=8, corner_radius=8)
        loading_bar.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        loading_bar.set(0.0)
        self.ids["assistant_loading_bar"] = loading_bar

        assistant_history = self._readonly_box(chat_card, height=560)
        assistant_history.widget.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 14))
        self._register("assistant_history", assistant_history)

        composer = ctk.CTkFrame(chat_card, fg_color="transparent")
        composer.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 16))
        composer.grid_columnconfigure(0, weight=1)
        composer.grid_columnconfigure(1, weight=0)
        assistant_input = self._edit_box(composer, height=126)
        assistant_input.widget.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self._register("assistant_input", assistant_input)
        self._bind_assistant_input_shortcuts(assistant_input)
        self._bind_assistant_input_live_context(assistant_input)

        assistant_status = self._label(
            composer,
            text="Local-only chat is ready. Press Enter to send and Shift+Enter for a new line.",
            muted=True,
            wrap=640,
        )
        assistant_status.widget.grid(row=1, column=0, columnspan=2, sticky="ew")
        self._register("assistant_status_line", assistant_status)
        buttons = ctk.CTkFrame(composer, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))
        context_toggle = self._button(
            buttons,
            text="Hide Context",
            command=self.toggle_assistant_context_panel,
            tone="neutral",
        )
        context_toggle.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.ids["assistant_context_toggle_button"] = context_toggle
        smaller_button = self._button(
            buttons,
            text="A-",
            command=lambda: self.adjust_assistant_chat_text_size(-1),
            tone="secondary",
        )
        smaller_button.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        larger_button = self._button(
            buttons,
            text="A+",
            command=lambda: self.adjust_assistant_chat_text_size(1),
            tone="secondary",
        )
        larger_button.grid(row=0, column=2, sticky="ew", padx=(0, 6))
        chat_font_label = self._label(buttons, text="Text +2", muted=True, wrap=84)
        chat_font_label.widget.grid(row=0, column=3, sticky="e", padx=(0, 10))
        self._register("assistant_chat_font_label", chat_font_label)
        send_button = self._button(buttons, text="Send", command=self.on_assistant_send)
        send_button.grid(row=0, column=4, sticky="ew", padx=(0, 8))
        self.ids["assistant_send_button"] = send_button
        clear_button = self._button(buttons, text="Clear", command=self.on_assistant_clear, tone="danger")
        clear_button.grid(row=0, column=5, sticky="ew")
        self.ids["assistant_clear_button"] = clear_button

        self.on_assistant_mode_change(self.assistant_mode)
        self.refresh_assistant_chat_font()
        self.set_assistant_context_visible(self.assistant_context_visible)
        self._set_assistant_ui_state()

    def _build_help_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        scroll.grid_columnconfigure(0, weight=1)

        overview = self._card(scroll)
        overview.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        overview.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            overview,
            text="Help & Flow Guide",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))
        ctk.CTkLabel(
            overview,
            text=(
                "This guide turns the README workflow into an in-app route map. It scores A-to-K paths "
                "by usefulness, visual clarity, smooth handoff, and backend readiness using local state only."
            ),
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        snapshot = self._readonly_box(overview, height=115)
        snapshot.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
        self._register("help_flow_snapshot", snapshot)
        quick = ctk.CTkFrame(overview, fg_color="transparent")
        quick.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))
        quick.grid_columnconfigure((0, 1, 2), weight=1)
        self._button(quick, text="Go To Suggested Next Step", command=self.on_open_best_flow_path).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(quick, text="Refresh Guide", command=self.refresh_help_ui, tone="neutral").grid(row=0, column=1, sticky="ew", padx=6)
        self._button(quick, text="Open Settings", command=lambda: self.navigate_to_tab("Settings"), tone="warning").grid(
            row=0, column=2, sticky="ew", padx=(6, 0)
        )

        route_card = self._card(scroll)
        route_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        route_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            route_card,
            text="Suggested Workflow Path",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))
        simulation = self._readonly_box(route_card, height=270)
        simulation.widget.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        self._register("help_flow_simulation", simulation)

        map_card = self._card(scroll)
        map_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        map_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            map_card,
            text="Feature Map",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))
        map_text = "\n".join(f"{letter}. {title} ({tab_name}) - {description}" for letter, tab_name, title, description in HELP_FLOW_STEPS)
        map_box = self._readonly_box(map_card, height=230)
        map_box.text = map_text
        map_box.widget.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        self._register("help_flow_map", map_box)

        feature_card = self._card(scroll)
        feature_card.grid(row=3, column=0, sticky="ew")
        feature_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            feature_card,
            text="Feature Help",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))
        topic_grid = ctk.CTkFrame(feature_card, fg_color="transparent")
        topic_grid.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        topic_grid.grid_columnconfigure((0, 1, 2), weight=1)
        for index, (topic, _body) in enumerate(HELP_FEATURE_GUIDE):
            self._button(
                topic_grid,
                text=topic,
                command=lambda selected_topic=topic: self.on_help_topic(selected_topic),
                tone="neutral" if topic != "Settings" else "warning",
            ).grid(row=index // 3, column=index % 3, sticky="ew", padx=4, pady=4)
        feature_detail = self._readonly_box(feature_card, height=220)
        feature_detail.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        self._register("help_feature_detail", feature_detail)

    def navigate_to_tab(self, tab_name: str) -> None:
        tabview = self.ids.get("main_tabs")
        if tabview is None:
            return
        clean_name = sanitize_text(tab_name, max_chars=80)
        if clean_name == "Assistant":
            clean_name = "Chat"
        if clean_name == "Vision":
            clean_name = "Pill Bottle Scanner"
        try:
            tabview.set(clean_name)
        except Exception:
            return
        if "workflow_hint_label" in self.ids:
            self.ids.workflow_hint_label.text = workflow_surface_hint(clean_name)
        if clean_name == "Chat":
            self.refresh_assistant_context_panel()
        self.set_status(f"Opened {clean_name}.")

    def on_help_topic(self, topic: str) -> None:
        self.help_selected_topic = sanitize_text(topic, max_chars=80)
        if "help_feature_detail" in self.ids:
            self.ids.help_feature_detail.text = build_help_feature_text(self.help_selected_topic)
        self.set_status(f"Help topic: {self.help_selected_topic}.")

    def on_open_best_flow_path(self) -> None:
        model_ready = bool(self.paths and self.paths.encrypted_model_path.exists())
        password_enabled = bool(self.vault and self.vault.is_key_protected())
        snapshot, _report = build_flow_simulation_report(
            self.data_cache,
            self.settings_data,
            selected_med_id=self.selected_med_id or "",
            model_ready=model_ready,
            password_enabled=password_enabled,
        )
        match = re.search(r"Best next path:\s*([A-K])->([A-K])", snapshot)
        target_letter = match.group(2) if match else "A"
        target_step = next((step for step in HELP_FLOW_STEPS if step[0] == target_letter), HELP_FLOW_STEPS[0])
        _letter, target_tab, target_title, target_description = target_step
        self.navigate_to_tab(target_tab)
        self.set_status(f"Suggested: {target_title}. {target_description}")

    def on_dashboard_best_action(self) -> None:
        target_tab = sanitize_text(getattr(self, "dashboard_best_action_target", "Dashboard") or "Dashboard", max_chars=80)
        self.navigate_to_tab(target_tab)
        target_messages = {
            "Dashboard": "Care Compass action opened. Use the daily checklist and timeline on this page.",
            "Dental": "Opened Dental for the next due hygiene or recovery check-in.",
            "Exercise": "Opened Exercise for the next due movement routine.",
            "Recovery": "Opened Recovery for the next due recovery check-in.",
            "Settings": "Opened Settings for model, password, and vault readiness.",
            "Safety": "Opened Safety for regimen review.",
        }
        self.set_status(target_messages.get(target_tab, f"Opened {target_tab}."))

    def show_command_palette(self) -> None:
        if self.window is None:
            return
        popup = ctk.CTkToplevel(self.window)
        popup.title("MedSafe Commands")
        popup.configure(fg_color=DESKTOP_BG)
        popup.resizable(False, False)
        try:
            popup.transient(self.window)
            popup.grab_set()
        except Exception:
            pass
        width = 620
        height = 520
        try:
            x = int(self.window.winfo_rootx()) + max(0, (int(self.window.winfo_width()) - width) // 2)
            y = int(self.window.winfo_rooty()) + 80
            popup.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            popup.geometry(f"{width}x{height}")
        popup.grid_columnconfigure(0, weight=1)
        card = self._card(popup)
        card.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card,
            text="Command Palette",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))
        ctk.CTkLabel(
            card,
            text="Jump straight to the workflow you need.",
            anchor="w",
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        commands = (
            ("Review Today", lambda: self.navigate_to_tab("Dashboard"), "Open due, missed, timeline, checklist, and Care Compass."),
            ("Run Safety Scan", self.on_run_all_meds_safety_check, "Check the active regimen with local rules and model support."),
            ("Add Medication", self._command_new_medication, "Open the editor and start a fresh current regimen entry."),
            ("Pill Bottle Scanner", lambda: self.navigate_to_tab("Pill Bottle Scanner"), "Open bottle-photo medication import."),
            ("Recovery Check-In", lambda: self.navigate_to_tab("Recovery"), "Open streaks, check-ins, resets, and coping plan."),
            ("Open Chat", lambda: self.navigate_to_tab("Chat"), "Open the local chat conversation."),
            ("Chat: What Next?", self._command_assistant_what_next, "Open Chat with a context-aware next-action prompt ready."),
            ("Security Status", self._command_security_status, "Open Settings and show the current startup unlock and vault state."),
            ("Help & Flow Guide", lambda: self.navigate_to_tab("Help"), "Open A-K path simulation and feature help."),
            ("Settings & Security", lambda: self.navigate_to_tab("Settings"), "Open model, password, text, and runtime controls."),
        )
        for index, (title, command, detail) in enumerate(commands, start=2):
            row = ctk.CTkFrame(card, fg_color=DESKTOP_SURFACE_ALT, border_width=1, border_color=DESKTOP_BORDER, corner_radius=12)
            row.grid(row=index, column=0, sticky="ew", padx=18, pady=(0, 8))
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkButton(
                row,
                text=title,
                command=lambda callback=command, window=popup: self._run_palette_command(window, callback),
                anchor="w",
                fg_color="transparent",
                hover_color="#223443",
                text_color=DESKTOP_TEXT,
                font=ctk.CTkFont(size=15, weight="bold"),
                height=34,
            ).grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
            ctk.CTkLabel(
                row,
                text=detail,
                anchor="w",
                justify="left",
                wraplength=520,
                text_color=DESKTOP_MUTED,
                font=ctk.CTkFont(size=12),
            ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        try:
            popup.bind("<Escape>", lambda _event: (popup.destroy(), "break")[1])
            popup.after(80, popup.focus_force)
        except Exception:
            pass

    def _run_palette_command(self, popup: Any, command: Callable[[], None]) -> None:
        try:
            popup.grab_release()
        except Exception:
            pass
        try:
            popup.destroy()
        except Exception:
            pass
        command()

    def _command_new_medication(self) -> None:
        self.navigate_to_tab("Medications")
        self.on_new_med()

    def _command_assistant_what_next(self) -> None:
        self.navigate_to_tab("Chat")
        self.on_assistant_quick_prompt(
            "What is the most useful next action based on my current MedSafe vault context?",
            label="What Next?",
        )

    def _command_security_status(self) -> None:
        self.navigate_to_tab("Settings")
        self.refresh_model_status()
        self.show_dialog("Security Status", self.security_state_summary())

    def refresh_help_ui(self) -> None:
        if "help_flow_snapshot" not in self.ids:
            return
        model_ready = bool(self.paths and self.paths.encrypted_model_path.exists())
        password_enabled = bool(self.vault and self.vault.is_key_protected())
        snapshot, report = build_flow_simulation_report(
            self.data_cache,
            self.settings_data,
            selected_med_id=self.selected_med_id or "",
            model_ready=model_ready,
            password_enabled=password_enabled,
        )
        self.ids.help_flow_snapshot.text = snapshot
        self.ids.help_flow_simulation.text = report
        if "help_feature_detail" in self.ids:
            self.ids.help_feature_detail.text = build_help_feature_text(self.help_selected_topic)

    def _build_recovery_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        scroll.grid_columnconfigure(0, weight=1)

        recovery_card = self._card(scroll)
        recovery_card.grid(row=0, column=0, sticky="ew")
        recovery_card.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(
            recovery_card,
            text="Recovery Support Studio",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 8))
        ctk.CTkLabel(
            recovery_card,
            text="Track clean days from your Clean since date, log check-ins or resets, and keep recovery milestones ready for the local coach.",
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))
        recovery_title = self._label(recovery_card, text="Recovery planner ready", bold=True, wrap=980)
        recovery_title.widget.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18)
        self._register("recovery_support_title", recovery_title)
        reward_line = self._label(recovery_card, text="0 clean days | 0 pts | Next milestone: day 1 (+10 pts)", muted=True, wrap=980)
        reward_line.widget.grid(row=3, column=0, columnspan=2, sticky="ew", padx=18, pady=(8, 12))
        self._register("recovery_reward_line", reward_line)
        reminder_line = self._label(recovery_card, text="Recovery check-ins are off.", muted=True, wrap=980)
        reminder_line.widget.grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))
        self._register("recovery_reminder_line", reminder_line)
        ctk.CTkLabel(recovery_card, text="Recovery focus", anchor="w", text_color=DESKTOP_MUTED).grid(row=5, column=0, sticky="w", padx=(18, 8))
        ctk.CTkLabel(recovery_card, text="Clean since (YYYY-MM-DD)", anchor="w", text_color=DESKTOP_MUTED).grid(row=5, column=1, sticky="w", padx=(8, 18))
        recovery_goal_name = self._entry(recovery_card, placeholder="Recovery focus")
        recovery_clean_start = self._entry(recovery_card, placeholder="YYYY-MM-DD")
        recovery_goal_name.widget.grid(row=6, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        recovery_clean_start.widget.grid(row=6, column=1, sticky="ew", padx=(8, 18), pady=(6, 12))
        self._register("recovery_goal_name", recovery_goal_name)
        self._register("recovery_clean_start", recovery_clean_start)
        ctk.CTkLabel(recovery_card, text="Why this matters", anchor="w", text_color=DESKTOP_MUTED).grid(row=7, column=0, sticky="w", padx=(18, 8))
        ctk.CTkLabel(recovery_card, text="Coping plan / trigger interrupts", anchor="w", text_color=DESKTOP_MUTED).grid(row=7, column=1, sticky="w", padx=(8, 18))
        recovery_motivation = self._edit_box(recovery_card, height=120)
        recovery_coping_plan = self._edit_box(recovery_card, height=120)
        recovery_motivation.widget.grid(row=8, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        recovery_coping_plan.widget.grid(row=8, column=1, sticky="ew", padx=(8, 18), pady=(6, 12))
        self._register("recovery_motivation", recovery_motivation)
        self._register("recovery_coping_plan", recovery_coping_plan)
        ctk.CTkLabel(recovery_card, text="Check-in reminder time", anchor="w", text_color=DESKTOP_MUTED).grid(
            row=9, column=0, sticky="w", padx=(18, 8)
        )
        recovery_reminder_time = self._entry(recovery_card, placeholder="8:00 PM")
        recovery_reminder_time.widget.grid(row=10, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
        self._register("recovery_reminder_time", recovery_reminder_time)
        slider_frame = ctk.CTkFrame(recovery_card, fg_color="transparent")
        slider_frame.grid(row=9, column=1, rowspan=2, sticky="ew", padx=(8, 18), pady=(0, 12))
        slider_frame.grid_columnconfigure((0, 1), weight=1)
        mood_value = self._label(slider_frame, text="Mood 5/10", bold=True, wrap=220)
        mood_value.widget.grid(row=0, column=0, sticky="w")
        self._register("recovery_mood_value", mood_value)
        craving_value = self._label(slider_frame, text="Craving 0/10", bold=True, wrap=220)
        craving_value.widget.grid(row=0, column=1, sticky="w", padx=(12, 0))
        self._register("recovery_craving_value", craving_value)
        mood_slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=10,
            number_of_steps=10,
            fg_color=DESKTOP_BORDER,
            progress_color=DESKTOP_SUCCESS,
            button_color=DESKTOP_SUCCESS,
            button_hover_color="#2d8b61",
            command=lambda value: self.on_recovery_slider_change("mood", value),
        )
        mood_slider.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        try:
            mood_slider.set(5)
        except Exception:
            pass
        self.ids["recovery_mood_slider"] = mood_slider
        craving_slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=10,
            number_of_steps=10,
            fg_color=DESKTOP_BORDER,
            progress_color=DESKTOP_WARNING,
            button_color=DESKTOP_WARNING,
            button_hover_color="#b8801f",
            command=lambda value: self.on_recovery_slider_change("craving", value),
        )
        craving_slider.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(8, 0))
        try:
            craving_slider.set(0)
        except Exception:
            pass
        self.ids["recovery_craving_slider"] = craving_slider
        ctk.CTkLabel(recovery_card, text="Daily check-in or reset note", anchor="w", text_color=DESKTOP_MUTED).grid(
            row=11, column=0, columnspan=2, sticky="w", padx=18
        )
        recovery_checkin_note = self._edit_box(recovery_card, height=110)
        recovery_checkin_note.widget.grid(row=12, column=0, columnspan=2, sticky="ew", padx=18, pady=(6, 12))
        self._register("recovery_checkin_note", recovery_checkin_note)
        recovery_buttons = ctk.CTkFrame(recovery_card, fg_color="transparent")
        recovery_buttons.grid(row=13, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))
        recovery_buttons.grid_columnconfigure((0, 1, 2), weight=1)
        self._button(recovery_buttons, text="Save Recovery Plan", command=self.on_save_recovery_support_plan, tone="warning").grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        self._button(recovery_buttons, text="Daily Check-In", command=self.on_recovery_support_checkin).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        self._button(recovery_buttons, text="Log Relapse / Restart", command=self.on_recovery_support_relapse, tone="danger").grid(
            row=0, column=2, sticky="ew", padx=(6, 0)
        )
        badges_label = self._label(recovery_card, text="Milestone shelf", bold=True, wrap=980)
        badges_label.widget.grid(row=14, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8))
        self._register("recovery_badges_label", badges_label)
        badges_box = self._readonly_box(recovery_card, height=130)
        badges_box.widget.grid(row=15, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))
        self._register("recovery_badges", badges_box)
        recovery_summary = self._readonly_box(recovery_card, height=220)
        recovery_summary.widget.grid(row=16, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))
        self._register("recovery_support_summary", recovery_summary)

    def _build_model_tab(self, tab: Any) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color="transparent",
            scrollbar_button_color="#314455",
            scrollbar_button_hover_color="#42586c",
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        card = self._card(scroll)
        card.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="Settings & Runtime", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )
        ctk.CTkLabel(
            card,
            text="Model download, inference controls, privacy tools, and startup protection now live together here.",
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
        backend_label = self._label(card, text="Backend: Auto", muted=True, wrap=980)
        backend_label.widget.grid(row=2, column=0, sticky="ew", padx=18)
        self._register("model_backend_label", backend_label)
        progress_widget = ctk.CTkProgressBar(card, progress_color=DESKTOP_ACCENT, fg_color="#2a3743", height=18, corner_radius=10)
        progress_widget.grid(row=3, column=0, sticky="ew", padx=18, pady=(12, 12))
        progress_widget.set(0.0)
        self._register("model_progress", DesktopProgressAdapter(progress_widget))
        model_status = self._readonly_box(card, height=165)
        model_status.widget.grid(row=4, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self._register("model_status", model_status)
        buttons_one = ctk.CTkFrame(card, fg_color="transparent")
        buttons_one.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 8))
        buttons_one.grid_columnconfigure((0, 1), weight=1)
        self._button(buttons_one, text="Download and Seal", command=self.on_model_download).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(buttons_one, text="Verify SHA", command=self.on_model_verify, tone="neutral").grid(row=0, column=1, sticky="ew", padx=(6, 0))
        buttons_two = ctk.CTkFrame(card, fg_color="transparent")
        buttons_two.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 8))
        buttons_two.grid_columnconfigure((0, 1), weight=1)
        self._button(buttons_two, text="Cycle Backend", command=self.on_cycle_backend, tone="neutral").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(buttons_two, text="Toggle Image Input", command=self.on_toggle_native_image_input, tone="warning").grid(row=0, column=1, sticky="ew", padx=(6, 0))
        buttons_three = ctk.CTkFrame(card, fg_color="transparent")
        buttons_three.grid(row=7, column=0, sticky="ew", padx=18, pady=(0, 18))
        buttons_three.grid_columnconfigure((0, 1), weight=1)
        self._button(buttons_three, text="Delete Plain Cache", command=self.on_delete_plain_model, tone="danger").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(buttons_three, text="Refresh", command=self.refresh_model_status, tone="neutral").grid(row=0, column=1, sticky="ew", padx=(6, 0))

        security = self._card(scroll)
        security.grid(row=1, column=0, sticky="ew", padx=14, pady=(8, 14))
        security.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            security,
            text="Security & Startup",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))
        ctk.CTkLabel(
            security,
            text=(
                "Control startup password protection, rotate the vault key, and check whether the first-run secure setup "
                "has been completed on this device."
            ),
            anchor="w",
            justify="left",
            wraplength=980,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        security_status = self._readonly_box(security, height=120)
        security_status.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
        self._register("model_security_status", security_status)
        startup_preferences = ctk.CTkFrame(
            security,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
        )
        startup_preferences.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))
        startup_preferences.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            startup_preferences,
            text="Startup Password",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))
        self.startup_password_lock_var = tk.BooleanVar(value=bool(self.vault and self.vault.is_key_protected()))
        startup_lock_toggle = ctk.CTkCheckBox(
            startup_preferences,
            text="Require startup password on launch",
            variable=self.startup_password_lock_var,
            onvalue=True,
            offvalue=False,
            command=self.on_toggle_startup_password_lock,
            fg_color=DESKTOP_ACCENT,
            hover_color="#0d6b63",
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        startup_lock_toggle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        self.ids["startup_password_lock_toggle"] = startup_lock_toggle
        ctk.CTkLabel(
            startup_preferences,
            text=(
                "On wraps the local vault key with a startup password and asks for it once per launch. "
                "Off removes that password wrapper after confirmation."
            ),
            anchor="w",
            justify="left",
            wraplength=920,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        security_buttons = ctk.CTkFrame(security, fg_color="transparent")
        security_buttons.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 18))
        security_buttons.grid_columnconfigure((0, 1, 2), weight=1)
        self._button(security_buttons, text="Add / Change Password", command=self.on_change_startup_password).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        self._button(security_buttons, text="Remove Password", command=self.on_remove_startup_password, tone="neutral").grid(
            row=0, column=1, sticky="ew", padx=6
        )
        self._button(security_buttons, text="Rotate Vault Key", command=self.on_rotate_vault_key, tone="warning").grid(
            row=0, column=2, sticky="ew", padx=(6, 0)
        )
        checklist_preferences = ctk.CTkFrame(
            security,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
        )
        checklist_preferences.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 18))
        checklist_preferences.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            checklist_preferences,
            text="Checklist Safeguards",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))
        self.allow_checklist_uncheck_var = tk.BooleanVar(value=bool(self.settings_data.get("allow_checklist_uncheck", False)))
        checklist_uncheck_toggle = ctk.CTkCheckBox(
            checklist_preferences,
            text="Allow unchecking completed checklist rows",
            variable=self.allow_checklist_uncheck_var,
            onvalue=True,
            offvalue=False,
            command=self.on_toggle_checklist_uncheck,
            fg_color=DESKTOP_ACCENT,
            hover_color="#0d6b63",
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        checklist_uncheck_toggle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        self.ids["allow_checklist_uncheck_toggle"] = checklist_uncheck_toggle
        ctk.CTkLabel(
            checklist_preferences,
            text="Off by default so stray clicks do not erase logged doses. Turn it on only if you want dashboard checklist undo.",
            anchor="w",
            justify="left",
            wraplength=920,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))

        recovery_preferences = ctk.CTkFrame(
            security,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
        )
        recovery_preferences.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 18))
        recovery_preferences.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            recovery_preferences,
            text="Recovery Support",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))
        recovery_state_for_toggle = self.current_recovery_support_state()
        self.recovery_enabled_var = tk.BooleanVar(value=bool(recovery_state_for_toggle.get("enabled", False)))
        recovery_toggle = ctk.CTkCheckBox(
            recovery_preferences,
            text="Enable recovery support and Days Clean dashboard tile",
            variable=self.recovery_enabled_var,
            onvalue=True,
            offvalue=False,
            command=self.on_toggle_recovery_support,
            fg_color=DESKTOP_ACCENT,
            hover_color="#0d6b63",
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        recovery_toggle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        self.ids["recovery_enabled_toggle"] = recovery_toggle
        ctk.CTkLabel(
            recovery_preferences,
            text="Turn this off when recovery tracking is not part of your app use. Existing recovery notes stay encrypted but the dashboard will not promote the streak tile.",
            anchor="w",
            justify="left",
            wraplength=920,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        accessibility_preferences = ctk.CTkFrame(
            security,
            fg_color=DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            corner_radius=14,
        )
        accessibility_preferences.grid(row=7, column=0, sticky="ew", padx=18, pady=(0, 18))
        accessibility_preferences.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            accessibility_preferences,
            text="Accessibility",
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 6))
        ctk.CTkLabel(
            accessibility_preferences,
            text="Text size",
            anchor="w",
            text_color=DESKTOP_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=(16, 12), pady=(0, 10))
        text_size_menu = ctk.CTkOptionMenu(
            accessibility_preferences,
            values=list(TEXT_SIZE_OPTIONS),
            command=self.on_text_size_change,
            fg_color=DESKTOP_SURFACE,
            button_color=DESKTOP_ACCENT,
            button_hover_color="#0d6b63",
            dropdown_fg_color=DESKTOP_SURFACE_ALT,
            dropdown_hover_color="#223443",
            text_color=DESKTOP_TEXT,
            corner_radius=12,
        )
        text_size_menu.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=(0, 10))
        try:
            text_size_menu.set(self.settings_data.get("text_size", "Default"))
        except Exception:
            pass
        self.ids["text_size_menu"] = text_size_menu
        ctk.CTkLabel(
            accessibility_preferences,
            text="Adjust the interface text live and keep the preference saved on this device.",
            anchor="w",
            justify="left",
            wraplength=920,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 14))

    def set_status(self, text: str) -> None:
        status_label = self.ids.get("status_label") if hasattr(self.ids, "get") else None
        if status_label is not None:
            status_label.text = sanitize_text(text, max_chars=220)

    def show_dialog(self, title: str, text: str) -> None:
        if self.window is None:
            return
        clean_title = sanitize_text(title, max_chars=80)
        clean_text = sanitize_text(text, max_chars=3000)
        lowered = clean_title.lower()
        if any(token in lowered for token in ("failed", "warning", "flag", "attention")):
            messagebox.showwarning(clean_title, clean_text, parent=self.window)
        else:
            messagebox.showinfo(clean_title, clean_text, parent=self.window)

    def set_field_text(self, widget_id: str, value: str, *, force: bool = False) -> None:
        widget = self.ids.get(widget_id)
        if widget is None:
            return
        next_text = sanitize_text(value, max_chars=4000)
        if force or not bool(getattr(widget, "focus", False)):
            if getattr(widget, "text", None) != next_text:
                widget.text = next_text

    def current_checklist_target_day(self, now_ts: Optional[float] = None) -> date:
        today = datetime.fromtimestamp(now_ts or time.time()).date()
        parsed = parse_date_string(self.checklist_target_date_text)
        if parsed is None:
            parsed = today
            self.checklist_target_date_text = parsed.isoformat()
        return parsed

    def _set_checklist_target_day(self, target_day: date, *, announce: bool = False) -> None:
        self.checklist_target_date_text = target_day.isoformat()
        self.set_field_text("daily_checklist_date", self.checklist_target_date_text, force=True)
        self.refresh_dashboard()
        if announce:
            self.set_status(f"Viewing checklist for {target_day.isoformat()}.")

    def on_checklist_date_prev(self) -> None:
        self._set_checklist_target_day(self.current_checklist_target_day() - timedelta(days=1), announce=True)

    def on_checklist_date_today(self) -> None:
        self._set_checklist_target_day(datetime.fromtimestamp(time.time()).date(), announce=True)

    def on_checklist_date_next(self) -> None:
        self._set_checklist_target_day(self.current_checklist_target_day() + timedelta(days=1), announce=True)

    def on_checklist_date_go(self) -> None:
        raw_value = sanitize_text(getattr(self.ids.get("daily_checklist_date"), "text", ""), max_chars=20)
        parsed = parse_date_string(raw_value)
        if parsed is None:
            self.set_status("Use YYYY-MM-DD for the checklist date.")
            self.set_field_text("daily_checklist_date", self.checklist_target_date_text, force=True)
            return
        self._set_checklist_target_day(parsed, announce=True)

    def refresh_from_disk(self) -> None:
        if not self.vault:
            return
        try:
            self.data_cache = ensure_vault_shape(self.vault.load())
        except RuntimeError as exc:
            self.data_cache = vault_defaults()
            if self.main_ui_started:
                self.set_status(str(exc))
            return
        if self.selected_med_id and not self.current_selected_med():
            self.selected_med_id = None
        if not self.selected_med_id and self.data_cache.get("meds"):
            ranked = sorted(
                list(self.data_cache.get("meds") or []),
                key=lambda med: (
                    0 if medication_due_status(med)["overdue"] else 1 if medication_due_status(med)["due_now"] else 2,
                    medication_due_status(med)["next_ts"] or float("inf"),
                ),
            )
            self.selected_med_id = str(ranked[0].get("id"))
        self._restore_saved_dose_safety_review()
        self.refresh_ui()

    def refresh_time_sensitive_labels(self) -> None:
        self.refresh_dashboard()
        self.refresh_med_list()
        self.refresh_safety_ui()
        self.refresh_dental_ui()
        self.refresh_exercise_ui()
        self.refresh_recovery_support_ui()
        self.refresh_help_ui()

    def refresh_ui(self) -> None:
        self.refresh_dashboard()
        self.refresh_med_list()
        self.refresh_safety_ui()
        self.refresh_form()
        self.refresh_assistant_history()
        self.refresh_assistant_context_panel()
        self.refresh_model_status()
        self.refresh_vision_summary()
        self.refresh_dental_ui()
        self.refresh_exercise_ui()
        self.refresh_recovery_support_ui()
        self.refresh_help_ui()

    def save_data(self) -> bool:
        if self.vault_write_blocked_reason:
            self._handle_save_error(self.vault_write_blocked_reason, True)
            return False
        if self.vault:
            try:
                self.vault.save(self.data_cache)
            except RuntimeError as exc:
                self._handle_save_error(str(exc), True)
                return False
        return True

    def current_selected_med(self) -> Optional[Dict[str, Any]]:
        for med in self.data_cache.get("meds", []) or []:
            if str(med.get("id")) == self.selected_med_id:
                return med
        return None

    def _render_daily_checklist(self, med: Optional[Dict[str, Any]], now: float) -> None:
        frame = self.ids.daily_checklist_frame
        for child in frame.winfo_children():
            child.destroy()
        frame.grid_columnconfigure(0, weight=1)
        if not med:
            ctk.CTkLabel(
                frame,
                text="Select a medication to build today's checklist.",
                anchor="w",
                justify="left",
                wraplength=500,
                text_color=DESKTOP_MUTED,
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return
        slots = build_medication_daily_slots(med, datetime.fromtimestamp(now).date(), now)
        if not slots:
            next_slot = next_unchecked_medication_slot(med, now)
            message = "Add custom times or save an interval to generate a daily checklist."
            if next_slot is not None:
                message = f"No remaining slots today. Next planned dose: {next_slot['label']} {next_slot['time_text']}."
            ctk.CTkLabel(
                frame,
                text=message,
                anchor="w",
                justify="left",
                wraplength=500,
                text_color=DESKTOP_MUTED,
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
            return
        for row_index, slot in enumerate(slots):
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.grid(row=row_index, column=0, sticky="ew", padx=8, pady=4)
            row.grid_columnconfigure(1, weight=1)

            checkbox = ctk.CTkCheckBox(
                row,
                text=f"{slot['label']} • {slot['time_text']}",
                fg_color=DESKTOP_ACCENT,
                hover_color="#0d6b63",
                border_color=DESKTOP_BORDER,
                text_color=DESKTOP_TEXT,
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            checkbox.grid(row=0, column=0, sticky="w", padx=(4, 10))
            if slot.get("status") == "taken":
                checkbox.select()
                checkbox.configure(state="disabled")
            elif slot.get("status") == "missed":
                checkbox.deselect()
                checkbox.configure(state="disabled")
            else:
                checkbox.deselect()
                checkbox.configure(
                    command=lambda med_id=str(med.get("id")), slot_label=str(slot.get("label")): self.on_checklist_take_dose(med_id, slot_label)
                )

            if slot.get("status") == "missed":
                status_color = DESKTOP_DANGER
                status_text = f"X {slot['status_text']}"
            elif slot.get("status") == "due":
                status_color = DESKTOP_WARNING
                status_text = f"! {slot['status_text']}"
            elif slot.get("status") == "taken":
                status_color = DESKTOP_SUCCESS
                status_text = slot["status_text"]
            else:
                status_color = DESKTOP_MUTED
                status_text = slot["status_text"]

            ctk.CTkLabel(
                row,
                text=status_text,
                anchor="w",
                justify="left",
                wraplength=260,
                text_color=status_color,
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=1, sticky="ew")

            if slot.get("status") == "missed":
                self._button(
                    row,
                    text="Take Now",
                    command=lambda med_id=str(med.get("id")), slot_label=str(slot.get("label")): self.on_checklist_take_dose(med_id, slot_label),
                    tone="warning",
                ).grid(row=0, column=2, sticky="e", padx=(10, 0))

    def _log_dose_for_med(
        self,
        med: Dict[str, Any],
        *,
        source_label: str = "dose",
        log_timestamp: Optional[float] = None,
        scheduled_ts: float = 0.0,
        slot_key: str = "",
        enforce_safety: bool = True,
    ) -> None:
        dose_value = max(0.0, safe_float(self.ids.dose_mg.text) or safe_float(med.get("dose_mg")))
        now = time.time()
        effective_timestamp = safe_float(log_timestamp) if log_timestamp is not None else now
        assessment_timestamp = effective_timestamp if effective_timestamp > 0.0 else now
        slot_info = {
            "slot_key": sanitize_text(slot_key or "", max_chars=64),
            "scheduled_ts": max(0.0, safe_float(scheduled_ts)),
        }
        existing_slot_record = (
            matching_medication_history_entry_for_slot(med, slot_info)
            if (slot_info["slot_key"] or slot_info["scheduled_ts"] > 0.0)
            else None
        )
        if existing_slot_record is not None:
            self.last_check_level = "Caution"
            self.last_check_display = "Already checked"
            self.last_check_message = f"{source_label or 'Dose'} was already recorded for this checklist slot."
            self.refresh_ui()
            self.set_status(self.last_check_message)
            return
        duplicate_ts = None
        if not slot_info["slot_key"] and slot_info["scheduled_ts"] <= 0.0:
            duplicate_ts = recent_duplicate_log_ts(med, dose_value, assessment_timestamp)
        if duplicate_ts is not None:
            self.last_check_level = "Caution"
            self.last_check_display = "Already checked"
            self.last_check_message = f"{source_label or 'Dose'} looks like a duplicate log from {format_timestamp(duplicate_ts)}."
            self.refresh_ui()
            self.set_status(self.last_check_message)
            return
        label, message = dose_safety_level(med, dose_value, assessment_timestamp)
        source_suffix = f" Logged for {source_label}." if source_label else ""
        self.last_check_level = label
        self.last_check_display = label
        self.last_check_message = message + (source_suffix if label != "High" else "")
        if label == "High":
            self.refresh_ui()
            self.set_status(message)
            if enforce_safety:
                self.show_dialog("High Safety Flag", message)
                return
            self.last_check_message = message + " Checklist slot marked anyway."
        original_data = self.clone_data_snapshot()
        original_med = self.clone_med_snapshot(med)
        append_medication_history_entry(
            med,
            effective_timestamp,
            dose_value,
            scheduled_ts=slot_info["scheduled_ts"],
            slot_key=slot_info["slot_key"],
        )
        if dose_value > 0:
            med["dose_mg"] = dose_value
        _desktop_apply_local_dose_review(self, original_med, dose_value, assessment_timestamp, source_label=source_label)
        if not self.save_data():
            self.data_cache = original_data
            self.refresh_ui()
            return
        self.refresh_ui()
        self.set_status(self.last_check_message)

    def on_checklist_take_dose(self, med_id: str, slot_label: str) -> None:
        self.selected_med_id = med_id
        med = self.current_selected_med()
        if not med:
            return
        self._log_dose_for_med(med, source_label=slot_label)

    def refresh_dashboard(self) -> None:
        now = time.time()
        meds = list(self.data_cache.get("meds") or [])
        med_statuses = [(medication_due_status(med, now), med) for med in meds]
        due_now = [med for status, med in med_statuses if status["due_now"] and not status["overdue"]]
        overdue = [med for status, med in med_statuses if status["overdue"]]
        next_due_items = [
            (status["next_ts"], med)
            for status, med in med_statuses
            if status["next_ts"] is not None
        ]
        next_due_items.sort(key=lambda item: item[0] or float("inf"))
        next_due_text = "Nothing scheduled yet"
        if next_due_items:
            next_due_ts, med = next_due_items[0]
            next_due_text = f"{sanitize_text(med.get('name'), max_chars=120)} | {format_relative_due(next_due_ts, now)}"

        selected = self.current_selected_med()
        selection_text = "Select a medication to log doses."
        summary_text = "No medication selected."
        schedule_text = "Today's dose plan will appear here."
        if selected:
            selected_slots = build_medication_daily_slots(selected, datetime.fromtimestamp(now).date(), now)
            remaining_slots = len([slot for slot in selected_slots if slot.get("status") != "taken"])
            selection_text = f"Focused med: {sanitize_text(selected.get('name'), max_chars=120)}"
            summary_text = (
                f"{sanitize_text(selected.get('name'), max_chars=120)}\n"
                f"{medication_card_line(selected, now)}\n"
                f"Last taken: {format_timestamp(last_effective_taken_ts(selected))}\n"
                f"Remaining planned slots today: {remaining_slots}\n"
                f"Directions: {sanitize_text(selected.get('schedule_text') or 'No bottle directions saved yet.', max_chars=260)}"
            )
            schedule_text = build_medication_schedule_text(selected, now)

        self.ids.dose_wheel.set_level(self.last_check_level)
        self.ids.dashboard_risk_title.text = self.last_check_display
        self.ids.dashboard_risk_caption.text = self.last_check_message
        self.ids.today_due_count.text = f"{len(due_now)} active | {len(overdue)} missed"
        self.ids.today_next_due.text = next_due_text
        self.ids.today_timeline.text = build_timeline_text(meds, now)
        self.ids.dashboard_selection.text = selection_text
        self.ids.selected_med_summary.text = summary_text
        if "selected_med_schedule" in self.ids:
            self.ids.selected_med_schedule.text = schedule_text
        self.ids.selected_med_history.text = build_recent_activity_text(self.data_cache)
        self.ids.dashboard_nudge.text = build_dashboard_nudge_text(
            selected,
            self.current_recovery_support_state(),
            now,
        )
        self._render_daily_checklist(selected, now)

    def refresh_med_list(self) -> None:
        med_list = self.ids.med_list
        med_list.clear_widgets()
        meds = list(self.data_cache.get("meds") or [])
        now = time.time()
        for med in sorted(
            meds,
            key=lambda item: (
                0 if medication_due_status(item, now)["overdue"] else 1 if medication_due_status(item, now)["due_now"] else 2,
                medication_due_status(item, now)["next_ts"] or float("inf"),
                sanitize_text(item.get("name"), max_chars=120).lower(),
            ),
        ):
            title = sanitize_text(med.get("name"), max_chars=120)
            prefix = "Selected | " if str(med.get("id")) == self.selected_med_id else ""
            med_list.add_widget(
                DesktopListItem(
                    text=prefix + title,
                    secondary_text=medication_card_line(med, now),
                    on_release=lambda _widget, med_id=str(med.get("id")): self.select_med(med_id),
                )
            )

    def refresh_form(self) -> None:
        med = self.current_selected_med()
        if not med:
            self.last_form_med_id = None
            self.ids.form_selection.text = "Creating a new medication"
            self.ids.form_schedule_preview.text = "Saved schedules appear below."
            self.set_field_text("first_dose_time", "", force=True)
            self.set_field_text("custom_times_text", "", force=True)
            return
        med_id = str(med.get("id"))
        force_sync = med_id != self.last_form_med_id
        self.ids.form_selection.text = f"Editing: {sanitize_text(med.get('name'), max_chars=120)}"
        self.set_field_text("med_name", sanitize_text(med.get("name") or "", max_chars=120), force=force_sync)
        self.set_field_text("dose_mg", f"{safe_float(med.get('dose_mg')):g}" if safe_float(med.get("dose_mg")) else "", force=force_sync)
        self.set_field_text("interval_h", f"{safe_float(med.get('interval_hours')):g}" if safe_float(med.get("interval_hours")) else "", force=force_sync)
        self.set_field_text("max_daily", f"{safe_float(med.get('max_daily_mg')):g}" if safe_float(med.get("max_daily_mg")) else "", force=force_sync)
        self.set_field_text("first_dose_time", sanitize_text(med.get("first_dose_time") or "", max_chars=20), force=force_sync)
        self.set_field_text("custom_times_text", sanitize_text(med.get("custom_times_text") or "", max_chars=320), force=force_sync)
        self.set_field_text("schedule_text", sanitize_text(med.get("schedule_text") or "", max_chars=240), force=force_sync)
        self.set_field_text("med_notes", sanitize_text(med.get("notes") or "", max_chars=500), force=force_sync)
        self.ids.form_schedule_preview.text = medication_card_line(med) + "\n" + build_medication_schedule_text(med)
        self.last_form_med_id = med_id

    def refresh_assistant_history(self) -> None:
        history = list(self.data_cache.get("assistant_history") or [])
        if not history:
            self.ids.assistant_history.text = "No assistant messages yet."
            return
        lines = []
        for item in history[-12:]:
            speaker = "You" if item.get("role") == "user" else "MedSafe"
            mode = normalize_assistant_mode(item.get("mode") or "General")
            mode_suffix = "" if mode == "General" else f" | {mode}"
            lines.append(f"{speaker}{mode_suffix}\n{sanitize_text(item.get('content') or '', max_chars=1200)}")
        self.ids.assistant_history.text = "\n\n".join(lines)

    def refresh_vision_summary(self) -> None:
        imports = list(self.data_cache.get("vision_imports") or [])
        if not imports:
            self.ids.vision_result.text = "No bottle photo processed yet."
            return
        latest = imports[-1]
        risk_score = max(0.0, min(100.0, safe_float(latest.get("risk_score"))))
        risk_level = normalized_risk_level_text(latest.get("risk_level") or "", risk_score)
        risk_summary = sanitize_text(latest.get("risk_summary") or "", max_chars=220)
        lines = [
            f"Imported from: {sanitize_text(latest.get('image_name') or 'photo', max_chars=120)}",
            sanitize_text(latest.get("summary") or "Schedule imported.", max_chars=300),
        ]
        if risk_score > 0 or risk_summary:
            lines.append(f"Review risk: {risk_level} | {risk_score:.0f}/100")
            if risk_summary:
                lines.append(f"Risk note: {risk_summary}")
        lines.append(format_timestamp(safe_float(latest.get("timestamp"))))
        self.ids.vision_result.text = "\n".join(lines)

    def refresh_dental_ui(self) -> None:
        now = time.time()
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        brush = habit_due_status(safe_float(hygiene.get("last_brush_ts")), safe_float(hygiene.get("brush_interval_hours")) or 12.0, now)
        floss = habit_due_status(safe_float(hygiene.get("last_floss_ts")), safe_float(hygiene.get("floss_interval_hours")) or 24.0, now)
        rinse = habit_due_status(safe_float(hygiene.get("last_rinse_ts")), safe_float(hygiene.get("rinse_interval_hours")) or 24.0, now)
        overview_title, overview_body = build_dental_overview(
            hygiene,
            dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults()),
            now,
        )
        self.ids.dental_overview_title.text = overview_title
        self.ids.dental_overview_body.text = overview_body
        for prefix, status, interval in (
            ("brush", brush, safe_float(hygiene.get("brush_interval_hours")) or 12.0),
            ("floss", floss, safe_float(hygiene.get("floss_interval_hours")) or 24.0),
            ("rinse", rinse, safe_float(hygiene.get("rinse_interval_hours")) or 24.0),
        ):
            title_color, caption_color = habit_palette(status)
            self.ids[f"dental_{prefix}_status"].text = status["state"]
            self.ids[f"dental_{prefix}_status"].text_color = title_color
            self.ids[f"dental_{prefix}_caption"].text = f"{status['text']} | every {interval:g}h"
            self.ids[f"dental_{prefix}_caption"].text_color = caption_color
        self.set_field_text("dental_brush_interval", f"{safe_float(hygiene.get('brush_interval_hours')):g}")
        self.set_field_text("dental_floss_interval", f"{safe_float(hygiene.get('floss_interval_hours')):g}")
        self.set_field_text("dental_rinse_interval", f"{safe_float(hygiene.get('rinse_interval_hours')):g}")
        self.ids.dental_hygiene_photo.text = f"Last hygiene photo: {sanitize_text(hygiene.get('latest_photo') or 'none', max_chars=120)}"
        if hygiene.get("latest_rating"):
            rating_color = score_palette(safe_float(hygiene.get("latest_score")))
            hygiene_history = list(hygiene.get("history") or [])
            latest_hygiene_review = hygiene_history[-1] if hygiene_history else {}
            self.ids.dental_hygiene_rating.text = (
                f"{sanitize_text(hygiene.get('latest_rating') or '', max_chars=80)} | {safe_float(hygiene.get('latest_score')):.0f}/100"
            )
            self.ids.dental_hygiene_rating.text_color = rating_color
            warning = sanitize_text(hygiene.get("latest_warning_flags") or "None flagged", max_chars=220)
            confidence = max(0.0, min(1.0, safe_float(latest_hygiene_review.get("confidence"))))
            risk_score = max(0.0, min(100.0, safe_float(hygiene.get("latest_risk_score"))))
            risk_level = normalized_risk_level_text(hygiene.get("latest_risk_level") or "", risk_score)
            risk_summary = sanitize_text(hygiene.get("latest_risk_summary") or "", max_chars=220)
            trend_text = f"Trend: {score_change_text(hygiene_history)} AI confidence {confidence:.2f}."
            if risk_score > 0 or risk_summary:
                trend_text += f" Risk: {risk_level} {risk_score:.0f}/100."
            self.ids.dental_hygiene_trend.text = trend_text
            summary_lines = [
                sanitize_text(hygiene.get("latest_summary") or "", max_chars=280),
                f"Suggestions: {sanitize_text(hygiene.get('latest_suggestions') or '', max_chars=320)}",
            ]
            if risk_score > 0 or risk_summary:
                summary_lines.append(
                    f"Risk: {risk_level} | {risk_score:.0f}/100 | "
                    f"{risk_summary or 'Use the photo and your symptoms together before acting.'}"
                )
            summary_lines.extend(
                [
                    f"Warnings: {warning}",
                    build_dental_hygiene_history_text(hygiene),
                ]
            )
            self.ids.dental_hygiene_summary.text = "\n".join(summary_lines)
        else:
            self.ids.dental_hygiene_rating.text = "No hygiene rating yet."
            self.ids.dental_hygiene_rating.text_color = DESKTOP_TEXT
            self.ids.dental_hygiene_trend.text = "Trend: take two AI reviews over time to compare your hygiene rhythm."
            self.ids.dental_hygiene_summary.text = "Take a photo for a cleanliness score, visible-sign review, and gentle brushing/flossing suggestions."
        if hygiene.get("latest_timestamp") and hygiene.get("latest_rating"):
            self.ids.dental_hygiene_status.text = (
                f"Latest review: {sanitize_text(hygiene.get('latest_rating') or '', max_chars=80)} | "
                f"{format_timestamp(safe_float(hygiene.get('latest_timestamp')))}"
            )
        else:
            self.ids.dental_hygiene_status.text = "Ready for a teeth photo."

        recovery = dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults())
        self.set_field_text("recovery_procedure_type", sanitize_text(recovery.get("procedure_type") or "", max_chars=120))
        self.set_field_text("recovery_procedure_date", sanitize_text(recovery.get("procedure_date") or "", max_chars=20))
        self.set_field_text("recovery_symptom_notes", sanitize_text(recovery.get("symptom_notes") or "", max_chars=600))
        self.set_field_text("recovery_care_notes", sanitize_text(recovery.get("care_notes") or "", max_chars=600))
        self.ids.recovery_last_photo.text = f"Last recovery photo: {sanitize_text(recovery.get('latest_photo') or 'none', max_chars=120)}"
        day_count = days_since_date_string(str(recovery.get("procedure_date") or ""))
        if recovery.get("enabled"):
            day_text = f"Day {day_count + 1}" if day_count is not None else "Day unknown"
            self.ids.recovery_mode_status.text = f"{sanitize_text(recovery.get('procedure_type') or 'Recovery mode', max_chars=120)} | {day_text}"
            self.ids.recovery_mode_status.text_color = score_palette(safe_float(recovery.get("latest_score") or 70.0))
            score_hint = f" Latest AI recovery score: {safe_float(recovery.get('latest_score')):.0f}/100." if safe_float(recovery.get("latest_score")) else ""
            self.ids.recovery_snapshot.text = f"Daily journal active. {score_change_text(list(recovery.get('daily_logs') or []))}{score_hint}"
        else:
            self.ids.recovery_mode_status.text = "Recovery mode is off."
            self.ids.recovery_mode_status.text_color = DESKTOP_MUTED
            self.ids.recovery_snapshot.text = "Set a procedure type and date to start a daily recovery journal."
        if recovery.get("latest_status"):
            recovery_logs = list(recovery.get("daily_logs") or [])
            latest_recovery_log = recovery_logs[-1] if recovery_logs else {}
            warning = sanitize_text(recovery.get("latest_warning_flags") or "None flagged", max_chars=260)
            confidence = max(0.0, min(1.0, safe_float(latest_recovery_log.get("confidence"))))
            risk_score = max(0.0, min(100.0, safe_float(recovery.get("latest_risk_score"))))
            risk_level = normalized_risk_level_text(recovery.get("latest_risk_level") or "", risk_score)
            risk_summary = sanitize_text(recovery.get("latest_risk_summary") or "", max_chars=240)
            result_lines = [
                f"{sanitize_text(recovery.get('latest_status') or '', max_chars=120)} | {safe_float(recovery.get('latest_score')):.0f}/100",
                sanitize_text(recovery.get("latest_summary") or "", max_chars=320),
                f"Suggestions: {sanitize_text(recovery.get('latest_advice') or '', max_chars=360)}",
            ]
            if risk_score > 0 or risk_summary:
                result_lines.append(
                    f"Risk: {risk_level} | {risk_score:.0f}/100 | "
                    f"{risk_summary or 'Use the image and symptoms together before deciding next steps.'}"
                )
            result_lines.extend(
                [
                    f"Warnings: {warning}",
                    f"AI confidence: {confidence:.2f}",
                    build_recovery_history_text(recovery),
                ]
            )
            self.ids.recovery_result.text = "\n".join(result_lines)
        else:
            self.ids.recovery_result.text = "Recovery suggestions here stay general and should never replace your dentist's instructions."

    def model_state_summary(self) -> str:
        if not self.paths:
            return "Storage not ready."
        plain_exists = self.paths.plain_model_path.exists()
        encrypted_exists = self.paths.encrypted_model_path.exists()
        encrypted_size = human_size(self.paths.encrypted_model_path.stat().st_size) if encrypted_exists else "0B"
        plain_size = human_size(self.paths.plain_model_path.stat().st_size) if plain_exists else "0B"
        return (
            f"Encrypted model: {'yes' if encrypted_exists else 'no'} ({encrypted_size})\n"
            f"Plain copy: {'yes' if plain_exists else 'no'} ({plain_size})\n"
            f"Model file: {MODEL_FILE}"
        )

    def security_state_summary(self) -> str:
        if not self.paths or not self.vault:
            return "Security state is not ready."
        password_enabled = self.vault.is_key_protected()
        unlocked = self.vault.is_unlocked()
        setup_complete = bool(self.settings_data.get("setup_complete", False))
        checklist_undo = "enabled" if self.settings_data.get("allow_checklist_uncheck", False) else "off"
        launch_lock = "required" if password_enabled or self.settings_data.get("startup_password_enabled", False) else "off"
        if password_enabled:
            verdict = "Startup password is protecting future launches."
        elif self.settings_data.get("startup_password_enabled", False):
            verdict = "Startup password is requested; MedSafe will require repair before opening a future locked session."
        else:
            verdict = "Startup password is off. The vault is still encrypted on disk."
        return (
            f"{verdict}\n"
            f"Startup password: {'enabled' if password_enabled else 'off'}\n"
            f"Require startup password on launch: {launch_lock}\n"
            f"Vault session: {'unlocked for this session' if unlocked else 'locked'}\n"
            f"First-start setup: {'complete' if setup_complete else 'pending'}\n"
            f"Checklist undo: {checklist_undo}\n"
            f"Key rotation: ready\n"
            f"Vault root: {self.paths.root}"
        )

    def refresh_model_status(self) -> None:
        settings = load_settings(self.paths) if self.paths else dict(DEFAULT_SETTINGS)
        self.settings_data = settings
        backend = settings.get("inference_backend", "Auto")
        auto_selected = settings.get("auto_selected_inference_backend", "")
        if backend != "Auto":
            backend_note = backend
        else:
            auto_hint = auto_selected
            if not auto_hint:
                try:
                    auto_hint = choose_auto_inference_backend_name()
                except Exception:
                    auto_hint = "pending"
            backend_note = f"Auto ({auto_hint})"
        image_state = "on" if settings.get("enable_native_image_input", True) else "off"
        password_state = "on" if self.vault and self.vault.is_key_protected() else "off"
        self.ids.model_status.text = self.model_state_summary()
        self.ids.model_security_status.text = self.security_state_summary()
        self.ids.model_backend_label.text = f"Backend: {backend_note} | Native image input: {image_state}"
        self.ids.dashboard_model_state.text = (
            f"Model: {'ready' if self.paths and self.paths.encrypted_model_path.exists() else 'not downloaded'}"
            f" | Image input {image_state} | Password {password_state}"
        )
        if self.allow_checklist_uncheck_var is not None:
            try:
                self.allow_checklist_uncheck_var.set(bool(settings.get("allow_checklist_uncheck", False)))
            except Exception:
                pass
        if self.recovery_enabled_var is not None:
            try:
                self.recovery_enabled_var.set(bool(self.current_recovery_support_state().get("enabled", False)))
            except Exception:
                pass
        if self.startup_password_lock_var is not None:
            try:
                self.startup_password_lock_var.set(bool(self.vault and self.vault.is_key_protected()))
            except Exception:
                pass

    def on_toggle_recovery_support(self) -> None:
        state = self.current_recovery_support_state()
        enabled = bool(self.recovery_enabled_var.get()) if self.recovery_enabled_var is not None else False
        state["enabled"] = enabled
        self.data_cache["recovery_support"] = state
        self.save_data()
        self.refresh_dashboard()
        self.refresh_recovery_support_ui()
        self.set_status(
            "Recovery support enabled. Days Clean appears after the first recovery check-in."
            if enabled
            else "Recovery support disabled. Existing encrypted recovery history was kept."
        )

    def on_toggle_checklist_uncheck(self) -> None:
        enabled = bool(self.allow_checklist_uncheck_var.get()) if self.allow_checklist_uncheck_var is not None else False
        save_settings({"allow_checklist_uncheck": enabled}, self.paths)
        self.settings_data = load_settings(self.paths)
        self.refresh_model_status()
        self.refresh_dashboard()
        self.set_status(
            "Checklist undo enabled. Taken rows can now be unchecked from the dashboard."
            if enabled
            else "Checklist undo disabled. Taken rows are locked again."
        )

    def on_toggle_startup_password_lock(self) -> None:
        if not self.vault:
            return
        enabled = bool(self.startup_password_lock_var.get()) if self.startup_password_lock_var is not None else False
        if enabled:
            if self.vault.is_key_protected():
                self._save_security_settings()
                self.refresh_model_status()
                self.set_status("Startup password is already required on future launches.")
                return
            password = self._prompt_new_password("Startup Password")
            if password is None:
                if self.startup_password_lock_var is not None:
                    self.startup_password_lock_var.set(False)
                self.refresh_model_status()
                self.set_status("Startup password setting was not changed.")
                return
            try:
                self.vault.enable_password(password)
                self._save_security_settings()
                self.refresh_model_status()
                self.set_status("Startup password required on the next launch.")
            except Exception as exc:
                if self.startup_password_lock_var is not None:
                    self.startup_password_lock_var.set(False)
                self.refresh_model_status()
                self.show_dialog("Startup Password Failed", str(exc))
                self.set_status("Startup password update failed.")
            return

        if not self.vault.is_key_protected():
            if self.paths is not None:
                save_settings({"startup_password_enabled": False}, self.paths)
                self.settings_data = load_settings(self.paths)
            self.refresh_model_status()
            self.set_status("Startup password is already off.")
            return
        if self.window is not None and not messagebox.askyesno(
            "Turn Off Startup Password",
            "Stop requiring the startup password on future launches?\n\n"
            "The vault stays encrypted, but the local key will no longer be password-wrapped.",
            parent=self.window,
        ):
            if self.startup_password_lock_var is not None:
                self.startup_password_lock_var.set(True)
            self.refresh_model_status()
            self.set_status("Startup password stayed on.")
            return
        current_password = self._prompt_current_password_if_needed("Remove Startup Password")
        if current_password is None:
            if self.startup_password_lock_var is not None:
                self.startup_password_lock_var.set(True)
            self.refresh_model_status()
            self.set_status("Startup password stayed on.")
            return
        try:
            self.vault.disable_password(current_password=current_password)
            self._save_security_settings()
            self.refresh_model_status()
            self.set_status("Startup password disabled for future launches.")
        except Exception as exc:
            if self.startup_password_lock_var is not None:
                self.startup_password_lock_var.set(True)
            self.refresh_model_status()
            self.show_dialog("Startup Password Failed", str(exc))
            self.set_status("Could not turn off startup password.")

    def reset_form_fields(self) -> None:
        self.ids.med_name.text = ""
        self.ids.dose_mg.text = ""
        self.ids.interval_h.text = ""
        self.ids.max_daily.text = ""
        self.ids.first_dose_time.text = ""
        self.ids.custom_times_text.text = ""
        self.ids.schedule_text.text = ""
        self.ids.med_notes.text = ""
        self.ids.form_selection.text = "Creating a new medication"
        self.ids.form_schedule_preview.text = "Saved schedules appear below."

    def select_med(self, med_id: str) -> None:
        self.selected_med_id = med_id
        self.refresh_ui()

    def on_dashboard_med_select(self, label: str) -> None:
        med_id = sanitize_text((self.dashboard_med_option_map or {}).get(label) or "", max_chars=32)
        self.selected_med_id = med_id or None
        if self.selected_med_id:
            med = self.med_by_id(self.selected_med_id)
            if med and medication_is_archived(med):
                self.set_status(f"Viewing completed history for {sanitize_text(med.get('name'), max_chars=120)}.")
            elif med:
                self.set_status(f"Dashboard focus set to {sanitize_text(med.get('name'), max_chars=120)}.")
        else:
            self.set_status("Dashboard focus cleared.")
        self.refresh_dashboard()
        self.refresh_med_list()

    def on_new_med(self) -> None:
        self.selected_med_id = None
        self.last_form_med_id = None
        self.reset_form_fields()
        self.set_status("Ready to add a new medication.")
        self.refresh_ui()

    def on_save_med(self) -> None:
        name = sanitize_text(self.ids.med_name.text, max_chars=120)
        if not name:
            self.set_status("Enter a medication name first.")
            return
        dose_mg = max(0.0, safe_float(self.ids.dose_mg.text))
        interval_hours = max(0.0, safe_float(self.ids.interval_h.text))
        max_daily_mg = max(0.0, safe_float(self.ids.max_daily.text))
        first_dose_time = sanitize_text(self.ids.first_dose_time.text, max_chars=20)
        custom_times_text = sanitize_text(self.ids.custom_times_text.text, max_chars=320)
        schedule_text = sanitize_text(self.ids.schedule_text.text, max_chars=240)
        notes = sanitize_text(self.ids.med_notes.text, max_chars=500)
        if first_dose_time and parse_clock_minutes(first_dose_time) is None:
            self.set_status("Use HH:MM or am/pm format for the first planned dose time.")
            return
        if custom_times_text and not parse_custom_dose_times_text(custom_times_text):
            self.set_status("Use times like Breakfast 08:00, Lunch 13:00, Dinner 18:00 in the custom plan.")
            return

        meds = list(self.data_cache.get("meds") or [])
        selected_med = self.current_selected_med()
        created_new = should_create_new_med_entry(selected_med, name)
        created_from_name_change = selected_med is not None and created_new
        med = selected_med
        if created_new:
            med = {
                "id": uuid.uuid4().hex[:12],
                "name": name,
                "dose_mg": dose_mg,
                "interval_hours": interval_hours,
                "max_daily_mg": max_daily_mg,
                "created_ts": time.time(),
                "first_dose_time": first_dose_time,
                "custom_times_text": custom_times_text,
                "schedule_text": schedule_text,
                "notes": notes,
                "source": "manual",
                "source_photo": "",
                "last_taken_ts": 0.0,
                "history": [],
            }
            meds.append(med)
            self.selected_med_id = med["id"]
        else:
            med["name"] = name
            med["dose_mg"] = dose_mg
            med["interval_hours"] = interval_hours
            med["max_daily_mg"] = max_daily_mg
            med["first_dose_time"] = first_dose_time
            med["custom_times_text"] = custom_times_text
            med["schedule_text"] = schedule_text
            med["notes"] = notes

        self.data_cache["meds"] = meds
        self.save_data()
        self.last_check_level = "Medium"
        self.last_check_display = "Schedule saved"
        self.last_check_message = f"{name} was saved to the encrypted schedule vault."
        if created_new:
            self.selected_med_id = None
            self.last_form_med_id = None
            self.reset_form_fields()
        self.refresh_ui()
        if created_new:
            if created_from_name_change:
                self.set_status(f"Saved {name} as a new medication. Ready to add another medication.")
            else:
                self.set_status(f"Saved {name}. Ready to add another medication.")
        else:
            self.set_status(f"Saved {name}.")

    def on_delete_med(self) -> None:
        med = self.current_selected_med()
        if not med:
            self.set_status("Select a medication first.")
            return
        name = sanitize_text(med.get("name"), max_chars=120)
        self.data_cache["meds"] = [item for item in self.data_cache.get("meds", []) or [] if str(item.get("id")) != self.selected_med_id]
        self.selected_med_id = None
        self.save_data()
        self.reset_form_fields()
        self.last_check_level = "Medium"
        self.last_check_display = "Medication removed"
        self.last_check_message = f"{name} was removed from the local schedule."
        self.refresh_ui()
        self.set_status(f"Deleted {name}.")

    def on_log_dose(self) -> None:
        med = self.current_selected_med()
        if not med:
            self.set_status("Select a medication before logging a dose.")
            return
        self._log_dose_for_med(med)

    def on_run_safety_check(self) -> None:
        med = self.current_selected_med()
        if not med:
            self.set_status("Select a medication before running a safety check.")
            return
        dose_value = max(0.0, safe_float(self.ids.dose_mg.text) or safe_float(med.get("dose_mg")))
        if dose_value <= 0:
            self.set_status("Enter or save a dose amount before running a safety check.")
            return
        self.start_dose_safety_assessment(med, dose_value, source_label="manual check")

    def on_run_all_meds_safety_check(self) -> None:
        self.trigger_safety_scan("manual safety scan", announce=True)

    def _all_meds_safety_done(self, result: Dict[str, Any]) -> None:
        review = dict(result or {})
        review["signature"] = review.get("signature") or regimen_signature(list(self.data_cache.get("meds") or []))
        self.regimen_check_review = review
        self.refresh_dashboard()
        self.set_status(sanitize_text(review.get("message") or "Combined regimen review updated.", max_chars=220))

    def on_log_dental_habit(self, habit: str) -> None:
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        now = time.time()
        habit_key = {
            "brush": "last_brush_ts",
            "floss": "last_floss_ts",
            "rinse": "last_rinse_ts",
        }.get(habit)
        if not habit_key:
            return
        hygiene[habit_key] = now
        self.data_cache["dental_hygiene"] = hygiene
        self.save_data()
        self.refresh_dental_ui()
        self.set_status(f"Logged dental {habit} routine.")

    def on_save_dental_intervals(self) -> None:
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        values = {
            "brush_interval_hours": max(1.0, safe_float(self.ids.dental_brush_interval.text) or safe_float(hygiene.get("brush_interval_hours")) or 12.0),
            "floss_interval_hours": max(1.0, safe_float(self.ids.dental_floss_interval.text) or safe_float(hygiene.get("floss_interval_hours")) or 24.0),
            "rinse_interval_hours": max(1.0, safe_float(self.ids.dental_rinse_interval.text) or safe_float(hygiene.get("rinse_interval_hours")) or 24.0),
        }
        hygiene.update(values)
        self.data_cache["dental_hygiene"] = hygiene
        self.save_data()
        self.set_field_text("dental_brush_interval", f"{values['brush_interval_hours']:g}", force=True)
        self.set_field_text("dental_floss_interval", f"{values['floss_interval_hours']:g}", force=True)
        self.set_field_text("dental_rinse_interval", f"{values['rinse_interval_hours']:g}", force=True)
        self.refresh_dental_ui()
        self.set_status("Dental reminder rhythm saved.")

    def on_reset_dental_intervals(self) -> None:
        hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
        defaults = dental_hygiene_defaults()
        hygiene["brush_interval_hours"] = defaults["brush_interval_hours"]
        hygiene["floss_interval_hours"] = defaults["floss_interval_hours"]
        hygiene["rinse_interval_hours"] = defaults["rinse_interval_hours"]
        self.data_cache["dental_hygiene"] = hygiene
        self.save_data()
        self.set_field_text("dental_brush_interval", f"{defaults['brush_interval_hours']:g}", force=True)
        self.set_field_text("dental_floss_interval", f"{defaults['floss_interval_hours']:g}", force=True)
        self.set_field_text("dental_rinse_interval", f"{defaults['rinse_interval_hours']:g}", force=True)
        self.refresh_dental_ui()
        self.set_status("Dental reminder rhythm reset to defaults.")

    def recovery_state_from_form(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "procedure_type": sanitize_text(self.ids.recovery_procedure_type.text, max_chars=120),
            "procedure_date": sanitize_text(self.ids.recovery_procedure_date.text, max_chars=20),
            "symptom_notes": sanitize_text(self.ids.recovery_symptom_notes.text, max_chars=600),
            "care_notes": sanitize_text(self.ids.recovery_care_notes.text, max_chars=600),
        }

    def on_save_recovery_mode(self) -> None:
        recovery = dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults())
        form_state = self.recovery_state_from_form()
        if not form_state["procedure_type"]:
            self.set_status("Enter the dental procedure before enabling recovery mode.")
            return
        if form_state["procedure_date"] and parse_date_string(form_state["procedure_date"]) is None:
            self.set_status("Use YYYY-MM-DD for the procedure date.")
            return
        recovery.update(form_state)
        self.data_cache["dental_recovery"] = recovery
        self.save_data()
        self.refresh_dental_ui()
        self.set_status("Dental recovery mode saved.")

    def on_pause_recovery_mode(self) -> None:
        recovery = dict(self.data_cache.get("dental_recovery") or dental_recovery_defaults())
        recovery["enabled"] = False
        self.data_cache["dental_recovery"] = recovery
        self.save_data()
        self.refresh_dental_ui()
        self.set_status("Dental recovery mode paused.")

    def _stage_desktop_image(self, source: Path) -> Path:
        if not self.paths:
            return source
        suffix = source.suffix.lower() if source.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS else ".jpg"
        target = self.paths.media_dir / f"desktop_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}{suffix}"
        try:
            shutil.copy2(source, target)
            _set_owner_only_permissions(target)
            return target
        except Exception:
            return source

    def _capture_photo(
        self,
        prefix: str,
        opening_status: str,
        on_ready: Callable[[Path], None],
        on_failure: Callable[[str], None],
    ) -> None:
        _ = prefix
        self.set_status(opening_status)
        self._pick_photo("Choose an image from your computer...", on_ready, on_failure)

    def _pick_photo(
        self,
        choose_status: str,
        on_ready: Callable[[Path], None],
        on_failure: Callable[[str], None],
    ) -> None:
        if self.window is None:
            on_failure("Desktop window is not available.")
            return
        self.set_status(choose_status)
        try:
            selection = filedialog.askopenfilename(
                parent=self.window,
                title="Select an image",
                initialdir=str(self.paths.media_dir if self.paths else Path.home()),
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")],
            )
        except Exception as exc:
            on_failure(str(exc))
            return
        if not selection:
            self.set_status("Photo selection cancelled.")
            return
        try:
            chosen = self._stage_desktop_image(Path(selection))
        except Exception as exc:
            on_failure(str(exc))
            return
        on_ready(chosen)

    def set_assistant_context_visible(self, visible: bool) -> None:
        self.assistant_context_visible = bool(visible)
        panel = self.ids.get("assistant_context_sidebar")
        chat_card = self.ids.get("assistant_chat_card")
        toggle = self.ids.get("assistant_context_toggle_button")
        if panel is not None:
            try:
                parent = getattr(panel, "master", None)
                if parent is not None:
                    parent.grid_columnconfigure(0, weight=0, minsize=330 if self.assistant_context_visible else 0)
                    parent.grid_columnconfigure(1, weight=1)
                if self.assistant_context_visible:
                    panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
                    if chat_card is not None:
                        chat_card.grid(row=0, column=1, columnspan=1, sticky="nsew", pady=0)
                else:
                    panel.grid_remove()
                    if chat_card is not None:
                        chat_card.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=0)
            except Exception:
                pass
        if toggle is not None:
            try:
                toggle.configure(text="Hide Context" if self.assistant_context_visible else "Show Context")
            except Exception:
                pass

    def toggle_assistant_context_panel(self) -> None:
        self.set_assistant_context_visible(not bool(self.assistant_context_visible))
        self.set_status("")

    def refresh_assistant_context_window_report(self) -> None:
        adapter = self.ids.get("assistant_context_window_report")
        if adapter is None:
            return
        prompt = ""
        try:
            prompt = self.ids.assistant_input.text
        except Exception:
            prompt = ""
        adapter.text = build_context_window_report(self.data_cache, prompt)

    def on_assistant_compact_memory(self) -> None:
        self.data_cache, compacted = compact_assistant_history_if_needed(self.data_cache, force=True)
        self.save_data()
        self.assistant_history_dirty = False
        self.refresh_assistant_history()
        self.refresh_assistant_context_panel()
        self.refresh_assistant_context_window_report()
        self.set_status("Chat memory compacted." if compacted else "Chat memory already fits the window.")

    def refresh_assistant_chat_font(self) -> None:
        box = getattr(self.ids.get("assistant_history"), "widget", None)
        if box is not None:
            self.configure_markdown_textbox(box, base_size=self.text_size_base_font_size() + self.assistant_chat_font_delta)
        input_box = getattr(self.ids.get("assistant_input"), "widget", None)
        if input_box is not None:
            try:
                input_box.configure(font=ctk.CTkFont(size=max(9, self.text_size_base_font_size() + self.assistant_chat_font_delta)))
            except Exception:
                pass
        label = self.ids.get("assistant_chat_font_label")
        if label is not None:
            sign = "+" if self.assistant_chat_font_delta >= 0 else ""
            label.text = f"Text {sign}{self.assistant_chat_font_delta}"
        self.refresh_assistant_history()

    def adjust_assistant_chat_text_size(self, delta: int) -> None:
        self.assistant_chat_font_delta = max(-6, min(10, int(self.assistant_chat_font_delta) + int(delta)))
        if self.paths is not None:
            try:
                save_settings({"assistant_chat_font_delta": self.assistant_chat_font_delta}, self.paths)
                self.settings_data = load_settings(self.paths)
            except Exception:
                self.settings_data["assistant_chat_font_delta"] = self.assistant_chat_font_delta
        else:
            self.settings_data["assistant_chat_font_delta"] = self.assistant_chat_font_delta
        self.refresh_assistant_chat_font()
        self.set_status("Chat text size updated.")

    def on_assistant_mode_change(self, value: str) -> None:
        self.assistant_mode = normalize_assistant_mode(value)
        palette = {
            "General": {
                "menu_fg": DESKTOP_SURFACE_ALT,
                "button": DESKTOP_ACCENT,
                "hover": "#0d6b63",
                "dropdown": DESKTOP_SURFACE_ALT,
                "text": DESKTOP_TEXT,
                "hint": DESKTOP_MUTED,
            },
            "Therapy": {
                "menu_fg": "#3b2b31",
                "button": "#b46e82",
                "hover": "#8d5566",
                "dropdown": "#3b2b31",
                "text": "#fff4f7",
                "hint": "#f4c9d7",
            },
            "Recovery Coach": {
                "menu_fg": "#20372e",
                "button": "#2f9d6a",
                "hover": "#277c54",
                "dropdown": "#20372e",
                "text": "#eefcf5",
                "hint": "#9fdfbf",
            },
        }.get(self.assistant_mode, {})
        mode_menu = self.ids.get("assistant_mode_menu")
        if mode_menu is not None and palette:
            try:
                mode_menu.configure(
                    fg_color=palette["menu_fg"],
                    button_color=palette["button"],
                    button_hover_color=palette["hover"],
                    dropdown_fg_color=palette["dropdown"],
                    dropdown_hover_color=palette["hover"],
                    dropdown_text_color=palette["text"],
                    text_color=palette["text"],
                )
                mode_menu.set(self.assistant_mode)
            except Exception:
                pass
        if "assistant_mode_hint" in self.ids:
            if self.assistant_mode == "Therapy":
                self.ids.assistant_mode_hint.text = (
                    "Therapy mode keeps the tone supportive and reflective. It is not a licensed therapist or crisis service."
                )
            elif self.assistant_mode == "Recovery Coach":
                self.ids.assistant_mode_hint.text = (
                    "Recovery Coach mode focuses on streak protection, relapse prevention, milestones, and the next 24 hours."
                )
            else:
                self.ids.assistant_mode_hint.text = (
                    "General mode focuses on schedule, wellness, dental, and practical vault guidance."
                )
        if palette and "assistant_mode_hint" in self.ids:
            self.ids.assistant_mode_hint.text_color = palette["hint"]
        self.refresh_assistant_quick_prompt_labels()
        self.refresh_assistant_context_panel()
        self.set_status(f"Chat mode set to {self.assistant_mode}.")

    def refresh_assistant_quick_prompt_labels(self) -> None:
        buttons = getattr(self, "assistant_quick_prompt_buttons", {})
        if not buttons:
            return
        labels_by_mode = {
            "Therapy": {
                "Summarize Today": "Reflect Today",
                "What Next?": "Next Step",
                "Check Routine": "Check Stress",
                "Draft Questions": "Draft Questions",
            },
            "Recovery Coach": {
                "Summarize Today": "Protect Today",
                "What Next?": "Craving Plan",
                "Check Routine": "Check Triggers",
                "Draft Questions": "Draft Questions",
            },
            "General": {
                "Summarize Today": "Summarize Today",
                "What Next?": "What Next?",
                "Check Routine": "Check Routine",
                "Draft Questions": "Draft Questions",
            },
        }.get(self.assistant_mode, {})
        for logical_label, button in buttons.items():
            try:
                button.configure(text=labels_by_mode.get(logical_label, logical_label))
            except Exception:
                pass

    def assistant_context_preview_facts(self) -> List[str]:
        facts: List[str] = []
        now = time.time()
        selected = self.current_selected_med()
        if selected:
            facts.append(f"Focus med: {sanitize_text(selected.get('name') or 'Medication', max_chars=80)}")
            next_slot = next_unchecked_medication_slot(selected, now)
            if next_slot:
                facts.append(f"Next slot: {sanitize_text(next_slot.get('time_text') or '', max_chars=40)} {sanitize_text(next_slot.get('label') or '', max_chars=80)}")
        else:
            meds = list(active_medications(self.data_cache))
            facts.append(f"Active meds: {len(meds)}")
        recovery = self.current_recovery_support_state()
        if recovery.get("enabled"):
            mood = safe_float(recovery.get("latest_mood"))
            craving = safe_float(recovery.get("latest_craving"))
            if mood > 0 or craving > 0:
                facts.append(f"Latest check-in: mood {mood:.0f}/10, craving {craving:.0f}/10")
        model_ready = bool(self.paths and self.paths.encrypted_model_path.exists())
        facts.append("Model ready" if model_ready else "Model not installed")
        return facts[:4]

    def refresh_assistant_context_panel(self) -> None:
        if "assistant_quantum_state" not in self.ids:
            return
        try:
            current_prompt = sanitize_text(getattr(self.ids.get("assistant_input"), "text", "") or "", max_chars=800)
            packet = build_assistant_quantum_context(
                self.data_cache,
                self.selected_med_id,
                current_prompt or "assistant context preview",
                self.assistant_mode,
            )
        except Exception as exc:
            self.ids.assistant_quantum_state.text = (
                "Context preview unavailable.\n"
                f"Reason: {sanitize_text(str(exc), max_chars=180)}"
            )
            if "assistant_prompt_lens" in self.ids:
                health = assistant_prompt_health(current_prompt, self.assistant_mode)
                self.ids.assistant_prompt_lens.text = (
                    "Prompt lens: direct local context with conservative safety boundaries. "
                    f"Prompt: {health['clarity']} | targets={health['targets']} | {health['suggestion']}"
                )
            self.refresh_assistant_context_window_report()
            return
        health = assistant_prompt_health(current_prompt, self.assistant_mode)
        context_bits = []
        for label, token in (
            ("schedule", "meds"),
            ("dental", "dental"),
            ("movement", "movement"),
            ("recovery", "recovery"),
            ("support", "support"),
        ):
            if token in health["targets"]:
                context_bits.append(label)
        if not context_bits:
            context_bits.append("vault summary")
        facts = self.assistant_context_preview_facts()
        lines = [
            f"Context preview: using {', '.join(context_bits)} context with a {health['stance']} response style.",
            f"Included facts: {' | '.join(facts)}",
            f"Prompt health: {health['clarity']} | {health['suggestion']}",
            f"Reply style: {packet.get('rag_route', 'direct').replace('_', ' ')} | safety emphasis {packet.get('risk_level')}.",
            "Private local signals only shape answer structure; they are not clinical evidence.",
        ]
        self.ids.assistant_quantum_state.text = "\n".join(lines)
        if "assistant_prompt_lens" in self.ids:
            lens = {
                "direct": "Reply plan: answer the exact request first, then add only the most useful vault context.",
                "context_expand": "Reply plan: include relevant context and surface missing details before suggesting next steps.",
                "safety_first": "Reply plan: lead with safety boundaries, verification points, and the smallest useful action.",
            }.get(packet.get("rag_route"), "Reply plan: use local context with conservative safety boundaries.")
            self.ids.assistant_prompt_lens.text = (
                f"{lens} Prompt: {health['clarity']} | style={health['stance']} | focus={health['targets']} | {health['suggestion']}"
            )
        self.refresh_assistant_context_window_report()

    def on_assistant_quick_prompt(self, prompt: str, *, label: str = "") -> None:
        clean = sanitize_text(prompt, max_chars=1000)
        if label:
            mode_hint = normalize_assistant_mode(self.assistant_mode)
            selected = self.current_selected_med()
            selected_name = sanitize_text(selected.get("name") if selected else "", max_chars=80)
            if mode_hint == "Therapy" and label == "Summarize Today":
                clean = "Help me reflect on today using my MedSafe context. Start with what seems most grounding, then give one small next step."
            elif mode_hint == "Recovery Coach" and label == "Summarize Today":
                clean = "Summarize my recovery momentum today and help me protect the next 24 hours using my stored plan."
            elif mode_hint == "Therapy" and label == "What Next?":
                clean = "What is one emotionally realistic next step I can take today, based on my current context?"
            elif mode_hint == "Recovery Coach" and label == "What Next?":
                clean = "What is the next recovery-protective action I should take in the next 10 minutes, next hour, and today?"
            elif label == "What Next?" and selected_name:
                clean = f"What is the most useful next action for {selected_name} and the rest of my current MedSafe routine?"
            elif mode_hint == "Therapy" and label == "Check Routine":
                clean = "Check my current support routine for stress points, avoidance loops, and one gentle adjustment I can actually do."
            elif mode_hint == "Recovery Coach" and label == "Check Routine":
                clean = "Check my recovery routine for trigger gaps, craving risk, and one concrete protection step for today."
            elif mode_hint == "Therapy" and label == "Draft Questions":
                clean = "Draft a few clear questions I could bring to a therapist, support person, or clinician about what I am noticing."
            elif mode_hint == "Recovery Coach" and label == "Draft Questions":
                clean = "Draft a few clear questions I could bring to a sponsor, support person, counselor, or clinician about my recovery plan."
        if "assistant_input" in self.ids:
            self.ids.assistant_input.text = clean
        self.refresh_assistant_context_panel()
        self.set_status("Quick prompt loaded. Edit it or press Enter to send.")
        self._focus_assistant_input()

    def on_recovery_slider_change(self, field: str, value: float) -> None:
        clean_field = sanitize_text(field, max_chars=24).lower()
        label_map = {
            "mood": ("recovery_mood_value", "Mood"),
            "craving": ("recovery_craving_value", "Craving"),
        }
        target = label_map.get(clean_field)
        if not target or target[0] not in self.ids:
            return
        self.ids[target[0]].text = f"{target[1]} {float(value):.0f}/10"

    def _slider_value(self, widget_id: str, default: float = 0.0) -> float:
        widget = self.ids.get(widget_id)
        if widget is None:
            return max(0.0, min(10.0, float(default)))
        try:
            raw_value = widget.get()
        except Exception:
            raw_value = getattr(widget, "_value", default)
        return max(0.0, min(10.0, safe_float(raw_value if raw_value is not None else default)))

    def _set_slider_value(self, widget_id: str, value: float) -> None:
        widget = self.ids.get(widget_id)
        if widget is None:
            return
        clamped = max(0.0, min(10.0, safe_float(value)))
        try:
            current = safe_float(widget.get())
        except Exception:
            current = safe_float(getattr(widget, "_value", clamped))
        if abs(current - clamped) <= 0.05:
            return
        try:
            widget.set(clamped)
        except Exception:
            return

    def _assistant_input_widget(self) -> Optional[Any]:
        adapter = self.ids.get("assistant_input")
        if adapter is None:
            return None
        return getattr(adapter, "widget", adapter)

    def _focus_assistant_input(self) -> None:
        widget = self._assistant_input_widget()
        if widget is None:
            return
        target = getattr(widget, "_textbox", None) or widget
        try:
            target.focus_set()
            target.mark_set("insert", "end-1c")
            target.see("insert")
        except Exception:
            pass

    def _set_assistant_ui_state(self) -> None:
        pending = bool(self.assistant_request_pending)
        streaming = bool(getattr(self, "assistant_reply_streaming", False))
        busy = pending or streaming
        status_line = self.ids.get("assistant_status_line")
        if status_line is not None:
            if streaming:
                status_line.text = "Streaming the reply into Chat..."
            elif pending:
                status_line.text = "Gemma is generating locally. The rest of MedSafe stays usable while this runs."
            else:
                status_line.text = "Local-only chat is ready. Press Enter to send and Shift+Enter for a new line."
            status_line.text_color = DESKTOP_WARNING if busy else DESKTOP_MUTED

        loading_badge = self.ids.get("assistant_loading_badge")
        if loading_badge is not None:
            try:
                loading_badge.configure(
                    text="Streaming..." if streaming else "Generating..." if pending else "Ready",
                    fg_color=DESKTOP_ACCENT if streaming else DESKTOP_WARNING if pending else "#20313e",
                    text_color="#08110f" if busy else DESKTOP_MUTED,
                )
            except Exception:
                pass

        loading_bar = self.ids.get("assistant_loading_bar")
        if loading_bar is not None:
            try:
                if busy:
                    loading_bar.configure(progress_color=DESKTOP_ACCENT if streaming else DESKTOP_WARNING)
                    loading_bar.start()
                else:
                    loading_bar.stop()
                    loading_bar.set(0.0)
            except Exception:
                pass

        send_button = self.ids.get("assistant_send_button")
        if send_button is not None:
            try:
                send_button.configure(
                    text="Working..." if busy else "Send",
                    state="disabled" if busy else "normal",
                )
            except Exception:
                pass

        clear_button = self.ids.get("assistant_clear_button")
        if clear_button is not None:
            try:
                clear_button.configure(
                    text="Reply Running" if busy else "Clear",
                    state="disabled" if busy else "normal",
                )
            except Exception:
                pass

        input_widget = self._assistant_input_widget()
        if input_widget is not None:
            try:
                input_widget.configure(border_color=DESKTOP_WARNING if busy else DESKTOP_ACCENT)
            except Exception:
                pass

    def _bind_assistant_input_shortcuts(self, adapter: DesktopTextboxAdapter) -> None:
        def newline_handler(_event: Any) -> str:
            target = getattr(adapter.widget, "_textbox", None) or adapter.widget
            try:
                target.insert("insert", "\n")
                target.see("insert")
            except Exception:
                pass
            return "break"

        def send_handler(_event: Any) -> str:
            self.on_assistant_send()
            return "break"

        for target in (getattr(adapter.widget, "_textbox", None), adapter.widget):
            if target is None:
                continue
            try:
                target.bind("<Shift-Return>", newline_handler, add="+")
                target.bind("<Shift-KP_Enter>", newline_handler, add="+")
                target.bind("<Return>", send_handler, add="+")
                target.bind("<KP_Enter>", send_handler, add="+")
            except Exception:
                continue

    def _bind_assistant_input_live_context(self, adapter: DesktopTextboxAdapter) -> None:
        def handler(_event: Any) -> None:
            self.on_assistant_input_changed()

        for target in (getattr(adapter.widget, "_textbox", None), adapter.widget):
            if target is None:
                continue
            try:
                target.bind("<KeyRelease>", handler, add="+")
            except Exception:
                continue

    def on_assistant_input_changed(self) -> None:
        self.assistant_context_refresh_request_id += 1
        request_id = self.assistant_context_refresh_request_id
        self.run_on_ui_thread(self._refresh_assistant_context_if_current, request_id, delay_ms=220)

    def _refresh_assistant_context_if_current(self, request_id: int) -> None:
        if request_id != self.assistant_context_refresh_request_id:
            return
        self.refresh_assistant_context_panel()

    def append_assistant_message(self, role: str, content: str, *, mode: Optional[str] = None, persist: bool = True) -> None:
        history = list(self.data_cache.get("assistant_history") or [])
        history.append(
            {
                "role": role,
                "mode": normalize_assistant_mode(mode or self.assistant_mode),
                "content": sanitize_text(content, max_chars=10000),
                "timestamp": time.time(),
            }
        )
        self.data_cache["assistant_history"] = history[-ASSISTANT_CONTEXT_MAX_MESSAGES:]
        self.data_cache, _compacted = compact_assistant_history_if_needed(self.data_cache, force=False)
        if persist:
            self.save_data()
            self.assistant_history_dirty = False
        else:
            self.assistant_history_dirty = True
        self.refresh_assistant_history()

    def on_assistant_send(self) -> None:
        prompt = sanitize_text(self.ids.assistant_input.text, max_chars=1600)
        if not prompt:
            self.set_status("Type a message before sending.")
            self._focus_assistant_input()
            return
        if not self.vault:
            self.set_status("Chat vault unavailable.")
            return
        if self.assistant_request_pending or self.assistant_reply_streaming:
            self.set_status("Chat is still working on the last message.")
            self._focus_assistant_input()
            return
        self.ids.assistant_input.text = ""
        active_mode = normalize_assistant_mode(self.assistant_mode)
        selected_med_id = self.selected_med_id
        settings = dict(self.settings_data)
        self.assistant_request_id += 1
        request_id = self.assistant_request_id
        self._cleanup_assistant_process(terminate=True)
        self.assistant_request_pending = True
        self._set_assistant_ui_state()
        self.append_assistant_message("user", prompt, mode=active_mode, persist=False)
        snapshot = self.clone_data_snapshot()
        self.set_status("Thinking with Gemma 4...")

        def launcher() -> None:
            try:
                if not self.vault:
                    raise RuntimeError("Chat vault unavailable.")
                key = self.vault.get_or_create_key()
                ctx = mp.get_context("spawn")
                result_queue = ctx.Queue()
                process = ctx.Process(
                    target=assistant_request_process_worker,
                    args=(result_queue, key, snapshot, prompt, selected_med_id, settings, active_mode),
                    daemon=True,
                )
                process.start()
                self.run_on_ui_thread(self._assistant_process_started, request_id, process, result_queue, active_mode)
            except Exception as exc:
                self.run_on_ui_thread(self._assistant_done, request_id, f"Chat unavailable: {exc}", active_mode)

        threading.Thread(target=launcher, daemon=True).start()

    def _assistant_process_started(self, request_id: int, process: Any, result_queue: Any, mode: str) -> None:
        if request_id != self.assistant_request_id:
            try:
                if process.is_alive():
                    process.terminate()
            except Exception:
                pass
            try:
                result_queue.close()
            except Exception:
                pass
            return
        self.assistant_process = process
        self.assistant_queue = result_queue
        self.run_on_ui_thread(self._poll_assistant_process, request_id, mode, delay_ms=120)

    def _poll_assistant_process(self, request_id: int, mode: str) -> None:
        if request_id != self.assistant_request_id:
            self._cleanup_assistant_process(terminate=True)
            return
        process = self.assistant_process
        result_queue = self.assistant_queue
        if process is None or result_queue is None:
            self._assistant_done(request_id, "Chat unavailable: worker did not start.", mode)
            return
        combined_delta = ""
        payload: Dict[str, Any] = {}
        has_payload = False
        try:
            while True:
                item = result_queue.get_nowait()
                if isinstance(item, dict) and "delta" in item:
                    combined_delta += sanitize_stream_delta(item.get("delta"), max_chars=2000)
                    if len(combined_delta) >= 6000:
                        break
                    continue
                payload = item if isinstance(item, dict) else {"ok": False, "error": "worker returned an invalid reply."}
                has_payload = True
                break
        except queue.Empty:
            pass
        if combined_delta:
            self._assistant_live_stream_delta(request_id, combined_delta, mode)
        if not has_payload:
            try:
                alive = process.is_alive()
            except Exception:
                alive = False
            if alive or combined_delta:
                self.run_on_ui_thread(self._poll_assistant_process, request_id, mode, delay_ms=25 if combined_delta else 120)
            else:
                self._cleanup_assistant_process(terminate=False)
                reply = "Chat unavailable: worker ended unexpectedly."
                if self.assistant_reply_streaming and self.assistant_stream_message_index >= 0:
                    current = sanitize_text(self.assistant_stream_text, max_chars=10000)
                    self._finish_assistant_live_stream(
                        request_id,
                        f"{current}\n\n{reply}" if current else reply,
                        mode,
                    )
                else:
                    self._assistant_done(request_id, reply, mode)
            return
        self._cleanup_assistant_process(terminate=False)
        if payload.get("ok"):
            reply = sanitize_text(payload.get("reply") or "", max_chars=10000) or "Chat returned an empty reply."
            if payload.get("streamed"):
                self._finish_assistant_live_stream(request_id, reply, mode)
                return
        else:
            reply = f"Chat unavailable: {sanitize_text(payload.get('error') or 'worker failed.', max_chars=240)}"
            if self.assistant_reply_streaming and self.assistant_stream_message_index >= 0:
                current = sanitize_text(self.assistant_stream_text, max_chars=10000)
                self._finish_assistant_live_stream(
                    request_id,
                    f"{current}\n\n{reply}" if current else reply,
                    mode,
                )
                return
        self._assistant_done(request_id, reply, mode)

    def _ensure_assistant_stream_message(self, request_id: int, mode: str) -> bool:
        if request_id != self.assistant_request_id:
            return False
        history = list(self.data_cache.get("assistant_history") or [])
        index = int(self.assistant_stream_message_index)
        if (
            self.assistant_reply_streaming
            and self.assistant_stream_request_id == request_id
            and 0 <= index < len(history)
        ):
            return True
        history.append(
            {
                "role": "assistant",
                "mode": normalize_assistant_mode(mode),
                "content": "",
                "timestamp": time.time(),
            }
        )
        self.data_cache["assistant_history"] = history[-ASSISTANT_CONTEXT_MAX_MESSAGES:]
        self.assistant_stream_message_index = len(self.data_cache["assistant_history"]) - 1
        self.assistant_stream_text = ""
        self.assistant_stream_index = 0
        self.assistant_stream_request_id = request_id
        self.assistant_reply_streaming = True
        self.assistant_history_dirty = True
        self._set_assistant_ui_state()
        self.refresh_assistant_history()
        return True

    def _assistant_live_stream_delta(self, request_id: int, delta: str, mode: str) -> None:
        if not sanitize_stream_delta(delta, max_chars=1):
            return
        if not self._ensure_assistant_stream_message(request_id, mode):
            return
        history = list(self.data_cache.get("assistant_history") or [])
        index = int(self.assistant_stream_message_index)
        if index < 0 or index >= len(history):
            return
        self.assistant_stream_text = sanitize_stream_delta(self.assistant_stream_text + delta, max_chars=10000)
        self.assistant_stream_index = len(self.assistant_stream_text)
        history[index]["content"] = self.assistant_stream_text
        self.data_cache["assistant_history"] = history
        self.assistant_history_dirty = True
        self.refresh_assistant_history()

    def _finish_assistant_live_stream(self, request_id: int, final_text: str, mode: str) -> None:
        if request_id != self.assistant_request_id:
            return
        if not self._ensure_assistant_stream_message(request_id, mode):
            return
        history = list(self.data_cache.get("assistant_history") or [])
        index = int(self.assistant_stream_message_index)
        if index < 0 or index >= len(history):
            return
        final_reply = sanitize_text(final_text, max_chars=10000) or sanitize_text(self.assistant_stream_text, max_chars=10000)
        history[index]["content"] = final_reply or "Chat returned an empty reply."
        self.data_cache["assistant_history"] = history
        self.assistant_request_pending = False
        self.assistant_reply_streaming = False
        self.assistant_stream_request_id = 0
        self.assistant_stream_message_index = -1
        self.assistant_stream_text = ""
        self.assistant_stream_index = 0
        self.assistant_history_dirty = True
        self.refresh_assistant_history()
        self.persist_data_async()
        self._set_assistant_ui_state()
        self.set_status("Chat reply ready.")
        self._focus_assistant_input()

    def _start_assistant_reply_stream(self, request_id: int, reply: str, mode: str) -> None:
        if request_id != self.assistant_request_id:
            return
        history = list(self.data_cache.get("assistant_history") or [])
        history.append(
            {
                "role": "assistant",
                "mode": normalize_assistant_mode(mode),
                "content": "",
                "timestamp": time.time(),
            }
        )
        self.data_cache["assistant_history"] = history[-ASSISTANT_CONTEXT_MAX_MESSAGES:]
        self.assistant_stream_message_index = len(self.data_cache["assistant_history"]) - 1
        self.assistant_stream_text = sanitize_text(reply, max_chars=10000)
        self.assistant_stream_index = 0
        self.assistant_stream_request_id = request_id
        self.assistant_reply_streaming = True
        self.assistant_history_dirty = True
        self._set_assistant_ui_state()
        self.refresh_assistant_history()
        self.run_on_ui_thread(self._assistant_stream_tick, request_id, delay_ms=18)

    def _assistant_stream_tick(self, request_id: int) -> None:
        if request_id != self.assistant_request_id or not self.assistant_reply_streaming:
            return
        history = list(self.data_cache.get("assistant_history") or [])
        index = int(self.assistant_stream_message_index)
        if index < 0 or index >= len(history):
            self.assistant_reply_streaming = False
            self.assistant_stream_request_id = 0
            self._set_assistant_ui_state()
            return
        total = len(self.assistant_stream_text)
        if self.assistant_stream_index < total:
            remaining = total - self.assistant_stream_index
            chunk = 18 if remaining < 160 else 32 if remaining < 800 else 48
            self.assistant_stream_index = min(total, self.assistant_stream_index + chunk)
            history[index]["content"] = self.assistant_stream_text[: self.assistant_stream_index]
            self.data_cache["assistant_history"] = history
            self.refresh_assistant_history()
            self.run_on_ui_thread(self._assistant_stream_tick, request_id, delay_ms=18)
            return
        history[index]["content"] = self.assistant_stream_text
        self.data_cache["assistant_history"] = history
        self.assistant_reply_streaming = False
        self.assistant_stream_request_id = 0
        self.assistant_stream_message_index = -1
        self.assistant_stream_text = ""
        self.assistant_stream_index = 0
        self.assistant_history_dirty = True
        self.refresh_assistant_history()
        self.persist_data_async()
        self._set_assistant_ui_state()
        self.set_status("Chat reply ready.")
        self._focus_assistant_input()

    def _assistant_done(self, request_id: int, reply: str, mode: str) -> None:
        if request_id != self.assistant_request_id:
            return
        self._cleanup_assistant_process(terminate=False)
        self.assistant_request_pending = False
        self._start_assistant_reply_stream(request_id, reply, mode)

    def on_assistant_clear(self) -> None:
        self.assistant_request_id += 1
        self.assistant_request_pending = False
        self.assistant_reply_streaming = False
        self.assistant_stream_request_id = 0
        self.assistant_stream_message_index = -1
        self.assistant_stream_text = ""
        self.assistant_stream_index = 0
        self._cleanup_assistant_process(terminate=True)
        self._set_assistant_ui_state()
        self.data_cache["assistant_history"] = []
        if "assistant_input" in self.ids:
            self.ids.assistant_input.text = ""
        self.save_data()
        self.assistant_history_dirty = False
        self.refresh_assistant_history()
        self.set_status("Chat cleared.")
        self._focus_assistant_input()

    def current_recovery_support_state(self) -> Dict[str, Any]:
        return dict(self.data_cache.get("recovery_support") or recovery_support_defaults())

    def refresh_recovery_support_ui(self) -> None:
        if "recovery_support_summary" not in self.ids:
            return
        state = self.current_recovery_support_state()
        now = time.time()
        title, body = build_recovery_support_summary(state, now)
        mood_value = max(0.0, min(10.0, safe_float(state.get("latest_mood") or 0.0)))
        craving_value = max(0.0, min(10.0, safe_float(state.get("latest_craving") or 0.0)))
        reminder_time = sanitize_text(state.get("reminder_time") or recovery_support_defaults()["reminder_time"], max_chars=20)
        due = recovery_support_due_status(state, now)
        milestone_count = len(
            [
                item
                for item in list(state.get("history") or [])
                if sanitize_text(item.get("type") or "", max_chars=20).lower() == "milestone"
            ]
        )
        self.ids.recovery_support_title.text = title
        self.ids.recovery_support_summary.text = body
        self.set_field_text("recovery_goal_name", sanitize_text(state.get("goal_name") or "Recovery", max_chars=120))
        self.set_field_text("recovery_clean_start", sanitize_text(state.get("clean_start_date") or "", max_chars=20))
        self.set_field_text("recovery_motivation", sanitize_text(state.get("motivation") or "", max_chars=1200))
        self.set_field_text("recovery_coping_plan", sanitize_text(state.get("coping_plan") or "", max_chars=1200))
        self.set_field_text("recovery_reminder_time", reminder_time)
        self._set_slider_value("recovery_mood_slider", mood_value)
        self._set_slider_value("recovery_craving_slider", craving_value)
        self.on_recovery_slider_change("mood", mood_value)
        self.on_recovery_slider_change("craving", craving_value)
        streak_days = recovery_clean_days(state, datetime.fromtimestamp(now).date())
        next_milestone = recovery_next_milestone(streak_days)
        next_text = (
            f"Next milestone: day {next_milestone[0]} (+{next_milestone[1]} pts)"
            if next_milestone is not None
            else "Top milestone already unlocked"
        )
        self.ids.recovery_reward_line.text = (
            f"{streak_days} clean day{'s' if streak_days != 1 else ''} | "
            f"{max(0, int(safe_float(state.get('points') or 0)))} pts | {next_text}"
        )
        reminder_prefix = f"Reminder {reminder_time} | " if state.get("enabled") else ""
        self.ids.recovery_reminder_line.text = reminder_prefix + sanitize_text(due.get("text") or "", max_chars=180)
        if due.get("overdue"):
            self.ids.recovery_reminder_line.text_color = DESKTOP_DANGER
        elif due.get("due_now"):
            self.ids.recovery_reminder_line.text_color = DESKTOP_WARNING
        elif sanitize_text(due.get("state") or "", max_chars=20).lower() == "done":
            self.ids.recovery_reminder_line.text_color = DESKTOP_SUCCESS
        else:
            self.ids.recovery_reminder_line.text_color = DESKTOP_MUTED
        self.ids.recovery_badges_label.text = (
            f"Milestone shelf ({milestone_count} unlocked)" if milestone_count else "Milestone shelf"
        )
        self.ids.recovery_badges.text = build_recovery_badges_text(state)

    def on_save_recovery_support_plan(self) -> None:
        state = self.current_recovery_support_state()
        goal_name = sanitize_text(self.ids.recovery_goal_name.text, max_chars=120) or "Recovery"
        clean_start_date = sanitize_text(self.ids.recovery_clean_start.text, max_chars=20)
        motivation = sanitize_text(self.ids.recovery_motivation.text, max_chars=1200)
        coping_plan = sanitize_text(self.ids.recovery_coping_plan.text, max_chars=1200)
        reminder_time = sanitize_text(self.ids.recovery_reminder_time.text, max_chars=20) or recovery_support_defaults()["reminder_time"]
        latest_mood = self._slider_value("recovery_mood_slider", state.get("latest_mood") or 5.0)
        latest_craving = self._slider_value("recovery_craving_slider", state.get("latest_craving") or 0.0)
        clean_start_parsed = parse_date_string(clean_start_date) if clean_start_date else None
        if clean_start_date and clean_start_parsed is None:
            self.set_status("Use YYYY-MM-DD for the clean start date.")
            return
        if clean_start_parsed is not None and clean_start_parsed > datetime.fromtimestamp(time.time()).date():
            self.set_status("Clean start date cannot be in the future.")
            return
        if reminder_time and parse_clock_minutes(reminder_time) is None:
            self.set_status("Use HH:MM or am/pm format for the recovery reminder time.")
            return
        state["enabled"] = bool(goal_name or clean_start_date or motivation or coping_plan)
        state["goal_name"] = goal_name
        state["clean_start_date"] = clean_start_date
        state["motivation"] = motivation
        state["coping_plan"] = coping_plan
        state["reminder_time"] = reminder_time
        state["latest_mood"] = latest_mood
        state["latest_craving"] = latest_craving
        state, rewards = apply_recovery_support_progress(state, now_ts=time.time(), award_checkin_points=False)
        self.data_cache["recovery_support"] = state
        self.save_data()
        self.refresh_dashboard()
        self.refresh_recovery_support_ui()
        if rewards:
            self.set_status("Recovery plan saved. " + " ".join(rewards[:2]))
        else:
            self.set_status(f"Saved {goal_name} recovery plan.")

    def on_recovery_support_checkin(self) -> None:
        state = self.current_recovery_support_state()
        now = time.time()
        note = sanitize_text(self.ids.recovery_checkin_note.text, max_chars=1200)
        mood_value = self._slider_value("recovery_mood_slider", state.get("latest_mood") or 5.0)
        craving_value = self._slider_value("recovery_craving_slider", state.get("latest_craving") or 0.0)
        reminder_time = sanitize_text(self.ids.recovery_reminder_time.text, max_chars=20)
        if not sanitize_text(state.get("goal_name") or "", max_chars=120):
            state["goal_name"] = "Recovery"
        if not sanitize_text(state.get("clean_start_date") or "", max_chars=20):
            state["clean_start_date"] = datetime.fromtimestamp(now).date().isoformat()
        if reminder_time and parse_clock_minutes(reminder_time) is not None:
            state["reminder_time"] = reminder_time
        days_clean = recovery_clean_days(state, datetime.fromtimestamp(now).date())
        already_checked_in = recovery_checked_in_today(state, now)
        points_delta = 0 if already_checked_in else 2
        state["enabled"] = True
        state["latest_note"] = note
        state["latest_checkin_ts"] = now
        state["latest_mood"] = mood_value
        state["latest_craving"] = craving_value
        history = list(state.get("history") or [])
        history.append(
            {
                "timestamp": now,
                "type": "checkin",
                "note": note or "Daily recovery check-in logged.",
                "streak_days": days_clean,
                "points_delta": points_delta,
                "mood": mood_value,
                "craving": craving_value,
                "label": "Daily check-in",
            }
        )
        state["history"] = history[-240:]
        state, rewards = apply_recovery_support_progress(state, now_ts=now, award_checkin_points=not already_checked_in)
        self.data_cache["recovery_support"] = state
        self.save_data()
        self.ids.recovery_checkin_note.text = ""
        self.refresh_dashboard()
        self.refresh_recovery_support_ui()
        if rewards:
            self.set_status("Recovery check-in saved. " + " ".join(rewards[:2]))
        else:
            self.set_status("Recovery check-in saved.")

    def on_recovery_support_relapse(self) -> None:
        state = self.current_recovery_support_state()
        now = time.time()
        today_text = datetime.fromtimestamp(now).date().isoformat()
        note = sanitize_text(self.ids.recovery_checkin_note.text, max_chars=1200) or "Relapse/reset logged. Starting a fresh day-one plan."
        mood_value = self._slider_value("recovery_mood_slider", state.get("latest_mood") or 5.0)
        craving_value = self._slider_value("recovery_craving_slider", state.get("latest_craving") or 0.0)
        reminder_time = sanitize_text(self.ids.recovery_reminder_time.text, max_chars=20)
        previous_streak = recovery_clean_days(state, datetime.fromtimestamp(now).date())
        state["enabled"] = True
        if reminder_time and parse_clock_minutes(reminder_time) is not None:
            state["reminder_time"] = reminder_time
        state["best_streak_days"] = max(previous_streak, max(0, int(safe_float(state.get("best_streak_days") or 0))))
        state["relapse_count"] = max(0, int(safe_float(state.get("relapse_count") or 0))) + 1
        state["last_relapse_date"] = today_text
        state["clean_start_date"] = today_text
        state["cycle"] = max(1, int(safe_float(state.get("cycle") or 1))) + 1
        state["latest_note"] = note
        state["latest_checkin_ts"] = now
        state["latest_mood"] = mood_value
        state["latest_craving"] = craving_value
        history = list(state.get("history") or [])
        history.append(
            {
                "timestamp": now,
                "type": "relapse",
                "note": note,
                "streak_days": previous_streak,
                "points_delta": 0,
                "mood": mood_value,
                "craving": craving_value,
                "label": "Reset",
            }
        )
        state["history"] = history[-240:]
        state, rewards = apply_recovery_support_progress(state, now_ts=now, award_checkin_points=False)
        self.data_cache["recovery_support"] = state
        self.save_data()
        self.ids.recovery_checkin_note.text = ""
        self.refresh_dashboard()
        self.refresh_recovery_support_ui()
        if rewards:
            self.set_status("Recovery reset saved. " + " ".join(rewards[:2]))
        else:
            self.set_status("Recovery reset saved. Day 1 starts again now.")

    def _start_image_analysis(self, image_path: Path) -> None:
        if not self.vault:
            return
        self.ids.vision_last_file.text = f"Last image: {image_path.name}"
        self.ids.vision_status.text = "Reading bottle photo with Gemma 4..."
        self.set_status("Importing medication from photo...")
        settings = dict(self.settings_data)
        selected_med_id = self.selected_med_id
        data_snapshot = self.clone_data_snapshot()

        def worker() -> None:
            try:
                if not self.vault:
                    raise RuntimeError("Bottle photo vault unavailable.")
                key = self.vault.get_or_create_key()
                payload, raw = analyze_medication_image(key, image_path, settings)
                updated, med_id, created = apply_vision_payload(data_snapshot, payload, selected_med_id=selected_med_id)
                self.run_on_ui_thread(self._vision_done, updated, med_id, payload, created, raw)
            except Exception as exc:
                self.run_on_ui_thread(self._vision_failed, str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _vision_done(self, updated: Dict[str, Any], med_id: str, payload: Dict[str, Any], created: bool, raw: str) -> None:
        self.data_cache = ensure_vault_shape(updated)
        self.selected_med_id = med_id
        self.save_data()
        action = "Added" if created else "Updated"
        confidence = payload.get("confidence", 0.0)
        self.ids.vision_status.text = f"{action} {payload['name']} from the bottle photo."
        self.ids.vision_result.text = (
            f"{action} {payload['name']}\n"
            f"Dose: {payload['dose_mg']:g} mg\n"
            f"Interval: {payload['interval_hours']:g} hours\n"
            f"Max daily: {payload['max_daily_mg']:g} mg\n"
            f"Directions: {payload['schedule_text']}\n"
            f"Notes: {payload['notes'] or 'None'}\n"
            f"Review risk: {payload['risk_level']} | {payload['risk_score']:.0f}/100\n"
            f"Risk note: {payload['risk_summary'] or 'Review the label manually before relying on the import.'}\n"
            f"Confidence: {confidence:.2f}\n"
            f"Model raw: {sanitize_text(raw, max_chars=420)}"
        )
        self.last_check_level = payload["risk_level"]
        self.last_check_display = f"Bottle review risk: {payload['risk_level']}"
        self.last_check_message = payload["risk_summary"] or f"{payload['name']} was saved from the bottle photo."
        self.refresh_ui()
        self.set_status(f"{action} {payload['name']} from the bottle photo.")
        if payload["risk_level"] == "High":
            self.show_dialog(
                "Bottle Photo Needs Review",
                "The quantum-assisted bottle import marked this photo as high review risk.\n\n"
                + sanitize_text(payload.get("risk_summary") or "", max_chars=320),
            )

    def _vision_failed(self, message: str) -> None:
        self.ids.vision_status.text = f"Import failed: {sanitize_text(message, max_chars=200)}"
        self.set_status("Bottle photo import failed.")
        self.show_dialog("Bottle Photo Import Failed", message)

    def on_take_bottle_photo(self) -> None:
        self.ids.vision_status.text = "Choose a bottle photo from this computer..."
        self._capture_photo("pill", "Choose a bottle photo from your computer...", self._start_image_analysis, self._vision_failed)

    def on_pick_bottle_photo(self) -> None:
        self.ids.vision_status.text = "Waiting for image selection..."
        self._pick_photo("Choose a medicine bottle photo...", self._start_image_analysis, self._vision_failed)

    def _dental_hygiene_failed(self, message: str) -> None:
        self.ids.dental_hygiene_status.text = f"Review failed: {sanitize_text(message, max_chars=220)}"
        self.set_status("Dental hygiene review failed.")
        self.show_dialog("Dental Hygiene Review Failed", message)

    def _start_dental_hygiene_analysis(self, image_path: Path) -> None:
        if not self.vault:
            return
        self.ids.dental_hygiene_photo.text = f"Last hygiene photo: {image_path.name}"
        self.ids.dental_hygiene_status.text = "Reviewing hygiene photo with Gemma 4..."
        self.set_status("Reviewing dental hygiene photo...")
        settings = dict(self.settings_data)
        data_snapshot = self.clone_data_snapshot()

        def worker() -> None:
            try:
                if not self.vault:
                    raise RuntimeError("Dental hygiene vault unavailable.")
                key = self.vault.get_or_create_key()
                payload, raw = analyze_dental_hygiene_image(key, image_path, settings)
                updated = apply_dental_hygiene_payload(data_snapshot, payload)
                self.run_on_ui_thread(self._dental_hygiene_done, updated, payload, raw)
            except Exception as exc:
                self.run_on_ui_thread(self._dental_hygiene_failed, str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _dental_hygiene_done(self, updated: Dict[str, Any], payload: Dict[str, Any], raw: str) -> None:
        self.data_cache = ensure_vault_shape(updated)
        self.save_data()
        _ = raw
        self.last_check_level = payload["risk_level"]
        self.last_check_display = f"Dental hygiene risk: {payload['risk_level']}"
        self.last_check_message = payload["risk_summary"] or f"{payload['rating']} hygiene rating saved in the encrypted dental journal."
        self.refresh_dental_ui()
        self.set_status("Dental hygiene review saved.")
        if payload["risk_level"] == "High" or warning_text_needs_attention(payload.get("warning_flags", "")):
            self.show_dialog(
                "Dental Hygiene Attention Flag",
                "The vision review noticed something worth checking more closely.\n\n"
                + sanitize_text(payload.get("risk_summary") or payload.get("warning_flags") or "", max_chars=320),
            )

    def on_take_dental_hygiene_photo(self) -> None:
        self.ids.dental_hygiene_status.text = "Choose a hygiene photo from this computer..."
        self._capture_photo("dental_hygiene", "Choose a dental hygiene photo...", self._start_dental_hygiene_analysis, self._dental_hygiene_failed)

    def on_pick_dental_hygiene_photo(self) -> None:
        self.ids.dental_hygiene_status.text = "Waiting for image selection..."
        self._pick_photo("Choose a teeth or mouth photo...", self._start_dental_hygiene_analysis, self._dental_hygiene_failed)

    def _recovery_failed(self, message: str) -> None:
        self.ids.recovery_mode_status.text = f"Review failed: {sanitize_text(message, max_chars=220)}"
        self.set_status("Dental recovery review failed.")
        self.show_dialog("Dental Recovery Review Failed", message)

    def _start_recovery_analysis(self, image_path: Path) -> None:
        if not self.vault:
            return
        recovery_state = self.recovery_state_from_form()
        if not recovery_state["procedure_type"]:
            self._recovery_failed("Enter the procedure type before running recovery mode.")
            return
        if recovery_state["procedure_date"] and parse_date_string(recovery_state["procedure_date"]) is None:
            self._recovery_failed("Use YYYY-MM-DD for the procedure date before running recovery mode.")
            return
        self.ids.recovery_last_photo.text = f"Last recovery photo: {image_path.name}"
        self.ids.recovery_mode_status.text = "Reviewing recovery photo with Gemma 4..."
        self.set_status("Reviewing dental recovery photo...")
        settings = dict(self.settings_data)
        data_snapshot = self.clone_data_snapshot()

        def worker() -> None:
            try:
                if not self.vault:
                    raise RuntimeError("Dental recovery vault unavailable.")
                key = self.vault.get_or_create_key()
                payload, raw = analyze_dental_recovery_image(key, image_path, settings, recovery_state)
                updated = apply_dental_recovery_payload(data_snapshot, payload, recovery_state)
                self.run_on_ui_thread(self._recovery_done, updated, payload, raw)
            except Exception as exc:
                self.run_on_ui_thread(self._recovery_failed, str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _recovery_done(self, updated: Dict[str, Any], payload: Dict[str, Any], raw: str) -> None:
        self.data_cache = ensure_vault_shape(updated)
        self.save_data()
        _ = raw
        self.last_check_level = payload["risk_level"]
        self.last_check_display = f"Recovery risk: {payload['risk_level']}"
        self.last_check_message = payload["risk_summary"] or (
            "General aftercare suggestions were saved. This is not a diagnosis and does not replace your dentist."
        )
        self.refresh_dental_ui()
        self.set_status("Dental recovery review saved.")
        if payload["risk_level"] == "High" or warning_text_needs_attention(payload.get("warning_flags", "")):
            self.show_dialog(
                "Dental Recovery Attention Flag",
                "The vision review noticed a recovery warning that may deserve a dentist check.\n\n"
                + sanitize_text(payload.get("risk_summary") or payload.get("warning_flags") or "", max_chars=320),
            )

    def on_take_recovery_photo(self) -> None:
        self.ids.recovery_mode_status.text = "Choose a recovery photo from this computer..."
        self._capture_photo("dental_recovery", "Choose a recovery check-in photo...", self._start_recovery_analysis, self._recovery_failed)

    def on_pick_recovery_photo(self) -> None:
        self.ids.recovery_mode_status.text = "Waiting for image selection..."
        self._pick_photo("Choose a recovery check-in photo...", self._start_recovery_analysis, self._recovery_failed)

    def _run_model_task(self, worker: Callable[[], Any], on_done: Callable[[Any], None], failure_title: str) -> None:
        def runner() -> None:
            try:
                result = worker()
                self.run_on_ui_thread(on_done, result)
            except Exception as exc:
                self.run_on_ui_thread(self._model_task_failed, failure_title, str(exc))

        threading.Thread(target=runner, daemon=True).start()

    def _model_task_failed(self, title: str, message: str) -> None:
        self.ids.model_progress.value = 0
        if sanitize_text(title, max_chars=80) == "All-Meds Check Failed":
            self.regimen_check_review = {}
            self.refresh_dashboard()
        self.set_status(message)
        self.show_dialog(title, message)
        self.refresh_model_status()

    def on_model_download(self) -> None:
        if not self.vault:
            return
        self.ids.model_progress.value = 0
        self.set_status("Downloading Gemma 4...")

        def worker() -> str:
            if not self.vault:
                raise RuntimeError("Model vault unavailable.")
            key = self.vault.get_or_create_key()

            def reporter(kind: str, payload: Any) -> None:
                if kind == "progress":
                    self.run_on_ui_thread(setattr, self.ids.model_progress, "value", int(float(payload) * 100))
                elif kind == "status":
                    self.run_on_ui_thread(self.set_status, sanitize_text(payload, max_chars=180))

            return download_and_encrypt_model(key, reporter)

        self._run_model_task(worker, self._model_download_done, "Model Download Failed")

    def _model_download_done(self, sha: str) -> None:
        self.ids.model_progress.value = 100
        self.set_status("Gemma 4 downloaded and sealed.")
        self.refresh_model_status()
        self.show_dialog("Gemma 4 Ready", f"Model sealed successfully.\nSHA-256: {sha}")

    def on_model_verify(self) -> None:
        if not self.vault:
            return
        self.ids.model_progress.value = 15
        self.set_status("Verifying model hash...")
        self._run_model_task(
            lambda: verify_model_hash(self.vault.get_or_create_key()) if self.vault else ("", False),
            self._model_verify_done,
            "Model Verification Failed",
        )

    def _model_verify_done(self, result: Tuple[str, bool]) -> None:
        sha, okay = result
        self.ids.model_progress.value = 100 if okay else 0
        self.set_status("Model hash verified." if okay else "Model hash mismatch.")
        self.refresh_model_status()
        self.show_dialog("Model Verification", f"SHA-256: {sha}\nMatches expected hash: {'yes' if okay else 'no'}")

    def on_cycle_backend(self) -> None:
        current = self.settings_data.get("inference_backend", "Auto")
        options = list(INFERENCE_BACKEND_OPTIONS)
        current_index = options.index(current) if current in options else 0
        next_value = options[(current_index + 1) % len(options)]
        save_settings({"inference_backend": next_value}, self.paths)
        self.settings_data = load_settings(self.paths)
        self.refresh_model_status()
        self.set_status(f"Inference backend set to {next_value}.")

    def on_toggle_native_image_input(self) -> None:
        enabled = not bool(self.settings_data.get("enable_native_image_input", True))
        save_settings({"enable_native_image_input": enabled}, self.paths)
        self.settings_data = load_settings(self.paths)
        self.refresh_model_status()
        self.set_status(f"Native image input {'enabled' if enabled else 'disabled'}.")

    def on_change_startup_password(self) -> None:
        if not self.vault:
            return
        current_password = self._prompt_current_password_if_needed("Startup Password")
        if self.vault.is_key_protected() and current_password is None:
            return
        password = self._prompt_new_password("Startup Password")
        if password is None:
            return
        try:
            self.vault.enable_password(password, current_password=current_password)
            self._save_security_settings()
            self.refresh_model_status()
            self.set_status("Startup password saved. MedSafe will ask for it on the next launch.")
        except Exception as exc:
            self.show_dialog("Password Update Failed", str(exc))
            self.set_status("Startup password update failed.")

    def on_remove_startup_password(self) -> None:
        if not self.vault:
            return
        if not self.vault.is_key_protected():
            self.set_status("Startup password is already off.")
            return
        if self.window is not None and not messagebox.askyesno(
            "Remove Startup Password",
            "Turn off the startup password for future launches?\n\nThe vault will stay encrypted, but the local key will no longer be password-wrapped.",
            parent=self.window,
        ):
            return
        current_password = self._prompt_current_password_if_needed("Remove Startup Password")
        if current_password is None:
            self.set_status("Startup password stayed on.")
            return
        try:
            self.vault.disable_password(current_password=current_password)
            self._save_security_settings()
            self.refresh_model_status()
            self.set_status("Startup password removed. The vault key now opens without a boot password.")
        except Exception as exc:
            self.show_dialog("Remove Password Failed", str(exc))
            self.set_status("Could not remove the startup password.")

    def on_rotate_vault_key(self) -> None:
        if not self.vault:
            return
        if self.window is not None and not messagebox.askyesno(
            "Rotate Vault Key",
            "Rotate the local encryption key and reseal the vault and model with a fresh key now?\n\nThis can take a little longer if the model is installed.",
            parent=self.window,
        ):
            return
        current_password = self._prompt_current_password_if_needed("Rotate Vault Key")
        if self.vault.is_key_protected() and current_password is None:
            return
        self.ids.model_progress.value = 12
        self.set_status("Rotating the encrypted vault key...")
        self._run_model_task(lambda: self.vault.rotate_key(current_password=current_password), self._rotate_vault_key_done, "Key Rotation Failed")

    def _rotate_vault_key_done(self, _result: Any) -> None:
        self.ids.model_progress.value = 100
        self._save_security_settings()
        self.refresh_model_status()
        self.set_status("Vault key rotated and resealed successfully.")
        self.show_dialog("Key Rotation Complete", "MedSafe rotated the local encryption key and re-sealed protected files.")

    def on_delete_plain_model(self) -> None:
        if not self.paths:
            return
        safe_cleanup([self.paths.plain_model_path])
        self.ids.model_progress.value = 0
        self.refresh_model_status()
        self.set_status("Deleted any leftover plaintext model copy.")


def _desktop_render_daily_checklist(self: DesktopMedSafeApp, meds: List[Dict[str, Any]], selected_med: Optional[Dict[str, Any]], now: float) -> None:
    frame = self.ids.daily_checklist_frame
    for child in frame.winfo_children():
        child.destroy()
    frame.grid_columnconfigure(0, weight=1)
    target_day = self.current_checklist_target_day(now)
    today = datetime.fromtimestamp(now).date()
    allow_uncheck = bool(self.settings_data.get("allow_checklist_uncheck", False))
    can_log_for_day = target_day <= today
    if not meds:
        ctk.CTkLabel(
            frame,
            text="Add a medication with planned times to build today's checklist.",
            anchor="w",
            justify="left",
            wraplength=560,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        return

    entries = build_dashboard_daily_checklist_entries(meds, target_day, now)
    if not entries:
        next_rows = []
        if target_day == today:
            for med in meds:
                next_slot = next_unchecked_medication_slot(med, now)
                if next_slot is not None:
                    next_rows.append((safe_float(next_slot.get("scheduled_ts")) or float("inf"), med, next_slot))
            next_rows.sort(key=lambda item: item[0])
        message = f"No planned medication slots for {target_day.isoformat()} yet."
        if target_day == today:
            message = "No planned medication slots for today yet. Add custom times or intervals to generate the checklist."
        if next_rows and target_day == today:
            _next_ts, med, next_slot = next_rows[0]
            message = (
                f"Nothing left for today. Next planned dose: "
                f"{sanitize_text(med.get('name') or 'Medication', max_chars=120)} at {next_slot['time_text']} ({next_slot['label']})."
            )
        ctk.CTkLabel(
            frame,
            text=message,
            anchor="w",
            justify="left",
            wraplength=560,
            text_color=DESKTOP_MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        return

    for row_index, entry in enumerate(entries):
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.grid(row=row_index, column=0, sticky="ew", padx=8, pady=4)
        row.grid_columnconfigure(1, weight=1)

        toggle_cell = ctk.CTkFrame(row, fg_color="transparent")
        toggle_cell.grid(row=0, column=0, sticky="w", padx=(4, 10))
        toggle_cell.grid_columnconfigure(1, weight=1)
        is_taken = entry.get("status") == "taken"
        can_toggle = can_log_for_day or (is_taken and allow_uncheck)
        toggle_command: Optional[Callable[[], None]] = None
        toggle_tone = "neutral"
        if is_taken:
            toggle_tone = "accent"
            if allow_uncheck and can_log_for_day:
                toggle_command = lambda med_id=str(entry.get("med_id")), slot_key=str(entry.get("slot_key") or ""), scheduled_ts=safe_float(entry.get("scheduled_ts")), slot_label=str(entry.get("label") or ""): self.on_checklist_uncheck_dose(
                    med_id,
                    slot_key,
                    scheduled_ts,
                    slot_label,
                )
        elif can_log_for_day:
            toggle_tone = "accent" if entry.get("status") == "due" else "neutral"
            toggle_command = lambda med_id=str(entry.get("med_id")), slot_key=str(entry.get("slot_key") or ""), scheduled_ts=safe_float(entry.get("scheduled_ts")), slot_label=str(entry.get("label") or ""): self.on_checklist_take_dose(
                med_id,
                slot_key,
                scheduled_ts,
                slot_label,
                False,
                False,
            )
        if is_taken:
            toggle_text = "Undo" if toggle_command is not None else "Taken"
            toggle_width = 74
        elif toggle_command is not None:
            toggle_text = "Mark Taken"
            toggle_width = 104
        else:
            toggle_text = "Future"
            toggle_width = 74
        toggle_button = ctk.CTkButton(
            toggle_cell,
            text=toggle_text,
            width=toggle_width,
            height=34,
            corner_radius=9,
            command=toggle_command,
            fg_color=DESKTOP_ACCENT if toggle_tone == "accent" else DESKTOP_SURFACE_ALT,
            hover_color="#0d6b63" if toggle_command else DESKTOP_SURFACE_ALT,
            border_width=1,
            border_color=DESKTOP_BORDER,
            text_color=DESKTOP_TEXT,
        )
        toggle_button.grid(row=0, column=0, sticky="w")
        if toggle_command is None:
            try:
                toggle_button.configure(state="disabled")
            except Exception:
                pass
        time_label = ctk.CTkLabel(
            toggle_cell,
            text=entry["time_text"],
            anchor="w",
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        time_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        details_text = f"{entry['med_name']} • {entry['dose_text']} • {entry['label']}"
        if selected_med and str(selected_med.get("id")) == str(entry.get("med_id")):
            details_text += " • Focused"
        details_label = ctk.CTkLabel(
            row,
            text=details_text,
            anchor="w",
            justify="left",
            wraplength=360,
            text_color=DESKTOP_TEXT,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        details_label.grid(row=0, column=1, sticky="ew")

        if entry.get("status") == "missed":
            status_color = DESKTOP_DANGER
            status_text = f"X {entry['status_text']}"
        elif entry.get("status") == "due":
            status_color = DESKTOP_WARNING
            status_text = f"! {entry['status_text']}"
        elif entry.get("status") == "taken":
            status_color = DESKTOP_SUCCESS
            status_text = entry["status_text"]
        else:
            status_color = DESKTOP_MUTED
            status_text = entry["status_text"]

        status_label = ctk.CTkLabel(
            row,
            text=status_text,
            anchor="w",
            justify="left",
            wraplength=250,
            text_color=status_color,
            font=ctk.CTkFont(size=13),
        )
        status_label.grid(row=0, column=2, sticky="ew", padx=(10, 0))

        if entry.get("status") == "missed" and target_day == today:
            self._button(
                row,
                text="Take Now",
                command=lambda med_id=str(entry.get("med_id")), slot_key=str(entry.get("slot_key") or ""), scheduled_ts=safe_float(entry.get("scheduled_ts")), slot_label=str(entry.get("label") or ""): self.on_checklist_take_dose(
                    med_id,
                    slot_key,
                    scheduled_ts,
                    slot_label,
                    True,
                    True,
                ),
                tone="warning",
            ).grid(row=0, column=3, sticky="e", padx=(10, 0))


def _desktop_apply_local_dose_review(
    self: DesktopMedSafeApp,
    med: Dict[str, Any],
    dose_value: float,
    when_ts: float,
    *,
    source_label: str = "dose",
) -> None:
    # Keep ordinary checklist/logging interactions deterministic and light.
    # The explicit Run Safety Check button still uses the heavier local model.
    context = build_dose_safety_model_context(med, dose_value, when_ts, source_label=source_label)
    action = normalize_dose_action_text(context.get("deterministic_level"), "Caution")
    self.last_check_level = action
    self.last_check_display = f"Dose safety: {action}"
    self.last_check_message = build_dose_safety_dashboard_message(med, action, when_ts, context)
    self.data_cache["dose_safety_review"] = self._saved_dose_safety_review(
        med,
        dose_value,
        source_label,
        action=action,
        display=self.last_check_display,
        message=self.last_check_message,
        deterministic_level=context.get("deterministic_level") or "",
        deterministic_message=context.get("deterministic_message") or "",
    )


def _desktop_sync_selected_dose_review(self: DesktopMedSafeApp, selected: Optional[Dict[str, Any]], now: float) -> None:
    if not selected:
        self.last_check_level = "Caution"
        self.last_check_display = "Dose safety"
        self.last_check_message = "Select a medication to review its schedule safety."
        return
    pending = sanitize_text(self.last_check_level, max_chars=24).lower()
    selected_name = sanitize_text(selected.get("name") or "Medication", max_chars=120)
    if pending.startswith("assess") and selected_name.lower() in sanitize_text(self.last_check_message, max_chars=420).lower():
        return
    review = dict(self.data_cache.get("dose_safety_review") or {})
    selected_id = sanitize_text(selected.get("id") or "", max_chars=32)
    source_label = sanitize_text(review.get("source_label") or "", max_chars=60).lower()
    can_reuse_saved_review = source_label in {"manual check", "manual plan check", "focused plan check"}
    if selected_id and can_reuse_saved_review and sanitize_text(review.get("med_id") or "", max_chars=32) == selected_id and safe_float(review.get("timestamp")) > 0:
        action = normalize_dose_action_text(review.get("action") or "", "")
        if action:
            self.last_check_level = action
        display = sanitize_text(review.get("display") or "", max_chars=160)
        message = sanitize_text(review.get("message") or "", max_chars=420)
        if display:
            self.last_check_display = display
        if message:
            self.last_check_message = message
        return
    snapshot = medication_safety_snapshot(selected, now, source_label="dashboard")
    self.last_check_level = snapshot.get("action") or "Caution"
    self.last_check_display = snapshot.get("display") or "Dose safety"
    self.last_check_message = snapshot.get("message") or "Dose safety review ready."


def _desktop_regimen_review_for_dashboard(self: DesktopMedSafeApp, meds: List[Dict[str, Any]], now: float) -> Dict[str, Any]:
    signature = regimen_signature(meds)
    review = dict(self.regimen_check_review or {})
    if review.get("signature") == signature and sanitize_text(review.get("message") or "", max_chars=320):
        return review
    context = build_regimen_safety_context(meds, now)
    return {
        "action": context.get("action") or "Caution",
        "display": f"All-meds safety: {context.get('action') or 'Caution'}",
        "message": context.get("message") or "Combined regimen review ready.",
        "signature": signature,
    }


def _desktop_on_checklist_take_dose(
    self: DesktopMedSafeApp,
    med_id: str,
    slot_key: str,
    scheduled_ts: float,
    slot_label: str,
    use_current_time: bool = True,
    enforce_safety: bool = True,
) -> None:
    self.selected_med_id = med_id
    med = self.med_by_id(med_id)
    if not med:
        self.set_status("Could not find that medication row anymore. Refresh the vault and try again.")
        return
    now = time.time()
    scheduled_value = max(0.0, safe_float(scheduled_ts))
    if not use_current_time and not enforce_safety:
        slot_info = {
            "slot_key": sanitize_text(slot_key or "", max_chars=64),
            "scheduled_ts": scheduled_value,
        }
        if matching_medication_history_entry_for_slot(med, slot_info) is not None:
            self.set_status(f"{slot_label} is already checked.")
            self.refresh_ui()
            return
        dose_value = max(0.0, safe_float(med.get("dose_mg")))
        if dose_value <= 0.0:
            self.set_status("Save a medication dose amount before checking this slot.")
            return
        original_data = self.clone_data_snapshot()
        original_med = self.clone_med_snapshot(med)
        append_medication_history_entry(
            med,
            now,
            dose_value,
            scheduled_ts=scheduled_value,
            slot_key=slot_info["slot_key"],
        )
        if dose_value > 0.0:
            med["dose_mg"] = dose_value
        _desktop_apply_local_dose_review(self, original_med, dose_value, now, source_label=f"{slot_label} checklist")
        planned_text = time.strftime("%b %d, %I:%M %p", time.localtime(scheduled_value or now)).replace(" 0", " ")
        marked_message = f"Recorded {slot_label} for its planned slot at {planned_text}."
        if not self.save_data():
            self.data_cache = original_data
            self.refresh_ui()
            return
        self.refresh_form()
        self.refresh_ui()
        self.set_status(marked_message)
        return
    target_timestamp = now if use_current_time else (scheduled_value or now)
    self._log_dose_for_med(
        med,
        source_label=slot_label,
        log_timestamp=target_timestamp,
        scheduled_ts=scheduled_ts,
        slot_key=slot_key,
        enforce_safety=enforce_safety,
    )


def _desktop_on_checklist_uncheck_dose(
    self: DesktopMedSafeApp,
    med_id: str,
    slot_key: str,
    scheduled_ts: float,
    slot_label: str,
) -> None:
    if not bool(self.settings_data.get("allow_checklist_uncheck", False)):
        self.set_status("Enable checklist undo in Settings before unchecking taken rows.")
        return
    self.selected_med_id = med_id
    med = self.med_by_id(med_id)
    if not med:
        self.set_status("Could not find that medication row anymore. Refresh the vault and try again.")
        return
    original_data = self.clone_data_snapshot()
    slot = {
        "slot_key": sanitize_text(slot_key or "", max_chars=64),
        "scheduled_ts": max(0.0, safe_float(scheduled_ts)),
    }
    if not remove_medication_history_entry_for_slot(med, slot):
        self.set_status(f"Could not undo the recorded {slot_label} dose.")
        return
    dose_value = max(0.0, safe_float(med.get("dose_mg")))
    if dose_value > 0.0:
        _desktop_apply_local_dose_review(self, self.clone_med_snapshot(med), dose_value, time.time(), source_label=f"{slot_label} undo")
    else:
        self.data_cache["dose_safety_review"] = dose_safety_review_defaults()
        self.last_check_level = "Safe"
        self.last_check_display = "Checklist updated"
        self.last_check_message = f"Removed the recorded {slot_label} dose."
    if not self.save_data():
        self.data_cache = original_data
        self.refresh_ui()
        return
    self.refresh_form()
    self.refresh_ui()
    self.set_status(f"Removed the recorded {slot_label} dose.")


def _desktop_refresh_dashboard(self: DesktopMedSafeApp) -> None:
    now = time.time()
    meds = list(active_medications(self.data_cache))
    archived = list(archived_medications(self.data_cache))
    target_day = self.current_checklist_target_day(now)
    today = datetime.fromtimestamp(now).date()
    med_statuses = [(medication_due_status(med, now), med) for med in meds]
    due_now = [med for status, med in med_statuses if status["due_now"] and not status["overdue"]]
    overdue = [med for status, med in med_statuses if status["overdue"]]
    next_due_items = [
        (status["next_ts"], med)
        for status, med in med_statuses
        if status["next_ts"] is not None
    ]
    next_due_items.sort(key=lambda item: item[0] or float("inf"))
    next_due_text = "Nothing scheduled yet"
    if next_due_items:
        next_due_ts, med = next_due_items[0]
        next_due_text = f"{sanitize_text(med.get('name'), max_chars=120)} | {format_relative_due(next_due_ts, now)}"

    selected = self.med_by_id(self.selected_med_id or "") if self.selected_med_id else None
    if self.selected_med_id and selected is None:
        self.selected_med_id = None
    picker_values = build_dashboard_med_picker_map(self.data_cache, now)
    self.dashboard_med_option_map = picker_values
    safety_state = effective_safety_reviews_state(self.data_cache.get("safety_reviews"), meds, now)
    regimen_review = dict(safety_state.get("regimen") or {})
    safety_action = "Assessing" if bool(safety_state.get("pending", False)) else normalize_dose_action_text(regimen_review.get("action") or "", "Caution")
    safety_title = "Safety scan in progress" if bool(safety_state.get("pending", False)) else sanitize_text(
        regimen_review.get("display") or f"All-meds safety: {safety_action}",
        max_chars=160,
    )
    safety_message = build_dashboard_safety_summary_text(safety_state, meds)
    hygiene = dict(self.data_cache.get("dental_hygiene") or dental_hygiene_defaults())
    exercise_state = dict(self.data_cache.get("exercise") or exercise_defaults())
    recovery_state = self.current_recovery_support_state()
    dental_due_count = len(
        [
            status
            for status in (
                habit_due_status(safe_float(hygiene.get("last_brush_ts")), safe_float(hygiene.get("brush_interval_hours")) or 12.0, now),
                habit_due_status(safe_float(hygiene.get("last_floss_ts")), safe_float(hygiene.get("floss_interval_hours")) or 24.0, now),
                habit_due_status(safe_float(hygiene.get("last_rinse_ts")), safe_float(hygiene.get("rinse_interval_hours")) or 24.0, now),
            )
            if status.get("due_now")
        ]
    )
    movement_due_count = len(
        [
            status
            for status in (
                habit_due_status(safe_float(exercise_state.get("last_walk_ts")), safe_float(exercise_state.get("walk_interval_hours")) or 4.0, now),
                habit_due_status(safe_float(exercise_state.get("last_light_ts")), safe_float(exercise_state.get("light_interval_hours")) or 8.0, now),
                habit_due_status(safe_float(exercise_state.get("last_stretch_ts")), safe_float(exercise_state.get("stretch_interval_hours")) or 2.0, now),
            )
            if status.get("due_now")
        ]
    )
    recovery_due = recovery_support_due_status(recovery_state, now)
    routine_due_count = dental_due_count + movement_due_count + (1 if recovery_due.get("due_now") else 0)
    password_enabled = bool(self.vault and self.vault.is_key_protected())
    model_ready = bool(self.paths and self.paths.encrypted_model_path.exists())
    selection_text = "Select a medication from Dashboard focus to review current and completed history."
    summary_text = "Use Dashboard focus to choose a medication from the current regimen or completed history."
    schedule_text = "Today's dose plan will appear here."
    if selected:
        med_name = sanitize_text(selected.get("name"), max_chars=120)
        selection_text = f"Focused med: {med_name}"
        if medication_is_archived(selected):
            selection_text = f"Focused med: {med_name} (Completed)"
            summary_text = (
                f"{med_name}\n"
                f"{medication_card_line(selected, now)}\n"
                f"Last taken: {format_timestamp(last_effective_taken_ts(selected))}\n"
                f"Status: {medication_archive_label(selected)}\n"
                f"Directions: {sanitize_text(selected.get('schedule_text') or 'No bottle directions were saved for this medication.', max_chars=260)}"
            )
        else:
            selected_slots = build_medication_daily_slots(selected, target_day, now)
            remaining_slots = len([slot for slot in selected_slots if slot.get("status") != "taken"])
            summary_text = (
                f"{med_name}\n"
                f"{medication_card_line(selected, now)}\n"
                f"Last taken: {format_timestamp(last_effective_taken_ts(selected))}\n"
                f"Remaining planned slots on {target_day.isoformat()}: {remaining_slots}\n"
                f"Directions: {sanitize_text(selected.get('schedule_text') or 'No bottle directions saved yet.', max_chars=260)}"
            )
        schedule_text = build_medication_schedule_text(selected, now, target_day=target_day)

    self.ids.dose_wheel.set_level(safety_action)
    if "care_compass_action" in self.ids:
        if overdue:
            compass_action = f"Best next step: reconcile {len(overdue)} missed medication slot{'s' if len(overdue) != 1 else ''}."
            self.dashboard_best_action_target = "Dashboard"
        elif due_now:
            compass_action = f"Best next step: check {len(due_now)} due medication slot{'s' if len(due_now) != 1 else ''}."
            self.dashboard_best_action_target = "Dashboard"
        elif routine_due_count:
            if dental_due_count:
                self.dashboard_best_action_target = "Dental"
                compass_action = f"Best next step: finish {dental_due_count} dental routine check-in{'s' if dental_due_count != 1 else ''}."
            elif movement_due_count:
                self.dashboard_best_action_target = "Exercise"
                compass_action = f"Best next step: finish {movement_due_count} movement check-in{'s' if movement_due_count != 1 else ''}."
            else:
                self.dashboard_best_action_target = "Recovery"
                compass_action = "Best next step: finish the recovery check-in."
        elif not model_ready:
            compass_action = "Best next step: download and seal Gemma from Settings when you are ready."
            self.dashboard_best_action_target = "Settings"
        else:
            compass_action = "Best next step: review the timeline and keep the next small action visible."
            self.dashboard_best_action_target = "Dashboard"
        self.ids.care_compass_action.text = compass_action
        self.ids.care_compass_meds.text = f"{len(due_now)} due | {len(overdue)} missed"
        self.ids.care_compass_meds.text_color = DESKTOP_DANGER if overdue else DESKTOP_WARNING if due_now else DESKTOP_SUCCESS
        self.ids.care_compass_safety.text = "Checking" if safety_state.get("pending") else safety_action
        self.ids.care_compass_safety.text_color = DESKTOP_WARNING if safety_action in {"Caution", "Assessing"} else DESKTOP_DANGER if safety_action in {"Unsafe", "High"} else DESKTOP_SUCCESS
        self.ids.care_compass_routines.text = f"{routine_due_count} due"
        self.ids.care_compass_routines.text_color = DESKTOP_WARNING if routine_due_count else DESKTOP_SUCCESS
        if "care_compass_days_clean" in self.ids:
            checked_in = safe_float(recovery_state.get("latest_checkin_ts") or 0.0) > 0.0
            if bool(recovery_state.get("enabled")) and checked_in:
                days_clean = recovery_clean_days(recovery_state, today)
                self.ids.care_compass_days_clean.text = f"{days_clean} day{'s' if days_clean != 1 else ''}"
                self.ids.care_compass_days_clean.text_color = DESKTOP_SUCCESS
            else:
                self.ids.care_compass_days_clean.text = "Recovery off"
                self.ids.care_compass_days_clean.text_color = DESKTOP_MUTED
    self.ids.dashboard_risk_title.text = safety_title
    self.ids.dashboard_risk_caption.text = safety_message
    self.ids.today_due_count.text = f"Due now: {len(due_now)} | Missed: {len(overdue)}"
    self.ids.today_next_due.text = next_due_text
    regimen_display = sanitize_text(regimen_review.get("display") or "All-meds safety", max_chars=120)
    regimen_message = sanitize_text(regimen_review.get("message") or "Combined regimen review ready.", max_chars=520)
    self.ids.dashboard_regimen_safety.text = f"{regimen_display}\n{regimen_message}"
    self.ids.dashboard_med_safety.text = build_safety_tab_per_med_text(safety_state, meds)
    self.ids.today_timeline.text = build_timeline_text(meds, now)
    self.ids.dashboard_selection.text = selection_text
    self.ids.selected_med_summary.text = summary_text
    if "selected_med_schedule" in self.ids:
        self.ids.selected_med_schedule.text = schedule_text
    self.ids.selected_med_history.text = build_recent_activity_text(self.data_cache)
    if "dashboard_focus_hint" in self.ids:
        if selected and medication_is_archived(selected):
            self.ids.dashboard_focus_hint.text = (
                f"Viewing completed medication history. Completed meds stay visible here, but they do not appear in the active checklist."
            )
        else:
            self.ids.dashboard_focus_hint.text = (
                f"Current regimen: {len(meds)} | Completed history: {len(archived)}. "
                "Choose any medication here to review schedule details and past doses."
            )
    dashboard_picker = self.ids.get("dashboard_med_picker")
    if dashboard_picker is not None:
        current_label = "Choose medication"
        selected_id = sanitize_text((selected or {}).get("id") or "", max_chars=32)
        if selected_id:
            for label, med_id in picker_values.items():
                if med_id == selected_id:
                    current_label = label
                    break
        try:
            dashboard_picker.configure(values=list(picker_values.keys()))
        except Exception:
            pass
        try:
            dashboard_picker.set(current_label)
        except Exception:
            pass
    self.ids.dashboard_nudge.text = build_dashboard_nudge_text(
        selected,
        self.current_recovery_support_state(),
        now,
    )
    self.set_field_text("daily_checklist_date", target_day.isoformat())
    if target_day == today:
        checklist_label = "Viewing Today"
    elif target_day < today:
        checklist_label = f"Viewing {target_day.isoformat()}"
    else:
        checklist_label = f"Future Plan {target_day.isoformat()}"
    self.ids.daily_checklist_date_label.text = checklist_label
    self.ids.daily_checklist_hint.text = (
        "Each row shows the time, medication, and planned dose. Check rows for the selected day to reconcile them, "
        "use Take Now for a current missed slot, and turn on checklist undo in Settings if you want reversible checkmarks."
    )
    self._render_daily_checklist(meds, selected, now)


def _desktop_med_by_id(self: DesktopMedSafeApp, med_id: str) -> Optional[Dict[str, Any]]:
    target = sanitize_text(med_id, max_chars=32)
    for med in all_stored_medications(self.data_cache):
        if str(med.get("id")) == target:
            return med
    return None


def _desktop_build_safety_tab(self: DesktopMedSafeApp, tab: Any) -> None:
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)
    scroll = ctk.CTkScrollableFrame(
        tab,
        fg_color="transparent",
        scrollbar_button_color="#314455",
        scrollbar_button_hover_color="#42586c",
    )
    scroll.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
    scroll.grid_columnconfigure((0, 1), weight=1)

    overview = self._card(scroll)
    overview.grid(row=0, column=0, sticky="nsew", padx=(0, 7), pady=(0, 12))
    overview.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(overview, text="Medication Safety", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=20, weight="bold")).grid(
        row=0, column=0, sticky="w", padx=18, pady=(18, 10)
    )
    safety_badge_widget = ctk.CTkLabel(
        overview,
        text="Safety Pending",
        fg_color=DESKTOP_WARNING,
        text_color="#08110f",
        corner_radius=18,
        width=190,
        height=44,
        font=ctk.CTkFont(size=17, weight="bold"),
    )
    safety_badge_widget.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))
    self._register("safety_overall_badge", DesktopRiskBadgeAdapter(safety_badge_widget))
    safety_title = self._label(overview, text="Awaiting safety scan", bold=True, wrap=420)
    safety_title.widget.grid(row=2, column=0, sticky="ew", padx=18)
    self._register("safety_overall_title", safety_title)
    safety_caption = self._label(
        overview,
        text="Run a scan to review each medication plan and the combined regimen.",
        muted=True,
        wrap=420,
    )
    safety_caption.widget.grid(row=3, column=0, sticky="ew", padx=18, pady=(8, 10))
    self._register("safety_overall_caption", safety_caption)
    button_row = ctk.CTkFrame(overview, fg_color="transparent")
    button_row.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 10))
    button_row.grid_columnconfigure(0, weight=1)
    self._button(button_row, text="Run Safety Scan Now", command=self.on_run_all_meds_safety_check, tone="warning").grid(
        row=0, column=0, sticky="ew"
    )
    safety_meta = self._label(overview, text="Encrypted local safety results will appear here.", muted=True, wrap=420)
    safety_meta.widget.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 18))
    self._register("safety_last_run", safety_meta)

    regimen_card = self._card(scroll)
    regimen_card.grid(row=0, column=1, sticky="nsew", padx=(7, 0), pady=(0, 12))
    regimen_card.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(regimen_card, text="Interaction Review", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=20, weight="bold")).grid(
        row=0, column=0, sticky="w", padx=18, pady=(18, 10)
    )
    regimen_box = self._readonly_box(regimen_card, height=240)
    regimen_box.widget.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
    self._register("safety_regimen_box", regimen_box)

    per_med_card = self._card(scroll)
    per_med_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
    per_med_card.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(per_med_card, text="Per-Medication Ratings", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=20, weight="bold")).grid(
        row=0, column=0, sticky="w", padx=18, pady=(18, 10)
    )
    per_med_box = self._readonly_box(per_med_card, height=380)
    per_med_box.widget.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
    self._register("safety_per_med_box", per_med_box)


def _desktop_refresh_safety_ui(self: DesktopMedSafeApp) -> None:
    meds = list(self.data_cache.get("meds") or [])
    now = time.time()
    state = effective_safety_reviews_state(self.data_cache.get("safety_reviews"), meds, now)
    regimen = dict(state.get("regimen") or {})
    action = normalize_dose_action_text(regimen.get("action") or "", "Caution")
    pending = bool(state.get("pending", False))
    title = sanitize_text(regimen.get("display") or f"All-meds safety: {action}", max_chars=160)
    message = sanitize_text(regimen.get("message") or "Run a scan to review the full regimen.", max_chars=420)
    if pending:
        title = "Safety scan in progress"
        message = build_dashboard_safety_summary_text(state, meds)
        action = "Assessing"
    if "safety_overall_badge" in self.ids:
        self.ids.safety_overall_badge.set_level(action)
    if "safety_overall_title" in self.ids:
        self.ids.safety_overall_title.text = title
    if "safety_overall_caption" in self.ids:
        self.ids.safety_overall_caption.text = message
    if "safety_last_run" in self.ids:
        if pending:
            self.ids.safety_last_run.text = f"Safety scan pending after {sanitize_text(state.get('reason') or 'recent medication changes', max_chars=120)}."
        else:
            timestamp = safe_float(state.get("timestamp") or 0.0)
            when = format_timestamp(timestamp) if timestamp > 0 else "Not run yet"
            self.ids.safety_last_run.text = f"Last completed scan: {when}."
    if "safety_regimen_box" in self.ids:
        raw = sanitize_text(regimen.get("raw") or "", max_chars=400)
        regimen_lines = [title, message]
        if raw:
            regimen_lines.append(f"Model trace: {raw}")
        self.ids.safety_regimen_box.text = "\n\n".join(line for line in regimen_lines if line)
    if "safety_per_med_box" in self.ids:
        self.ids.safety_per_med_box.text = build_safety_tab_per_med_text(state, meds)


def _desktop_trigger_safety_scan(self: DesktopMedSafeApp, reason: str = "manual safety scan", *, announce: bool = False) -> None:
    meds = [self.clone_med_snapshot(med) for med in list(active_medications(self.data_cache))]
    state = safety_reviews_defaults()
    state["timestamp"] = time.time()
    state["signature"] = regimen_signature(meds)
    state["pending"] = True
    state["reason"] = sanitize_text(reason, max_chars=160)
    self.data_cache["safety_reviews"] = state
    self.safety_scan_request_id += 1
    request_id = self.safety_scan_request_id
    self._cleanup_safety_scan_process(terminate=True)
    self.refresh_dashboard()
    self.refresh_safety_ui()
    if not meds:
        self.save_data_async()
        if announce:
            self.set_status("No medications to scan yet.")
        return
    if not self.vault:
        self.data_cache["safety_reviews"] = effective_safety_reviews_state({}, meds, time.time())
        self.refresh_dashboard()
        self.refresh_safety_ui()
        self.set_status("The encrypted vault is not ready for the safety scan.")
        return
    settings = dict(self.settings_data)
    if announce:
        self.set_status(f"Scanning safety for {len(meds)} medication(s)...")

    def launcher() -> None:
        try:
            if not self.vault:
                raise RuntimeError("Dose safety vault unavailable.")
            key = self.vault.get_or_create_key()
            ctx = mp.get_context("spawn")
            result_queue = ctx.Queue()
            process = ctx.Process(
                target=all_meds_safety_process_worker,
                args=(result_queue, key, meds, time.time(), settings, sanitize_text(reason, max_chars=160)),
                daemon=True,
            )
            process.start()
            self.run_on_ui_thread(self._safety_scan_process_started, request_id, process, result_queue, announce)
        except Exception as exc:
            self.run_on_ui_thread(self._safety_scan_failed, request_id, str(exc), announce)

    threading.Thread(target=launcher, daemon=True).start()


def _desktop_safety_scan_done(self: DesktopMedSafeApp, request_id: int, result: Dict[str, Any], announce: bool = False) -> None:
    if request_id != self.safety_scan_request_id:
        return
    self.data_cache["safety_reviews"] = ensure_vault_shape({"safety_reviews": result}).get("safety_reviews") or result
    self.save_data_async()
    self.refresh_dashboard()
    self.refresh_safety_ui()
    if announce:
        regimen = dict((self.data_cache.get("safety_reviews") or {}).get("regimen") or {})
        self.set_status(sanitize_text(regimen.get("message") or "Medication safety scan updated.", max_chars=220))


def _desktop_safety_scan_failed(self: DesktopMedSafeApp, request_id: int, error_text: str, announce: bool = False) -> None:
    if request_id != self.safety_scan_request_id:
        return
    meds = list(self.data_cache.get("meds") or [])
    fallback = effective_safety_reviews_state({}, meds, time.time())
    fallback["reason"] = sanitize_text(error_text, max_chars=160)
    fallback["pending"] = False
    self.data_cache["safety_reviews"] = fallback
    self.save_data_async()
    self.refresh_dashboard()
    self.refresh_safety_ui()
    self.set_status("Safety scan fell back to stored schedule rules.")
    if announce and self.window is not None:
        self.show_dialog("Safety Scan Fallback", sanitize_text(error_text, max_chars=280))


def _desktop_build_exercise_tab(self: DesktopMedSafeApp, tab: Any) -> None:
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)
    scroll = ctk.CTkScrollableFrame(
        tab,
        fg_color="transparent",
        scrollbar_button_color="#314455",
        scrollbar_button_hover_color="#42586c",
    )
    scroll.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
    scroll.grid_columnconfigure(0, weight=1)

    overview = self._card(scroll)
    overview.grid(row=0, column=0, sticky="ew", pady=(0, 12))
    overview.grid_columnconfigure(0, weight=1)
    overview_title = self._label(overview, text="Movement studio ready", bold=True, wrap=980)
    overview_title.widget.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
    self._register("exercise_overview_title", overview_title)
    overview_body = self._label(
        overview,
        text="Walking, gentle exercise, and stretch reminders all stay local and follow your computer clock.",
        muted=True,
        wrap=980,
    )
    overview_body.widget.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
    self._register("exercise_overview_body", overview_body)
    goal_summary = self._label(
        overview,
        text="Today's movement totals will appear here.",
        muted=True,
        wrap=980,
    )
    goal_summary.widget.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
    self._register("exercise_goal_summary", goal_summary)

    habits = self._card(scroll)
    habits.grid(row=1, column=0, sticky="ew", pady=(0, 12))
    habits.grid_columnconfigure((0, 1, 2), weight=1)
    for column, (prefix, title, default_minutes) in enumerate(EXERCISE_HABITS):
        habit_card = ctk.CTkFrame(habits, fg_color=DESKTOP_SURFACE_ALT, border_width=1, border_color=DESKTOP_BORDER, corner_radius=14)
        habit_card.grid(row=0, column=column, sticky="nsew", padx=(18 if column == 0 else 8, 18 if column == 2 else 8), pady=18)
        habit_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(habit_card, text=title, anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 6)
        )
        status = self._label(habit_card, text="Ready", bold=True, wrap=240)
        status.widget.grid(row=1, column=0, sticky="ew", padx=14)
        self._register(f"exercise_{prefix}_status", status)
        caption = self._label(habit_card, text="Ready now", muted=True, wrap=240)
        caption.widget.grid(row=2, column=0, sticky="ew", padx=14, pady=(6, 12))
        self._register(f"exercise_{prefix}_caption", caption)
        self._button(
            habit_card,
            text=f"Log {title} ({default_minutes:g}m)",
            command=lambda habit_name=prefix: self.on_log_exercise_habit(habit_name),
            tone="neutral" if prefix != "light" else "warning",
        ).grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))

    settings = self._card(scroll)
    settings.grid(row=2, column=0, sticky="ew", pady=(0, 12))
    settings.grid_columnconfigure((0, 1, 2), weight=1)
    ctk.CTkLabel(settings, text="Walk interval (h)", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=0, sticky="w", padx=(18, 8), pady=(18, 0))
    ctk.CTkLabel(settings, text="Light exercise interval (h)", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=1, sticky="w", padx=8, pady=(18, 0))
    ctk.CTkLabel(settings, text="Stretch interval (h)", anchor="w", text_color=DESKTOP_MUTED).grid(row=0, column=2, sticky="w", padx=(8, 18), pady=(18, 0))
    walk_interval = self._entry(settings, placeholder="Walk every 4h")
    light_interval = self._entry(settings, placeholder="Light exercise every 8h")
    stretch_interval = self._entry(settings, placeholder="Stretch every 2h")
    walk_interval.widget.grid(row=1, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
    light_interval.widget.grid(row=1, column=1, sticky="ew", padx=8, pady=(6, 12))
    stretch_interval.widget.grid(row=1, column=2, sticky="ew", padx=(8, 18), pady=(6, 12))
    self._register("exercise_walk_interval", walk_interval)
    self._register("exercise_light_interval", light_interval)
    self._register("exercise_stretch_interval", stretch_interval)

    ctk.CTkLabel(settings, text="Walk goal (min/day)", anchor="w", text_color=DESKTOP_MUTED).grid(row=2, column=0, sticky="w", padx=(18, 8))
    ctk.CTkLabel(settings, text="Light exercise goal (min/day)", anchor="w", text_color=DESKTOP_MUTED).grid(row=2, column=1, sticky="w", padx=8)
    ctk.CTkLabel(settings, text="Stretch goal (min/day)", anchor="w", text_color=DESKTOP_MUTED).grid(row=2, column=2, sticky="w", padx=(8, 18))
    walk_goal = self._entry(settings, placeholder="30")
    light_goal = self._entry(settings, placeholder="20")
    stretch_goal = self._entry(settings, placeholder="10")
    walk_goal.widget.grid(row=3, column=0, sticky="ew", padx=(18, 8), pady=(6, 12))
    light_goal.widget.grid(row=3, column=1, sticky="ew", padx=8, pady=(6, 12))
    stretch_goal.widget.grid(row=3, column=2, sticky="ew", padx=(8, 18), pady=(6, 12))
    self._register("exercise_walk_goal", walk_goal)
    self._register("exercise_light_goal", light_goal)
    self._register("exercise_stretch_goal", stretch_goal)

    ctk.CTkLabel(settings, text="Movement notes", anchor="w", text_color=DESKTOP_MUTED).grid(row=4, column=0, columnspan=3, sticky="w", padx=18)
    notes = self._edit_box(settings, height=110)
    notes.widget.grid(row=5, column=0, columnspan=3, sticky="ew", padx=18, pady=(6, 12))
    self._register("exercise_notes", notes)
    buttons = ctk.CTkFrame(settings, fg_color="transparent")
    buttons.grid(row=6, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 18))
    buttons.grid_columnconfigure((0, 1), weight=1)
    self._button(buttons, text="Save Movement Settings", command=self.on_save_exercise_settings).grid(row=0, column=0, sticky="ew", padx=(0, 6))
    self._button(buttons, text="Reset Defaults", command=self.on_reset_exercise_settings, tone="neutral").grid(row=0, column=1, sticky="ew", padx=(6, 0))

    history = self._card(scroll)
    history.grid(row=3, column=0, sticky="ew")
    history.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(history, text="Movement History", anchor="w", text_color=DESKTOP_TEXT, font=ctk.CTkFont(size=18, weight="bold")).grid(
        row=0, column=0, sticky="w", padx=18, pady=(18, 10)
    )
    history_box = self._readonly_box(history, height=220)
    history_box.widget.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
    self._register("exercise_history", history_box)


def _desktop_refresh_exercise_ui(self: DesktopMedSafeApp) -> None:
    now = time.time()
    state = dict(self.data_cache.get("exercise") or exercise_defaults())
    overview_title, overview_body = build_exercise_overview(state, now)
    totals = build_exercise_daily_totals(state, now)
    self.ids.exercise_overview_title.text = overview_title
    self.ids.exercise_overview_body.text = overview_body
    self.ids.exercise_goal_summary.text = (
        f"Walk {totals['walk']:.0f}/{max(1.0, safe_float(state.get('daily_walk_goal_minutes')) or 30.0):.0f} min | "
        f"Light {totals['light']:.0f}/{max(1.0, safe_float(state.get('daily_light_goal_minutes')) or 20.0):.0f} min | "
        f"Stretch {totals['stretch']:.0f}/{max(1.0, safe_float(state.get('daily_stretch_goal_minutes')) or 10.0):.0f} min"
    )

    for prefix, last_key, interval_key in (
        ("walk", "last_walk_ts", "walk_interval_hours"),
        ("light", "last_light_ts", "light_interval_hours"),
        ("stretch", "last_stretch_ts", "stretch_interval_hours"),
    ):
        status = habit_due_status(safe_float(state.get(last_key)), safe_float(state.get(interval_key)) or 1.0, now)
        title_color, caption_color = habit_palette(status)
        self.ids[f"exercise_{prefix}_status"].text = status["state"]
        self.ids[f"exercise_{prefix}_status"].text_color = title_color
        self.ids[f"exercise_{prefix}_caption"].text = f"{status['text']} | every {max(0.5, safe_float(state.get(interval_key))):g}h"
        self.ids[f"exercise_{prefix}_caption"].text_color = caption_color

    self.set_field_text("exercise_walk_interval", f"{max(0.5, safe_float(state.get('walk_interval_hours'))):g}")
    self.set_field_text("exercise_light_interval", f"{max(0.5, safe_float(state.get('light_interval_hours'))):g}")
    self.set_field_text("exercise_stretch_interval", f"{max(0.5, safe_float(state.get('stretch_interval_hours'))):g}")
    self.set_field_text("exercise_walk_goal", f"{max(1.0, safe_float(state.get('daily_walk_goal_minutes'))):g}")
    self.set_field_text("exercise_light_goal", f"{max(1.0, safe_float(state.get('daily_light_goal_minutes'))):g}")
    self.set_field_text("exercise_stretch_goal", f"{max(1.0, safe_float(state.get('daily_stretch_goal_minutes'))):g}")
    self.set_field_text("exercise_notes", sanitize_text(state.get("notes") or "", max_chars=800))
    self.ids.exercise_history.text = build_exercise_history_text(state)


def _desktop_on_log_exercise_habit(self: DesktopMedSafeApp, habit: str) -> None:
    config = {
        "walk": ("Walk", "last_walk_ts", 15.0),
        "light": ("Light exercise", "last_light_ts", 10.0),
        "stretch": ("Stretch", "last_stretch_ts", 5.0),
    }
    if habit not in config:
        return
    label, last_key, minutes = config[habit]
    state = dict(self.data_cache.get("exercise") or exercise_defaults())
    now = time.time()
    state[last_key] = now
    state["history"] = list(state.get("history") or []) + [{"timestamp": now, "habit": habit, "minutes": minutes}]
    state["history"] = state["history"][-240:]
    self.data_cache["exercise"] = state
    self.save_data()
    self.refresh_exercise_ui()
    self.set_status(f"Logged {label.lower()} session ({minutes:g} min).")


def _desktop_on_save_exercise_settings(self: DesktopMedSafeApp) -> None:
    state = dict(self.data_cache.get("exercise") or exercise_defaults())
    walk_interval = max(0.5, safe_float(self.ids.exercise_walk_interval.text) or safe_float(state.get("walk_interval_hours")) or 4.0)
    light_interval = max(0.5, safe_float(self.ids.exercise_light_interval.text) or safe_float(state.get("light_interval_hours")) or 8.0)
    stretch_interval = max(0.5, safe_float(self.ids.exercise_stretch_interval.text) or safe_float(state.get("stretch_interval_hours")) or 2.0)
    walk_goal = max(1.0, safe_float(self.ids.exercise_walk_goal.text) or safe_float(state.get("daily_walk_goal_minutes")) or 30.0)
    light_goal = max(1.0, safe_float(self.ids.exercise_light_goal.text) or safe_float(state.get("daily_light_goal_minutes")) or 20.0)
    stretch_goal = max(1.0, safe_float(self.ids.exercise_stretch_goal.text) or safe_float(state.get("daily_stretch_goal_minutes")) or 10.0)
    state.update(
        {
            "walk_interval_hours": walk_interval,
            "light_interval_hours": light_interval,
            "stretch_interval_hours": stretch_interval,
            "daily_walk_goal_minutes": walk_goal,
            "daily_light_goal_minutes": light_goal,
            "daily_stretch_goal_minutes": stretch_goal,
            "notes": sanitize_text(self.ids.exercise_notes.text, max_chars=800),
        }
    )
    self.data_cache["exercise"] = state
    self.save_data()
    self.refresh_exercise_ui()
    self.set_status("Exercise reminder rhythm saved.")


def _desktop_on_reset_exercise_settings(self: DesktopMedSafeApp) -> None:
    defaults = exercise_defaults()
    state = dict(self.data_cache.get("exercise") or exercise_defaults())
    state.update(
        {
            "walk_interval_hours": defaults["walk_interval_hours"],
            "light_interval_hours": defaults["light_interval_hours"],
            "stretch_interval_hours": defaults["stretch_interval_hours"],
            "daily_walk_goal_minutes": defaults["daily_walk_goal_minutes"],
            "daily_light_goal_minutes": defaults["daily_light_goal_minutes"],
            "daily_stretch_goal_minutes": defaults["daily_stretch_goal_minutes"],
            "notes": defaults["notes"],
        }
    )
    self.data_cache["exercise"] = state
    self.save_data()
    self.refresh_exercise_ui()
    self.set_status("Exercise reminder defaults restored.")


def _desktop_refresh_from_disk(self: DesktopMedSafeApp) -> None:
    if not self.vault:
        return
    try:
        self.data_cache = ensure_vault_shape(self.vault.load())
    except RuntimeError as exc:
        self.vault_write_blocked_reason = sanitize_text(str(exc), max_chars=260)
        if self.main_ui_started:
            self.set_status(self.vault_write_blocked_reason)
        return
    self.vault_write_blocked_reason = ""
    if self.selected_med_id and self.med_by_id(self.selected_med_id) is None:
        self.selected_med_id = None
    if not self.selected_med_id:
        ranked_active = sorted(
            active_medications(self.data_cache),
            key=lambda med: (
                0 if medication_due_status(med)["overdue"] else 1 if medication_due_status(med)["due_now"] else 2,
                medication_due_status(med)["next_ts"] or float("inf"),
                sanitize_text(med.get("name"), max_chars=120).lower(),
            ),
        )
        if ranked_active:
            self.selected_med_id = str(ranked_active[0].get("id"))
        else:
            ranked_archived = sorted(
                archived_medications(self.data_cache),
                key=lambda med: (
                    -medication_archived_ts(med),
                    -last_effective_taken_ts(med),
                    sanitize_text(med.get("name"), max_chars=120).lower(),
                ),
            )
            if ranked_archived:
                self.selected_med_id = str(ranked_archived[0].get("id"))
    self._restore_saved_dose_safety_review()
    self.refresh_ui()


def _desktop_refresh_med_list(self: DesktopMedSafeApp) -> None:
    med_list = self.ids.med_list
    med_list.clear_widgets()
    now = time.time()
    active = sorted(
        active_medications(self.data_cache),
        key=lambda item: (
            0 if medication_due_status(item, now)["overdue"] else 1 if medication_due_status(item, now)["due_now"] else 2,
            medication_due_status(item, now)["next_ts"] or float("inf"),
            sanitize_text(item.get("name"), max_chars=120).lower(),
        ),
    )
    archived = sorted(
        archived_medications(self.data_cache),
        key=lambda item: (
            -medication_archived_ts(item),
            -last_effective_taken_ts(item),
            sanitize_text(item.get("name"), max_chars=120).lower(),
        ),
    )
    if active:
        med_list.add_section("Current Regimen")
        for med in active:
            title = sanitize_text(med.get("name"), max_chars=120)
            prefix = "Selected | " if str(med.get("id")) == self.selected_med_id else ""
            med_list.add_widget(
                DesktopListItem(
                    text=prefix + title,
                    secondary_text=medication_card_line(med, now),
                    on_release=lambda _widget, med_id=str(med.get("id")): self.select_med(med_id),
                )
            )
    if archived:
        med_list.add_section("Completed / History")
        for med in archived:
            title = sanitize_text(med.get("name"), max_chars=120)
            prefix = "Selected | " if str(med.get("id")) == self.selected_med_id else ""
            med_list.add_widget(
                DesktopListItem(
                    text=prefix + title,
                    secondary_text=medication_card_line(med, now),
                    on_release=lambda _widget, med_id=str(med.get("id")): self.select_med(med_id),
                )
            )
    if not active and not archived:
        med_list.add_section("No medications saved yet")
    if "med_list_summary" in self.ids:
        self.ids.med_list_summary.text = (
            f"Current regimen: {len(active)} | Completed history: {len(archived)}. "
            "Select any item to review it on the dashboard or in the medication editor."
        )


def _desktop_refresh_form(self: DesktopMedSafeApp) -> None:
    med = self.current_selected_med()
    selected_any = self.med_by_id(self.selected_med_id or "") if self.selected_med_id else None
    if med is None:
        self.last_form_med_id = None
        if selected_any is not None and medication_is_archived(selected_any):
            med_name = sanitize_text(selected_any.get("name") or "Medication", max_chars=120)
            self.ids.form_selection.text = f"Completed: {med_name}"
            self.ids.form_schedule_preview.text = (
                f"{medication_archive_label(selected_any)}\n"
                "This medication is kept for history only. Use New Medication to add a current regimen entry."
            )
            if "med_form_hint" in self.ids:
                self.ids.med_form_hint.text = (
                    "Completed medications are read-only in this editor so their history stays intact. "
                    "Use New Medication to add something back into the current regimen."
                )
        else:
            self.ids.form_selection.text = "Creating a new medication"
            self.ids.form_schedule_preview.text = "Saved schedules appear below."
            if "med_form_hint" in self.ids:
                self.ids.med_form_hint.text = (
                    "Create a current regimen entry here. When a medication is finished, use Complete / Archive to keep its history."
                )
        self.set_field_text("med_name", "", force=True)
        self.set_field_text("dose_mg", "", force=True)
        self.set_field_text("interval_h", "", force=True)
        self.set_field_text("max_daily", "", force=True)
        self.set_field_text("first_dose_time", "", force=True)
        self.set_field_text("custom_times_text", "", force=True)
        self.set_field_text("schedule_text", "", force=True)
        self.set_field_text("med_notes", "", force=True)
        return
    med_id = str(med.get("id"))
    force_sync = med_id != self.last_form_med_id
    self.ids.form_selection.text = f"Editing: {sanitize_text(med.get('name'), max_chars=120)}"
    self.set_field_text("med_name", sanitize_text(med.get("name") or "", max_chars=120), force=force_sync)
    self.set_field_text("dose_mg", f"{safe_float(med.get('dose_mg')):g}" if safe_float(med.get("dose_mg")) else "", force=force_sync)
    self.set_field_text("interval_h", f"{safe_float(med.get('interval_hours')):g}" if safe_float(med.get("interval_hours")) else "", force=force_sync)
    self.set_field_text("max_daily", f"{safe_float(med.get('max_daily_mg')):g}" if safe_float(med.get("max_daily_mg")) else "", force=force_sync)
    self.set_field_text("first_dose_time", sanitize_text(med.get("first_dose_time") or "", max_chars=20), force=force_sync)
    self.set_field_text("custom_times_text", sanitize_text(med.get("custom_times_text") or "", max_chars=320), force=force_sync)
    self.set_field_text("schedule_text", sanitize_text(med.get("schedule_text") or "", max_chars=240), force=force_sync)
    self.set_field_text("med_notes", sanitize_text(med.get("notes") or "", max_chars=500), force=force_sync)
    self.ids.form_schedule_preview.text = medication_card_line(med) + "\n" + build_medication_schedule_text(med)
    if "med_form_hint" in self.ids:
        self.ids.med_form_hint.text = (
            "Save edits, run a focused safety check, log a dose, or complete/archive this medication when it leaves the current regimen."
        )
    self.last_form_med_id = med_id


def _desktop_text_size_base_font_size(self: DesktopMedSafeApp) -> int:
    choice = normalize_setting_choice(self.settings_data.get("text_size"), TEXT_SIZE_OPTIONS, "Default")
    return int(TEXT_SIZE_BASE_FONT_MAP.get(choice, TEXT_SIZE_BASE_FONT_MAP["Default"]))


def _desktop_sync_text_size_widgets(self: DesktopMedSafeApp) -> None:
    if ctk is None:
        return
    base = self.text_size_base_font_size()
    for value in list(self.ids.values()):
        widget = getattr(value, "widget", value)
        if widget is None:
            continue
        class_name = widget.__class__.__name__
        try:
            if class_name == "CTkTextbox":
                widget.configure(font=ctk.CTkFont(size=base))
            elif class_name == "CTkEntry":
                widget.configure(font=ctk.CTkFont(size=max(9, base)))
            elif class_name == "CTkOptionMenu":
                widget.configure(font=ctk.CTkFont(size=max(9, base)))
            elif class_name == "CTkButton":
                widget.configure(font=ctk.CTkFont(size=max(9, base), weight="bold"))
        except Exception:
            continue
    assistant_box = getattr(self.ids.get("assistant_history"), "widget", None)
    if assistant_box is not None:
        self.configure_markdown_textbox(assistant_box, base_size=base + int(getattr(self, "assistant_chat_font_delta", 0)))


def _desktop_configure_markdown_textbox(self: DesktopMedSafeApp, textbox: Any, *, base_size: Optional[int] = None) -> None:
    try:
        text_widget = textbox._textbox
    except Exception:
        return
    size = max(9, min(26, int(base_size or self.text_size_base_font_size())))
    meta_size = max(8, size - 2)
    code_size = max(8, size - 1)
    text_widget.configure(
        font=("DejaVu Sans", size),
        foreground=DESKTOP_TEXT,
        background=DESKTOP_SURFACE_ALT,
        insertbackground=DESKTOP_TEXT,
        spacing1=1,
        spacing2=1,
        spacing3=5,
    )
    text_widget.tag_config("md_you_header", foreground=DESKTOP_WARNING, font=("DejaVu Sans", size, "bold"))
    text_widget.tag_config("md_assistant_header", foreground=DESKTOP_ACCENT, font=("DejaVu Sans", size, "bold"))
    text_widget.tag_config("md_meta", foreground=DESKTOP_MUTED, font=("DejaVu Sans", meta_size))
    text_widget.tag_config("md_h1", foreground=DESKTOP_ACCENT, font=("DejaVu Sans", size + 4, "bold"), spacing1=8, spacing3=6)
    text_widget.tag_config("md_h2", foreground=DESKTOP_WARNING, font=("DejaVu Sans", size + 2, "bold"), spacing1=6, spacing3=4)
    text_widget.tag_config("md_h3", foreground="#7fd0c6", font=("DejaVu Sans", size + 1, "bold"), spacing1=4, spacing3=3)
    text_widget.tag_config("md_bold", foreground=DESKTOP_TEXT, font=("DejaVu Sans", size, "bold"))
    text_widget.tag_config("md_italic", foreground="#dce9e6", font=("DejaVu Sans", size, "italic"))
    text_widget.tag_config("md_code_inline", foreground="#ffdd8f", background="#0f1922", font=("DejaVu Sans Mono", code_size))
    text_widget.tag_config(
        "md_code_block",
        foreground="#9fe7d9",
        background="#0f1922",
        font=("DejaVu Sans Mono", code_size),
        lmargin1=14,
        lmargin2=14,
        spacing1=4,
        spacing3=6,
    )
    text_widget.tag_config("md_quote_bar", foreground="#6fb9c1", font=("DejaVu Sans Mono", size, "bold"))
    text_widget.tag_config("md_quote", foreground="#cfe6eb", font=("DejaVu Sans", size, "italic"), lmargin1=16, lmargin2=16)
    text_widget.tag_config("md_link", foreground="#84c8ff", underline=True)
    text_widget.tag_config("md_list_marker", foreground=DESKTOP_ACCENT, font=("DejaVu Sans Mono", size, "bold"))
    text_widget.tag_config("md_list_text", foreground=DESKTOP_TEXT, font=("DejaVu Sans", size), lmargin2=24)
    text_widget.tag_config("md_hr", foreground=DESKTOP_MUTED, font=("DejaVu Sans Mono", meta_size), spacing1=6, spacing3=8)
    for tag_name in ("md_bold", "md_italic", "md_code_inline", "md_link"):
        try:
            text_widget.tag_raise(tag_name)
        except Exception:
            pass


def _desktop_clear_markdown_widgets(self: DesktopMedSafeApp, textbox: Any) -> None:
    for widget in getattr(textbox, "_markdown_widgets", []):
        try:
            widget.destroy()
        except Exception:
            pass
    setattr(textbox, "_markdown_widgets", [])


def _desktop_copy_text_to_clipboard(self: DesktopMedSafeApp, value: str, label: str = "Text") -> None:
    if self.window is None:
        return
    try:
        self.window.clipboard_clear()
        self.window.clipboard_append(sanitize_text(value, max_chars=20000))
        self.window.update_idletasks()
        self.set_status(f"{label} copied to clipboard.")
    except Exception:
        pass


def _desktop_insert_markdown_copy_button(
    self: DesktopMedSafeApp,
    textbox: Any,
    text_widget: Any,
    value: str,
    label: str = "Copy",
) -> None:
    button = tk.Button(
        text_widget,
        text=label,
        command=lambda copy_value=value, copy_label=label: self.copy_text_to_clipboard(copy_value, copy_label),
        bg=DESKTOP_ACCENT,
        fg="#041310",
        activebackground="#2eb5ab",
        activeforeground="#041310",
        relief="flat",
        bd=0,
        padx=8,
        pady=2,
        cursor="hand2",
        font=("DejaVu Sans", 9, "bold"),
    )
    widgets = getattr(textbox, "_markdown_widgets", [])
    widgets.append(button)
    setattr(textbox, "_markdown_widgets", widgets)
    text_widget.window_create("end", window=button, padx=8)


def _desktop_insert_markdown_inline(
    self: DesktopMedSafeApp,
    text_widget: Any,
    line: str,
    *,
    default_tag: Optional[str] = None,
) -> None:
    token_re = re.compile(
        r"(!\[[^\]]*\]\([^)]+\)|\[[^\]]+\]\([^)]+\)|`[^`\n]+`|\*\*[^*\n]+?\*\*|__[^_\n]+?__|(?<!\*)\*[^*\n]+?\*(?!\*)|(?<!_)_[^_\n]+?_(?!_))"
    )
    pos = 0
    for match in token_re.finditer(line):
        if match.start() > pos:
            text_widget.insert("end", line[pos:match.start()], (default_tag,) if default_tag else ())
        token = match.group(0)
        image = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", token)
        link = MARKDOWN_LINK_RE.match(token)
        if image:
            alt, url = image.groups()
            text_widget.insert("end", f"[image: {alt or 'untitled'}]", ("md_link",))
            text_widget.insert("end", f" ({url})", ("md_meta",))
        elif link:
            label, url = link.groups()
            text_widget.insert("end", label, ("md_link",))
            text_widget.insert("end", f" ({url})", ("md_meta",))
        elif token.startswith("`") and token.endswith("`"):
            tags = ("md_code_inline", default_tag) if default_tag else ("md_code_inline",)
            text_widget.insert("end", token[1:-1], tags)
        elif token.startswith(("**", "__")) and token.endswith(("**", "__")):
            tags = ("md_bold", default_tag) if default_tag else ("md_bold",)
            text_widget.insert("end", token[2:-2], tags)
        elif token.startswith(("*", "_")) and token.endswith(("*", "_")):
            tags = ("md_italic", default_tag) if default_tag else ("md_italic",)
            text_widget.insert("end", token[1:-1], tags)
        else:
            text_widget.insert("end", token, (default_tag,) if default_tag else ())
        pos = match.end()
    if pos < len(line):
        text_widget.insert("end", line[pos:], (default_tag,) if default_tag else ())


def _desktop_insert_markdown_text(self: DesktopMedSafeApp, textbox: Any, value: Any, *, max_chars: int = 12000) -> None:
    try:
        text_widget = textbox._textbox
    except Exception:
        textbox.insert("end", markdown_to_plain_text(value, max_chars=max_chars))
        return
    text = sanitize_text(value, max_chars=max_chars).replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not text:
        return
    lines = text.split("\n")
    line_index = 0
    while line_index < len(lines):
        raw_line = lines[line_index]
        stripped = raw_line.strip()
        fence = re.match(r"^```([\w.+-]*)\s*$", stripped)
        if fence:
            line_index += 1
            code_lines: List[str] = []
            while line_index < len(lines):
                if re.match(r"^```[\w.+-]*\s*$", lines[line_index].strip()):
                    break
                code_lines.append(lines[line_index])
                line_index += 1
            code_text = "\n".join(code_lines).rstrip("\n")
            label = fence.group(1).strip() or "text"
            text_widget.insert("end", f" code: {label} ", ("md_meta",))
            if code_text:
                self.insert_markdown_copy_button(textbox, text_widget, code_text, "Copy code")
            text_widget.insert("end", "\n", ("md_meta",))
            if code_text:
                text_widget.insert("end", code_text + "\n", ("md_code_block",))
            else:
                text_widget.insert("end", "[empty code block]\n", ("md_meta",))
            if line_index < len(lines):
                line_index += 1
            text_widget.insert("end", "\n")
            continue
        if re.fullmatch(r"\s*([-*_])(?:\s*\1){2,}\s*", raw_line):
            text_widget.insert("end", "─" * 54 + "\n", ("md_hr",))
            line_index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", raw_line)
        if heading:
            level = min(len(heading.group(1)), 3)
            text_widget.insert("end", heading.group(2).strip() + "\n", (f"md_h{level}",))
            line_index += 1
            continue
        quote = re.match(r"^\s*>\s?(.*)$", raw_line)
        if quote:
            text_widget.insert("end", "┃ ", ("md_quote_bar",))
            self.insert_markdown_inline(text_widget, quote.group(1), default_tag="md_quote")
            text_widget.insert("end", "\n")
            line_index += 1
            continue
        unordered = re.match(r"^(\s*)([-+*])\s+(.+)$", raw_line)
        if unordered:
            text_widget.insert("end", unordered.group(1) + "• ", ("md_list_marker",))
            self.insert_markdown_inline(text_widget, unordered.group(3), default_tag="md_list_text")
            text_widget.insert("end", "\n")
            line_index += 1
            continue
        ordered = re.match(r"^(\s*)(\d+)\.\s+(.+)$", raw_line)
        if ordered:
            text_widget.insert("end", f"{ordered.group(1)}{ordered.group(2)}. ", ("md_list_marker",))
            self.insert_markdown_inline(text_widget, ordered.group(3), default_tag="md_list_text")
            text_widget.insert("end", "\n")
            line_index += 1
            continue
        self.insert_markdown_inline(text_widget, raw_line)
        text_widget.insert("end", "\n")
        line_index += 1


def _desktop_refresh_assistant_history(self: DesktopMedSafeApp) -> None:
    history = list(self.data_cache.get("assistant_history") or [])
    box = getattr(self.ids.get("assistant_history"), "widget", None)
    if box is None:
        return
    try:
        box.configure(state="normal")
        self.clear_markdown_widgets(box)
        box.delete("1.0", tk.END)
        self.configure_markdown_textbox(box, base_size=self.text_size_base_font_size() + int(getattr(self, "assistant_chat_font_delta", 0)))
        text_widget = box._textbox
    except Exception:
        self.ids.assistant_history.text = "No assistant messages yet." if not history else "\n\n".join(
            markdown_to_plain_text(item.get("content") or "", max_chars=10000) for item in history[-12:]
        )
        return
    if not history:
        text_widget.insert("end", "No assistant messages yet.\n", ("md_meta",))
    else:
        visible_history = history[-12:]
        for index, item in enumerate(visible_history):
            speaker = "You" if item.get("role") == "user" else "MedSafe"
            header_tag = "md_you_header" if item.get("role") == "user" else "md_assistant_header"
            mode = normalize_assistant_mode(item.get("mode") or "General")
            timestamp = safe_float(item.get("timestamp") or 0.0)
            when = time.strftime("%I:%M %p", time.localtime(timestamp)).lstrip("0") if timestamp > 0 else ""
            text_widget.insert("end", speaker, (header_tag,))
            if mode != "General":
                text_widget.insert("end", f" | {mode}", ("md_meta",))
            if when:
                text_widget.insert("end", f" | {when}", ("md_meta",))
            text_widget.insert("end", "\n")
            self.insert_markdown_text(box, item.get("content") or "", max_chars=10000)
            if index != len(visible_history) - 1:
                text_widget.insert("end", "─" * 54 + "\n\n", ("md_hr",))
    try:
        box.see("end")
    except Exception:
        pass
    try:
        box.configure(state="disabled")
    except Exception:
        pass


def _desktop_on_delete_med(self: DesktopMedSafeApp) -> None:
    med = self.current_selected_med()
    if not med:
        selected_any = self.med_by_id(self.selected_med_id or "") if self.selected_med_id else None
        if selected_any is not None and medication_is_archived(selected_any):
            self.set_status("This medication is already completed and kept in history.")
        else:
            self.set_status("Select a current medication first.")
        return
    original_data = self.clone_data_snapshot()
    original_selected_id = self.selected_med_id
    name = sanitize_text(med.get("name"), max_chars=120)
    archived_med = normalized_med_entry(self.clone_med_snapshot(med), default_archived_ts=time.time())
    if archived_med is None:
        self.set_status("Could not archive that medication right now.")
        return
    archived_med["archived_ts"] = max(time.time(), medication_archived_ts(archived_med))
    med_id = str(med.get("id"))
    self.data_cache["meds"] = [item for item in self.data_cache.get("meds", []) or [] if str(item.get("id")) != med_id]
    archives = [item for item in list(self.data_cache.get("med_archives") or []) if str(item.get("id")) != med_id]
    archives.append(archived_med)
    archives.sort(
        key=lambda item: (
            medication_archived_ts(item),
            last_effective_taken_ts(item),
            sanitize_text(item.get("name"), max_chars=120).lower(),
        )
    )
    self.data_cache["med_archives"] = archives[-240:]
    self.selected_med_id = med_id
    self.last_form_med_id = None
    self.last_check_level = "Medium"
    self.last_check_display = "Medication completed"
    self.last_check_message = f"{name} was removed from the current regimen and kept in history."
    if not self.save_data():
        self.data_cache = original_data
        self.selected_med_id = original_selected_id
        self.refresh_ui()
        return
    self.refresh_ui()
    self.trigger_safety_scan("medication removal", announce=False)
    self.set_status(f"Completed {name}. Past doses are still saved in history.")


def _desktop_on_text_size_change(self: DesktopMedSafeApp, choice: str) -> None:
    normalized = normalize_setting_choice(choice, TEXT_SIZE_OPTIONS, self.settings_data.get("text_size", "Default"))
    self.apply_text_size_setting(normalized)
    if self.paths is not None:
        save_settings({"text_size": normalized}, self.paths)
        self.settings_data = load_settings(self.paths)
    else:
        self.settings_data["text_size"] = normalized
    if "text_size_menu" in self.ids:
        try:
            self.ids.text_size_menu.set(normalized)
        except Exception:
            pass
    if self.main_ui_started:
        self.sync_text_size_widgets()
        self.refresh_ui()
    self.set_status(f"Text size set to {normalized}.")

DesktopMedSafeApp._build_exercise_tab = _desktop_build_exercise_tab
DesktopMedSafeApp.refresh_exercise_ui = _desktop_refresh_exercise_ui
DesktopMedSafeApp.on_log_exercise_habit = _desktop_on_log_exercise_habit
DesktopMedSafeApp.on_save_exercise_settings = _desktop_on_save_exercise_settings
DesktopMedSafeApp.on_reset_exercise_settings = _desktop_on_reset_exercise_settings

DesktopMedSafeApp._build_safety_tab = _desktop_build_safety_tab
DesktopMedSafeApp.refresh_safety_ui = _desktop_refresh_safety_ui
DesktopMedSafeApp.trigger_safety_scan = _desktop_trigger_safety_scan
DesktopMedSafeApp._safety_scan_done = _desktop_safety_scan_done
DesktopMedSafeApp._safety_scan_failed = _desktop_safety_scan_failed


DesktopMedSafeApp._render_daily_checklist = _desktop_render_daily_checklist
DesktopMedSafeApp.on_checklist_take_dose = _desktop_on_checklist_take_dose
DesktopMedSafeApp.on_checklist_uncheck_dose = _desktop_on_checklist_uncheck_dose
DesktopMedSafeApp.refresh_dashboard = _desktop_refresh_dashboard
DesktopMedSafeApp.med_by_id = _desktop_med_by_id
DesktopMedSafeApp.refresh_from_disk = _desktop_refresh_from_disk
DesktopMedSafeApp.refresh_med_list = _desktop_refresh_med_list
DesktopMedSafeApp.refresh_form = _desktop_refresh_form
DesktopMedSafeApp.text_size_base_font_size = _desktop_text_size_base_font_size
DesktopMedSafeApp.sync_text_size_widgets = _desktop_sync_text_size_widgets
DesktopMedSafeApp.configure_markdown_textbox = _desktop_configure_markdown_textbox
DesktopMedSafeApp.clear_markdown_widgets = _desktop_clear_markdown_widgets
DesktopMedSafeApp.copy_text_to_clipboard = _desktop_copy_text_to_clipboard
DesktopMedSafeApp.insert_markdown_copy_button = _desktop_insert_markdown_copy_button
DesktopMedSafeApp.insert_markdown_inline = _desktop_insert_markdown_inline
DesktopMedSafeApp.insert_markdown_text = _desktop_insert_markdown_text
DesktopMedSafeApp.refresh_assistant_history = _desktop_refresh_assistant_history
DesktopMedSafeApp.on_delete_med = _desktop_on_delete_med
DesktopMedSafeApp.on_text_size_change = _desktop_on_text_size_change


MedSafeApp = DesktopMedSafeApp


if __name__ == "__main__":
    MedSafeApp().run()