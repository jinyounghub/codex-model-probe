# Windows Defender detection in v0.3.0

## v0.4.0 architecture change

The new installer uses an embedded, explicit HTTP proxy built from the Python mitmproxy package. It removes process capture and transparent capture as product features. The bundle excludes `mitmproxy_windows`, `pydivert`, WinDivert, the Windows redirector, kernel drivers, and the old standalone `mitmdump.exe`. Upstream's unconditional transparent-mode platform import is replaced with an adapter that reports the feature as unsupported; the runtime exposes only regular HTTP mode on `127.0.0.1`. The restricted worker does not accept arbitrary proxy modes or scripts and does not load `config.yaml`.

Builds use an inspectable directory layout, include a file hash manifest and dependency notices, and reject forbidden components before packaging. The installer is per-user, includes shortcuts and uninstall support, and does not alter Defender settings or certificate trust. Certificate installation still requires the user's in-app confirmation. This is a capability and dependency reduction, not a determination that the old detection was a false positive. The application remains unsigned.

## 한국어

v0.4.0은 프로세스 캡처·투명 프록시 기능을 제거하고 일반 HTTP 프록시만 내장한 설치판입니다. WinDivert, `pydivert`, Windows 리디렉터, 드라이버, 기존 `mitmdump.exe`를 포함하지 않습니다. 인증서 신뢰는 앱에서 사용자 동의를 받은 뒤에만 설정합니다. 아래는 v0.3.0의 과거 탐지 기록이며, 기존 파일의 오탐 여부는 여전히 확정하지 않았습니다.

2026-09-22, v0.3.0 ZIP에 포함된 `mitmdump.exe`가 Microsoft Defender에서 **`Trojan:Win64/WinDivert`**로 탐지됐습니다. 해당 PC에서 실행 차단과 파일 제거를 확인했습니다. **차단된 PC에서는 간편 연결과 실시간 캡처를 사용할 수 없습니다.** 인증서를 다시 설치해도 이 문제는 해결되지 않습니다.

확인한 다운로드 ZIP은 공개 배포본과 SHA-256이 일치합니다. 배포 준비 당시 공식 mitmproxy 12.2.3 Windows 아카이브와 실행 파일의 해시를 검증했습니다. 출처와 무결성 확인은 악성 여부에 대한 판정을 대신하지 않으며, 현재 오탐으로 확정하지 않았습니다.

- Windows 보안 > 바이러스 및 위협 방지 > 보호 기록에서 `mitmdump.exe`의 탐지명을 확인하세요.
- 보안 차단 상태를 유지하고, 보안 검토 결과나 검증된 수정 배포본을 기다려 주세요. Defender 해제, 예외 추가 또는 격리 파일 복원은 해결 절차로 제공하지 않습니다.
- Codex가 프록시 연결 때문에 재연결 중이면 Codex를 완전히 닫고 평소 바로가기로 다시 여세요.
- 기존 결과 파일은 GUI의 `--watch-only`로 계속 열 수 있습니다. 새 통신은 수집되지 않습니다.

오류 안내는 WinError 225/226과 파일 누락을 구별합니다. 예전 `vendor_mitmdump.py`는 같은 실행 파일을 다시 내려받거나 재패키징하지 않도록 계속 중단 상태입니다. **기존 v0.3.0 ZIP에는 v0.4.0 변경 사항이 반영되지 않습니다.**

## English

On 2026-09-22, Microsoft Defender detected the `mitmdump.exe` bundled in v0.3.0 as **`Trojan:Win64/WinDivert`**. Execution was blocked and the file was removed on the affected PC. **Quick connect and live capture are unavailable on a PC where the runtime is blocked.** Reinstalling the certificate does not resolve this condition.

The downloaded Korean ZIP matches the published release's SHA-256. During release preparation, the official mitmproxy 12.2.3 Windows archive and executable were checked against the hashes below. Provenance and integrity checks do not establish whether a detection is correct. This detection has **not** been confirmed to be a false positive.

Check Windows Security > Virus & threat protection > Protection history for the detection on `mitmdump.exe`. Keep the block in place pending a security review or a verified corrected release. Disabling Defender, adding exclusions, or restoring the quarantined file is not a supported resolution. To recover ordinary Codex connectivity, fully close Codex and reopen it using its normal shortcut. Existing records can still be viewed with `--watch-only`; no new traffic is captured.

The source distinguishes WinError 225/226 from a missing executable. The legacy `vendor_mitmdump.py` still stops before downloading or repackaging the affected standalone runtime. **The existing v0.3.0 ZIPs do not include the v0.4.0 architecture changes.**

## Review evidence

No private capture data, local usernames, certificate material, or tokens are included here.

| Item | Value |
| --- | --- |
| Detection | `Trojan:Win64/WinDivert` |
| Defender threat ID | `2147861799` |
| Security intelligence version at observation | `1.459.327.0` |
| Defender action succeeded | `true` |
| Defender reported threat execution | `false` |
| Runtime | Official mitmproxy 12.2.3 Windows x86-64 standalone `mitmdump.exe` |
| Runtime SHA-256, verified during release preparation | `36a45aadeb842185b8064b8f0be3730e079c9f9c125bc8be22363332969857bf` |
| Official archive SHA-256 | `04a01ea95ae96df75058a893e774957d294e69012dab1f4e256ce2b0c6725483` |
| Korean v0.3.0 ZIP SHA-256 | `a35d066235a26f4b73323160a5708d5a80f94515cb83d68c1da00850e44f1338` |

`DidThreatExecute=false` describes this Defender record, not the entire history of the PC or an independent malware assessment. The quarantined file was not restored or executed for this investigation.

The runtime originally came from [the official mitmproxy snapshot](https://snapshots.mitmproxy.org/12.2.3/mitmproxy-12.2.3-windows-x86_64.zip). This link documents provenance; it is not a workaround recommendation.

[Microsoft's error reference](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-) defines 225 as a virus/PUA block and 226 as a virus/PUA file removal. Microsoft provides a [file analysis submission portal](https://www.microsoft.com/en-us/wdsi/filesubmission) for detection review. A submission has not been made by this project as part of this investigation.

There is an [upstream report about Defender flagging mitmproxy 12.2.2](https://github.com/mitmproxy/mitmproxy/issues/8184). That report concerns a different version and detection name and does not resolve the 12.2.3 / WinDivert observation here.
