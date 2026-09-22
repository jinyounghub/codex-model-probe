#!/usr/bin/env python3
"""Desktop monitor for server-reported model IDs in Codex response payloads."""

from __future__ import annotations

import json
import os
import queue
import re
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from codex_metadata import CodexMetadataResolver
from model_probe import analyze_file
from translations import translate


HERE = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LANGUAGE = "ko"


def tr(value: str) -> str:
    return translate(value, LANGUAGE)


def edition_language(executable: str | Path) -> str:
    return "en" if Path(executable).stem.lower().endswith("-en") else "ko"


def clean_child_environment() -> dict[str, str]:
    """Do not leak PyInstaller's temporary Tcl paths to Codex children."""
    env = os.environ.copy()
    for name in list(env):
        if name in {"TCL_LIBRARY", "TK_LIBRARY", "_MEIPASS2", "PYINSTALLER_RESET_ENVIRONMENT"} or name.startswith("_PYI_"):
            env.pop(name, None)
    return env


def default_mitmdump() -> str:
    explicit = os.environ.get("CODEX_MODEL_PROBE_MITMDUMP")
    packaged = HERE / ".venv" / "Scripts" / "mitmdump.exe"
    local = HERE.parents[1] / "work" / "mitmproxy-venv" / "Scripts" / "mitmdump.exe"
    for candidate in (explicit, str(packaged), str(local), shutil.which("mitmdump")):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return ""


def display_time(value: str | None) -> str:
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value).astimezone().strftime("%H:%M:%S")
    except ValueError:
        return value[:8]


def model_comparison(record: dict) -> str:
    requested = record.get("requested_model")
    final = record.get("model")
    if not isinstance(requested, str) or not requested or not isinstance(final, str) or not final:
        return tr("확인 불가")
    return tr("값 일치") if requested == final else tr("값 다름")


def mitmproxy_certificate_trusted() -> bool:
    """Match the exact locally generated CA against Windows' trusted ROOT store."""
    cert = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.cer"
    if not cert.is_file() or not hasattr(ssl, "enum_certificates"):
        return False
    try:
        expected = ssl.PEM_cert_to_DER_cert(cert.read_text(encoding="ascii"))
        return any(encoding == "x509_asn" and data == expected
                   for data, encoding, _trust in ssl.enum_certificates("ROOT"))
    except (OSError, UnicodeError, ValueError):
        return False


def codex_desktop_executable() -> Path | None:
    if os.name != "nt":
        return None
    command = ["powershell.exe", "-NoProfile", "-Command",
               "(Get-AppxPackage -Name OpenAI.Codex | Select-Object -First 1 -ExpandProperty InstallLocation)"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        install_dir = result.stdout.strip().splitlines()[0] if result.returncode == 0 and result.stdout.strip() else ""
        executable = Path(install_dir) / "app" / "ChatGPT.exe" if install_dir else None
        return executable if executable and executable.is_file() else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def codex_desktop_running() -> bool:
    command = ["powershell.exe", "-NoProfile", "-Command",
               "@(Get-CimInstance Win32_Process -Filter \"Name='ChatGPT.exe'\" | "
               "Where-Object { $_.ExecutablePath -like '*OpenAI.Codex*' }).Count"]
    result = subprocess.run(command, capture_output=True, text=True, timeout=10,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode != 0:
        raise OSError(result.stderr.strip() or tr("Codex 프로세스를 확인할 수 없습니다"))
    try:
        return int(result.stdout.strip()) > 0
    except ValueError as exc:
        raise OSError(tr("Codex 프로세스 수를 읽을 수 없습니다")) from exc


class MonitorState:
    def __init__(self):
        self.responses = 0
        self.models = 0
        self.unknown = 0
        self.last_model = tr("대기 중")

    def consume(self, record: dict) -> bool:
        kind = record.get("kind")
        if kind == "response_seen":
            self.responses += 1
            return False
        if kind == "model" or (kind is None and "evidence" in record):
            self.models += 1
            model = record.get("model")
            if not isinstance(model, str) or not model:
                self.unknown += 1
                self.last_model = tr("확인 불가")
            else:
                self.last_model = model
            return True
        return False


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.watch_only = "--watch-only" in sys.argv
        root.title(tr("Codex 요청·최종 모델 및 세션 모니터"))
        root.geometry("1450x720")
        root.minsize(950, 580)

        self.proc: subprocess.Popen | None = None
        self.desktop_launch_cancel = threading.Event()
        self.desktop_relaunch_pending = False
        self.desktop_messages: queue.Queue[str] = queue.Queue()
        self.process_messages: queue.Queue[str] = queue.Queue()
        self.state = MonitorState()
        self.codex_metadata = CodexMetadataResolver()
        self.offset = 0
        self.pending = b""
        self.selected_file = Path(HERE / "results.jsonl")

        self.mitmdump_var = tk.StringVar(value=default_mitmdump())
        self.output_var = tk.StringVar(value=str(self.selected_file))
        self.port_var = tk.StringVar(value="8080")
        self.mode_var = tk.StringVar(value=tr("수동 HTTP 프록시"))
        self.cli_model_var = tk.StringVar(value="")
        self.target_var = tk.StringVar(value="codex,codex-code-mode-host")
        self.hosts_var = tk.StringVar(value="chatgpt.com,api.openai.com")
        self.status_var = tk.StringVar(value=tr("기존 프록시 결과 감시 중") if self.watch_only else tr("중지됨 · 응답 기록 대기"))
        self.responses_var = tk.StringVar(value="0")
        self.models_var = tk.StringVar(value="0")
        self.unknown_var = tk.StringVar(value="0")
        self.last_model_var = tk.StringVar(value=tr("대기 중"))

        self._build()
        self._set_tail_start()
        if self.watch_only:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="disabled")
            self.cli_button.configure(state="disabled")
            self.desktop_button.configure(state="disabled")
            if self.selected_file.exists():
                self.offset = max(0, self.selected_file.stat().st_size - 1_000_000)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(250, self._tick)

    def _build(self):
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Value.TLabel", font=("Segoe UI", 14, "bold"))

        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text=tr("Codex 요청·최종 모델 및 세션 모니터"), style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.status_var, foreground="#2563eb").grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Button(header, text=tr("사용 설명서"), command=self.open_manual).grid(row=0, column=1, rowspan=2, sticky="e")

        config = ttk.LabelFrame(outer, text=tr("실시간 캡처 설정"), padding=10)
        config.grid(row=1, column=0, sticky="ew")
        config.columnconfigure(1, weight=1)
        self._field(config, 0, "mitmdump", self.mitmdump_var, self._browse_executable)
        self._field(config, 1, tr("결과 파일"), self.output_var, self._browse_output)
        ttk.Label(config, text=tr("캡처 방식")).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        mode = ttk.Combobox(config, textvariable=self.mode_var, state="readonly", width=31,
                            values=(tr("수동 HTTP 프록시"), tr("Codex 프로세스 캡처 (실험적)")))
        mode.grid(row=2, column=1, sticky="w", pady=4)
        mode.bind("<<ComboboxSelected>>", lambda _event: self._update_mode())
        ttk.Label(config, text=tr("대상 프로세스")).grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.target_entry = ttk.Entry(config, textvariable=self.target_var)
        self.target_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=4)
        ttk.Label(config, text=tr("수동 프록시 포트")).grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
        self.port_entry = ttk.Entry(config, textvariable=self.port_var, width=8)
        self.port_entry.grid(row=4, column=1, sticky="w", pady=4)
        ttk.Label(config, text=tr("호스트")).grid(row=5, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(config, textvariable=self.hosts_var).grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)
        ttk.Label(config, text=tr("CLI 요청 모델 (선택)")).grid(row=6, column=0, sticky="w", padx=(0, 8), pady=4)
        self.cli_model_entry = ttk.Entry(config, textvariable=self.cli_model_var)
        self.cli_model_entry.grid(row=6, column=1, columnspan=2, sticky="ew", pady=4)

        controls = ttk.Frame(config)
        controls.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        self.start_button = ttk.Button(controls, text=tr("프록시 시작"), command=self.start_proxy)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(controls, text=tr("중지"), command=self.stop_proxy, state="disabled")
        self.stop_button.pack(side="left", padx=6)
        self.copy_button = ttk.Button(controls, text=tr("프록시 주소 복사"), command=self.copy_proxy)
        self.copy_button.pack(side="left", padx=6)
        self.cli_button = ttk.Button(controls, text=tr("프록시로 Codex CLI 열기"), command=self.launch_cli)
        self.cli_button.pack(side="left", padx=6)
        self.desktop_button = ttk.Button(controls, text=tr("Codex 앱 연결 예약"), command=self.schedule_desktop_relaunch)
        self.desktop_button.pack(side="left", padx=6)
        ttk.Button(controls, text=tr("인증서 파일 보기"), command=self.open_certificate).pack(side="left", padx=6)
        ttk.Button(controls, text=tr("캡처 파일 분석"), command=self.open_capture).pack(side="right")
        self._update_mode()

        cards = ttk.Frame(outer)
        cards.grid(row=2, column=0, sticky="ew", pady=14)
        for index in range(4):
            cards.columnconfigure(index, weight=1)
        for index, (label, variable) in enumerate((
            (tr("수신한 서버 메시지"), self.responses_var),
            (tr("최종 모델 이벤트"), self.models_var),
            (tr("모델 확인 불가"), self.unknown_var),
            (tr("마지막 모델"), self.last_model_var),
        )):
            frame = ttk.LabelFrame(cards, text=label, padding=(12, 8))
            frame.grid(row=0, column=index, sticky="ew", padx=(0, 8) if index < 3 else 0)
            ttk.Label(frame, textvariable=variable, style="Value.TLabel").pack(anchor="w")

        table_frame = ttk.LabelFrame(outer, text=tr("최종 응답 기록"), padding=8)
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, columns=("time", "project_name", "conversation_title",
                                                        "requested_model", "request_reasoning_effort", "model",
                                                        "response_reasoning_effort", "reasoning_tokens", "comparison",
                                                        "session_id", "thread_id", "response_id", "transport", "evidence"),
                                  show="headings")
        for name, label, width in (
            ("time", tr("시각"), 85), ("project_name", tr("프로젝트"), 150),
            ("conversation_title", tr("대화 제목"), 235),
            ("requested_model", tr("요청 모델"), 145),
            ("request_reasoning_effort", tr("요청 reasoning"), 125),
            ("model", tr("최종 응답 모델"), 155),
            ("response_reasoning_effort", tr("응답 reasoning"), 125),
            ("reasoning_tokens", tr("reasoning 토큰"), 120),
            ("comparison", tr("값 비교"), 115), ("session_id", tr("세션 ID"), 275),
            ("thread_id", tr("대화 ID"), 275),
            ("response_id", tr("응답 ID"), 220), ("transport", tr("통신"), 95),
            ("evidence", tr("최종 페이로드 필드"), 270),
        ):
            self.table.heading(name, text=label)
            self.table.column(name, width=width, minwidth=75, stretch=False)
        self.table.tag_configure("different", foreground="#b91c1c")
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        self.table.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal_scroll.set)

        ttk.Label(outer, text=tr("모델·reasoning은 실제 요청과 서버 완료 응답에서 읽고, 프로젝트·대화 제목은 로컬 Codex 메타데이터에서 대화 ID로 찾습니다. 연결할 수 없는 정보는 '확인 불가'로 표시합니다."),
                  wraplength=1180, foreground="#4b5563").grid(row=4, column=0, sticky="ew", pady=(10, 0))

    def _update_mode(self):
        local = self.mode_var.get() == tr("Codex 프로세스 캡처 (실험적)")
        self.target_entry.configure(state="normal" if local else "disabled")
        self.port_entry.configure(state="disabled" if local else "normal")
        self.copy_button.configure(state="disabled" if local else "normal")
        self.cli_button.configure(state="disabled" if local else "normal")
        self.desktop_button.configure(state="disabled" if local else "normal")
        self.cli_model_entry.configure(state="disabled" if local else "normal")

    def _capture_label(self):
        if self.mode_var.get() == tr("Codex 프로세스 캡처 (실험적)"):
            return tr("로컬 Codex 프로세스")
        return f"127.0.0.1:{self.port_var.get()}"

    def _field(self, parent, row: int, label: str, variable: tk.StringVar, action):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Button(parent, text=tr("찾기"), command=action).grid(row=row, column=2, padx=(8, 0), pady=4)

    def _browse_executable(self):
        path = filedialog.askopenfilename(title=tr("mitmdump 실행 파일 선택"))
        if path:
            self.mitmdump_var.set(path)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(title=tr("결과 JSONL 파일"), defaultextension=".jsonl")
        if path:
            self.output_var.set(path)
            self.selected_file = Path(path)
            self._set_tail_start()

    def _set_tail_start(self):
        self.offset = self.selected_file.stat().st_size if self.selected_file.exists() else 0
        self.pending = b""

    def _reset_live_state(self):
        self.state = MonitorState()
        for item in self.table.get_children():
            self.table.delete(item)
        self._refresh_cards()

    def start_proxy(self):
        if self.watch_only:
            return
        executable = Path(self.mitmdump_var.get().strip())
        if not executable.is_file():
            messagebox.showerror(tr("mitmdump 필요"), tr("mitmdump 실행 파일을 선택하세요. 설치 방법은 README.md에 있습니다."))
            return
        local = self.mode_var.get() == tr("Codex 프로세스 캡처 (실험적)")
        if local:
            if not mitmproxy_certificate_trusted():
                messagebox.showerror(
                    tr("인증서 신뢰 필요"),
                    tr("현재 mitmproxy 인증서가 Windows의 신뢰할 수 있는 루트 인증 기관에 없습니다. 먼저 '인증서 파일 보기'에서 현재 사용자 루트 저장소에 설치하세요. 설치 전 캡처를 시작하면 Codex 연결이 끊길 수 있습니다."),
                )
                return
            targets = self.target_var.get().strip()
            if not targets:
                messagebox.showerror(tr("대상 오류"), tr("캡처할 프로세스 이름을 입력하세요."))
                return
        else:
            try:
                port = int(self.port_var.get())
                if not 1 <= port <= 65535:
                    raise ValueError
            except ValueError:
                messagebox.showerror(tr("포트 오류"), tr("포트는 1부터 65535까지의 숫자여야 합니다."))
                return
        hosts = self.hosts_var.get().strip()
        if not hosts:
            messagebox.showerror(tr("호스트 오류"), tr("캡처할 정확한 호스트를 입력하세요."))
            return
        self.selected_file = Path(self.output_var.get().strip()).expanduser()
        self.selected_file.parent.mkdir(parents=True, exist_ok=True)
        self._set_tail_start()
        self._reset_live_state()
        args = [str(executable), "-q", "-s", str(HERE / "capture.py"),
                "--set", f"modelprobe_output={self.selected_file}",
                "--set", f"modelprobe_hosts={hosts}"]
        if local:
            args.extend(["--mode", f"local:{targets}"])
            # Let unrelated Codex traffic pass through without interception.
            for host in (host.strip() for host in hosts.split(",")):
                if host:
                    args.extend(["--set", f"allow_hosts={re.escape(host)}"])
        else:
            args.extend(["--listen-host", "127.0.0.1", "--listen-port", str(port)])
        try:
            self.proc = subprocess.Popen(
                args, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except OSError as exc:
            messagebox.showerror(tr("프록시 실행 실패"), str(exc))
            return
        threading.Thread(target=self._read_process_output, args=(self.proc,), daemon=True).start()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_var.set(tr("캡처 시작 중 · {label}").format(label=self._capture_label()))

    def _read_process_output(self, proc: subprocess.Popen):
        if proc.stdout:
            for line in proc.stdout:
                if line.strip():
                    self.process_messages.put(line.strip()[-500:])

    def stop_proxy(self):
        self.desktop_launch_cancel.set()
        self.desktop_relaunch_pending = False
        self.desktop_button.configure(state="normal" if self.mode_var.get() == tr("수동 HTTP 프록시") else "disabled")
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.status_var.set(tr("프록시 중지 중"))

    def copy_proxy(self):
        address = f"http://127.0.0.1:{self.port_var.get().strip()}"
        self.root.clipboard_clear()
        self.root.clipboard_append(address)
        self.status_var.set(tr("복사됨: {address}").format(address=address))

    def launch_cli(self):
        if self.proc is None or self.proc.poll() is not None:
            messagebox.showerror(tr("프록시 필요"), tr("먼저 수동 HTTP 프록시를 시작하세요."))
            return
        cli = shutil.which("codex")
        if not cli:
            messagebox.showerror(tr("Codex CLI 없음"), tr("codex.exe를 PATH에서 찾지 못했습니다."))
            return
        cert = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem"
        if not cert.is_file() or not mitmproxy_certificate_trusted():
            messagebox.showerror(tr("인증서 신뢰 필요"), tr("mitmproxy 인증서를 현재 사용자 루트 저장소에 설치하세요."))
            return
        try:
            with socket.create_connection(("127.0.0.1", int(self.port_var.get())), timeout=1):
                pass
        except OSError:
            messagebox.showerror(tr("프록시 준비 중"), tr("프록시가 아직 포트에서 대기하지 않습니다. 잠시 후 다시 누르세요."))
            return
        env = clean_child_environment()
        address = f"http://127.0.0.1:{self.port_var.get().strip()}"
        env["HTTP_PROXY"] = address
        env["HTTPS_PROXY"] = address
        env["CODEX_CA_CERTIFICATE"] = str(cert)
        env["NO_PROXY"] = ",".join(filter(None, (env.get("NO_PROXY"), "localhost,127.0.0.1,::1")))
        command = [cli, "--enable", "respect_system_proxy"]
        requested_model = self.cli_model_var.get().strip()
        if requested_model:
            command.extend(["-m", requested_model])
        try:
            subprocess.Popen(command, env=env,
                             creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0)
        except OSError as exc:
            messagebox.showerror(tr("Codex CLI 실행 실패"), str(exc))
            return
        self.status_var.set(tr("Codex CLI 새 창 실행 · 요청 모델 {model} · 응답 대기").format(
            model=requested_model or tr("기본값")))

    def schedule_desktop_relaunch(self):
        if self.proc is None or self.proc.poll() is not None:
            messagebox.showerror(tr("프록시 필요"), tr("먼저 수동 HTTP 프록시를 시작하세요."))
            return
        if not mitmproxy_certificate_trusted():
            messagebox.showerror(tr("인증서 신뢰 필요"), tr("mitmproxy 인증서를 현재 사용자 루트 저장소에 설치하세요."))
            return
        executable = codex_desktop_executable()
        if executable is None:
            messagebox.showerror(tr("Codex 앱 없음"), tr("설치된 Codex 데스크톱 앱의 ChatGPT.exe를 찾지 못했습니다."))
            return
        try:
            with socket.create_connection(("127.0.0.1", int(self.port_var.get())), timeout=1):
                pass
        except OSError:
            messagebox.showerror(tr("프록시 준비 중"), tr("프록시가 아직 포트에서 대기하지 않습니다."))
            return
        self.desktop_launch_cancel.set()
        self.desktop_launch_cancel = threading.Event()
        cancel = self.desktop_launch_cancel
        self.desktop_relaunch_pending = True
        self.desktop_button.configure(state="disabled")
        self.status_var.set(tr("Codex 앱 종료 대기 · 앱을 완전히 닫으면 프록시로 다시 엽니다"))
        address = f"http://127.0.0.1:{self.port_var.get().strip()}"
        threading.Thread(target=self._relaunch_desktop_when_closed,
                         args=(executable, address, cancel), daemon=True).start()

    def _relaunch_desktop_when_closed(self, executable: Path, address: str,
                                     cancel: threading.Event):
        try:
            while not cancel.is_set() and codex_desktop_running():
                time.sleep(2)
            if cancel.is_set() or self.proc is None or self.proc.poll() is not None:
                return
            env = clean_child_environment()
            env["HTTP_PROXY"] = address
            env["HTTPS_PROXY"] = address
            env["CODEX_CA_CERTIFICATE"] = str(Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem")
            env["NO_PROXY"] = ",".join(filter(None, (env.get("NO_PROXY"), "localhost,127.0.0.1,::1")))
            subprocess.Popen([str(executable)], env=env, cwd=executable.parent)
            self.desktop_messages.put(tr("Codex 앱 프록시 환경으로 다시 열림 · 서버 응답 대기"))
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.desktop_messages.put(tr("Codex 앱 재실행 실패: {error}").format(error=exc))
        finally:
            if cancel is self.desktop_launch_cancel:
                self.desktop_relaunch_pending = False

    def open_certificate(self):
        cert = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.cer"
        if not cert.is_file():
            messagebox.showerror(tr("인증서 없음"), tr("캡처를 한 번 시작한 뒤 다시 시도하세요."))
            return
        if os.name == "nt":
            os.startfile(cert)
        else:
            messagebox.showinfo(tr("인증서 위치"), str(cert))

    def open_manual(self):
        manual = HERE / ("README.en.md" if LANGUAGE == "en" else "README.ko.md")
        if not manual.is_file():
            messagebox.showerror(tr("결과"), str(manual))
            return
        if os.name == "nt":
            os.startfile(manual)
        else:
            messagebox.showinfo(tr("사용 설명서"), str(manual))

    def open_capture(self):
        path = filedialog.askopenfilename(title=tr("서버 응답 캡처 선택"), filetypes=[
            (tr("캡처 파일"), "*.har *.json *.jsonl *.txt"), (tr("모든 파일"), "*.*")])
        if not path:
            return
        try:
            records = analyze_file(Path(path))
        except (OSError, UnicodeError) as exc:
            messagebox.showerror(tr("파일 분석 실패"), str(exc))
            return
        if not records:
            messagebox.showinfo(tr("결과"), tr("서버의 최종 응답 페이로드를 찾지 못했습니다."))
            return
        for item in records:
            self._show_model({"kind": "model", "time_utc": None, "host": tr("파일"),
                              "response_id": item["response_id"], "model": item["model"], "transport": tr("파일"),
                              "evidence": item["evidence"],
                              "response_reasoning_effort": item.get("response_reasoning_effort"),
                              "reasoning_tokens": item.get("reasoning_tokens")})
        self.status_var.set(tr("파일 분석 완료 · 최종 응답 {count}개").format(count=len(records)))

    def _show_model(self, record: dict):
        if not self.state.consume(record):
            return
        comparison = model_comparison(record)
        labels = self.codex_metadata.resolve(record.get("thread_id") or record.get("session_id"))
        tokens = record.get("reasoning_tokens")
        self.table.insert("", 0, values=(
            display_time(record.get("time_utc")),
            labels["project_name"] or tr("확인 불가"), labels["conversation_title"] or tr("확인 불가"),
            record.get("requested_model") or tr("확인 불가"),
            record.get("request_reasoning_effort") or tr("확인 불가"),
            record.get("model") or tr("확인 불가"),
            record.get("response_reasoning_effort") or tr("확인 불가"),
            tokens if isinstance(tokens, int) and not isinstance(tokens, bool) else tr("확인 불가"),
            comparison, record.get("session_id") or tr("확인 불가"),
            record.get("thread_id") or tr("확인 불가"), record.get("response_id") or "-",
            record.get("transport") or "-", record.get("evidence") or "-",
        ), tags=("different",) if comparison == tr("값 다름") else ())
        children = self.table.get_children()
        if len(children) > 500:
            self.table.delete(children[-1])
        self._refresh_cards()

    def _refresh_cards(self):
        self.responses_var.set(str(self.state.responses))
        self.models_var.set(str(self.state.models))
        self.unknown_var.set(str(self.state.unknown))
        self.last_model_var.set(self.state.last_model)

    def _read_new_records(self):
        path = self.selected_file
        if not path.exists():
            return
        size = path.stat().st_size
        if size < self.offset:
            self.offset, self.pending = 0, b""
            self._reset_live_state()
        if size == self.offset:
            return
        with path.open("rb") as file:
            file.seek(self.offset)
            data = file.read()
            self.offset = file.tell()
        parts = (self.pending + data).split(b"\n")
        self.pending = parts.pop()
        for raw in parts:
            try:
                record = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(record, dict):
                continue
            if record.get("kind") == "response_seen":
                self.state.consume(record)
                self._refresh_cards()
                if self.proc and self.proc.poll() is None:
                    self.status_var.set(tr("서버 응답 감지 · 최종 페이로드 대기"))
            elif record.get("kind") == "model" or (record.get("kind") is None and "evidence" in record):
                self._show_model(record)
                if self.watch_only or (self.proc and self.proc.poll() is None):
                    self.status_var.set(tr("최종 응답 모델 확인") if record.get("model") else tr("최종 응답 모델 확인 불가"))

    def _tick(self):
        try:
            had_desktop_message = False
            while not self.desktop_messages.empty():
                self.status_var.set(self.desktop_messages.get_nowait())
                self.desktop_button.configure(state="normal")
                had_desktop_message = True
            self._read_new_records()
            if self.proc:
                code = self.proc.poll()
                if code is not None:
                    self.desktop_launch_cancel.set()
                    self.desktop_relaunch_pending = False
                    self.status_var.set(tr("프록시 종료됨 · 코드 {code}").format(code=code))
                    self.proc = None
                    self.start_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self.desktop_button.configure(state="normal")
                elif self.state.responses == 0 and not self.desktop_relaunch_pending and not had_desktop_message:
                    self.status_var.set(tr("캡처 실행 중 · {label} · 트래픽 대기").format(label=self._capture_label()))
            if self.proc is None and not self.process_messages.empty():
                last = ""
                while not self.process_messages.empty():
                    last = self.process_messages.get_nowait()
                if last:
                    self.status_var.set(tr("프록시 메시지: {message}").format(message=last))
        except OSError as exc:
            self.status_var.set(tr("결과 파일 읽기 오류: {error}").format(error=exc))
        self.root.after(300, self._tick)

    def close(self):
        self.desktop_launch_cancel.set()
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.root.destroy()


def main(language: str | None = None):
    global LANGUAGE
    if language is None:
        LANGUAGE = edition_language(sys.executable)
    else:
        LANGUAGE = language
    if "--check-cert" in sys.argv:
        return 0 if mitmproxy_certificate_trusted() else 1
    root = tk.Tk()
    App(root)
    if "--check-ui" in sys.argv:
        root.withdraw()
        root.update_idletasks()
        root.destroy()
        return 0
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
