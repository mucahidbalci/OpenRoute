"""OpenRoute Windows prototype: transparent DNS and HTTPS diagnostics.

This tool reports observations only; it does not change system settings or
route traffic. A failed test is not conclusive proof of filtering.
"""
from __future__ import annotations

import socket
import ssl
import threading
import time
import urllib.error
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from datetime import datetime

APP_NAME = "OpenRoute"
TARGETS = (
    ("Instagram", "www.instagram.com"),
    ("TikTok", "www.tiktok.com"),
    ("GitHub", "github.com"),
)
TIMEOUT_SECONDS = 5

try:
    import customtkinter as ctk
    USE_CTK = True
except ImportError:  # pragma: no cover - standard library fallback
    ctk = None
    USE_CTK = False


@dataclass
class CheckResult:
    service: str
    host: str
    dns: str
    https: str
    detail: str
    elapsed_ms: int


def check_host(service: str, host: str) -> CheckResult:
    started = time.monotonic()
    dns_result = "FAIL"
    https_result = "NOT TESTED"
    details: list[str] = []
    try:
        socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        dns_result = "OK"
    except (socket.gaierror, TimeoutError, OSError) as exc:
        details.append(f"DNS: {type(exc).__name__}: {exc}")

    if dns_result == "OK":
        request = urllib.request.Request(
            f"https://{host}/", headers={"User-Agent": "OpenRoute-Diagnostics/0.1"}
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                https_result = f"OK (HTTP {response.status})"
        except urllib.error.HTTPError as exc:
            # HTTP error means DNS/TLS/HTTP reached the remote service.
            https_result = f"REACHED (HTTP {exc.code})"
        except (urllib.error.URLError, TimeoutError, ssl.SSLError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            details.append(f"HTTPS: {type(reason).__name__}: {reason}")
            https_result = "FAIL"

    elapsed = int((time.monotonic() - started) * 1000)
    detail = "; ".join(details) if details else "No obvious connection error observed."
    return CheckResult(service, host, dns_result, https_result, detail, elapsed)


class OpenRouteApp:
    def __init__(self) -> None:
        if USE_CTK:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Network diagnostics")
        self.root.geometry("780x560")
        self.root.minsize(640, 440)
        self._build_ui()

    def _build_ui(self) -> None:
        if USE_CTK:
            frame = ctk.CTkFrame(self.root, corner_radius=14)
            frame.pack(fill="both", expand=True, padx=18, pady=18)
            ctk.CTkLabel(frame, text="OpenRoute", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=18, pady=(16, 2))
            ctk.CTkLabel(frame, text="Transparent network diagnostics · Preview 0.1", text_color="gray70").pack(anchor="w", padx=18)
            ctk.CTkLabel(frame, text="Tests DNS and HTTPS reachability. It does not bypass account or age checks.", wraplength=700, justify="left").pack(anchor="w", padx=18, pady=(12, 10))
            self.run_button = ctk.CTkButton(frame, text="Run connection tests", command=self.run_tests)
            self.run_button.pack(anchor="w", padx=18, pady=(0, 12))
            self.output = ctk.CTkTextbox(frame, wrap="word")
            self.output.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        else:
            frame = ttk.Frame(self.root, padding=18)
            frame.pack(fill="both", expand=True)
            ttk.Label(frame, text="OpenRoute", font=("Segoe UI", 22, "bold")).pack(anchor="w")
            ttk.Label(frame, text="Transparent network diagnostics · Preview 0.1").pack(anchor="w", pady=(0, 8))
            ttk.Label(frame, text="Tests DNS and HTTPS reachability. It does not bypass account or age checks.", wraplength=700).pack(anchor="w", pady=(0, 8))
            self.run_button = ttk.Button(frame, text="Run connection tests", command=self.run_tests)
            self.run_button.pack(anchor="w", pady=(0, 8))
            self.output = tk.Text(frame, wrap="word", height=20)
            self.output.pack(fill="both", expand=True)
        self._write("Ready. Press ‘Run connection tests’.\n")
        self._write("Note: results can be affected by outages, firewalls, DNS providers and network filtering.\n\n")

    def _write(self, text: str) -> None:
        self.output.insert("end", text)
        self.output.see("end")

    def run_tests(self) -> None:
        self.run_button.configure(state="disabled")
        self._write(f"\n--- Test started {datetime.now().astimezone().isoformat(timespec='seconds')} ---\n")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        results = [check_host(name, host) for name, host in TARGETS]
        self.root.after(0, self._show_results, results)

    def _show_results(self, results: list[CheckResult]) -> None:
        for result in results:
            self._write(
                f"{result.service} ({result.host})\n"
                f"  DNS: {result.dns} | HTTPS: {result.https} | {result.elapsed_ms} ms\n"
                f"  Detail: {result.detail}\n\n"
            )
        self._write("Interpretation: these checks indicate reachability only; they cannot reliably identify the cause of a failure.\n")
        self.run_button.configure(state="normal")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    OpenRouteApp().run()
