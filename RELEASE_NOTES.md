# Codex Model Probe v0.4.0

## 한국어

**`CodexModelProbe-Setup-ko.exe` 하나를 내려받아 설치하세요.** 시작 메뉴/바탕화면의 Codex Model Probe를 연 뒤 **간편 연결 시작 → 최초 인증서 확인 → Codex 완전히 종료** 순서로 진행하면 모니터가 Codex를 다시 연결합니다. Python 설치나 스크립트 실행은 필요 없습니다.

- 일반 HTTP 프록시를 앱에 내장하고 프로세스 캡처·투명 프록시 기능을 제거했습니다.
- WinDivert, Windows 리디렉터, 캡처 드라이버 및 이전 standalone `mitmdump.exe`를 배포하지 않습니다.
- 현재 사용자 폴더에 설치하며 바로가기와 제거 기능을 제공합니다.
- 인증서 신뢰는 GUI에서 동의한 뒤에만 추가합니다. 설치 프로그램은 Defender 설정과 인증서 저장소를 바꾸지 않습니다.
- 요청/완료 응답 모델, reasoning, 대화 제목·프로젝트 표시 기능을 유지합니다.
- 설치 파일과 휴대용 ZIP의 SHA-256 목록, 내부 파일 해시, 의존성 라이선스를 제공합니다.

휴대용 ZIP은 새 폴더에 전부 압축 해제하고 `_internal` 폴더를 함께 유지하세요. v0.3.0 파일에 덮어쓰지 마세요. 결과 기록과 로컬 인증서는 기존 위치를 사용합니다. 프로그램 제거 시 이 사용자 데이터는 보존합니다.

[한글 사용법](https://github.com/jinyounghub/codex-model-probe/blob/main/README.ko.md) · [기존 Defender 탐지와 구조 변경](https://github.com/jinyounghub/codex-model-probe/blob/main/DEFENDER.md#한국어)

## English

**Download and install the single `CodexModelProbe-Setup-en.exe` file.** Open Codex Model Probe from the desktop/Start menu, click **Quick connect**, confirm the local certificate on first use, then fully close Codex once. The monitor reopens Codex through the proxy. No separate Python or setup script is needed.

- Embeds an explicit HTTP proxy and removes process/transparent capture.
- Excludes WinDivert, the Windows redirector, capture drivers, and the old standalone `mitmdump.exe`.
- Installs for the current user with shortcuts and an uninstaller.
- Requires in-app consent before adding certificate trust. The installer does not change Defender settings or certificate trust.
- Preserves requested/completed models, reasoning metadata, and local conversation/project labels.
- Includes artifact SHA-256 sums, an internal file manifest, and dependency notices.

Extract portable ZIPs into a new folder and keep `_internal` beside the EXE. Do not overlay v0.3.0. Existing results and certificates retain their locations and are preserved when uninstalling.

[English guide](https://github.com/jinyounghub/codex-model-probe/blob/main/README.en.md) · [Historical detection and architecture change](https://github.com/jinyounghub/codex-model-probe/blob/main/DEFENDER.md)

These application/installer builds are unsigned. Removing unused capture capabilities does not establish that the old binary's detection was a false positive or guarantee acceptance by every security product.

## 검증 / Verification

- 한국어·영어 GUI 및 내장 프록시 시작 검사 통과. / Both GUI editions and embedded proxy startup checks passed.
- 회귀 테스트 33개 통과. / 33 regression tests passed.
- 실제 Codex WebSocket 완료 응답에서 요청/응답 모델과 reasoning 필드 수신 확인. / Live Codex WebSocket completion capture verified, including request/response model and reasoning fields.
- 현재 사용자 설치·실행·제거 테스트 통과. / Per-user installation, execution, and uninstall tested.
- 2026-09-22 이 Windows PC에서 실시간 보호를 켠 상태로 최종 배포 폴더를 Defender 사용자 지정 검사했고, 해당 파일 탐지 기록은 0건이었습니다. 정의 버전: `1.459.327.0`. / A Defender custom scan of the final release folder on this Windows PC completed with real-time protection enabled and no detections for these artifacts (security intelligence `1.459.327.0`). This is a result for this machine and definition version.
