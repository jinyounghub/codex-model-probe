# Codex Model Probe: English user guide

This Windows tool continuously displays the **model and reasoning effort requested in the actual Codex network message**, the **model, reasoning effort, and reasoning token usage reported by the server's completed response**, plus locally matched project and conversation labels. It keeps recording while the proxy and Codex remain open.

> “Final response model” means a string from `response.completed.response.model` or another completed server response payload. It does not independently prove which model weights or internal route produced the answer. If the request and completion cannot be paired, the requested model and session ID are shown as `Unknown`.

## 1. Start without installing dependencies

Windows 10/11 and the Windows Codex desktop app are required. **You do not need to install Python or run a PowerShell setup script.**

1. Download `codex-model-probe-en-win64.zip` from [Releases](https://github.com/jinyounghub/codex-model-probe/releases) and **extract** it. Keep `CodexModelMonitor-en.exe`, `mitmdump.exe`, `capture.py`, and `model_probe.py` together. Open `CodexModelMonitor-en.exe`.
2. Click **Quick connect**. The monitor prepares the local proxy and certificate. It selects a free port if the default is busy.
3. On the first run, inspect the locally generated certificate's SHA-256 fingerprint and trust scope in **Confirm certificate trust**. If you agree, the app adds that certificate to **Current User > Trusted Root Certification Authorities**. Administrator rights are not required.
4. **Fully close** the running Codex app. The monitor reopens it through the proxy. Send a message and look for a new row. Monitoring continues while the monitor remains open.

A running Codex process cannot inherit new proxy settings, so one restart is required. Automatic reopening currently supports the Microsoft Store/Appx Codex app. The ZIP includes the official mitmproxy 12.2.3 standalone `mitmdump.exe`; no separate Python installation is needed. The executables are unsigned. You can check the ZIP against the release's `SHA256SUMS.txt`.

## 2. Certificate and connection management

The proxy needs a trusted certificate to read HTTPS traffic. Quick connect shows the fingerprint of `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer` and adds it to the **Current User** root store only after your confirmation. The release ZIP contains neither a certificate nor a private key. Do not install a certificate supplied by another computer. See the [official mitmproxy certificate guide](https://docs.mitmproxy.org/stable/concepts/certificates/).

To finish, close the Codex app opened through the proxy first, click **Stop connection** in the monitor, then reopen Codex normally. If the proxy stops first, Codex may show `Reconnecting... waiting for network`.

## 3. Advanced settings and Codex CLI

Click **Show advanced settings** for manual proxy controls, port/host/result-file settings, the certificate file, and CLI support. To use the CLI, start the proxy, trust the certificate, then click **Open Codex CLI via proxy**. That button sets proxy environment variables only for the new CLI process. It does not change Windows-wide proxy settings.

## 4. Read the table and results file

| Column | Source and meaning |
| --- | --- |
| Project, Conversation title | Display labels joined by the thread ID in local Codex metadata. When a project ID is absent, the saved project root is matched against the thread working directory. |
| Session ID, Thread ID | `client_metadata.session_id` and `client_metadata.thread_id` in the actual request |
| Requested model | `response.create.model` or the HTTP request body's `model` |
| Requested reasoning | `reasoning.effort` in the actual request, such as `high` or `xhigh` |
| Final response model | `response.completed.response.model`, or `model` on a completed non-streaming Response object |
| Response reasoning | `response.reasoning.effort` in the completed server response |
| Reasoning tokens | `usage.output_tokens_details.reasoning_tokens` in the completed response. Zero means the server reported zero. |
| Value comparison | Literal string comparison only. **Values differ** is not a definitive conclusion about internal routing. |
| Response ID | Server response ID used to associate request and completion |
| Final payload field | Exact field used as evidence for the final model |

Records append to `%LOCALAPPDATA%\CodexModelProbe\results.jsonl`. It includes requested and response reasoning effort, response mode/context, and reasoning token usage. The file does not store raw prompts, response bodies, authorization headers, or conversation titles. It **does** contain session, thread, and turn IDs; treat it as personal data. The repository and release ZIPs exclude it. The GUI shows the latest 500 rows; the file continues to grow. Use the horizontal scrollbar for columns on the right. You can select an older version's results file in advanced settings.

The server response does not itself contain a project or conversation title. The GUI reads `~/.codex/state_5.sqlite` **read-only** to match an exact thread ID to its display title and a saved project path to its project name. Missing local metadata or threads on another host show as **Unknown**. Each response ID identifies an individual response, so its original value remains visible. For WebSocket traffic, a request is associated with the next `response.created.response.id` on the same connection, then checked against `response.completed.response.id`. Uncertain associations are left blank.

`reasoning.effort` is a requested or server-reported setting. It does not expose the model's hidden reasoning or prove the amount of internal reasoning performed. Reasoning tokens are also server-reported usage. Missing fields show as **Unknown**. **If an existing proxy is running an older `capture.py`, the new fields will appear after its next normal restart.**

## 5. Watch a proxy already owned by another GUI

If another monitor window is already running the proxy, do not click Quick connect in a second window. Open the EXE from the same folder with `--watch-only` to view the default results file:

```powershell
.\CodexModelMonitor-en.exe --watch-only
```

Keep the original monitor window open because it owns the proxy. Closing the watch-only window does not stop that proxy.

## 6. Shutdown and troubleshooting

**Shutdown order:** fully close the Codex app or CLI that uses the proxy, click **Stop connection** in the monitor, then reopen Codex normally. If the proxy stops first, Codex may show `Reconnecting... waiting for network`. Closing the monitor also stops the proxy it started.

| Symptom | Check |
| --- | --- |
| **mitmdump required** | Keep `mitmdump.exe` from the ZIP beside the GUI EXE. |
| **Certificate trust required** | Confirm the certificate prompt in Quick connect. If policy blocks the command, use **Open certificate file** in advanced settings for manual installation. |
| Codex keeps reconnecting | Check that the proxy is running and Codex was restarted through it. If needed, close Codex, stop the proxy, and start Codex normally. |
| No new table row | Check that the app/CLI was reopened through the proxy, a response completed, and the **Hosts** field includes the actual host. |
| Requested model or session is **Unknown** | Only the completion may have been captured, or the request could not be paired with `response.created`. Try another request. |
| Port 8080 is occupied | Quick connect chooses a free port. In manual mode, change the port in advanced settings. |

**Codex process capture (experimental)** caused connection errors on the machine used for testing. The recommended mode is **Manual HTTP proxy**. **Analyze capture file** can inspect a separate HAR/JSON/SSE file, although ordinary HAR exports may omit WebSocket messages.

## 7. Certificate removal and security

When you no longer need the proxy, restart Codex normally. You may then open Windows `certmgr.msc` and remove only this PC's mitmproxy certificate under **Current User > Trusted Root Certification Authorities > Certificates**. The `.mitmproxy` folder also contains the CA **private key**; never share or upload it. Removing the certificate or replacing the CA files requires a new certificate installation before the next use.

mitmproxy can read HTTPS traffic that passes through it. Use this only for your own Codex account and machine, and run the proxy only when needed. See the official [certificate](https://docs.mitmproxy.org/stable/concepts/certificates/) and [proxy mode](https://docs.mitmproxy.org/stable/concepts/modes/) documentation.

## Run and test from source

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_mitmproxy.ps1
python .\gui_en.py
python -m unittest discover -p 'test_*.py' -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_windows.ps1
python .\package_release.py
```

The GUI itself uses Python's standard library. Live capture requires `capture.py`, `model_probe.py`, and mitmdump in the same extracted folder. Running the GUI from source also requires `codex_metadata.py` beside `gui.py`. Release builds run `vendor_mitmdump.py`, which downloads the official 12.2.3 standalone executable and verifies its SHA-256 hash.
