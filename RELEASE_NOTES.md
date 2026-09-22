# Codex Model Probe v0.2.0

This update adds local Codex project and conversation labels to the GUI, matched by the request thread ID. It also shows the requested and server-reported `reasoning.effort` and the server-reported reasoning token count. The response ID remains visible. Missing metadata is shown as Unknown / 확인 불가. Existing proxies must be restarted normally to load the updated capture addon.

## 한국어

`codex-model-probe-ko-win64.zip`을 다운로드해 압축을 푸세요. 한글 GUI EXE, 캡처 애드온, mitmproxy 설치 스크립트, 자세한 [한글 설명서](https://github.com/jinyounghub/codex-model-probe/blob/main/README.ko.md)가 들어 있습니다. **EXE만 따로 실행하면 프록시 구성 파일이 없어 캡처를 시작할 수 없습니다.** ZIP 전체를 압축 해제해 사용하세요.

1. `powershell -NoProfile -ExecutionPolicy Bypass -File .\install_mitmproxy.ps1`
2. `CodexModelMonitor-ko.exe` 실행 → `프록시 시작`
3. 설명서에 따라 이 PC에서 생성된 mitmproxy 인증서를 **현재 사용자 > 신뢰할 수 있는 루트 인증 기관**에 설치
4. `Codex 앱 연결 예약` 또는 `프록시로 Codex CLI 열기`

## English

Download and extract `codex-model-probe-en-win64.zip`. It contains the English GUI EXE, capture addon, mitmproxy installer, and the full [English guide](https://github.com/jinyounghub/codex-model-probe/blob/main/README.en.md). **Do not run the EXE alone without extracting the other files.**

1. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\install_mitmproxy.ps1`.
2. Open `CodexModelMonitor-en.exe` and click **Start proxy**.
3. Install the locally generated mitmproxy certificate under **Current User > Trusted Root Certification Authorities**, as described in the guide.
4. Choose **Connect Codex app on restart** or **Open Codex CLI via proxy**.

Both editions display the requested model, completed server payload model, reasoning metadata, local conversation labels, session ID, thread ID, and response ID. `Values differ` compares payload strings; it does not independently verify internal model routing. The archives contain no certificate, private key, request body, or captured session data.
