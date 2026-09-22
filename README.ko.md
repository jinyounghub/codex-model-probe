# Codex Model Probe: 한글판 사용 설명서

> **v0.4.0:** 설치 프로그램에 일반 HTTP 프록시를 내장했습니다. v0.3.0의 `mitmdump.exe`와 프로세스 캡처용 WinDivert 드라이버는 포함하지 않습니다. [변경 내역과 기존 탐지 기록](https://github.com/jinyounghub/codex-model-probe/blob/main/DEFENDER.md#한국어).

Codex가 **실제 통신에서 요청한 모델과 reasoning effort**, 서버의 **완료 응답 페이로드가 보고한 모델·reasoning effort·토큰 수**, 로컬 대화 제목과 프로젝트명을 실시간으로 나란히 보여주는 Windows 도구입니다. 한 번 검사하고 끝나는 방식이 아니라 프록시와 Codex를 켜둔 동안 계속 기록합니다.

> `최종 응답 모델`은 `response.completed.response.model` 등 서버 완료 페이로드의 문자열입니다. 실제 모델 가중치나 내부 라우팅을 독립적으로 증명하는 값은 아닙니다. 요청과 완료 응답을 연결할 수 없는 경우 요청 모델과 세션 ID는 `확인 불가`로 표시합니다.

## 1. 설치 파일 하나로 시작

Windows 10/11과 Windows Codex 데스크톱 앱이 필요합니다. **Python 설치와 PowerShell 스크립트 실행은 필요 없습니다.**

1. [최신 Releases](https://github.com/jinyounghub/codex-model-probe/releases/latest)에서 **`CodexModelProbe-Setup-ko.exe`**를 내려받아 실행하고 **설치**를 누릅니다. 현재 사용자 폴더에 설치되며 시작 메뉴와 바탕화면에 **Codex Model Probe (ko)** 바로가기가 생깁니다. 영문판 설치 파일은 `CodexModelProbe-Setup-en.exe`입니다.
2. 실행 파일을 열고 **간편 연결 시작**을 누릅니다. 처음 실행하면 로컬 프록시와 인증서를 준비합니다. 기본 포트가 사용 중이면 빈 포트를 자동으로 고릅니다.
3. 처음에만 표시되는 **인증서 신뢰 확인** 창에서 이 PC에서 만든 인증서의 SHA-256 지문과 신뢰 범위를 확인하고 선택합니다. 동의하면 앱이 Windows **현재 사용자 > 신뢰할 수 있는 루트 인증 기관**에 해당 인증서를 추가합니다. 관리자 권한은 요구하지 않습니다.
4. 현재 Codex 앱을 **완전히 종료**합니다. 모니터가 Codex를 프록시 환경으로 다시 열면 메시지를 보내고 표의 새 행을 확인합니다. 모니터 창을 켜두면 계속 기록됩니다.

이미 실행 중인 Codex에는 프록시 설정을 붙일 수 없어 **한 번 종료 후 재실행**해야 합니다. 이 방식은 Microsoft Store/Appx 형태의 Codex 앱을 자동으로 찾습니다. 기본 설치 위치는 `%LOCALAPPDATA%\Programs\CodexModelProbe-ko`이며 관리자 권한이나 별도 Python 설치가 필요 없습니다. 설치 프로그램 자체는 인증서를 추가하지 않습니다.

설치 없이 사용하려면 `codex-model-probe-ko-win64.zip`을 **새 폴더에 전부 압축 해제**하고 `CodexModelMonitor-ko.exe`를 실행하세요. `_internal` 폴더를 반드시 함께 유지하세요. 이전 v0.3.0 폴더에 덮어쓰지 마세요. 이전 `mitmdump.exe`는 필요하지 않습니다. 결과 기록과 현재 PC 인증서는 기존 위치를 사용합니다.

배포 파일에는 코드 서명이 없습니다. [SHA256SUMS.txt](https://github.com/jinyounghub/codex-model-probe/releases/latest)로 설치 파일·ZIP의 무결성을 확인할 수 있고, 설치 폴더의 `BUNDLE-MANIFEST.json`에는 내부 파일 해시가 있습니다. 모든 보안 제품에서 탐지가 발생하지 않는다고 보장하지는 않습니다.

## 2. 인증서와 연결 관리

인증서 신뢰는 HTTPS 내용을 읽는 프록시에 필요한 단계입니다. 간편 연결은 `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer`의 지문을 보여주고, 사용자가 동의한 뒤에만 **현재 사용자** 루트 저장소에 추가합니다. 인증서와 개인 키는 ZIP에 들어 있지 않습니다. 다른 PC에서 받은 인증서를 설치하지 마세요. [mitmproxy 공식 설명](https://docs.mitmproxy.org/stable/concepts/certificates/)을 참고하세요.

종료할 때는 프록시로 열린 Codex 앱을 먼저 닫고, 모니터의 **연결 중지**를 누른 뒤 Codex를 평소 방식으로 다시 여세요. 프록시가 먼저 꺼지면 Codex에 `Reconnecting... waiting for network`가 나타날 수 있습니다.

## 3. 고급 설정과 Codex CLI

**고급 설정 보기**를 누르면 수동 프록시 시작, 포트·호스트·결과 파일 설정, 인증서 파일 보기, CLI 연결 기능이 나옵니다. 내장 프록시는 `127.0.0.1`에서만 대기하며 HTTPS 분석 대상은 `chatgpt.com`, `api.openai.com`입니다. CLI를 사용하려면 프록시가 켜진 상태에서 인증서 신뢰를 마친 뒤 **프록시로 Codex CLI 열기**를 누릅니다. 이 버튼은 새 CLI 프로세스에만 프록시 환경 변수를 지정하며 Windows 전체 프록시 설정을 바꾸지 않습니다. 프로세스 캡처 모드는 제거했습니다.

## 4. 표와 결과 파일 읽기

| 열 | 출처와 의미 |
| --- | --- |
| 프로젝트, 대화 제목 | 요청의 대화 ID를 로컬 Codex 메타데이터와 연결한 표시 이름. 프로젝트 ID가 없으면 저장된 프로젝트 경로와 대화 작업 폴더가 일치하는지 확인합니다. |
| 세션 ID, 대화 ID | 실제 요청의 `client_metadata.session_id`, `client_metadata.thread_id` |
| 요청 모델 | 실제 `response.create.model` 또는 HTTP 요청 본문 `model` |
| 요청 reasoning | 실제 요청의 `reasoning.effort` (예: `high`, `xhigh`) |
| 최종 응답 모델 | 서버의 `response.completed.response.model`, 또는 완료된 일반 Response 객체의 `model` |
| 응답 reasoning | 서버 완료 응답의 `response.reasoning.effort` |
| reasoning 토큰 | 서버 완료 응답의 `usage.output_tokens_details.reasoning_tokens`. `0`은 서버가 0으로 보고한 값입니다. |
| 값 비교 | 위 두 문자열의 일치 여부만 비교합니다. `값 다름`은 내부 라우팅에 대한 확정 판정이 아닙니다. |
| 응답 ID | 요청과 완료 응답을 연결할 때 사용한 서버 응답 ID |
| 최종 페이로드 필드 | 최종 모델을 읽은 근거 필드 |

결과는 `%LOCALAPPDATA%\CodexModelProbe\results.jsonl`에 계속 추가됩니다. 요청/응답 reasoning effort와 응답 mode/context, reasoning 토큰 수도 기록합니다. 파일에 원본 프롬프트, 응답 본문, 인증 헤더, 대화 제목은 저장하지 않지만 **세션/대화/턴 ID**가 포함되므로 개인 데이터로 취급하세요. GitHub 저장소와 배포 ZIP에는 결과 파일이 들어 있지 않습니다. GUI에는 최신 500개 행을 표시하며 파일에는 계속 누적됩니다. 가로 스크롤로 오른쪽 열을 확인할 수 있습니다. 이전 버전의 결과 파일은 고급 설정에서 직접 선택할 수 있습니다.

서버 응답 자체에는 프로젝트나 대화 제목이 없습니다. GUI는 `~/.codex/state_5.sqlite`의 대화 ID와 표시 제목을 **읽기 전용**으로 연결하며, 저장된 프로젝트 경로로 프로젝트명을 찾습니다. 로컬 기록이 없거나 다른 호스트의 대화이면 `확인 불가`로 표시합니다. 응답 ID는 개별 응답을 식별하므로 대화 제목으로 바꾸지 않고 원래 값을 유지합니다. WebSocket에서는 같은 연결의 요청을 다음 `response.created.response.id`에 순서대로 연결하고 최종 `response.completed.response.id`로 검증합니다. 연결이 불확실하면 요청 정보는 비워 둡니다.

`reasoning.effort`는 요청 설정과 서버가 보고한 설정이며, 모델 내부의 실제 추론 과정이나 숨겨진 사고 내용을 보여주지는 않습니다. reasoning 토큰 수도 서버 사용량 보고값입니다. 필드가 없는 경우 `확인 불가`로 표시합니다. **기존 프록시가 이전 버전의 `capture.py`를 실행 중이면 새 필드는 다음 정상 재시작 후 기록됩니다.**

## 5. 기존 프록시의 기록만 보기

이미 다른 GUI 창이 프록시를 실행 중이면 두 번째 창에서 간편 연결을 누르지 마세요. 같은 폴더의 실행 파일을 `--watch-only`로 열면 기본 결과 파일을 읽기만 합니다.

```powershell
.\CodexModelMonitor-ko.exe --watch-only
```

기존 프록시를 소유한 원래 GUI 창을 닫으면 프록시도 종료됩니다. 기록만 보는 창을 닫아도 원래 프록시는 종료되지 않습니다.

## 6. 정상 종료 및 문제 해결

**종료 순서:** 프록시로 열린 Codex 앱/CLI를 먼저 완전히 닫고, GUI의 `연결 중지`를 누른 뒤, Codex를 평소 방식으로 다시 엽니다. 프록시를 먼저 끄면 Codex에 `Reconnecting... waiting for network`가 보일 수 있습니다. GUI 창을 닫아도 그 창이 시작한 프록시가 종료됩니다.

| 증상 | 확인할 것 |
| --- | --- |
| `WinError 225/226` 또는 `프록시 보안 차단` | 보안 프로그램이 실행을 차단하거나 파일을 제거한 상태. Windows 보안의 보호 기록과 [차단 관련 안내](https://github.com/jinyounghub/codex-model-probe/blob/main/DEFENDER.md#한국어) 확인. 인증서 재설치로 해결되지 않습니다. |
| `mitmdump 필요` 또는 `프록시 파일을 찾을 수 없음` | 먼저 Windows 보안의 보호 기록 확인. 차단 기록이 없을 때 ZIP 압축 해제 위치와 실행 파일 경로 확인 |
| `인증서 신뢰 필요` | 간편 연결의 인증서 확인에서 동의했는지 확인. 차단된 경우 고급 설정의 `인증서 파일 보기`로 수동 설치 |
| Codex 앱이 다시 연결 중 | 프록시가 계속 실행 중인지, 앱이 프록시 환경으로 재시작됐는지 확인. 필요하면 앱을 닫고 프록시를 중지한 뒤 일반 방식으로 재실행 |
| 표에 새 행이 없음 | 앱/CLI가 새로 프록시로 열렸는지, 실제 응답이 완료됐는지, `호스트` 목록이 맞는지 확인 |
| 요청 모델/세션 ID가 `확인 불가` | 완료 메시지만 잡혔거나 요청과 `response.created`를 연결하지 못한 경우. 다음 요청부터 다시 확인 |
| 포트 8080 사용 중 | 간편 연결은 빈 포트를 자동 선택합니다. 수동 모드에서는 고급 설정에서 포트를 변경하세요. |

v0.4.0부터 프로세스 캡처 모드는 제공하지 않습니다. 간편 연결과 수동 시작 모두 일반 HTTP 프록시를 사용합니다. `캡처 파일 분석`은 외부 HAR/JSON/SSE 파일의 서버 완료 응답을 읽으며, 일반 HAR에는 WebSocket 메시지가 없을 수 있습니다.

## 7. 인증서 제거와 보안

더 이상 프록시를 사용하지 않을 때는 Codex를 일반 방식으로 다시 실행한 다음 Windows `certmgr.msc`의 **현재 사용자 > 신뢰할 수 있는 루트 인증 기관 > 인증서**에서 이 PC의 mitmproxy 인증서만 선택해 제거할 수 있습니다. `.mitmproxy` 폴더에는 CA **개인 키**도 있으므로 공유하거나 GitHub에 업로드하지 마세요. 인증서를 제거하거나 CA 파일을 바꾸면 다음 사용 때 새 인증서를 다시 설치해야 합니다.

mitmproxy는 통과하는 HTTPS 트래픽을 해독할 수 있습니다. 본인 PC와 본인 계정의 Codex 연결에만 사용하고, 필요할 때만 프록시를 켜세요. [mitmproxy 공식 인증서 안내](https://docs.mitmproxy.org/stable/concepts/certificates/)와 [프록시 모드 안내](https://docs.mitmproxy.org/stable/concepts/modes/)를 참고하세요.

## 소스에서 실행·테스트

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_mitmproxy.ps1
python .\gui_ko.py
python -m unittest discover -p 'test_*.py' -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_windows.ps1
python .\package_release.py
```

개발 환경의 Python은 3.12 이상이며 `mitmproxy==12.2.3`을 사용합니다. GUI와 `proxy_runtime.py`, `capture.py`, `model_probe.py`, `codex_metadata.py`, `translations.py`를 함께 둡니다. 실시간 캡처는 내장 worker가 담당합니다. `build_windows.ps1` 한 번으로 두 언어의 폴더형 앱, 설치 EXE, 휴대용 ZIP, SHA-256 목록을 생성합니다. 빌드 도구용 Inno Setup은 공식 다운로드의 서명을 검증한 뒤 준비합니다. 배포 전에 WinDivert·리디렉터·드라이버·개인 기록 포함 여부와 내부 파일 해시를 검사합니다. 예전 `vendor_mitmdump.py` 경로는 계속 중단 상태입니다.

## 8. 업데이트와 제거

프록시를 사용하는 Codex와 모니터를 종료한 뒤 새 설치 파일을 실행하세요. 제거는 Windows **설정 > 앱 > 설치된 앱 > Codex Model Probe**에서 할 수 있습니다. 제거해도 결과 기록과 사용자 인증서는 보존합니다. 인증서를 더 이상 사용하지 않으면 위 7절에 따라 해당 인증서만 직접 제거하세요.
