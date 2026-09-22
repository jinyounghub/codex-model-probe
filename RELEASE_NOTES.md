# Codex Model Probe v0.3.0

> **2026-09-22 / Defender 차단 확인:** ZIP의 `mitmdump.exe`가 `Trojan:Win64/WinDivert`로 탐지됐습니다. 차단된 PC에서는 간편 연결과 실시간 캡처가 동작하지 않습니다. 보안 검토 전까지 재패키징을 중단합니다. 수정 EXE는 아직 없습니다. [한국어 안내](https://github.com/jinyounghub/codex-model-probe/blob/main/DEFENDER.md#한국어).
>
> **Defender detection confirmed:** The bundled `mitmdump.exe` was detected as `Trojan:Win64/WinDivert`. Quick connect and live capture are unavailable where it is blocked. New packaging is on hold pending security review. No corrected EXE has been published. [Details](https://github.com/jinyounghub/codex-model-probe/blob/main/DEFENDER.md). The existing ZIP assets remain the original v0.3.0 files.

## 한국어

설치 스크립트가 필요 없는 버전입니다. [한글 ZIP](https://github.com/jinyounghub/codex-model-probe/releases)을 압축 해제하고 `CodexModelMonitor-ko.exe`를 연 뒤 **간편 연결 시작**을 누르세요. 처음에는 이 PC에서 생성된 인증서의 지문과 신뢰 범위를 확인하고 동의해야 합니다. 이후 Codex 앱을 완전히 닫으면 모니터가 프록시 환경으로 다시 엽니다. 자세한 내용은 [한글 설명서](https://github.com/jinyounghub/codex-model-probe/blob/main/README.ko.md)를 보세요.

ZIP에는 검증된 공식 mitmproxy 12.2.3 단독 실행 파일이 포함됩니다. Python 설치나 PowerShell 실행은 필요 없습니다. 프록시 포트는 자동으로 선택하고, 고급 설정은 필요할 때만 펼칩니다. 결과는 `%LOCALAPPDATA%\CodexModelProbe\results.jsonl`에 저장합니다.

## English

No setup script is required. Extract the [English ZIP](https://github.com/jinyounghub/codex-model-probe/releases), open `CodexModelMonitor-en.exe`, and click **Quick connect**. On the first run, review and confirm the locally generated certificate's fingerprint and trust scope. Fully close Codex; the monitor then reopens it through the proxy. See the [English guide](https://github.com/jinyounghub/codex-model-probe/blob/main/README.en.md).

The ZIP includes a verified official mitmproxy 12.2.3 standalone binary. No Python or PowerShell setup is needed. The GUI selects a free proxy port, hides advanced controls until requested, and stores results under `%LOCALAPPDATA%\CodexModelProbe\results.jsonl`.

Both ZIPs contain no certificate, private key, prompts, or captured results.
