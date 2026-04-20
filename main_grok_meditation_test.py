"""
Grok Meditation Voice Surface Ultra RT LEAP — consolidated full file
Includes:
- realtime partial STT
- barge-in TTS interruption
- continuous voice loop
- live monitor + timeline
- preset save/load
- interrupted reply recovery
- provider fallback
- ritual generation
"""

from __future__ import annotations

import io
import json
import math
import os
import queue
import re
import threading
import time
import hashlib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import customtkinter as ctk
import httpx
import numpy as np
import sounddevice as sd
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


APP_TITLE = "Grok Meditation Voice Surface Ultra RT"
APP_SIZE = "1940x1180"

APP_DIR = Path(".grok_meditation_surface_rt")
APP_DIR.mkdir(exist_ok=True)
TEMP_DIR = APP_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)
VAULT_PATH = APP_DIR / "vault.aes"
SALT_PATH = APP_DIR / "salt.bin"
BOOT_CONFIG_PATH = APP_DIR / "boot_config.json"
PRESETS_PATH = APP_DIR / "presets.json"
TTS_CACHE_DIR = APP_DIR / "tts_cache"
TTS_CACHE_DIR.mkdir(exist_ok=True)

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"
PBKDF2_ITERATIONS = 650_000
FRAME_SECONDS = 0.08

PALETTE = {
    "bg": "#040806",
    "panel": "#0a1510",
    "panel_alt": "#10201a",
    "panel_soft": "#152720",
    "text": "#ddffe8",
    "muted": "#8ab89a",
    "line": "#234233",
    "accent": "#33f08d",
    "accent_2": "#9fffc6",
    "accent_3": "#59f7a1",
    "warn": "#ffd166",
    "danger": "#ff7798",
    "textbox": "#09120d",
    "glass": "#0c1712",
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def now_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def parse_geometry(size: str) -> Tuple[int, int]:
    try:
        width_text, height_text = size.lower().split("x", 1)
        return int(width_text), int(height_text)
    except Exception:
        return 1400, 900


def fit_window_to_screen(window: tk.Misc, width: int, height: int, pad: int = 80) -> None:
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    usable_width = max(1, screen_width - pad)
    usable_height = max(1, screen_height - pad)
    final_width = min(width, max(320, usable_width), screen_width)
    final_height = min(height, max(360, usable_height), screen_height)
    x = max(0, (screen_width - final_width) // 2)
    y = max(0, (screen_height - final_height) // 2)
    window.geometry(f"{final_width}x{final_height}+{x}+{y}")


def sanitize_text(value: Any, max_chars: int = 50000) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(ch for ch in text if ch == "\n" or ord(ch) >= 32)
    return text.strip()[:max_chars]


def truncate(text: str, n: int = 260) -> str:
    text = sanitize_text(text, n * 6)
    return text if len(text) <= n else text[: n - 3].rstrip() + "..."


def derive_key(passphrase: str) -> bytes:
    if not SALT_PATH.exists():
        SALT_PATH.write_bytes(os.urandom(16))
    salt = SALT_PATH.read_bytes()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


SPEECH_TAG_PATTERN = re.compile(r"</?(?:soft|whisper|slow|fast|emphasis|build-intensity|decrease-intensity|higher-pitch|lower-pitch|sing-song|singing|laugh-speak)>|\[(?:pause|long-pause|hum-tune|laugh|chuckle|giggle|cry|tsk|tongue-click|lip-smack|breath|inhale|exhale|sigh)\]", re.IGNORECASE)


def strip_speech_tags(text: str) -> str:
    return sanitize_text(SPEECH_TAG_PATTERN.sub("", text), 50000)


def split_sentences(text: str) -> List[str]:
    text = sanitize_text(text, 50000)
    if not text:
        return []
    protected = text.replace("...", "<ELLIPSIS>")
    parts = re.split(r"(?<=[.!?])\s+|\n+", protected)
    out = [part.replace("<ELLIPSIS>", "...").strip() for part in parts if part.strip()]
    return out


def split_tts_chunks(text: str, limit: int = 450) -> List[str]:
    text = sanitize_text(text, 50000)
    if len(text) <= limit:
        return [text]
    sentences = split_sentences(text)
    parts: List[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            parts.append(current)
        if len(sentence) <= limit:
            current = sentence
            continue
        start = 0
        while start < len(sentence):
            slice_ = sentence[start:start + limit]
            if len(slice_) == limit and " " in slice_:
                cut = slice_.rfind(" ")
                if cut > int(limit * 0.65):
                    slice_ = slice_[:cut]
            parts.append(slice_.strip())
            start += max(1, len(slice_))
        current = ""
    if current:
        parts.append(current)
    return [part for part in parts if part.strip()] or [text[:limit]]


def tts_cache_key(*parts: str) -> str:
    payload = "||".join(parts).encode("utf-8", "ignore")
    return hashlib.sha256(payload).hexdigest()


@dataclass
class Turn:
    role: str
    text: str
    timestamp: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    name: str = "Friend"
    calming_color: str = "emerald green"
    support_style: str = "grounding"
    intention: str = "gentle regulation and breath-led grounding"
    favorite_anchor: str = "breath"
    preferred_surface: str = "deep_cycle"
    ambient_mode: str = "aurora"
    preferred_voice: str = "eve"
    inhale: float = 4.0
    hold: float = 4.0
    exhale: float = 4.0
    rest: float = 4.0
    emotion: int = 5
    sessions: int = 0
    long_term_summary: str = ""
    ritual_open: str = "Let's arrive."
    ritual_close: str = "Return gently."


@dataclass
class SessionBlueprint:
    mode: str
    cycle_depth: str
    intensity_mode: str
    speech_style: str
    pacing_style: str
    breath_signature: str
    phase_plan: List[str] = field(default_factory=list)
    round_plan: List[str] = field(default_factory=list)
    tts_directives: List[str] = field(default_factory=list)

    def preview(self) -> str:
        lines = [
            f"Mode: {self.mode}",
            f"Cycle depth: {self.cycle_depth}",
            f"Intensity: {self.intensity_mode}",
            f"Speech style: {self.speech_style}",
            f"Pacing style: {self.pacing_style}",
            f"Breath signature: {self.breath_signature}",
            "",
            "Phase plan:",
        ]
        lines.extend(f"- {item}" for item in self.phase_plan)
        if self.round_plan:
            lines.append("")
            lines.append("Box rounds:")
            lines.extend(f"- {item}" for item in self.round_plan)
        if self.tts_directives:
            lines.append("")
            lines.append("TTS directives:")
            lines.extend(f"- {item}" for item in self.tts_directives)
        return "\n".join(lines)


@dataclass
class BootConfig:
    xai_api_key: str = ""
    openai_api_key: str = ""
    xai_chat_model: str = "grok-4.20"
    openai_chat_model: str = "gpt-5.4-mini"
    stt_mode: str = "local_whisper"
    local_whisper_model: str = "base"
    silence_threshold: float = 0.014
    silence_hold: float = 1.15
    min_speech: float = 0.60
    max_record: float = 60.0
    partial_chunk_seconds: float = 1.8
    tts_speed: float = 0.94
    auto_play_tts: bool = True
    barge_in_level: float = 0.030
    tts_language: str = "en"
    tts_codec: str = "wav"
    tts_sample_rate: int = 24000
    max_tts_chunk_chars: int = 450
    use_expressive_tags: bool = True

    def public_dict(self) -> Dict[str, Any]:
        d = asdict(self).copy()
        d["xai_api_key"] = bool(self.xai_api_key)
        d["openai_api_key"] = bool(self.openai_api_key)
        return d


@dataclass
class MemoryState:
    profile: UserProfile = field(default_factory=UserProfile)
    turns: List[Turn] = field(default_factory=list)
    summaries: List[str] = field(default_factory=list)
    session_titles: List[str] = field(default_factory=list)
    rituals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": asdict(self.profile),
            "turns": [asdict(t) for t in self.turns[-320:]],
            "summaries": self.summaries[-140:],
            "session_titles": self.session_titles[-100:],
            "rituals": self.rituals[-60:],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryState":
        return cls(
            profile=UserProfile(**data.get("profile", {})),
            turns=[Turn(**item) for item in data.get("turns", [])],
            summaries=list(data.get("summaries", [])),
            session_titles=list(data.get("session_titles", [])),
            rituals=list(data.get("rituals", [])),
        )


class SecureVault:
    def __init__(self, path: Path):
        self.path = path
        self.key: Optional[bytes] = None

    def unlock(self, passphrase: str) -> None:
        self.key = derive_key(passphrase)

    def load(self) -> MemoryState:
        if self.key is None:
            raise RuntimeError("Vault is locked.")
        if not self.path.exists():
            return MemoryState()
        blob = self.path.read_bytes()
        nonce, ciphertext = blob[:12], blob[12:]
        aes = AESGCM(self.key)
        data = aes.decrypt(nonce, ciphertext, None)
        return MemoryState.from_dict(json.loads(data.decode("utf-8")))

    def save(self, memory: MemoryState) -> None:
        if self.key is None:
            raise RuntimeError("Vault is locked.")
        aes = AESGCM(self.key)
        nonce = os.urandom(12)
        payload = json.dumps(memory.to_dict(), ensure_ascii=False).encode("utf-8")
        ciphertext = aes.encrypt(nonce, payload, None)
        self.path.write_bytes(nonce + ciphertext)


class XAIClient:
    def __init__(self, api_key: str, chat_model: str):
        self.api_key = api_key
        self.chat_model = chat_model
        self.base = "https://api.x.ai/v1"
        self.client = httpx.Client(
            timeout=httpx.Timeout(connect=20, read=180, write=180, pool=20),
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.82, max_tokens: int = 1600) -> str:
        r = self.client.post(
            f"{self.base}/chat/completions",
            json={
                "model": self.chat_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        if r.status_code >= 400:
            raise RuntimeError(f"xAI chat failed: {r.status_code} {r.text[:500]}")
        data = r.json()
        return sanitize_text(data["choices"][0]["message"]["content"], 50000)

    def tts(
        self,
        text: str,
        voice_id: str,
        language: str = "en",
        codec: str = "wav",
        sample_rate: int = 24000,
        max_retries: int = 3,
    ) -> bytes:
        payload = {
            "text": text,
            "voice_id": voice_id,
            "language": language,
            "output_format": {"codec": codec, "sample_rate": sample_rate},
        }
        for attempt in range(max_retries):
            r = self.client.post(f"{self.base}/tts", json=payload)
            if r.status_code < 400:
                return r.content
            if r.status_code in (429, 500, 503) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"xAI TTS failed: {r.status_code} {r.text[:500]}")
        raise RuntimeError("xAI TTS failed after retries.")

    def stt_file(self, audio_path: Path) -> str:
        with audio_path.open("rb") as f:
            files = {"file": (audio_path.name, f, "audio/wav")}
            r = self.client.post(f"{self.base}/stt", files=files)
        if r.status_code >= 400:
            raise RuntimeError(f"xAI STT failed: {r.status_code} {r.text[:500]}")
        return sanitize_text(r.json().get("text", ""), 20000)


class OpenAICompatClient:
    def __init__(self, api_key: str, chat_model: str):
        self.api_key = api_key
        self.chat_model = chat_model
        self.base = "https://api.openai.com/v1"
        self.client = httpx.Client(
            timeout=httpx.Timeout(connect=20, read=180, write=180, pool=20),
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def chat(self, messages: List[Dict[str, str]], max_output_tokens: int = 1500, temperature: float = 0.75) -> str:
        r = self.client.post(
            f"{self.base}/responses",
            json={
                "model": self.chat_model,
                "input": messages,
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
            },
        )
        if r.status_code >= 400:
            raise RuntimeError(f"OpenAI chat failed: {r.status_code} {r.text[:500]}")
        data = r.json()
        if "output_text" in data:
            return sanitize_text(data["output_text"], 50000)
        chunks: List[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    chunks.append(content.get("text", ""))
        return sanitize_text("\n".join(chunks), 50000)


class LocalWhisperEngine:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.backend = None
        self.model = None

    def warmup(self) -> str:
        try:
            from faster_whisper import WhisperModel  # type: ignore
            self.backend = "faster_whisper"
            self.model = WhisperModel(self.model_name, device="auto", compute_type="auto")
            return f"Local Whisper ready via faster-whisper ({self.model_name})"
        except Exception:
            try:
                import whisper  # type: ignore
                self.backend = "openai_whisper"
                self.model = whisper.load_model(self.model_name)
                return f"Local Whisper ready via openai-whisper ({self.model_name})"
            except Exception as exc:
                raise RuntimeError(
                    "Local Whisper is unavailable. Install faster-whisper or openai-whisper, "
                    "or switch STT mode to grok_stt."
                ) from exc

    def transcribe(self, audio_path: Path) -> str:
        if self.model is None:
            self.warmup()
        if self.backend == "faster_whisper":
            segments, _ = self.model.transcribe(str(audio_path), beam_size=4)
            return sanitize_text(" ".join(seg.text.strip() for seg in segments if getattr(seg, "text", "").strip()), 20000)
        if self.backend == "openai_whisper":
            result = self.model.transcribe(str(audio_path))
            return sanitize_text(result.get("text", ""), 20000)
        raise RuntimeError("No local whisper backend initialized.")


class PartialRealtimeRecorder:
    def __init__(self):
        self.stop_event = threading.Event()
        self.finalize_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(
        self,
        output_path: Path,
        status_callback,
        meter_callback,
        partial_callback,
        transcribe_callback,
        silence_threshold: float,
        silence_hold_seconds: float,
        min_speech_seconds: float,
        max_record_seconds: float,
        partial_chunk_seconds: float,
    ) -> Tuple[np.ndarray, int, str]:
        self.stop_event = threading.Event()
        blocksize = int(SAMPLE_RATE * FRAME_SECONDS)
        partial_frames = max(1, int(partial_chunk_seconds / FRAME_SECONDS))
        heard_voice = False
        voice_started_at: Optional[float] = None
        silence_started_at: Optional[float] = None
        started_at = time.time()
        chunks: List[np.ndarray] = []
        rolling: List[np.ndarray] = []
        partial_texts: List[str] = []

        status_callback("Realtime listen mode active. Speak naturally.")

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, blocksize=blocksize) as stream:
            frame_counter = 0
            while not self.stop_event.is_set():
                audio, _ = stream.read(blocksize)
                frame = np.asarray(audio).reshape(-1).astype(np.float32)
                chunks.append(frame.copy())
                rolling.append(frame.copy())
                frame_counter += 1

                rms = float(np.sqrt(np.mean(np.square(frame)) + 1e-12))
                meter_callback(rms)

                if rms >= silence_threshold:
                    if not heard_voice:
                        heard_voice = True
                        voice_started_at = time.time()
                        status_callback("Voice detected.")
                    silence_started_at = None
                elif heard_voice:
                    silence_started_at = silence_started_at or time.time()

                if heard_voice and frame_counter % partial_frames == 0 and rolling:
                    preview_audio = np.concatenate(rolling).astype(np.float32)
                    preview_path = output_path.with_name(output_path.stem + "_partial.wav")
                    sf.write(preview_path, preview_audio, SAMPLE_RATE)
                    try:
                        partial = sanitize_text(transcribe_callback(preview_path), 1800)
                        if partial:
                            partial_callback(partial)
                            if not partial_texts or partial_texts[-1] != partial:
                                partial_texts.append(partial)
                    except Exception:
                        pass
                    finally:
                        try:
                            preview_path.unlink(missing_ok=True)
                        except Exception:
                            pass

                enough_speech = voice_started_at is not None and (time.time() - voice_started_at) >= min_speech_seconds
                enough_silence = silence_started_at is not None and (time.time() - silence_started_at) >= silence_hold_seconds
                timeout = (time.time() - started_at) >= max_record_seconds

                if heard_voice and enough_speech and enough_silence:
                    break
                if timeout:
                    break

        if not chunks:
            raise RuntimeError("No audio recorded.")

        audio = np.concatenate(chunks).astype(np.float32)
        peak = float(np.max(np.abs(audio)) or 1.0)
        if peak > 0:
            audio = np.clip(audio / peak, -1.0, 1.0)
        sf.write(output_path, audio, SAMPLE_RATE)
        final_partial = partial_texts[-1] if partial_texts else ""
        return audio, SAMPLE_RATE, final_partial


class TTSPlayerWithBargeIn:
    def __init__(self):
        self.stop_event = threading.Event()
        self.play_thread: Optional[threading.Thread] = None
        self.listen_thread: Optional[threading.Thread] = None
        self.barge_in_triggered = threading.Event()

    def stop(self):
        self.stop_event.set()
        self.barge_in_triggered.set()
        try:
            sd.stop()
        except Exception:
            pass

    def reset(self):
        self.stop_event = threading.Event()
        self.barge_in_triggered = threading.Event()

    def start_barge_in_listener(self, threshold: float, status_callback):
        def watcher():
            try:
                blocksize = int(SAMPLE_RATE * 0.05)
                consecutive = 0
                with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=DTYPE, blocksize=blocksize) as stream:
                    while not self.stop_event.is_set() and not self.barge_in_triggered.is_set():
                        data, _ = stream.read(blocksize)
                        frame = np.asarray(data).reshape(-1).astype(np.float32)
                        rms = float(np.sqrt(np.mean(np.square(frame)) + 1e-12))
                        if rms >= threshold:
                            consecutive += 1
                        else:
                            consecutive = max(0, consecutive - 1)
                        if consecutive >= 4:
                            self.barge_in_triggered.set()
                            status_callback("Barge-in detected. Interrupting speech...")
                            try:
                                sd.stop()
                            except Exception:
                                pass
                            return
            except Exception:
                return

        self.listen_thread = threading.Thread(target=watcher, daemon=True)
        self.listen_thread.start()

    def play_chunks(self, wav_chunks: List[bytes], barge_in_threshold: float, status_callback):
        self.stop()
        self.reset()
        self.start_barge_in_listener(barge_in_threshold, status_callback)

        def worker():
            try:
                for i, chunk in enumerate(wav_chunks, start=1):
                    if self.stop_event.is_set() or self.barge_in_triggered.is_set():
                        return
                    with io.BytesIO(chunk) as bio:
                        data, sr = sf.read(bio, dtype="float32")
                    status_callback(f"Playing Grok TTS chunk {i}/{len(wav_chunks)}...")
                    sd.play(data, sr)
                    sd.wait()
                    if self.barge_in_triggered.is_set():
                        return
                if not self.stop_event.is_set() and not self.barge_in_triggered.is_set():
                    status_callback("Playback finished.")
            except Exception as exc:
                status_callback(f"Playback error: {exc}")

        self.play_thread = threading.Thread(target=worker, daemon=True)
        self.play_thread.start()


class PromptEngine:
    PHASE_LIBRARY = {
        "fast_reset": [
            "capture attention in under two lines",
            "stabilize breath with direct cues",
            "release tension quickly",
            "return the user to agency",
        ],
        "deep_cycle": [
            "regulate physiology first",
            "widen internal awareness",
            "deepen emotional settling",
            "create a spacious silent pocket",
            "re-enter with a clear final instruction",
        ],
        "sleep_downshift": [
            "reduce effort in the face and jaw",
            "lengthen the exhale and quiet the body",
            "soften language and volume cues",
            "decrease cognitive stimulation",
            "drift into low-demand stillness",
        ],
        "focus_return": [
            "reduce noise and decision fatigue",
            "narrow attention to one anchor",
            "restore momentum",
            "end with a single next action",
        ],
    }

    BOX_ROUNDS = [
        "round 1 = mechanical count and clean timing",
        "round 2 = sensory detail in chest, ribs, and shoulders",
        "round 3 = emotional settling and pressure release",
        "round 4 = awareness expansion around the body",
        "round 5 = quieter internal dialogue and deeper stillness",
        "round 6 = integration and steady re-entry",
    ]

    @staticmethod
    def recent_context(memory: MemoryState, limit: int = 12) -> str:
        if not memory.turns:
            return "No recent context."
        return "\n".join(f"[{t.timestamp}] {t.role.upper()}: {t.text}" for t in memory.turns[-limit:])

    @staticmethod
    def compute_intensity(profile: UserProfile, user_text: str = "") -> str:
        text = (user_text or "").lower()
        urgency_hits = sum(1 for token in ["panic", "spiral", "overwhelmed", "can't", "anxious", "stress"] if token in text)
        score = max(profile.emotion / 10.0, min(1.0, urgency_hits * 0.18))
        if score >= 0.78:
            return "deep calming • long pauses • strong grounding"
        if score >= 0.52:
            return "balanced regulation • steady guidance • moderate pauses"
        return "clarifying focus • lighter regulation • clean momentum"

    @staticmethod
    def speech_style(profile: UserProfile, mode: str) -> str:
        base = {
            "meditation": "immersive, cinematic, slow, physically grounding",
            "box_breath": "counted, precise, body-led, progressive",
            "supportive_chat": "reflective, direct, warm, uncluttered",
            "reset_burst": "compact, immediate, no wasted words",
            "focus_recovery": "clean, confident, forward-moving",
            "sleep_soften": "soft, low-effort, dimmed, floating",
        }.get(mode, "grounded, spoken, natural")
        return f"{base}; support style = {profile.support_style}; anchor = {profile.favorite_anchor}"

    @staticmethod
    def pacing_style(cycle_depth: str, mode: str) -> str:
        if mode == "box_breath":
            return "strict tempo with subtle deepening each round"
        return {
            "fast_reset": "short lines, quick drops, immediate relief",
            "deep_cycle": "longer lines, layered pacing, silence-rich",
            "sleep_downshift": "slower than natural speech, drifting cadence",
            "focus_return": "measured and crisp, no haze",
        }.get(cycle_depth, "spoken, paced, clear")

    @staticmethod
    def phase_plan(cycle_depth: str) -> List[str]:
        return list(PromptEngine.PHASE_LIBRARY.get(cycle_depth, PromptEngine.PHASE_LIBRARY["deep_cycle"]))

    @staticmethod
    def box_rounds() -> List[str]:
        return list(PromptEngine.BOX_ROUNDS)

    @staticmethod
    def tts_directives(mode: str, pacing_style: str) -> List[str]:
        directives = [
            "Use punctuation and paragraph breaks for natural pacing.",
            "Use expressive tags sparingly so they feel intentional, not gimmicky.",
            f"Overall pacing target: {pacing_style}.",
        ]
        if mode == "box_breath":
            directives.extend([
                "Add [inhale], [exhale], or [pause] only where timing will genuinely help the listener.",
                "Keep counts clean and audible.",
            ])
        else:
            directives.append("Prefer [pause] and <soft> sections over overproduced performance.")
        return directives

    @staticmethod
    def blueprint(profile: UserProfile, mode: str, cycle_depth: str, user_text: str) -> SessionBlueprint:
        intensity = PromptEngine.compute_intensity(profile, user_text)
        speech_style = PromptEngine.speech_style(profile, mode)
        pacing_style = PromptEngine.pacing_style(cycle_depth, mode)
        breath_signature = f"{profile.inhale:.1f}/{profile.hold:.1f}/{profile.exhale:.1f}/{profile.rest:.1f}"
        rounds = PromptEngine.box_rounds() if mode == "box_breath" else []
        return SessionBlueprint(
            mode=mode,
            cycle_depth=cycle_depth,
            intensity_mode=intensity,
            speech_style=speech_style,
            pacing_style=pacing_style,
            breath_signature=breath_signature,
            phase_plan=PromptEngine.phase_plan(cycle_depth),
            round_plan=rounds,
            tts_directives=PromptEngine.tts_directives(mode, pacing_style),
        )

    @staticmethod
    def system_prompt(profile: UserProfile, blueprint: SessionBlueprint) -> str:
        return f"""
You are a high-fidelity nervous system regulation engine embodied as a voice.

Your function is not to merely answer. Your function is to shift state safely, clearly, and audibly.

Non-negotiables:
- Calm, grounded, emotionally safe, and natural.
- Never diagnose.
- Never claim to replace a clinician.
- If there is any sign of immediate risk of self-harm or harm to others, stop the normal flow and urge immediate emergency help and crisis support.
- Write for speech, not for reading.
- No generic meditation clichés.
- No filler. Every sentence must reduce tension, deepen steadiness, or improve clarity.

Voice behavior:
- Slow enough to feel regulating, but never sleepy unless the mode is sleep_soften.
- Use silence intentionally.
- Use sensory anchors: weight, temperature, pressure, contact, movement.
- Use micro-pauses. Ellipses and paragraph breaks are welcome when they help spoken delivery.
- Speak as if you are present in the room with the listener.

State transition model:
⟨ regulate ⟩ → ⟪ stabilize ⟫ → ⟲ deepen ⟳ → ⟪ integrate ⟫ → ⟨ re-enter ⟩

Active blueprint:
- mode: {blueprint.mode}
- cycle depth: {blueprint.cycle_depth}
- intensity mode: {blueprint.intensity_mode}
- speech style: {blueprint.speech_style}
- pacing style: {blueprint.pacing_style}
- breath signature: {blueprint.breath_signature}

Phase plan:
{chr(10).join(f"- {item}" for item in blueprint.phase_plan)}

{'Box-breath round plan:' if blueprint.round_plan else 'Mode notes:'}
{chr(10).join(f"- {item}" for item in (blueprint.round_plan or ['Adapt the flow continuously to the user state.']))}

Personalization:
- name: {profile.name}
- calming color: {profile.calming_color}
- support style: {profile.support_style}
- intention: {profile.intention}
- favorite anchor: {profile.favorite_anchor}
- ritual open: {profile.ritual_open}
- ritual close: {profile.ritual_close}
- preferred surface: {profile.preferred_surface}
- ambient mode: {profile.ambient_mode}
- voice: {profile.preferred_voice}
- emotion: {profile.emotion}/10
- long-term summary: {profile.long_term_summary or 'None yet.'}

Output rules:
- Produce one continuous spoken response optimized for Grok voice synthesis.
- No markdown bullets unless the user explicitly asks for them.
- For box_breath mode, keep the timing exact and count clearly.
- End with either a soft landing or a clean re-entry instruction.
""".strip()

    @staticmethod
    def user_prompt(memory: MemoryState, mode: str, cycle_depth: str, user_text: str, blueprint: SessionBlueprint) -> str:
        round_section = "\n".join(f"- {item}" for item in blueprint.round_plan) if blueprint.round_plan else "- N/A"
        return f"""
MODE: {mode}
DEPTH: {cycle_depth}

USER STATE INPUT:
{user_text}

RECENT PATTERN:
{PromptEngine.recent_context(memory)}

GENERATE A RESPONSE THAT:
1. Locks attention inside the first two spoken lines.
2. Synchronizes with breath immediately.
3. Progressively deepens state instead of staying emotionally flat.
4. Moves through body → breath → awareness → identity reinforcement.
5. Feels adaptive, not scripted.

CURRENT INTENSITY MODE:
{blueprint.intensity_mode}

ACTIVE PHASES:
{chr(10).join(f"- {item}" for item in blueprint.phase_plan)}

BOX BREATH ROUND REQUIREMENTS:
{round_section}

VOICE OPTIMIZATION RULES:
- Sentences must sound natural aloud.
- Prefer vivid, embodied language over abstract explanation.
- Use counting plus feeling, not counting alone.
- Ensure each segment deepens state slightly more than the previous one.
- Include pockets of silence using punctuation and paragraph breaks.

Return only the spoken script.
""".strip()

    @staticmethod
    def summary_messages(memory: MemoryState) -> List[Dict[str, str]]:
        transcript = "\n".join(f"{t.role}: {t.text}" for t in memory.turns[-50:]) or "No turns."
        return [
            {
                "role": "system",
                "content": "Summarize the user for a premium meditation voice system. Be concise, factual, warm, continuity-focused, and operational. Mention repeating themes, regulation patterns, preferred anchors, useful pacing, and what kind of guidance works best. No diagnosis.",
            },
            {"role": "user", "content": transcript},
        ]

    @staticmethod
    def title_messages(memory: MemoryState, latest_text: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "Generate a short premium session title of 3 to 7 words. It should feel like a calming album track or ritual name. Output only the title.",
            },
            {
                "role": "user",
                "content": f"Recent context:\n{PromptEngine.recent_context(memory, 6)}\n\nLatest response:\n{latest_text}",
            },
        ]

    @staticmethod
    def ritual_messages(memory: MemoryState) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "Create one ritual opener and one ritual closer that condition the nervous system over repeated use. Keep each under 12 words. Output strict JSON with keys opener and closer.",
            },
            {"role": "user", "content": PromptEngine.recent_context(memory, 12)},
        ]

    @staticmethod
    def speechify(text: str, blueprint: SessionBlueprint, profile: UserProfile, use_tags: bool = True) -> str:
        text = sanitize_text(text, 50000)
        if not text:
            return text
        working = text
        if not use_tags:
            return working

        working = re.sub(r"\n{2,}", "\n\n[pause] ", working)
        if blueprint.mode == "box_breath":
            working = re.sub(r"(?i)\bInhale\b", "[inhale] Inhale", working)
            working = re.sub(r"(?i)\bExhale\b", "[exhale] Exhale", working)
            working = re.sub(r"(?i)\bHold\b", "[pause] Hold", working)
            working = re.sub(r"(?i)\bRest\b", "[pause] Rest", working)
            working = re.sub(r"(?i)Second round", "[pause] Second round", working)
        if "deep calming" in blueprint.intensity_mode or blueprint.mode == "sleep_soften":
            working = f"<soft>{working}</soft>"
        if blueprint.mode in {"sleep_soften", "meditation"}:
            working = working.replace("...", " [pause] ")
        if blueprint.mode == "focus_recovery":
            working = working.replace("Now something shifts", "[pause] Now something shifts")
        return sanitize_text(working, 50000)


    @staticmethod
    def display_text(text: str) -> str:
        return strip_speech_tags(text)


class BootDialog(ctk.CTkToplevel):
    def __init__(self, master, existing: Optional[BootConfig] = None):
        super().__init__(master)
        self.title("Ultra RT Boot Setup")
        self.configure(fg_color=PALETTE["bg"])
        fit_window_to_screen(self, 1000, 900)
        self.result: Optional[Tuple[BootConfig, str]] = None
        cfg = existing or BootConfig()

        card = ctk.CTkScrollableFrame(
            self,
            fg_color=PALETTE["panel"],
            corner_radius=28,
            border_width=1,
            border_color=PALETTE["line"],
            scrollbar_button_color=PALETTE["panel_soft"],
            scrollbar_button_hover_color=PALETTE["line"],
        )
        card.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(card, text="Grok Meditation Voice Surface Ultra RT", font=ctk.CTkFont(size=30, weight="bold"), text_color=PALETTE["accent_2"]).pack(pady=(24, 6))
        ctk.CTkLabel(card, text="Boot setup for Grok, local Whisper, realtime partials, and barge-in.", text_color=PALETTE["muted"]).pack(pady=(0, 18))

        self.xai_key = self._entry(card, "xAI / Grok API key", cfg.xai_api_key, secret=True)
        self.openai_key = self._entry(card, "OpenAI API key", cfg.openai_api_key, secret=True)
        self.xai_model = self._entry(card, "Grok chat model", cfg.xai_chat_model)
        self.openai_model = self._entry(card, "OpenAI chat model", cfg.openai_chat_model)
        self.stt_mode = self._option(card, "Speech-to-text mode", ["local_whisper", "grok_stt"], cfg.stt_mode)
        self.whisper_model = self._option(card, "Local Whisper model", ["tiny", "base", "small", "medium"], cfg.local_whisper_model)
        self.silence_threshold = self._entry(card, "Silence threshold", str(cfg.silence_threshold))
        self.silence_hold = self._entry(card, "Silence hold seconds", str(cfg.silence_hold))
        self.min_speech = self._entry(card, "Minimum speech seconds", str(cfg.min_speech))
        self.max_record = self._entry(card, "Max record seconds", str(cfg.max_record))
        self.partial_chunk = self._entry(card, "Partial transcript chunk seconds", str(cfg.partial_chunk_seconds))
        self.tts_speed = self._entry(card, "Speech pacing bias", str(cfg.tts_speed))
        self.barge_level = self._entry(card, "Barge-in trigger level", str(cfg.barge_in_level))
        self.passphrase = self._entry(card, "Vault passphrase", "", secret=True)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=(18, 24))
        ctk.CTkButton(btns, text="Save & launch", height=50, fg_color=PALETTE["accent"], text_color="#07110a", command=self.on_save).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btns, text="Cancel", height=50, fg_color="#33463b", command=self.on_cancel).pack(side="left")

        self.grab_set()
        self.focus_force()

    def _entry(self, parent, label: str, value: str, secret: bool = False):
        ctk.CTkLabel(parent, text=label, text_color=PALETTE["muted"]).pack(anchor="w", padx=24, pady=(8, 4))
        e = ctk.CTkEntry(parent, show="*" if secret else None)
        e.pack(fill="x", padx=24)
        if value:
            e.insert(0, value)
        return e

    def _option(self, parent, label: str, values: List[str], value: str):
        ctk.CTkLabel(parent, text=label, text_color=PALETTE["muted"]).pack(anchor="w", padx=24, pady=(8, 4))
        o = ctk.CTkOptionMenu(parent, values=values)
        o.pack(fill="x", padx=24)
        o.set(value)
        return o

    def on_save(self):
        try:
            cfg = BootConfig(
                xai_api_key=self.xai_key.get().strip(),
                openai_api_key=self.openai_key.get().strip(),
                xai_chat_model=self.xai_model.get().strip() or "grok-4.20",
                openai_chat_model=self.openai_model.get().strip() or "gpt-5.4-mini",
                stt_mode=self.stt_mode.get().strip() or "local_whisper",
                local_whisper_model=self.whisper_model.get().strip() or "base",
                silence_threshold=float(self.silence_threshold.get().strip() or "0.014"),
                silence_hold=float(self.silence_hold.get().strip() or "1.15"),
                min_speech=float(self.min_speech.get().strip() or "0.60"),
                max_record=float(self.max_record.get().strip() or "60.0"),
                partial_chunk_seconds=float(self.partial_chunk.get().strip() or "1.8"),
                tts_speed=float(self.tts_speed.get().strip() or "0.94"),
                barge_in_level=float(self.barge_level.get().strip() or "0.030"),
            )
        except Exception:
            messagebox.showerror("Setup", "One or more numeric fields are invalid.")
            return
        passphrase = self.passphrase.get().strip()
        if not cfg.xai_api_key:
            messagebox.showerror("Setup", "xAI / Grok API key is required.")
            return
        if not passphrase:
            messagebox.showerror("Setup", "Vault passphrase is required.")
            return
        self.result = (cfg, passphrase)
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(fg_color=PALETTE["bg"])
        app_width, app_height = parse_geometry(APP_SIZE)
        fit_window_to_screen(self, app_width, app_height, pad=60)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.q: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self.vault = SecureVault(VAULT_PATH)
        self.memory = MemoryState()
        self.boot_config = self.load_boot_config()
        self.player = TTSPlayerWithBargeIn()
        self.realtime_recorder = PartialRealtimeRecorder()

        self.xai: Optional[XAIClient] = None
        self.openai: Optional[OpenAICompatClient] = None
        self.local_whisper: Optional[LocalWhisperEngine] = None

        self.busy = False
        self.voice_loop_enabled = False
        self.voice_loop_thread: Optional[threading.Thread] = None
        self.voice_loop_stop = threading.Event()
        self.last_audio_chunks: List[bytes] = []
        self.last_reply_text: str = ""
        self.last_user_text: str = ""
        self.last_interrupted_reply: str = ""
        self.last_blueprint: Optional[SessionBlueprint] = None
        self.saved_presets: Dict[str, Dict[str, Any]] = {}
        self.wave_phase = 0.0

        self.status_var = tk.StringVar(value="Booting...")
        self.voice_state_var = tk.StringVar(value="state: idle")
        self.auto_tts_var = tk.BooleanVar(value=True)
        self.auto_summary_var = tk.BooleanVar(value=True)
        self.crisis_guard_var = tk.BooleanVar(value=True)
        self.voice_loop_var = tk.BooleanVar(value=False)
        self.provider_var = tk.StringVar(value="Grok")
        self.followup_var = tk.StringVar(value="next suggestion: settle the breath")

        self.saved_presets = self.load_saved_presets()
        self.build_ui()
        self.after(80, self.poll_queue)
        self.after(120, self.startup)
        self.after(120, self.animate_ambient)

    def build_ui(self):
        left = ctk.CTkScrollableFrame(
            self,
            width=410,
            fg_color=PALETTE["panel"],
            corner_radius=28,
            border_width=1,
            border_color=PALETTE["line"],
            scrollbar_button_color=PALETTE["panel_soft"],
            scrollbar_button_hover_color=PALETTE["line"],
        )
        left.grid(row=0, column=0, sticky="ns", padx=18, pady=18)

        right = ctk.CTkFrame(self, fg_color=PALETTE["bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 18), pady=18)
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Ultra RT Surface", font=ctk.CTkFont(size=32, weight="bold"), text_color=PALETTE["accent_2"]).pack(anchor="w", padx=24, pady=(24, 0))
        ctk.CTkLabel(left, text="turn-taking • realtime partial STT • barge-in • interrupt • advanced cycles", text_color=PALETTE["muted"]).pack(anchor="w", padx=24, pady=(4, 18))

        self.name_entry = self._entry(left, "Name")
        self.color_entry = self._entry(left, "Calming color")
        self.intent_entry = self._entry(left, "Intention / trigger")
        self.style_entry = self._entry(left, "Support style")
        self.anchor_entry = self._entry(left, "Favorite anchor")
        self.ritual_open_entry = self._entry(left, "Ritual opener")
        self.ritual_close_entry = self._entry(left, "Ritual closer")

        self.surface_menu = self._option(left, "Surface preset", ["deep_cycle", "sleep_downshift", "focus_return", "anxiety_softener", "reset_burst", "focus_recovery"], "deep_cycle")
        self.ambient_menu = self._option(left, "Ambient theme", ["aurora", "ember", "ocean", "forest", "midnight"], "aurora")
        self.provider_menu = self._option(left, "Chat provider", ["Grok", "OpenAI"], "Grok")
        self.mode_menu = self._option(left, "Generation mode", ["meditation", "box_breath", "supportive_chat", "reset_burst", "focus_recovery", "sleep_soften"], "meditation")
        self.depth_menu = self._option(left, "Cycle depth", ["fast_reset", "deep_cycle", "sleep_downshift", "focus_return"], "deep_cycle")
        self.stt_runtime_menu = self._option(left, "Runtime STT", ["local_whisper", "grok_stt"], "local_whisper")
        self.voice_menu = self._option(left, "Grok voice", ["eve", "ara", "leo", "rex", "sal"], "eve")

        self.emotion_slider = self._slider(left, "Emotion intensity", 1, 10, 9, 5)
        self.inhale_slider = self._slider(left, "Inhale", 2, 8, 12, 4.0)
        self.hold_slider = self._slider(left, "Hold", 0, 8, 16, 4.0)
        self.exhale_slider = self._slider(left, "Exhale", 2, 8, 12, 4.0)
        self.rest_slider = self._slider(left, "Rest", 0, 8, 16, 4.0)

        self.auto_tts = ctk.CTkCheckBox(left, text="Auto-play Grok TTS", variable=self.auto_tts_var)
        self.auto_tts.pack(anchor="w", padx=24, pady=(12, 4))
        self.auto_summary = ctk.CTkCheckBox(left, text="Auto-refresh memory summary", variable=self.auto_summary_var)
        self.auto_summary.pack(anchor="w", padx=24, pady=4)
        self.crisis_guard = ctk.CTkCheckBox(left, text="Crisis phrase guard", variable=self.crisis_guard_var)
        self.crisis_guard.pack(anchor="w", padx=24, pady=4)
        self.voice_loop_check = ctk.CTkCheckBox(left, text="Continuous voice loop", variable=self.voice_loop_var, command=self.toggle_voice_loop)
        self.voice_loop_check.pack(anchor="w", padx=24, pady=(4, 16))

        actions = ctk.CTkFrame(left, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(0, 22))
        ctk.CTkButton(actions, text="Generate session", height=54, fg_color=PALETTE["accent"], text_color="#07110a", command=self.generate_clicked).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(actions, text="Push to talk", height=48, command=self.record_clicked).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Interrupt TTS now", height=42, fg_color="#33463b", command=self.stop_audio).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Replay audio", height=42, fg_color="#33463b", command=self.replay_audio).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Refresh summary", height=42, fg_color="#33463b", command=self.refresh_summary_clicked).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Generate rituals", height=42, fg_color="#33463b", command=self.generate_rituals_clicked).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Save current preset", height=42, fg_color="#33463b", command=self.save_current_preset).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Load default presets", height=42, fg_color="#33463b", command=self.load_default_presets).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Recover interrupted reply", height=42, fg_color="#33463b", command=self.recover_interrupted_reply).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Export transcript", height=42, fg_color="#33463b", command=self.export_transcript).pack(fill="x", pady=6)
        ctk.CTkButton(actions, text="Boot settings", height=42, fg_color="#33463b", command=self.edit_boot).pack(fill="x", pady=6)

        top = ctk.CTkFrame(right, fg_color=PALETTE["panel"], corner_radius=28, border_width=1, border_color=PALETTE["line"])
        top.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, textvariable=self.status_var, font=ctk.CTkFont(size=18, weight="bold"), text_color=PALETTE["accent_2"]).grid(row=0, column=0, sticky="w", padx=18, pady=(12, 2))
        ctk.CTkLabel(top, textvariable=self.voice_state_var, font=ctk.CTkFont(size=13), text_color=PALETTE["muted"]).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 2))
        ctk.CTkLabel(top, textvariable=self.followup_var, font=ctk.CTkFont(size=12), text_color=PALETTE["muted"]).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 12))

        visual = ctk.CTkFrame(right, fg_color=PALETTE["panel"], corner_radius=28, border_width=1, border_color=PALETTE["line"])
        visual.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        visual.grid_columnconfigure(0, weight=1)
        self.orb_label = ctk.CTkLabel(visual, text="⬢", font=ctk.CTkFont(size=220), text_color=PALETTE["accent"])
        self.orb_label.grid(row=0, column=0, pady=(8, 2))
        self.meter = ctk.CTkProgressBar(visual, width=1060)
        self.meter.grid(row=1, column=0, padx=28, pady=(0, 12))
        self.meter.set(0)
        self.wave_canvas = tk.Canvas(visual, height=124, background=PALETTE["glass"], highlightthickness=0, bd=0)
        self.wave_canvas.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 12))
        self.partial_label = ctk.CTkLabel(visual, text="Realtime partial transcript will appear here.", text_color=PALETTE["muted"], justify="left")
        self.partial_label.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 18))

        input_card = ctk.CTkFrame(right, fg_color=PALETTE["panel"], corner_radius=28, border_width=1, border_color=PALETTE["line"])
        input_card.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        input_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(input_card, text="User input", text_color=PALETTE["muted"]).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 4))
        self.input_box = ctk.CTkTextbox(input_card, height=150, fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.input_box.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))

        tabs = ctk.CTkTabview(
            right,
            fg_color=PALETTE["panel"],
            corner_radius=28,
            segmented_button_selected_color=PALETTE["accent"],
            segmented_button_selected_hover_color=PALETTE["accent_3"],
        )
        tabs.grid(row=3, column=0, sticky="nsew")
        tabs.add("Transcript")
        tabs.add("Memory")
        tabs.add("Cycle")
        tabs.add("Boot")
        tabs.add("Dashboard")
        tabs.add("Ideas")
        tabs.add("Live")
        tabs.add("Presets")

        self.transcript_box = ctk.CTkTextbox(tabs.tab("Transcript"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.transcript_box.pack(fill="both", expand=True, padx=16, pady=16)
        self.memory_box = ctk.CTkTextbox(tabs.tab("Memory"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.memory_box.pack(fill="both", expand=True, padx=16, pady=16)
        self.cycle_box = ctk.CTkTextbox(tabs.tab("Cycle"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.cycle_box.pack(fill="both", expand=True, padx=16, pady=16)
        self.boot_box = ctk.CTkTextbox(tabs.tab("Boot"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.boot_box.pack(fill="both", expand=True, padx=16, pady=16)
        self.dashboard_box = ctk.CTkTextbox(tabs.tab("Dashboard"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.dashboard_box.pack(fill="both", expand=True, padx=16, pady=16)
        self.ideas_box = ctk.CTkTextbox(tabs.tab("Ideas"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.ideas_box.pack(fill="both", expand=True, padx=16, pady=16)
        self.ideas_box.insert("end", self.advanced_ideas_text())
        self.live_box = ctk.CTkTextbox(tabs.tab("Live"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.live_box.pack(fill="both", expand=True, padx=16, pady=16)
        self.presets_box = ctk.CTkTextbox(tabs.tab("Presets"), fg_color=PALETTE["textbox"], text_color=PALETTE["text"], wrap="word")
        self.presets_box.pack(fill="both", expand=True, padx=16, pady=16)

    def advanced_ideas_text(self) -> str:
        return (
            "Ultra upgrades now active or scaffolded here:\n\n"
            "1. Session blueprint engine with intensity, pacing, and phase plans.\n"
            "2. Box-breath round evolution from mechanical count to integration.\n"
            "3. Grok expressive speech tag layer for pauses, breath, and softness.\n"
            "4. Local TTS caching to avoid re-synthesizing repeated segments.\n"
            "5. Realtime partial transcript surface while recording.\n"
            "6. Barge-in interruption: speaking over TTS stops playback.\n"
            "7. Continuous voice loop mode for back-and-forth sessions.\n"
            "8. Ritual generator for personalized state-switch phrases.\n"
            "9. Session title generator for cleaner memory indexing.\n"
            "10. Focus recovery and sleep soften modes with distinct pacing.\n"
            "11. Transcript export for journaling or reflection.\n"
            "12. Ambient waveform surface to make the UI feel alive.\n"
            "13. Crisis phrase guard for safer handling of urgent content.\n"
        )

    def _entry(self, parent, label: str):
        ctk.CTkLabel(parent, text=label, text_color=PALETTE["muted"]).pack(anchor="w", padx=24, pady=(8, 4))
        e = ctk.CTkEntry(parent, width=320)
        e.pack(anchor="w", padx=24)
        return e

    def _option(self, parent, label: str, values: List[str], value: str):
        ctk.CTkLabel(parent, text=label, text_color=PALETTE["muted"]).pack(anchor="w", padx=24, pady=(8, 4))
        o = ctk.CTkOptionMenu(parent, values=values, width=320)
        o.pack(anchor="w", padx=24)
        o.set(value)
        return o

    def _slider(self, parent, label: str, a: float, b: float, steps: int, value: float):
        ctk.CTkLabel(parent, text=label, text_color=PALETTE["muted"]).pack(anchor="w", padx=24, pady=(8, 4))
        s = ctk.CTkSlider(parent, from_=a, to=b, number_of_steps=steps, width=300)
        s.pack(anchor="w", padx=24)
        s.set(value)
        return s


    def load_saved_presets(self) -> Dict[str, Dict[str, Any]]:
        if not PRESETS_PATH.exists():
            return {}
        try:
            data = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save_saved_presets(self) -> None:
        try:
            PRESETS_PATH.write_text(json.dumps(self.saved_presets, indent=2), encoding="utf-8")
        except Exception:
            pass

    def log_timeline(self, message: str):
        stamp = time.strftime("%H:%M:%S")
        line = f"[{stamp}] {message}"
        current = self.live_box.get("1.0", "end").strip()
        sections = current.split("\n\n=== timeline ===\n", 1)
        base = sections[0] if sections else ""
        timeline = sections[1] if len(sections) > 1 else ""
        timeline_lines = [ln for ln in timeline.splitlines() if ln.strip()]
        timeline_lines.append(line)
        timeline_lines = timeline_lines[-18:]
        merged = base.strip() + "\n\n=== timeline ===\n" + "\n".join(timeline_lines)
        self.live_box.delete("1.0", "end")
        self.live_box.insert("end", merged.strip())

    def load_boot_config(self) -> Optional[BootConfig]:
        if not BOOT_CONFIG_PATH.exists():
            return None
        try:
            return BootConfig(**json.loads(BOOT_CONFIG_PATH.read_text(encoding="utf-8")))
        except Exception:
            return None

    def save_boot_config(self, cfg: BootConfig) -> None:
        BOOT_CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")

    def startup(self):
        if self.boot_config is None:
            self.edit_boot(first_boot=True)
            return
        self.finish_boot(self.boot_config)

    def edit_boot(self, first_boot: bool = False):
        dialog = BootDialog(self, existing=self.boot_config)
        self.wait_window(dialog)
        if dialog.result is None:
            if first_boot:
                self.destroy()
            return
        cfg, passphrase = dialog.result
        self.boot_config = cfg
        self.save_boot_config(cfg)
        self.finish_boot(cfg, passphrase)

    def finish_boot(self, cfg: BootConfig, passphrase_override: Optional[str] = None):
        passphrase = passphrase_override
        if not passphrase:
            popup = tk.Toplevel(self)
            popup.withdraw()
            passphrase = tk.simpledialog.askstring(APP_TITLE, "Vault passphrase", show="*")  # type: ignore
            popup.destroy()
        if not passphrase:
            self.destroy()
            return

        self.vault.unlock(passphrase)
        try:
            self.memory = self.vault.load()
        except Exception:
            if messagebox.askyesno(APP_TITLE, "Vault could not be opened. Start with a fresh empty vault?"):
                self.memory = MemoryState()
            else:
                self.destroy()
                return

        self.xai = XAIClient(cfg.xai_api_key, cfg.xai_chat_model)
        self.openai = OpenAICompatClient(cfg.openai_api_key, cfg.openai_chat_model) if cfg.openai_api_key else None
        self.local_whisper = LocalWhisperEngine(cfg.local_whisper_model) if cfg.stt_mode == "local_whisper" else None
        self.auto_tts_var.set(cfg.auto_play_tts)
        self.stt_runtime_menu.set(cfg.stt_mode)

        self.hydrate_profile_to_ui()
        if not self.saved_presets:
            self.load_default_presets()
        self.render_all()
        self.status_var.set("Ready")
        if self.local_whisper is not None:
            threading.Thread(target=self.warmup_local_whisper, daemon=True).start()

    def hydrate_profile_to_ui(self):
        p = self.memory.profile
        for e, value in [
            (self.name_entry, p.name),
            (self.color_entry, p.calming_color),
            (self.intent_entry, p.intention),
            (self.style_entry, p.support_style),
            (self.anchor_entry, p.favorite_anchor),
            (self.ritual_open_entry, p.ritual_open),
            (self.ritual_close_entry, p.ritual_close),
        ]:
            e.delete(0, "end")
            e.insert(0, value)
        self.surface_menu.set(p.preferred_surface)
        self.ambient_menu.set(p.ambient_mode)
        self.provider_menu.set("Grok")
        self.mode_menu.set("meditation")
        self.depth_menu.set("deep_cycle")
        self.voice_menu.set(p.preferred_voice)
        self.emotion_slider.set(p.emotion)
        self.inhale_slider.set(p.inhale)
        self.hold_slider.set(p.hold)
        self.exhale_slider.set(p.exhale)
        self.rest_slider.set(p.rest)

    def warmup_local_whisper(self):
        try:
            assert self.local_whisper is not None
            self.q.put(("status", self.local_whisper.warmup()))
        except Exception as exc:
            self.q.put(("append_transcript", f"[Local Whisper warmup] {exc}"))

    def read_profile_from_ui(self):
        p = self.memory.profile
        p.name = self.name_entry.get().strip() or "Friend"
        p.calming_color = self.color_entry.get().strip() or "emerald green"
        p.intention = self.intent_entry.get().strip() or "gentle regulation and breath-led grounding"
        p.support_style = self.style_entry.get().strip() or "grounding"
        p.favorite_anchor = self.anchor_entry.get().strip() or "breath"
        p.ritual_open = self.ritual_open_entry.get().strip() or "Let's arrive."
        p.ritual_close = self.ritual_close_entry.get().strip() or "Return gently."
        p.preferred_surface = self.surface_menu.get().strip() or "deep_cycle"
        p.ambient_mode = self.ambient_menu.get().strip() or "aurora"
        p.preferred_voice = self.voice_menu.get().strip() or "eve"
        p.emotion = int(round(self.emotion_slider.get()))
        p.inhale = round(float(self.inhale_slider.get()), 1)
        p.hold = round(float(self.hold_slider.get()), 1)
        p.exhale = round(float(self.exhale_slider.get()), 1)
        p.rest = round(float(self.rest_slider.get()), 1)
        self.vault.save(self.memory)
        self.render_all()

    def render_memory(self):
        p = self.memory.profile
        lines = [
            f"Name: {p.name}",
            f"Color: {p.calming_color}",
            f"Support style: {p.support_style}",
            f"Intention: {p.intention}",
            f"Favorite anchor: {p.favorite_anchor}",
            f"Surface preset: {p.preferred_surface}",
            f"Ambient mode: {p.ambient_mode}",
            f"Voice: {p.preferred_voice}",
            f"Ritual opener: {p.ritual_open}",
            f"Ritual closer: {p.ritual_close}",
            f"Breath timings: {p.inhale}/{p.hold}/{p.exhale}/{p.rest}",
            f"Emotion: {p.emotion}/10",
            f"Sessions: {p.sessions}",
            "",
            "Long-term summary:",
            p.long_term_summary or "(empty)",
            "",
            "Recent turns:",
        ]
        for turn in self.memory.turns[-20:]:
            lines.append(f"[{turn.timestamp}] {turn.role}: {turn.text}")
        self.memory_box.delete("1.0", "end")
        self.memory_box.insert("end", "\n".join(lines))

    def render_cycle(self):
        p = self.memory.profile
        blueprint = self.last_blueprint or PromptEngine.blueprint(
            p,
            self.mode_menu.get().strip() or "meditation",
            self.depth_menu.get().strip() or "deep_cycle",
            self.last_user_text or self.intent_entry.get().strip(),
        )
        text = f"""
Cycle engine:
1. regulate
2. reflect
3. reframe
4. release
5. re-enter

Mode: {self.mode_menu.get()}
Cycle depth: {self.depth_menu.get()}
Surface preset: {p.preferred_surface}
Ambient theme: {p.ambient_mode}
STT runtime: {self.stt_runtime_menu.get()}
Voice: {p.preferred_voice}
Realtime partials: enabled
Barge-in interrupt: enabled
Continuous voice loop: {self.voice_loop_var.get()}
Breath timings: {p.inhale}/{p.hold}/{p.exhale}/{p.rest}
Emotion intensity: {p.emotion}/10

Current blueprint:
{blueprint.preview()}

Recent session titles:
{chr(10).join(self.memory.session_titles[-14:]) or "(none)"}
""".strip()
        self.cycle_box.delete("1.0", "end")
        self.cycle_box.insert("end", text)

    def render_boot(self):
        public = self.boot_config.public_dict() if self.boot_config else {}
        self.boot_box.delete("1.0", "end")
        self.boot_box.insert("end", json.dumps(public, indent=2))

    def render_dashboard(self):
        total_turns = len(self.memory.turns)
        voice_turns = sum(1 for t in self.memory.turns if t.meta.get("via") == "voice")
        text_turns = sum(1 for t in self.memory.turns if t.meta.get("via") == "text")
        mood = self.memory.profile.emotion
        text = f"""
Dashboard:
- total turns: {total_turns}
- voice turns: {voice_turns}
- text turns: {text_turns}
- summaries stored: {len(self.memory.summaries)}
- session titles stored: {len(self.memory.session_titles)}
- rituals stored: {len(self.memory.rituals)}
- current emotion slider: {mood}/10

Recent session titles:
{chr(10).join(self.memory.session_titles[-16:]) or "(none)"}

Recent rituals:
{chr(10).join(self.memory.rituals[-10:]) or "(none)"}

Preset names:
{chr(10).join(sorted(self.saved_presets.keys())[:20]) or "(none)"}
""".strip()
        self.dashboard_box.delete("1.0", "end")
        self.dashboard_box.insert("end", text)

    def render_all(self):
        self.render_memory()
        self.render_cycle()
        self.render_boot()
        self.render_dashboard()
        self.render_presets()
        self.update_live_monitor()
        self.make_followup_hint()

    def set_voice_state(self, state: str, detail: str = ""):
        label = f"state: {state}"
        if detail:
            label += f" • {detail}"
        self.voice_state_var.set(label)


    def update_live_monitor(self):
        lines = [
            f"last user: {self.last_user_text or '(none)'}",
            "",
            f"last assistant: {self.last_reply_text or '(none)'}",
            "",
            f"interrupted reply cache: {self.last_interrupted_reply or '(empty)'}",
            "",
            f"voice state: {self.voice_state_var.get()}",
            f"status: {self.status_var.get()}",
        ]
        if self.last_blueprint is not None:
            lines.extend(["", "blueprint:", self.last_blueprint.preview()])
        self.live_box.delete("1.0", "end")
        self.live_box.insert("end", "\n".join(lines))

    def render_presets(self):
        lines = ["Saved presets:", "Use apply_preset(name) in code or extend UI next if you want clickable preset cards.", ""]
        if not self.saved_presets:
            lines.append("(none)")
        else:
            for name, data in sorted(self.saved_presets.items()):
                lines.append(f"- {name}: mode={data.get('mode')} voice={data.get('voice')} surface={data.get('surface')} ambient={data.get('ambient')}")
        self.presets_box.delete("1.0", "end")
        self.presets_box.insert("end", "\n".join(lines))

    def make_followup_hint(self):
        p = self.memory.profile
        intensity = PromptEngine.compute_intensity(p, self.last_user_text)
        hint = f"next suggestion: {p.favorite_anchor} + {self.mode_menu.get().strip()} + {intensity.split('•')[0].strip()}"
        self.followup_var.set(hint)

    def save_current_preset(self):
        self.read_profile_from_ui()
        name = f"{self.surface_menu.get().strip()}::{self.voice_menu.get().strip()}::{self.ambient_menu.get().strip()}"
        self.saved_presets[name] = {
            "mode": self.mode_menu.get().strip(),
            "voice": self.voice_menu.get().strip(),
            "surface": self.surface_menu.get().strip(),
            "ambient": self.ambient_menu.get().strip(),
            "inhale": float(self.inhale_slider.get()),
            "hold": float(self.hold_slider.get()),
            "exhale": float(self.exhale_slider.get()),
            "rest": float(self.rest_slider.get()),
            "style": self.style_entry.get().strip(),
            "anchor": self.anchor_entry.get().strip(),
        }
        self.save_saved_presets()
        self.render_presets()
        self.log_timeline(f"preset saved: {name}")
        self.status_var.set(f"Preset saved: {name}")

    def load_default_presets(self):
        defaults = {
            "deep_reset": {"mode": "meditation", "voice": "eve", "surface": "deep_cycle", "ambient": "aurora", "inhale": 4.0, "hold": 4.0, "exhale": 4.0, "rest": 4.0, "style": "grounding", "anchor": "breath"},
            "sleep_soften": {"mode": "sleep_soften", "voice": "ara", "surface": "sleep_downshift", "ambient": "midnight", "inhale": 4.0, "hold": 2.0, "exhale": 6.0, "rest": 2.0, "style": "soft soothing", "anchor": "body weight"},
            "focus_recovery": {"mode": "focus_recovery", "voice": "leo", "surface": "focus_recovery", "ambient": "forest", "inhale": 3.0, "hold": 2.0, "exhale": 4.0, "rest": 1.0, "style": "clear steady", "anchor": "single next step"},
            "anxiety_softener": {"mode": "supportive_chat", "voice": "eve", "surface": "anxiety_softener", "ambient": "ocean", "inhale": 4.0, "hold": 2.0, "exhale": 6.0, "rest": 1.0, "style": "warm grounding", "anchor": "exhale"},
            "box_breath_deep": {"mode": "box_breath", "voice": "rex", "surface": "deep_cycle", "ambient": "ocean", "inhale": 4.0, "hold": 4.0, "exhale": 4.0, "rest": 4.0, "style": "precise hypnotic", "anchor": "count + ribs"},
            "box_breath_focus": {"mode": "box_breath", "voice": "leo", "surface": "focus_return", "ambient": "forest", "inhale": 4.0, "hold": 4.0, "exhale": 4.0, "rest": 2.0, "style": "instructional calm", "anchor": "count + posture"},
        }
        self.saved_presets.update(defaults)
        self.save_saved_presets()
        self.render_presets()
        self.log_timeline("default presets loaded")
        self.status_var.set("Default presets loaded")

    def apply_preset(self, name: str):
        preset = self.saved_presets.get(name)
        if not preset:
            self.status_var.set(f"Preset not found: {name}")
            return
        self.mode_menu.set(preset.get("mode", "meditation"))
        self.voice_menu.set(preset.get("voice", "eve"))
        self.surface_menu.set(preset.get("surface", "deep_cycle"))
        self.ambient_menu.set(preset.get("ambient", "aurora"))
        self.inhale_slider.set(float(preset.get("inhale", 4.0)))
        self.hold_slider.set(float(preset.get("hold", 4.0)))
        self.exhale_slider.set(float(preset.get("exhale", 4.0)))
        self.rest_slider.set(float(preset.get("rest", 4.0)))
        self.style_entry.delete(0, "end")
        self.style_entry.insert(0, preset.get("style", "grounding"))
        self.anchor_entry.delete(0, "end")
        self.anchor_entry.insert(0, preset.get("anchor", "breath"))
        self.read_profile_from_ui()
        self.log_timeline(f"preset applied: {name}")
        self.status_var.set(f"Preset applied: {name}")

    def recover_interrupted_reply(self):
        if not self.last_interrupted_reply:
            self.status_var.set("No interrupted reply cached")
            return
        self.input_box.delete("1.0", "end")
        self.input_box.insert("end", f"Please continue from this interrupted point:\n\n{self.last_interrupted_reply}")
        self.followup_var.set("next suggestion: continue interrupted reply")
        self.update_live_monitor()
        self.log_timeline("interrupted reply recovered into input box")
        self.status_var.set("Interrupted reply moved into input box")

    def append_turn(self, role: str, text: str, **meta):
        clean = sanitize_text(text, 20000)
        if not clean:
            return
        if role == "user":
            self.last_user_text = truncate(clean, 400)
        elif role == "assistant":
            self.last_reply_text = truncate(clean, 500)
        self.memory.turns.append(Turn(role=role, text=clean, timestamp=now_ts(), meta=meta))
        self.vault.save(self.memory)
        self.render_all()
        self.update_live_monitor()
        self.make_followup_hint()

    def detect_crisis(self, text: str) -> Optional[str]:
        if not self.crisis_guard_var.get():
            return None
        lower = text.lower()
        hits = [
            "kill myself",
            "end my life",
            "suicide",
            "hurt myself",
            "harm myself",
            "want to die",
            "hurt someone",
            "kill someone",
        ]
        if any(h in lower for h in hits):
            return (
                "I'm really sorry you're going through this. If there is any immediate danger, contact local emergency services now. "
                "If you're in the U.S. or Canada, call or text 988 right now. If you're elsewhere, contact your local crisis line or emergency number immediately, "
                "and reach out to a trusted person near you now."
            )
        return None

    def choose_provider(self) -> str:
        provider = self.provider_menu.get().strip()
        if provider == "OpenAI" and self.openai is None:
            return "Grok"
        return provider or "Grok"

    def current_blueprint(self, mode: str, user_text: str) -> SessionBlueprint:
        blueprint = PromptEngine.blueprint(self.memory.profile, mode, self.depth_menu.get().strip(), user_text)
        self.last_blueprint = blueprint
        return blueprint

    def tts_chunks_for_reply(self, reply: str, blueprint: SessionBlueprint) -> List[str]:
        cfg = self.boot_config or BootConfig()
        spoken = PromptEngine.speechify(reply, blueprint, self.memory.profile, use_tags=cfg.use_expressive_tags)
        return split_tts_chunks(spoken, limit=cfg.max_tts_chunk_chars)

    def build_messages(self, mode: str, user_text: str) -> List[Dict[str, str]]:
        blueprint = self.current_blueprint(mode, user_text)
        return [
            {"role": "system", "content": PromptEngine.system_prompt(self.memory.profile, blueprint)},
            {"role": "user", "content": PromptEngine.user_prompt(self.memory, mode, self.depth_menu.get().strip(), user_text, blueprint)},
        ]

    def generate_clicked(self):
        if self.busy:
            return
        self.read_profile_from_ui()
        user_text = sanitize_text(self.input_box.get("1.0", "end"), 7000)
        if not user_text:
            user_text = self.intent_entry.get().strip() or "Guide me into a deep calming meditation."
        self.append_turn("user", user_text, via="text")
        self.log_timeline("text turn submitted")
        self.q.put(("append_transcript", f"You: {user_text}"))
        self.busy = True
        threading.Thread(target=self.generate_worker, args=(user_text,), daemon=True).start()

    def generate_worker(self, user_text: str):
        try:
            self.q.put(("voice_state", ("thinking", "building response")))
            guard = self.detect_crisis(user_text)
            mode = self.mode_menu.get().strip() or "meditation"
            provider = "safety_guard"
            reply = guard or ""
            blueprint = self.current_blueprint(mode, user_text)
            if not guard:
                provider = self.choose_provider()
                messages = self.build_messages(mode, user_text)
                self.q.put(("status", f"Generating via {provider}..."))
                if provider == "OpenAI":
                    try:
                        assert self.openai is not None
                        reply = self.openai.chat(messages)
                    except Exception:
                        assert self.xai is not None
                        provider = "Grok-fallback"
                        self.q.put(("status", "OpenAI unavailable, falling back to Grok..."))
                        reply = self.xai.chat(messages)
                else:
                    assert self.xai is not None
                    reply = self.xai.chat(messages)

            display_reply = PromptEngine.display_text(reply)
            self.append_turn("assistant", display_reply, provider=provider, mode=self.mode_menu.get(), intensity=blueprint.intensity_mode)
            self.log_timeline(f"assistant reply ready via {provider}")
            self.memory.profile.sessions += 1
            self.vault.save(self.memory)
            self.q.put(("append_transcript", f"Agent: {display_reply}"))
            rounds = 6 if mode == "box_breath" else 3
            self.q.put(("animate_breath", (self.memory.profile.inhale, self.memory.profile.hold, self.memory.profile.exhale, self.memory.profile.rest, rounds)))

            if provider != "safety_guard" and self.xai is not None:
                cfg = self.boot_config or BootConfig()
                chunks: List[bytes] = []
                text_chunks = self.tts_chunks_for_reply(reply, blueprint)
                self.last_interrupted_reply = truncate(display_reply, 1200)
                for idx, piece in enumerate(text_chunks, start=1):
                    preview = truncate(PromptEngine.display_text(piece).replace("\n", " "), 220)
                    self.q.put(("partial", f"Assistant live chunk {idx}/{len(text_chunks)}: {preview}"))
                    self.q.put(("voice_state", ("synthesizing", f"chunk {idx}/{len(text_chunks)}")))
                    key = tts_cache_key(piece, self.memory.profile.preferred_voice, cfg.tts_language, cfg.tts_codec, str(cfg.tts_sample_rate))
                    cache_path = TTS_CACHE_DIR / f"{key}.{cfg.tts_codec}"
                    if cache_path.exists():
                        audio_bytes = cache_path.read_bytes()
                    else:
                        audio_bytes = self.xai.tts(
                            piece,
                            voice_id=self.memory.profile.preferred_voice,
                            language=cfg.tts_language,
                            codec=cfg.tts_codec,
                            sample_rate=cfg.tts_sample_rate,
                        )
                        cache_path.write_bytes(audio_bytes)
                    chunks.append(audio_bytes)
                self.last_audio_chunks = chunks
                if self.auto_tts_var.get():
                    barge = cfg.barge_in_level if self.boot_config else 0.03
                    self.q.put(("voice_state", ("speaking", "barge-in enabled")))
                    self.player.play_chunks(chunks, barge_in_threshold=barge, status_callback=lambda s: self.q.put(("status", s)))

            if self.auto_summary_var.get() and len(self.memory.turns) % 4 == 0:
                self.refresh_summary_worker(push_done=False)

            if self.xai is not None:
                try:
                    title = self.xai.chat(PromptEngine.title_messages(self.memory, display_reply), temperature=0.35, max_tokens=24)
                    title = truncate(title.replace("\n", " "), 90)
                    self.memory.session_titles.append(title)
                    self.vault.save(self.memory)
                except Exception:
                    pass

            self.q.put(("render_all", None))
            self.q.put(("status", "Response ready"))
            self.q.put(("voice_state", ("idle", "response complete")))
        except Exception as exc:
            self.q.put(("error", str(exc)))
            self.q.put(("voice_state", ("idle", "error")))
        finally:
            self.q.put(("done", None))

    def transcribe_path(self, path: Path) -> str:
        stt_mode = self.stt_runtime_menu.get().strip() or "local_whisper"
        if stt_mode == "grok_stt":
            assert self.xai is not None
            return self.xai.stt_file(path)
        if self.local_whisper is None:
            model = self.boot_config.local_whisper_model if self.boot_config else "base"
            self.local_whisper = LocalWhisperEngine(model)
        return self.local_whisper.transcribe(path)

    def record_clicked(self):
        if self.busy:
            return
        self.read_profile_from_ui()
        self.player.stop()
        self.q.put(("voice_state", ("listening", "manual push-to-talk")))
        self.busy = True
        threading.Thread(target=self.record_worker, daemon=True).start()

    def record_worker(self):
        if self.boot_config is None:
            self.q.put(("error", "Boot config missing."))
            self.q.put(("done", None))
            return
        path = TEMP_DIR / f"voice_{int(time.time() * 1000)}.wav"
        try:
            self.q.put(("partial", "Listening..."))
            self.q.put(("voice_state", ("listening", "realtime partials active")))
            _audio, _sr, partial = self.realtime_recorder.run(
                output_path=path,
                status_callback=lambda s: self.q.put(("status", s)),
                meter_callback=lambda v: self.q.put(("meter", min(1.0, v * 12.0))),
                partial_callback=lambda p: self.q.put(("partial", p)),
                transcribe_callback=self.transcribe_path,
                silence_threshold=self.boot_config.silence_threshold,
                silence_hold_seconds=self.boot_config.silence_hold,
                min_speech_seconds=self.boot_config.min_speech,
                max_record_seconds=self.boot_config.max_record,
                partial_chunk_seconds=self.boot_config.partial_chunk_seconds,
            )
            self.q.put(("status", "Finalizing transcript..."))
            self.q.put(("voice_state", ("transcribing", "building final transcript")))
            transcript = sanitize_text(self.transcribe_path(path), 20000)
            if not transcript and partial:
                transcript = partial
            if not transcript:
                raise RuntimeError("No speech detected.")

            self.input_box.delete("1.0", "end")
            self.input_box.insert("end", transcript)
            self.intent_entry.delete(0, "end")
            self.intent_entry.insert(0, truncate(transcript, 190))
            self.append_turn("user", transcript, via="voice", stt_mode=self.stt_runtime_menu.get().strip())
            self.q.put(("append_transcript", f"Voice transcript ({self.stt_runtime_menu.get().strip()}): {transcript}"))
            self.q.put(("voice_state", ("thinking", "voice turn captured")))
            self.generate_worker(transcript)
        except Exception as exc:
            self.q.put(("error", str(exc)))
            self.q.put(("done", None))
        finally:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass
            self.q.put(("meter", 0.0))
            self.q.put(("partial", "Realtime partial transcript will appear here."))
            self.q.put(("voice_state", ("idle", "awaiting next turn")))

    def toggle_voice_loop(self):
        enabled = bool(self.voice_loop_var.get())
        self.voice_loop_enabled = enabled
        if enabled:
            self.voice_loop_stop = threading.Event()
            if self.voice_loop_thread is None or not self.voice_loop_thread.is_alive():
                self.voice_loop_thread = threading.Thread(target=self.voice_loop_worker, daemon=True)
                self.voice_loop_thread.start()
            self.status_var.set("Continuous voice loop enabled")
            self.q.put(("voice_state", ("loop", "hands-free voice loop")))
        else:
            self.voice_loop_stop.set()
            self.player.stop()
            self.realtime_recorder.stop()
            self.status_var.set("Continuous voice loop disabled")
            self.q.put(("voice_state", ("idle", "loop off")))

    def voice_loop_worker(self):
        while self.voice_loop_enabled and not self.voice_loop_stop.is_set():
            if not self.busy:
                self.busy = True
                try:
                    self.player.stop()
                    self.record_worker()
                except Exception:
                    pass
                finally:
                    self.busy = False
            time.sleep(0.25)

    def refresh_summary_clicked(self):
        if self.busy:
            return
        self.busy = True
        threading.Thread(target=self.refresh_summary_worker, daemon=True).start()

    def refresh_summary_worker(self, push_done: bool = True):
        try:
            assert self.xai is not None
            summary = self.xai.chat(PromptEngine.summary_messages(self.memory), temperature=0.35, max_tokens=320)
            self.memory.profile.long_term_summary = summary
            self.memory.summaries.append(f"{now_ts()} :: {summary}")
            self.vault.save(self.memory)
            self.q.put(("render_all", None))
            self.q.put(("status", "Memory summary refreshed"))
            self.log_timeline("memory summary refreshed")
        except Exception as exc:
            self.q.put(("error", str(exc)))
        finally:
            if push_done:
                self.q.put(("done", None))

    def generate_rituals_clicked(self):
        if self.busy:
            return
        self.busy = True
        threading.Thread(target=self.generate_rituals_worker, daemon=True).start()

    def generate_rituals_worker(self):
        try:
            assert self.xai is not None
            raw = self.xai.chat(PromptEngine.ritual_messages(self.memory), temperature=0.5, max_tokens=120)
            opener = ""
            closer = ""
            try:
                parsed = json.loads(raw)
                opener = sanitize_text(parsed.get("opener", ""), 200)
                closer = sanitize_text(parsed.get("closer", ""), 200)
            except Exception:
                lines = [line.strip() for line in raw.splitlines() if line.strip()]
                if lines:
                    opener = lines[0]
                if len(lines) > 1:
                    closer = lines[1]
            if opener:
                self.memory.profile.ritual_open = opener
                self.ritual_open_entry.delete(0, "end")
                self.ritual_open_entry.insert(0, opener)
                self.memory.rituals.append(f"open: {opener}")
            if closer:
                self.memory.profile.ritual_close = closer
                self.ritual_close_entry.delete(0, "end")
                self.ritual_close_entry.insert(0, closer)
                self.memory.rituals.append(f"close: {closer}")
            self.vault.save(self.memory)
            self.q.put(("render_all", None))
            self.q.put(("status", "Ritual phrases generated"))
            self.log_timeline("ritual phrases generated")
        except Exception as exc:
            self.q.put(("error", str(exc)))
        finally:
            self.q.put(("done", None))

    def replay_audio(self):
        if self.last_audio_chunks:
            barge = self.boot_config.barge_in_level if self.boot_config else 0.03
            self.q.put(("voice_state", ("speaking", "replaying cached audio")))
            self.log_timeline("replaying cached audio")
            self.player.play_chunks(self.last_audio_chunks, barge_in_threshold=barge, status_callback=lambda s: self.q.put(("status", s)))

    def stop_audio(self):
        self.player.stop()
        if self.last_reply_text:
            self.last_interrupted_reply = self.last_reply_text
        self.status_var.set("Audio interrupted")
        self.voice_state_var.set("state: interrupted")
        self.followup_var.set("next suggestion: recover interrupted reply")
        self.update_live_monitor()
        self.log_timeline("audio interrupted")

    def export_transcript(self):
        text = []
        for turn in self.memory.turns:
            text.append(f"[{turn.timestamp}] {turn.role}: {turn.text}")
        path = filedialog.asksaveasfilename(
            title="Export transcript",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        Path(path).write_text("\n\n".join(text), encoding="utf-8")
        self.status_var.set("Transcript exported")
        self.log_timeline("transcript exported")

    def animate_breath(self, inhale: float, hold: float, exhale: float, rest: float, rounds: int):
        phases = [
            ("Inhale", inhale, 1.20, PALETTE["accent"]),
            ("Hold", hold, 1.20, PALETTE["accent_2"]),
            ("Exhale", exhale, 0.86, PALETTE["muted"]),
            ("Rest", rest, 0.84, PALETTE["text"]),
        ]
        base = 220

        def step(index: int, remaining: int):
            if remaining <= 0:
                self.orb_label.configure(text="⬢", font=ctk.CTkFont(size=base), text_color=PALETTE["accent"])
                return
            label, seconds, scale, color = phases[index]
            self.status_var.set(f"{label}...")
            self.orb_label.configure(text="⬢", font=ctk.CTkFont(size=int(base * scale)), text_color=color)
            delay = int(max(seconds, 0.12) * 1000)
            next_index = (index + 1) % len(phases)
            next_remaining = remaining - 1 if next_index == 0 else remaining
            self.after(delay, lambda: step(next_index, next_remaining))

        step(0, rounds)

    def animate_ambient(self):
        try:
            self.wave_canvas.delete("all")
            w = max(280, self.wave_canvas.winfo_width())
            h = max(80, self.wave_canvas.winfo_height())
            mid = h / 2
            theme = self.ambient_menu.get().strip() if hasattr(self, "ambient_menu") else "aurora"
            amp = {"aurora": 16, "ember": 10, "ocean": 20, "forest": 14, "midnight": 8}.get(theme, 14)
            color = {"aurora": PALETTE["accent"], "ember": "#ff9f68", "ocean": "#73d7ff", "forest": "#66e39a", "midnight": "#c1b8ff"}.get(theme, PALETTE["accent"])
            self.wave_phase += 0.12
            points = []
            for x in range(0, w, 8):
                y = mid
                y += math.sin((x / 80.0) + self.wave_phase) * amp
                y += math.sin((x / 34.0) + self.wave_phase * 0.7) * amp * 0.35
                y += math.sin((x / 140.0) + self.wave_phase * 1.3) * amp * 0.25
                points.extend([x, y])
            self.wave_canvas.create_line(points, fill=color, width=3, smooth=True)
        except Exception:
            pass
        self.after(90, self.animate_ambient)

    def poll_queue(self):
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "status":
                    self.status_var.set(str(payload))
                elif kind == "append_transcript":
                    self.transcript_box.insert("end", f"\n{payload}\n")
                    self.transcript_box.see("end")
                elif kind == "meter":
                    self.meter.set(float(payload))
                elif kind == "partial":
                    self.partial_label.configure(text=str(payload))
                    self.update_live_monitor()
                elif kind == "voice_state":
                    state, detail = payload
                    self.set_voice_state(str(state), str(detail))
                    self.update_live_monitor()
                elif kind == "done":
                    self.busy = False
                elif kind == "error":
                    self.busy = False
                    messagebox.showerror(APP_TITLE, str(payload))
                elif kind == "animate_breath":
                    self.animate_breath(*payload)
                elif kind == "render_all":
                    self.render_all()
        except queue.Empty:
            pass
        self.after(80, self.poll_queue)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
