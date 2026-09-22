# Codex Model Probe

**v0.4.0: download one installer, install, then click Quick connect.** Korean and English installers include Python and the explicit HTTP proxy. Process capture, WinDivert, and the old standalone `mitmdump.exe` are not part of this edition. [Why the architecture changed](DEFENDER.md).

**v0.4.0: 설치 파일 하나를 실행한 뒤 간편 연결을 누르세요.** 한국어·영어 설치판을 제공하며, 프로세스 캡처와 WinDivert 드라이버를 제거했습니다. [변경 이유](DEFENDER.md#한국어).

Live Windows GUI for inspecting the **requested model and reasoning effort**, the **model, reasoning effort, and reasoning token usage reported in Codex's completed server response**, plus local Codex project and conversation labels matched by thread ID. The two GUI editions have the same capture behavior.

- [English setup and user guide](README.en.md)
- [한국어 설치 및 사용 설명서](README.ko.md)

Download `CodexModelProbe-Setup-ko.exe` or `CodexModelProbe-Setup-en.exe` from [Releases](https://github.com/jinyounghub/codex-model-probe/releases/latest). Installation uses the current user's folder, creates shortcuts, and includes an uninstaller. Click **Quick connect / 간편 연결 시작**, confirm the local certificate on first use, then close Codex once so it can reopen with the proxy. No separate Python installation or setup script is needed. Portable ZIPs are also available; keep their `_internal` folder beside the EXE.

The installers do not change certificate trust or Defender settings. Certificate trust requires confirmation in the GUI. Releases include file hashes and dependency notices, and contain no private certificate, private key, request body, or captured session data. These builds are unsigned; this architecture change is not a guarantee that every security product will accept them.

The observed `response.completed.response.model` is a server payload field. It is not an independent audit of the physical model that produced the response.
