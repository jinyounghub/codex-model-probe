# Codex Model Probe

Live Windows GUI for inspecting the **requested model and reasoning effort**, the **model, reasoning effort, and reasoning token usage reported in Codex's completed server response**, plus local Codex project and conversation labels matched by thread ID. The two GUI editions have the same capture behavior.

- [English setup and user guide](README.en.md)
- [한국어 설치 및 사용 설명서](README.ko.md)

Download the Korean or English Windows ZIP from [Releases](https://github.com/jinyounghub/codex-model-probe/releases). Extract it, open the GUI EXE, and click **Quick connect / 간편 연결 시작**. Each ZIP includes the official standalone mitmdump, the capture addon, and a guide. No Python installation or PowerShell setup script is needed. No certificate, private key, request body, or captured session data is bundled.

The observed `response.completed.response.model` is a server payload field. It is not an independent audit of the physical model that produced the response.
