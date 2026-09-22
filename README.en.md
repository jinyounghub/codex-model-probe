# Codex Model Probe: English user guide

This Windows tool continuously displays the **model requested in the actual Codex network message**, the **model reported by the server's completed response payload**, and the session ID. It keeps recording while the proxy and Codex remain open.

> “Final response model” means a string from `response.completed.response.model` or another completed server response payload. It does not independently prove which model weights or internal route produced the answer. If the request and completion cannot be paired, the requested model and session ID are shown as `Unknown`.

## 1. Requirements and download

- Windows 10/11 and the Codex desktop app or Codex CLI.
- **Python 3.12 or newer** and internet access for the one-time mitmproxy installation. The installer first checks for Codex's bundled Python 3.12. Otherwise, install Python from the [official Windows download page](https://www.python.org/downloads/windows/).
- Download `codex-model-probe-en-win64.zip` from [GitHub Releases](https://github.com/jinyounghub/codex-model-probe/releases), then **extract** it to a **writable folder** such as Documents. Keep all ZIP contents in the same folder. The EXE is unsigned; you can compare `Get-FileHash .\codex-model-probe-en-win64.zip -Algorithm SHA256` with the release's `SHA256SUMS.txt`.
- `CodexModelMonitor-en.exe` is the English GUI. The Korean GUI is in the Korean ZIP.

Open PowerShell in the extracted folder and run this **once**. The script installs pinned `mitmproxy==12.2.3` into a local `.venv` folder.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_mitmproxy.ps1
```

`ExecutionPolicy Bypass` applies only to this PowerShell process. Double-click `CodexModelMonitor-en.exe`. The `mitmdump` field should show `.venv\Scripts\mitmdump.exe`; if it does not, select that file with **Browse**.

## 2. Install the local certificate

The proxy must decrypt HTTPS traffic, so Codex must trust the **mitmproxy certificate generated on your PC**. See the [official mitmproxy certificate guide](https://docs.mitmproxy.org/stable/concepts/certificates/).

1. Leave **Capture mode** on **Manual HTTP proxy** and click **Start proxy**. This creates `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer` and `mitmproxy-ca-cert.pem`. Do not connect Codex yet.
2. Click **Open certificate file**. In the Windows Certificate Import Wizard, choose **Install Certificate**.
3. Select **Current User**. Select **Place all certificates in the following store**, click **Browse**, and choose **Trusted Root Certification Authorities**. Select **Next** and **Finish**.
4. Windows may display a security warning about trusting the certificate. Verify that this is the certificate you just generated locally and decide whether to accept it yourself. The tool does not accept this warning automatically.
5. Try **Connect Codex app on restart** or **Open Codex CLI via proxy**. Both buttons recheck that the exact current certificate is in the Current User root store. If you still see **Certificate trust required**, recheck the store location.

Keep the certificate installed while the proxied Codex process is running. Neither the certificate nor its private key is included in the release ZIP. Do not install a certificate supplied by another machine.

## 3A. Monitor the Codex desktop app continuously

1. Click **Start proxy**. The default listener is `127.0.0.1:8080`.
2. Complete the certificate installation above.
3. Click **Connect Codex app on restart**. The monitor waits until the current Codex app has **fully exited**.
4. Close all Codex app windows and background processes. The monitor reopens the installed app with proxy settings. Save current work before closing the app.
5. Send a message in the reopened Codex app. Look for a new row containing **Session ID**, **Requested model**, and **Final response model**. Later messages continue to accumulate while the monitor stays open.

The restart button locates the Windows Microsoft Store/Appx Codex app. It may not find other installation types. An already running app cannot inherit new proxy environment variables, so it must be reopened. Clicking **Start proxy** alone does not reroute an existing Codex app.

## 3B. Monitor Codex CLI continuously

1. Click **Start proxy** and install the certificate.
2. Optionally enter a model ID in **CLI model to request**. Leave it blank for Codex's default.
3. Click **Open Codex CLI via proxy**, send messages in the new console, and watch the GUI table.

This button sets `HTTP_PROXY`, `HTTPS_PROXY`, and `CODEX_CA_CERTIFICATE` only for the new CLI process and enables Codex's `respect_system_proxy` feature. It does not change Windows-wide proxy settings.

## 4. Read the table and results file

| Column | Source and meaning |
| --- | --- |
| Session ID, Thread ID | `client_metadata.session_id` and `client_metadata.thread_id` in the actual request |
| Requested model | `response.create.model` or the HTTP request body's `model` |
| Final response model | `response.completed.response.model`, or `model` on a completed non-streaming Response object |
| Value comparison | Literal string comparison only. **Values differ** is not a definitive conclusion about internal routing. |
| Response ID | Server response ID used to associate request and completion |
| Final payload field | Exact field used as evidence for the final model |

Records append to `results.jsonl` in the same folder. The file does not store raw prompts, response bodies, or authorization headers. It **does** contain session, thread, and turn IDs; treat it as personal data. The repository and release ZIPs exclude it. The GUI shows the latest 500 rows; the file continues to grow. Use the horizontal scrollbar for columns on the right.

The network payload does not include a human-readable conversation title, so the tool does not invent one. For WebSocket traffic, a request is associated with the next `response.created.response.id` on the same connection, then checked against `response.completed.response.id`. Uncertain associations are left blank.

## 5. Watch a proxy already owned by another GUI

If another monitor window is already running the proxy, do not start a second proxy on the same port. Open the EXE from the same folder with `--watch-only` to view its `results.jsonl`:

```powershell
.\CodexModelMonitor-en.exe --watch-only
```

Keep the original monitor window open because it owns the proxy. Closing the watch-only window does not stop that proxy.

## 6. Shutdown and troubleshooting

**Shutdown order:** fully close the Codex app or CLI that uses the proxy, click **Stop** in the monitor, then reopen Codex normally. If the proxy stops first, Codex may show `Reconnecting... waiting for network`. Closing the monitor also stops the proxy it started.

| Symptom | Check |
| --- | --- |
| **mitmdump required** | Run the installer and select `.venv\Scripts\mitmdump.exe`. |
| **Certificate trust required** | Install the current `.cer` under **Current User > Trusted Root Certification Authorities**. |
| Codex keeps reconnecting | Check that the proxy is running and Codex was restarted through it. If needed, close Codex, stop the proxy, and start Codex normally. |
| No new table row | Check that the app/CLI was reopened through the proxy, a response completed, and the **Hosts** field includes the actual host. |
| Requested model or session is **Unknown** | Only the completion may have been captured, or the request could not be paired with `response.created`. Try another request. |
| Port 8080 is occupied | Close the other proxy or select another port in the GUI. |

**Codex process capture (experimental)** caused connection errors on the machine used for testing. The recommended mode is **Manual HTTP proxy**. **Analyze capture file** can inspect a separate HAR/JSON/SSE file, although ordinary HAR exports may omit WebSocket messages.

## 7. Certificate removal and security

When you no longer need the proxy, restart Codex normally. You may then open Windows `certmgr.msc` and remove only this PC's mitmproxy certificate under **Current User > Trusted Root Certification Authorities > Certificates**. The `.mitmproxy` folder also contains the CA **private key**; never share or upload it. Removing the certificate or replacing the CA files requires a new certificate installation before the next use.

mitmproxy can read HTTPS traffic that passes through it. Use this only for your own Codex account and machine, and run the proxy only when needed. See the official [certificate](https://docs.mitmproxy.org/stable/concepts/certificates/) and [proxy mode](https://docs.mitmproxy.org/stable/concepts/modes/) documentation.

## Run and test from source

```powershell
python .\gui_en.py
python -m unittest discover -p 'test_*.py' -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_windows.ps1
python .\package_release.py
```

The GUI itself uses Python's standard library. Live capture requires `capture.py`, `model_probe.py`, and the mitmproxy installation in the same extracted folder.
