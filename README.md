# Codex Model Probe

> **2026-09-22: v0.3.0 runtime blocked by Defender.** The bundled `mitmdump.exe` was detected as `Trojan:Win64/WinDivert`. Quick connect cannot work while it is blocked. New Windows packaging is on hold pending review; no corrected EXE is available yet. [Detection details and next steps](DEFENDER.md).
>
> **v0.3.0 Defender 차단 확인:** `mitmdump.exe`가 차단된 PC에서는 간편 연결을 사용할 수 없습니다. 재배포는 보안 검토 전까지 중단하며 수정 EXE는 아직 없습니다. [상세 안내](DEFENDER.md#한국어).

Live Windows GUI for inspecting the **requested model and reasoning effort**, the **model, reasoning effort, and reasoning token usage reported in Codex's completed server response**, plus local Codex project and conversation labels matched by thread ID. The two GUI editions have the same capture behavior.

- [English setup and user guide](README.en.md)
- [한국어 설치 및 사용 설명서](README.ko.md)

Download the Korean or English Windows ZIP from [Releases](https://github.com/jinyounghub/codex-model-probe/releases). Extract it, open the GUI EXE, and click **Quick connect / 간편 연결 시작**. Each ZIP includes the official standalone mitmdump, the capture addon, and a guide. No Python installation or PowerShell setup script is needed. No certificate, private key, request body, or captured session data is bundled.

The observed `response.completed.response.model` is a server payload field. It is not an independent audit of the physical model that produced the response.
