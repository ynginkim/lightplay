# 검증 기록

2026-10-23. Python 3.15.0, Node v22.22.2, npx 10.9.7(로컬), GitHub Actions ubuntu-latest·Python 3.12·Node 22. 도메인 스크립트(렌더·TTS·믹스·검수·정리, op55 포함)는 하나도 실행하지 않았다. 아래 PASS는 구조·설치·정적 흐름에 대한 것이며 영상·음악 품질을 뜻하지 않는다.

## 구조와 설치

| 검사 | 대상 커밋 | 결과 | 근거 |
| --- | --- | --- | --- |
| `python3 scripts/check.py . --write-docs`, `python3 scripts/check.py .` | 9028c20, a723dde, 이후 문서 커밋 | PASS | skill 10개(mode 1, playbook 2, leaf 6, principle 3), 오류·경고 0 |
| `python3 scripts/selftest.py` | 같음 | PASS | 49개 테스트 |
| 조건부 검사 오류 주입 | 9028c20 작업본 사본 | PASS | transition 삭제 → PORTABILITY, LICENSE 사본 변경 → COPY_DRIFT, 명령 문자열 변경 → COMMAND_SNAPSHOT, adapter 포인터 삭제 → ADAPTER_POINTER, pending 재등록 → MIGRATION_STALE. 다섯 건 모두 실패로 잡힘 |
| `install_smoke.py`(임시 Git 폴더, `npx skills add <로컬 경로> -a claude-code -a codex -y`) | 9028c20 | PASS | 10개 설치, 두 하네스 경로에서 playbook 4개·참조 126개 열람, 원본 자원 불변 |
| 같음 | a723dde | PASS | 10개 설치, playbook 4개·참조 130개 열람 |
| GitHub Actions `check` | dd967a3 | FAIL | [run 39967752917](https://github.com/ynginkim/motion-graphic-skills/actions/runs/39967752917). 골격 커밋에는 원본 루트 `SKILL.md`가 남아 있어 설치기가 저장소를 skill 하나(`showreel`)로 설치함. 골격 단계에서 로컬 install smoke를 돌리지 않아 push 전에 잡지 못함 |
| 같음 | 9028c20 | PASS | [run 39968655252](https://github.com/ynginkim/motion-graphic-skills/actions/runs/39968655252). 루트 `SKILL.md` 삭제 뒤 |
| 같음 | a723dde | PASS | [run 39970174838](https://github.com/ynginkim/motion-graphic-skills/actions/runs/39970174838) |

이식한 파일의 바이트 대조는 [이식 장부](migration.md)에 있다. scripts 22개·assets 5개·`design.md`는 `374df70`과 같고, references 7개는 장부에 적은 줄만 다르다.

## dry-run

판정자는 골격·이식을 작성하지 않은 별도 하위 agent(보고 모델 Claude Opus 5.5)다. 원본(`374df70`), 대상 커밋, op55 기준 커밋(`828990b`), 인계 6절의 시나리오·대조 항목·의도된 차이 목록만 주었고 작성 세션의 해석은 주지 않았다. 판정문은 고치지 않고 그대로 커밋했다.

| 라운드 | 대상 | 시나리오 | 결과 | 원문 |
| --- | --- | --- | --- | --- |
| 1 | 9028c20 | 1~8 | 의도된 차이 7, 회귀 1(시나리오 7, 경미·조건부), 판정 불가 0 | [round1.md](dryrun/round1.md) |
| 수정 | a723dde | | 복원 분기에서 파일마다 되돌릴 버전을 정함(최신 엔진과 같으면 HEAD, 미커밋 수정이면 보관본, 불명확하면 한 번 질문). 관찰 2건(공유 계약 명시 Read, `gain_db` 수정 뒤 `timeline.py`)도 보완 | |
| 2 | a723dde | 7 | 의도된 차이, 회귀 0 | [round2.md](dryrun/round2.md) |

| # | 시나리오 | 최종 판정 |
| --- | --- | --- |
| 1 | 새 영상, 나레이션 없음 | 의도된 차이 |
| 2 | 새 영상, VO 있음 | 의도된 차이 |
| 3 | VO gain·리버브만 수정 | 의도된 차이 |
| 4 | 음악 교체(hit·energy·cue 소비) | 의도된 차이 |
| 5 | 9:16 규격 수정 | 의도된 차이 |
| 6 | 납품 뒤 정리 | 의도된 차이 |
| 7 | 옛 프로젝트 폰트 재준비·엔진 복원 | 의도된 차이(라운드 2) |
| 8 | leaf 직접 호출의 hard constraint | 의도된 차이 |

시나리오 1~6·8은 라운드 1에서 9028c20을 판정했다. a723dde의 수정은 adapter 복원 분기, plan-video·create-video의 공유 계약 Read 한 줄, revise-video·deliver-video의 `timeline.py` 한 줄이다. 이 세 곳은 다른 시나리오에서 읽는 파일이지만 새 명령이나 승인 지점을 줄이지 않았다. 다시 판정받지는 않았다.

### 작성 세션 의견

판정과 이견은 없다. 라운드 1의 회귀는 원본 skill 저장소만 보면 없던 기능이지만, 원본이 운영되던 작업 폴더 규칙을 기준으로 하면 타당한 지적이라 고쳤다.

라운드 2의 관찰 다섯 건은 회귀가 아니라서 판정받은 버전을 유지하고 후속 항목으로 남겼다(DESIGN "확인하지 못한 것"). 특히 미추적(`??`) 엔진 파일을 "수정됨"으로 잘못 읽으면 HEAD 분기가 빈 파일을 쓸 수 있다(보관본과 `cmp`로 복구 가능). 또 `.restore/`가 프로젝트 커밋에 섞일 수 있다.

## 하지 않은 것

- 실제 영상·음악 제작, 렌더, TTS·효과음·이미지 생성, 도메인 스크립트 실행(인계 금지선).
- 내부 검증 skill(`verify-<skillset>`) 작성과 새 모델 세션의 경로 시험. 실제 제작·유료 호출이 금지됐고 경로 시험 예산이 승인되지 않았다. 닫을 조건은 DESIGN에 있다.
- GitHub 형식 설치(`npx skills add ynginkim/motion-graphic-skills`)와 앱 메뉴 표시 확인.
