"""Text for the two Windows GUI editions."""

EN = {
    "확인 불가": "Unknown",
    "값 일치": "Values match",
    "값 다름": "Values differ",
    "Codex 프로세스를 확인할 수 없습니다": "Could not inspect Codex processes",
    "Codex 프로세스 수를 읽을 수 없습니다": "Could not read the Codex process count",
    "대기 중": "Waiting",
    "Codex 요청·최종 모델 및 세션 모니터": "Codex Request, Final Model & Session Monitor",
    "수동 HTTP 프록시": "Manual HTTP proxy",
    "Codex 프로세스 캡처 (실험적)": "Codex process capture (experimental)",
    "기존 프록시 결과 감시 중": "Watching an existing proxy result file",
    "중지됨 · 응답 기록 대기": "Stopped · waiting for response records",
    "실시간 캡처 설정": "Live capture settings",
    "결과 파일": "Results file",
    "캡처 방식": "Capture mode",
    "대상 프로세스": "Target process",
    "수동 프록시 포트": "Manual proxy port",
    "호스트": "Hosts",
    "CLI 요청 모델 (선택)": "CLI model to request (optional)",
    "프록시 시작": "Start proxy",
    "중지": "Stop",
    "프록시 주소 복사": "Copy proxy address",
    "프록시로 Codex CLI 열기": "Open Codex CLI via proxy",
    "Codex 앱 연결 예약": "Connect Codex app on restart",
    "인증서 파일 보기": "Open certificate file",
    "캡처 파일 분석": "Analyze capture file",
    "사용 설명서": "User guide",
    "수신한 서버 메시지": "Server messages received",
    "최종 모델 이벤트": "Final model events",
    "모델 확인 불가": "Model unknown",
    "마지막 모델": "Latest model",
    "최종 응답 기록": "Completed response records",
    "시각": "Time",
    "프로젝트": "Project",
    "대화 제목": "Conversation title",
    "세션 ID": "Session ID",
    "요청 모델": "Requested model",
    "요청 reasoning": "Requested reasoning",
    "최종 응답 모델": "Final response model",
    "응답 reasoning": "Response reasoning",
    "reasoning 토큰": "Reasoning tokens",
    "값 비교": "Value comparison",
    "대화 ID": "Thread ID",
    "응답 ID": "Response ID",
    "통신": "Transport",
    "최종 페이로드 필드": "Final payload field",
    "모델·reasoning은 실제 요청과 서버 완료 응답에서 읽고, 프로젝트·대화 제목은 로컬 Codex 메타데이터에서 대화 ID로 찾습니다. 연결할 수 없는 정보는 '확인 불가'로 표시합니다.":
        "Models and reasoning come from actual requests and completed server responses. Project and conversation labels come from local Codex metadata matched by thread ID. Unavailable fields show as Unknown.",
    "로컬 Codex 프로세스": "Local Codex process",
    "찾기": "Browse",
    "mitmdump 실행 파일 선택": "Select mitmdump executable",
    "결과 JSONL 파일": "Results JSONL file",
    "mitmdump 필요": "mitmdump required",
    "mitmdump 실행 파일을 선택하세요. 설치 방법은 README.md에 있습니다.":
        "Select mitmdump.exe. Installation instructions are in the user guide.",
    "인증서 신뢰 필요": "Certificate trust required",
    "현재 mitmproxy 인증서가 Windows의 신뢰할 수 있는 루트 인증 기관에 없습니다. 먼저 '인증서 파일 보기'에서 현재 사용자 루트 저장소에 설치하세요. 설치 전 캡처를 시작하면 Codex 연결이 끊길 수 있습니다.":
        "The current mitmproxy certificate is not in the Windows Trusted Root store. Use Open certificate file and install it under Current User > Trusted Root Certification Authorities before capture.",
    "대상 오류": "Target error",
    "캡처할 프로세스 이름을 입력하세요.": "Enter a target process name.",
    "포트 오류": "Port error",
    "포트는 1부터 65535까지의 숫자여야 합니다.": "Port must be a number from 1 to 65535.",
    "호스트 오류": "Host error",
    "캡처할 정확한 호스트를 입력하세요.": "Enter the exact hosts to capture.",
    "프록시 실행 실패": "Could not start proxy",
    "캡처 시작 중 · {label}": "Starting capture · {label}",
    "프록시 중지 중": "Stopping proxy",
    "복사됨: {address}": "Copied: {address}",
    "프록시 필요": "Proxy required",
    "먼저 수동 HTTP 프록시를 시작하세요.": "Start the manual HTTP proxy first.",
    "Codex CLI 없음": "Codex CLI not found",
    "codex.exe를 PATH에서 찾지 못했습니다.": "codex.exe was not found on PATH.",
    "mitmproxy 인증서를 현재 사용자 루트 저장소에 설치하세요.":
        "Install the mitmproxy certificate in the Current User Trusted Root store.",
    "프록시 준비 중": "Proxy not ready",
    "프록시가 아직 포트에서 대기하지 않습니다. 잠시 후 다시 누르세요.":
        "The proxy is not listening yet. Try again shortly.",
    "Codex CLI 실행 실패": "Could not start Codex CLI",
    "기본값": "default",
    "Codex CLI 새 창 실행 · 요청 모델 {model} · 응답 대기":
        "Codex CLI opened · requested model {model} · waiting for response",
    "Codex 앱 없음": "Codex app not found",
    "설치된 Codex 데스크톱 앱의 ChatGPT.exe를 찾지 못했습니다.":
        "Could not find the installed Codex desktop app's ChatGPT.exe.",
    "프록시가 아직 포트에서 대기하지 않습니다.": "The proxy is not listening yet.",
    "Codex 앱 종료 대기 · 앱을 완전히 닫으면 프록시로 다시 엽니다":
        "Waiting for Codex to close · it will reopen through the proxy",
    "Codex 앱 프록시 환경으로 다시 열림 · 서버 응답 대기":
        "Codex app reopened with proxy settings · waiting for server response",
    "Codex 앱 재실행 실패: {error}": "Could not reopen Codex app: {error}",
    "인증서 없음": "Certificate not found",
    "캡처를 한 번 시작한 뒤 다시 시도하세요.": "Start capture once, then try again.",
    "인증서 위치": "Certificate location",
    "서버 응답 캡처 선택": "Select server response capture",
    "캡처 파일": "Capture files",
    "모든 파일": "All files",
    "파일 분석 실패": "Could not analyze file",
    "결과": "Result",
    "서버의 최종 응답 페이로드를 찾지 못했습니다.":
        "No completed server response payload was found.",
    "파일": "File",
    "파일 분석 완료 · 최종 응답 {count}개":
        "File analysis complete · {count} completed responses",
    "서버 응답 감지 · 최종 페이로드 대기":
        "Server response seen · waiting for final payload",
    "최종 응답 모델 확인": "Final response model found",
    "최종 응답 모델 확인 불가": "Final response model unknown",
    "프록시 종료됨 · 코드 {code}": "Proxy exited · code {code}",
    "캡처 실행 중 · {label} · 트래픽 대기":
        "Capture running · {label} · waiting for traffic",
    "프록시 메시지: {message}": "Proxy message: {message}",
    "결과 파일 읽기 오류: {error}": "Could not read results file: {error}",
}


def translate(value: str, language: str) -> str:
    if language == "ko":
        return value
    if language == "en":
        return EN[value]
    raise ValueError(f"Unsupported language: {language}")
