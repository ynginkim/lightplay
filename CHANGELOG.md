# Changelog

Changes are grouped using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versioned using [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- op55의 공개 출력 계약만 소비하고, WAV 일치 확인과 나레이션 대 배경 검사를 MGS 믹서로 모은다. 옛 설치 이름을 거부하고 사용 버전 또는 버전 미확인을 기록한다.
- 음악 생성을 op55 런타임 발견 기본, ElevenLabs Music BYOK 선택, 내장 합성 fallback으로 변경한다. 기존 외부 Music API 금지 정책과 op55 커밋 의존을 정리한다.
- Upgrade the local renderer's Playwright dependency from 1.63.0 to 1.64.1.

### Fixed
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
