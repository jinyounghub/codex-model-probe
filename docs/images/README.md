# Published screenshots / 공개용 스크린샷

These PNGs are actual captures of the running Korean GUI supplied by the project owner. They were edited locally without generative image editing. The overview uses the owner's newer capture; the expanded view retains the earlier capture with the same blur style.

| Image | Redacted values |
| --- | --- |
| `live-overview-redacted.png` | Timestamps, project names, conversation titles |
| `live-details-redacted.png` | Timestamps, project names, conversation titles, session IDs, thread IDs, response IDs |

Private cell pixels were completely replaced with a white background and neutral placeholder text, then Gaussian blur was applied to those placeholders. The blurred shapes contain no original identifying text. This keeps a soft, row-by-row blur appearance without retaining the original private pixels.

The original dimensions are retained. Pixels outside the redacted regions were compared with the originals and are unchanged, including model names, reasoning effort, token counts, counters, and comparison results. Image metadata was removed. Only the redacted copies are included in the repository; the original captures are not included.

The blurred privacy areas are publication edits, not an application privacy mode. Redact identifying values from your own screenshots or results before sharing them. These captures illustrate observed values; they do not establish which model weights or internal routing produced any response.

---

프로젝트 소유자가 제공한 실제 한글판 구동 화면입니다. 기본 화면은 새로 제공한 캡처로 교체하고, ID 열이 보이는 이전 상세 화면에도 같은 블러 스타일을 적용했습니다. 생성형 이미지 편집은 사용하지 않았습니다.

로컬 코드로 시각·프로젝트명·대화 제목과 화면에 보이는 세션·대화·응답 ID의 원본 픽셀을 먼저 지웠습니다. 그 자리에 식별 정보가 없는 임시 문자를 배치하고 Gaussian blur를 적용해 행별로 부드럽게 흐려지는 모양을 만들었습니다. 블러 영역에 원래 식별 문자는 남아 있지 않습니다.

원본 크기를 유지하고, 가린 영역 밖의 픽셀이 원본과 같은지 검증했습니다. 모델명·reasoning effort·토큰 수·집계 수치·비교 결과는 변경하지 않았습니다. 이미지 메타데이터는 제거했으며 저장소에는 가림 처리한 사본만 포함합니다.

개인 식별 영역의 블러는 게시용 이미지 편집이며 앱의 개인정보 모드가 아닙니다. 자신의 화면이나 결과 파일을 공유할 때도 식별값을 가리세요. 캡처에 보이는 값은 해당 실행에서 관찰된 보고값이며 실제 모델 가중치나 내부 라우팅의 증거로 단정할 수 없습니다.
