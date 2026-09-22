# Codex Model Probe: 한글판 사용 설명서

Codex가 **실제 통신에서 요청한 모델과 reasoning effort**, 서버의 **완료 응답 페이로드가 보고한 모델·reasoning effort·토큰 수**, 로컬 대화 제목과 프로젝트명을 실시간으로 나란히 보여주는 Windows 도구입니다. 한 번 검사하고 끝나는 방식이 아니라 프록시와 Codex를 켜둔 동안 계속 기록합니다.

> `최종 응답 모델`은 `response.completed.response.model` 등 서버 완료 페이로드의 문자열입니다. 실제 모델 가중치나 내부 라우팅을 독립적으로 증명하는 값은 아닙니다. 요청과 완료 응답을 연결할 수 없는 경우 요청 모델과 세션 ID는 `확인 불가`로 표시합니다.

## 1. 준비 및 다운로드

- Windows 10/11, Codex 데스크톱 앱 또는 Codex CLI가 필요합니다.
- mitmproxy 설치에는 **Python 3.12 이상**과 인터넷 연결이 필요합니다. 이 PC에 Codex 번들 Python 3.12가 있으면 설치 스크립트가 먼저 사용합니다. 없으면 [Python 공식 다운로드](https://www.python.org/downloads/windows/)에서 설치하세요.
- [GitHub Releases](https://github.com/jinyounghub/codex-model-probe/releases)에서 `codex-model-probe-ko-win64.zip`을 다운로드하고 **쓰기 가능한 폴더**(예: 문서)에 **압축을 풉니다**. ZIP 안의 파일을 같은 폴더에 둡니다. 실행 파일은 코드 서명이 되어 있지 않으므로 배포 페이지의 `SHA256SUMS.txt`와 `Get-FileHash .\codex-model-probe-ko-win64.zip -Algorithm SHA256` 결과를 비교할 수 있습니다.
- `CodexModelMonitor-ko.exe`가 한글 GUI 실행 파일입니다. `CodexModelMonitor-en.exe`는 영문판 ZIP에 있습니다.

압축을 푼 폴더에서 PowerShell을 열어 다음을 **한 번** 실행하세요. 인터넷에서 고정 버전 `mitmproxy==12.2.3`을 설치하고 같은 폴더에 `.venv`를 만듭니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_mitmproxy.ps1
```

`ExecutionPolicy Bypass`는 이 PowerShell 프로세스에만 적용됩니다. 설치 후 `CodexModelMonitor-ko.exe`를 더블클릭하세요. `mitmdump` 칸에 `.venv\Scripts\mitmdump.exe`가 자동으로 표시되어야 합니다. 표시되지 않으면 `찾기`에서 그 파일을 선택하세요.

## 2. 인증서 설치

프록시는 HTTPS 내용을 읽으므로 **이 PC에서 생성된 mitmproxy 인증서**를 현재 사용자 루트 저장소에서 신뢰해야 합니다. [mitmproxy 공식 인증서 설명](https://docs.mitmproxy.org/stable/concepts/certificates/)도 참고하세요.

1. GUI에서 캡처 방식을 `수동 HTTP 프록시`로 두고 `프록시 시작`을 누릅니다. 이때 `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer`와 `mitmproxy-ca-cert.pem`이 생성됩니다. 아직 Codex 연결 예약을 누르지 마세요.
2. `인증서 파일 보기`를 눌러 Windows 인증서 가져오기 마법사를 엽니다. **인증서 설치**를 선택합니다.
3. 저장소 위치로 **현재 사용자**를 선택합니다. `모든 인증서를 다음 저장소에 저장`을 선택하고 `찾아보기`에서 **신뢰할 수 있는 루트 인증 기관**을 고릅니다. `다음` → `마침`을 누릅니다.
4. Windows가 신뢰 여부를 묻는 보안 경고를 표시하면 인증서가 방금 이 PC의 mitmproxy에서 생성한 파일인지 직접 확인하고 결정합니다. 자동으로 이 경고를 수락하지 않습니다.
5. 설치가 끝나면 GUI의 `Codex 앱 연결 예약` 또는 `프록시로 Codex CLI 열기`를 눌러보세요. 두 버튼은 현재 인증서가 사용자 루트 저장소에 들어 있는지 다시 검사합니다. `인증서 신뢰 필요`가 나오면 저장소 위치를 다시 확인하세요.

**프록시를 끄고 Codex를 일반 방식으로 다시 열기 전에는 인증서를 제거하지 마세요.** 인증서와 개인 키는 배포 ZIP에 들어 있지 않습니다. 다른 PC에서 받은 인증서를 설치하지 마세요.

## 3A. Codex 데스크톱 앱을 계속 모니터링

1. GUI에서 `프록시 시작`을 누르고 상단에 캡처 실행 상태가 뜨는지 확인합니다. 기본 주소는 `127.0.0.1:8080`입니다.
2. 위의 인증서 설치를 마칩니다.
3. `Codex 앱 연결 예약`을 누릅니다. 버튼은 현재 Codex 앱이 **완전히 종료**될 때까지 기다립니다.
4. 열려 있는 Codex 앱의 창과 백그라운드 프로세스를 모두 종료합니다. GUI가 설치된 Codex 앱을 프록시 환경으로 다시 엽니다. 현재 진행 중인 대화는 앱이 다시 열릴 때 복원되지만, 종료 전에 작업을 저장하세요.
5. 새로 열린 Codex 앱에서 메시지를 보냅니다. GUI 표에 `세션 ID`, `요청 모델`, `최종 응답 모델`이 추가되는지 확인합니다. 창과 프록시를 켜둔 동안 이후 메시지도 누적됩니다.

이 버튼은 Microsoft Store/Appx 형태의 Windows Codex 앱을 찾습니다. 다른 설치 방식에서는 앱을 찾지 못할 수 있습니다. 이미 실행 중인 앱에 프록시 환경 변수를 붙일 수는 없으므로 앱을 다시 열어야 합니다. `프록시 시작`만 누르면 기존 앱은 프록시를 사용하지 않습니다.

## 3B. Codex CLI를 계속 모니터링

1. `프록시 시작` 및 인증서 설치를 마칩니다.
2. 원하는 경우 `CLI 요청 모델 (선택)`에 모델 ID를 입력합니다. 빈칸이면 Codex 기본값을 사용합니다.
3. `프록시로 Codex CLI 열기`를 누릅니다. 새 콘솔의 Codex에서 메시지를 보내고 GUI 표를 확인합니다.

이 버튼은 새 CLI 프로세스에만 `HTTP_PROXY`, `HTTPS_PROXY`, `CODEX_CA_CERTIFICATE`를 지정하고 Codex의 `respect_system_proxy` 기능을 켭니다. Windows 전체 프록시 설정을 변경하지 않습니다.

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

결과는 같은 폴더의 `results.jsonl`에 계속 추가됩니다. 요청/응답 reasoning effort와 응답 mode/context, reasoning 토큰 수도 기록합니다. 파일에 원본 프롬프트, 응답 본문, 인증 헤더, 대화 제목은 저장하지 않지만 **세션/대화/턴 ID**가 포함되므로 개인 데이터로 취급하세요. GitHub 저장소와 배포 ZIP에는 결과 파일이 들어 있지 않습니다. GUI에는 최신 500개 행을 표시하며 파일에는 계속 누적됩니다. 가로 스크롤로 오른쪽 열을 확인할 수 있습니다.

서버 응답 자체에는 프로젝트나 대화 제목이 없습니다. GUI는 `~/.codex/state_5.sqlite`의 대화 ID와 표시 제목을 **읽기 전용**으로 연결하며, 저장된 프로젝트 경로로 프로젝트명을 찾습니다. 로컬 기록이 없거나 다른 호스트의 대화이면 `확인 불가`로 표시합니다. 응답 ID는 개별 응답을 식별하므로 대화 제목으로 바꾸지 않고 원래 값을 유지합니다. WebSocket에서는 같은 연결의 요청을 다음 `response.created.response.id`에 순서대로 연결하고 최종 `response.completed.response.id`로 검증합니다. 연결이 불확실하면 요청 정보는 비워 둡니다.

`reasoning.effort`는 요청 설정과 서버가 보고한 설정이며, 모델 내부의 실제 추론 과정이나 숨겨진 사고 내용을 보여주지는 않습니다. reasoning 토큰 수도 서버 사용량 보고값입니다. 필드가 없는 경우 `확인 불가`로 표시합니다. **기존 프록시가 이전 버전의 `capture.py`를 실행 중이면 새 필드는 다음 정상 재시작 후 기록됩니다.**

## 5. 기존 프록시의 기록만 보기

이미 다른 GUI 창이 프록시를 실행 중이면 두 번째 창에서 `프록시 시작`을 누르지 마세요. 같은 폴더의 실행 파일을 `--watch-only`로 열면 기존 `results.jsonl`을 읽기만 합니다.

```powershell
.\CodexModelMonitor-ko.exe --watch-only
```

기존 프록시를 소유한 원래 GUI 창을 닫으면 프록시도 종료됩니다. 기록만 보는 창을 닫아도 원래 프록시는 종료되지 않습니다.

## 6. 정상 종료 및 문제 해결

**종료 순서:** 프록시로 열린 Codex 앱/CLI를 먼저 완전히 닫고, GUI의 `중지`를 누른 뒤, Codex를 평소 방식으로 다시 엽니다. 프록시를 먼저 끄면 Codex에 `Reconnecting... waiting for network`가 보일 수 있습니다. GUI 창을 닫아도 그 창이 시작한 프록시가 종료됩니다.

| 증상 | 확인할 것 |
| --- | --- |
| `mitmdump 필요` | 설치 스크립트를 실행하고 `.venv\Scripts\mitmdump.exe`를 선택했는지 확인 |
| `인증서 신뢰 필요` | **현재 사용자 > 신뢰할 수 있는 루트 인증 기관**에 현재 `.cer` 파일을 설치했는지 확인 |
| Codex 앱이 다시 연결 중 | 프록시가 계속 실행 중인지, 앱이 프록시 환경으로 재시작됐는지 확인. 필요하면 앱을 닫고 프록시를 중지한 뒤 일반 방식으로 재실행 |
| 표에 새 행이 없음 | 앱/CLI가 새로 프록시로 열렸는지, 실제 응답이 완료됐는지, `호스트` 목록이 맞는지 확인 |
| 요청 모델/세션 ID가 `확인 불가` | 완료 메시지만 잡혔거나 요청과 `response.created`를 연결하지 못한 경우. 다음 요청부터 다시 확인 |
| 포트 8080 사용 중 | 다른 모니터/프로그램이 8080을 쓰는지 확인하고 GUI의 포트를 바꾸거나 기존 프록시를 중지 |

`Codex 프로세스 캡처 (실험적)`는 이 PC에서 Codex 연결 오류를 일으킨 적이 있어 권장 경로는 **수동 HTTP 프록시**입니다. `캡처 파일 분석`은 외부 HAR/JSON/SSE 파일의 서버 완료 응답을 읽으며, 일반 HAR에는 WebSocket 메시지가 없을 수 있습니다.

## 7. 인증서 제거와 보안

더 이상 프록시를 사용하지 않을 때는 Codex를 일반 방식으로 다시 실행한 다음 Windows `certmgr.msc`의 **현재 사용자 > 신뢰할 수 있는 루트 인증 기관 > 인증서**에서 이 PC의 mitmproxy 인증서만 선택해 제거할 수 있습니다. `.mitmproxy` 폴더에는 CA **개인 키**도 있으므로 공유하거나 GitHub에 업로드하지 마세요. 인증서를 제거하거나 CA 파일을 바꾸면 다음 사용 때 새 인증서를 다시 설치해야 합니다.

mitmproxy는 통과하는 HTTPS 트래픽을 해독할 수 있습니다. 본인 PC와 본인 계정의 Codex 연결에만 사용하고, 필요할 때만 프록시를 켜세요. [mitmproxy 공식 인증서 안내](https://docs.mitmproxy.org/stable/concepts/certificates/)와 [프록시 모드 안내](https://docs.mitmproxy.org/stable/concepts/modes/)를 참고하세요.

## 소스에서 실행·테스트

```powershell
python .\gui_ko.py
python -m unittest discover -p 'test_*.py' -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_windows.ps1
python .\package_release.py
```

GUI 소스는 표준 라이브러리로 실행되며, 실시간 캡처에는 같은 폴더의 `capture.py`, `model_probe.py` 및 설치한 mitmproxy가 필요합니다. 소스에서 GUI를 실행할 때는 `codex_metadata.py`도 같은 폴더에 둡니다.
