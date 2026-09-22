# Codex Model Probe

Live Windows GUI for inspecting the **requested model, session ID, and model reported in Codex's completed server response payload**. The two GUI editions have the same capture behavior.

- [English setup and user guide](README.en.md)
- [한국어 설치 및 사용 설명서](README.ko.md)

Download the Korean or English Windows ZIP from [Releases](https://github.com/jinyounghub/codex-model-probe/releases). Each ZIP contains its GUI EXE, the capture addon, the installer script, and the corresponding guide. No certificate, private key, request body, or captured session data is bundled.

The observed `response.completed.response.model` is a server payload field. It is not an independent audit of the physical model that produced the response.
