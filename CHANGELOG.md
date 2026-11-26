# Changelog

Changes are grouped using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versioned using [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- 저장소를 public으로 전환했다(2026-11-26). 비공개 작업 폴더를 인용하는 dry-run 판정 원문(`docs/dryrun/`)을 빼고, 비공개를 전제한 문장을 고쳤다(#15). playwright-core를 1.65.1로 올렸다(#13). GitHub 경로 설치를 확인했다.

### Added
- revise-video에 언어판(장면 코드 하나, `reel/i18n.js`와 `reel_<lang>/index.html`의 `window.LANG`, 그 언어의 자료만, 영어판 한글 0건 확인), 짧은 판, 나레이션 추가판 분기를 더한다. deliver-video에 10MB 미만 README·GitHub용 사본(2패스 x264, 첫 프레임이 포스터, 900px 플레이어 글자 크기) 절차를 더한다.
- `vo_split.py`: 사용자가 한 파일로 녹음한 나레이션을 줄별 클립(`audio/vo/<id>.mp3`, `.align.json`, `report.json`)으로 나눠 `timeline.py`로 바로 잇는다. 받아쓰기가 있으면 단어 시각으로, 없으면 소리 크기와 macOS `say` 기준 낭독의 MFCC·DTW 거리로 줄을 찾고 다시 읽은 줄은 마지막 테이크를 쓴다. `--timeline`은 줄 길이 대 장면 표를 낸다. prepare-video-audio에 녹음 원고 형식, 길이 선택지, `--sfx-duck 0.8` 기준을 더한다.
- `text_probe.mjs`: 초안의 화면 글자를 시간에 따라 읽어 글 덩어리마다 다 보이는 시간과 필요한 시간(공백 제외 한국어 초당 6자, 영어 초당 10자)을 비교하고 ✗ 줄을 낸다. `--groups`는 같이 뜬 여러 줄 캡션을 합쳐 보고, `--no-hangul`은 영어판 화면 글자의 한글을 찾는다. critique-video의 "읽는 시간"과 engine.md의 "읽기 대기와 카메라 호흡"이 쓰는 법을 적는다.
- deliver-video `references/poster.md`: 영상과 함께 낼 안내 포스터. 그림은 이미지 모델이 만들고 글자는 HTML로 조판해 `capture.mjs`로 렌더한다. 서체 한 가족, 글자색과 강조색 두 가지, 가장 작은 글자 크기, 세로판과 가로판을 읽히게 하기 위한 기준으로 적는다.
- `capture.mjs`: 실제 제품 화면을 2배율 스틸·전체 페이지·프레임 단위 스크롤로 찍는다. 설정 파일 하나가 기록이 되고, 로그인 전용 임시 프로필(사용자가 직접 로그인, 촬영 뒤 `forget`으로 삭제), 찍기 전 실명 가리기, `manifest.json` 크기 기록을 지원한다. 로컬 HTML 포스터 렌더에도 쓴다. 사용법은 build-video-scenes의 `references/capture.md`.

### Changed
- 제품 화면은 실제 화면 캡처를 먼저 쓰고, 캡처할 수 없을 때만 코드 목업을 그려 화면에 밝힌다. 정보 영상의 콘셉트 비교에 "실제 자료" 기준을 더하고 비유는 이름 짓기·도입에만 쓴다.
- 카피 규칙에 보는 사람이 알 수 없는 맥락(공개되지 않은 문서, 제작 일화)을 화면과 크레딧에 넣지 않는다는 줄을 더한다.
- 제품 소개·설명·행사 안내·강의처럼 정보를 전하는 영상은 만들기 전에 의도·핵심 메시지·내용 흐름 표를 제안해 사용자와 합의한다. 콘셉트와 아트 디렉션은 계속 Claude가 정하고, 쇼릴처럼 보여 주는 영상은 그대로 진행한다.
- 저장소 이름 변경(`motion-graphic-skills` → `lightplay`)에 맞춰 기여·지원 링크, 이슈 템플릿, 설치 확인 명령, 문서 제목을 고친다. 당시를 적은 기록의 옛 이름은 유지한다.
- op55의 공개 출력 계약만 소비하고, WAV 일치 확인과 나레이션 대 배경 검사를 MGS 믹서로 모은다. 옛 설치 이름을 거부하고 사용 버전 또는 버전 미확인을 기록한다.
- 음악 생성을 op55 런타임 발견 기본, ElevenLabs Music BYOK 선택, 내장 합성 fallback으로 변경한다. 기존 외부 Music API 금지 정책과 op55 커밋 의존을 정리한다.
- Upgrade the local renderer's Playwright dependency from 1.63.0 to 1.64.1.

### Fixed
- `cleanup.py`가 최종 믹스 `audio/mix.wav`까지 지울 목록에 올려 매번 파일을 하나씩 지워야 했다. 규칙 표 하나로 다시 써서 최종 믹스·영상이 쓰는 음악·판별 보존 음악을 남기고, 후보를 "다시 안 쓸 것"과 "후속 작업용"(무음 렌더, 렌더 조각, 음악 스템, 녹음 원본)으로 나눈다. `--apply`는 휴지통으로 옮기는 것이 기본이고 `--trash`는 없앴다. `--followup`, `--delete`, `--trash-dir`를 더했고 `scripts/test_cleanup.py`를 CI에서 돌린다.
- 옛 프로젝트 복원은 미추적 파일에 보관본을 쓰고, 현재 엔진과 다른 파일은 diff와 제작노트로 판별한 뒤 불명확하면 한 번 질문한다.
- 옛 프로젝트 재렌더 진입에 엔진 상태 확인을 추가하고, 복원 뒤 Git 상태를 세 경로로 한정하며 `.restore/`를 프로젝트 커밋에서 제외한다.
- 덮이거나 누락된 추적 엔진은 원본 `git checkout --`와 같은 index 버전을 보관한 뒤 복원해 스테이징된 엔진 변경도 유지한다.
- deliver-video audio-only refinish no longer reruns `finish.py` under the master's name. It always writes a new name (`_r2`), so the existing master is kept until the new QA passes.
- deliver-video audio-only refinish now compares the per-line narration-over-bed table from `mix.py` with the previous mix. `qa_check.py` does not check that table, so a louder bed could pass QA.
- The shared SFX library location now matches `sfx_library.py`: `--lib`, then `SHOWREEL_SFX_LIBRARY`, then `$CLAUDE_PROJECT_DIR/sfx-library`. Without any of these the script stops, and the docs say to pass `--lib` before the subcommand.

### Changed
- 시나리오 7의 독립 정적 dry-run 라운드 3·4와 관찰별 처리 근거를 기록하고, 확정 회귀 0과 전체 수용 분류의 판정 불가를 구분해 설계·검증 문서를 갱신한다.

## [0.1.0] - 2026-10-24

### Added
- Contribution, conduct, security, support, and release-readiness documentation.
- A development version source and explicit release verification checklist.

### Changed
- README installation and third-party license guidance reviewed for reproducibility and scope.

This is the first versioned code release. Earlier development history remains available in Git. Cross-repository integration and model/media quality are not guaranteed by structural or installation checks.
