# 검증 기록

2026-10-25 음악 경로 변경의 검증과 한계는 [음악 검증 기록](music-validation.md)에 있다. 아래 dry-run은 각 표에 적힌 커밋의 과거 판정이다.

2026-10-23. Python 3.15.0, Node v22.22.2, npx 10.9.7(로컬), GitHub Actions ubuntu-latest·Python 3.12·Node 22. 도메인 스크립트(렌더·TTS·믹스·검수·정리, op55 포함)는 하나도 실행하지 않았다. 아래 PASS는 구조·설치·정적 흐름에 대한 것이며 영상·음악 품질을 뜻하지 않는다.

## 구조와 설치

| 검사 | 대상 커밋 | 결과 | 근거 |
| --- | --- | --- | --- |
| `python3 scripts/check.py . --write-docs`, `python3 scripts/check.py .` | 9028c20, a723dde, 이후 문서 커밋 | PASS | skill 10개(mode 1, playbook 2, leaf 6, principle 3), 오류·경고 0 |
| `python3 scripts/selftest.py` | 같음 | PASS | 49개 테스트 |
| 조건부 검사 오류 주입 | 9028c20 작업본 사본 | PASS | transition 삭제 → PORTABILITY, LICENSE 사본 변경 → COPY_DRIFT, 명령 문자열 변경 → COMMAND_SNAPSHOT, adapter 포인터 삭제 → ADAPTER_POINTER, pending 재등록 → MIGRATION_STALE. 다섯 건 모두 실패로 잡힘 |
| `install_smoke.py`(임시 Git 폴더, `npx skills add <로컬 경로> -a claude-code -a codex -y`) | 9028c20 | PASS | 10개 설치, 두 하네스 경로에서 playbook 4개·참조 126개 열람, 원본 자원 불변 |
| 같음 | a723dde | PASS | 10개 설치, playbook 4개·참조 130개 열람 |
| `python3 scripts/check.py .`, `python3 scripts/selftest.py` | 7f669d7 | PASS | 2026-10-25, Python 3.15.0. 오류·경고 0, 49개 테스트. Python 3.12는 원격 CI에서 확인 |
| `python3 scripts/install_smoke.py . --dest <새 임시 폴더>/install` | 7f669d7 | PASS | Node v22.22.2, npx 10.9.7. 10개 설치, 두 하네스 경로에서 playbook 4개·참조 130개 열람, 원본 자원 불변 |
| 위 검사 3종 재실행 | 5f84cc1 | PASS | index·누락 파일 분기 보완 뒤 오류·경고 0, 49개 테스트, 새 임시 폴더에 10개 설치·playbook 4개·참조 130개 열람 |
| GitHub Actions `check` | dd967a3 | FAIL | [run 39967752917](https://github.com/ynginkim/motion-graphic-skills/actions/runs/39967752917). 골격 커밋에는 원본 루트 `SKILL.md`가 남아 있어 설치기가 저장소를 skill 하나(`showreel`)로 설치함. 골격 단계에서 로컬 install smoke를 돌리지 않아 push 전에 잡지 못함 |
| 같음 | 9028c20 | PASS | [run 39968655252](https://github.com/ynginkim/motion-graphic-skills/actions/runs/39968655252). 루트 `SKILL.md` 삭제 뒤 |
| 같음 | a723dde | PASS | [run 39970174838](https://github.com/ynginkim/motion-graphic-skills/actions/runs/39970174838) |

이식한 파일의 바이트 대조는 [이식 장부](migration.md)에 있다. scripts 22개·assets 5개·`design.md`는 `374df70`과 같고, references 7개는 장부에 적은 줄만 다르다.

## dry-run

판정자는 각 수정에 참여하지 않은 별도 하위 agent다. 라운드 1·2는 Claude Opus 5.5, 라운드 3·4는 Codex 에이전트이며 매번 새 판정자를 썼다. 원본(`374df70`), 대상 커밋, op55 기준 커밋(`828990b`), 시나리오·대조 항목·의도된 차이 목록만 주었고 수정 의도나 기대 결론은 주지 않았다. 판정문은 고치지 않고 그대로 기록한다.

| 라운드 | 대상 | 시나리오 | 결과 | 원문 |
| --- | --- | --- | --- | --- |
| 1 | 9028c20 | 1~8 | 의도된 차이 7, 회귀 1(시나리오 7, 경미·조건부), 판정 불가 0 | [round1.md](dryrun/round1.md) |
| 수정 | a723dde | | 복원 분기에서 파일마다 되돌릴 버전을 정함(최신 엔진과 같으면 HEAD, 미커밋 수정이면 보관본, 불명확하면 한 번 질문). 관찰 2건(공유 계약 명시 Read, `gain_db` 수정 뒤 `timeline.py`)도 보완 | |
| 2 | a723dde | 7 | 의도된 차이, 회귀 0 | [round2.md](dryrun/round2.md) |
| 3 | 7f669d7 | 7 | 회귀 1(index와 HEAD가 다를 때), 누락 파일·정보 부재·실제 실행은 판정 불가 | [round3.md](dryrun/round3.md) |
| 수정 | 5f84cc1 | 7 | 원본 checkout의 기준인 index를 별도 추출한 뒤 복원한다. 누락 엔진은 index에서 복원하고, 원본이 없거나 규격이 불명확하면 묻고 멈춘다 | |
| 4 | 5f84cc1 | 7 | 확정 회귀 0. 전체 판정은 판정 불가(보존·질문 분기의 명세상 수용 범위). 실제 프로젝트 정보와 런타임도 별도 미확인 | [round4.md](dryrun/round4.md) |

| # | 시나리오 | 최종 판정 |
| --- | --- | --- |
| 1 | 새 영상, 나레이션 없음 | 의도된 차이 |
| 2 | 새 영상, VO 있음 | 의도된 차이 |
| 3 | VO gain·리버브만 수정 | 의도된 차이 |
| 4 | 음악 교체(hit·energy·cue 소비) | 의도된 차이 |
| 5 | 9:16 규격 수정 | 의도된 차이 |
| 6 | 납품 뒤 정리 | 의도된 차이 |
| 7 | 옛 프로젝트 폰트 재준비·엔진 복원 | 판정 불가(라운드 4, 확정 회귀 0, 보존·질문 분기의 수용 분류 미확정) |
| 8 | leaf 직접 호출의 hard constraint | 의도된 차이 |

시나리오 1~6·8은 라운드 1에서 9028c20을 판정했다. a723dde의 수정은 adapter 복원 분기, plan-video·create-video의 공유 계약 Read 한 줄, revise-video·deliver-video의 `timeline.py` 한 줄이다. 이 세 곳은 다른 시나리오에서 읽는 파일이지만 새 명령이나 승인 지점을 줄이지 않았다. 7f669d7·5f84cc1의 수정은 adapter 복원 절차와 revise-video의 재렌더 진입 확인이다. 시나리오 1~6·8은 다시 판정받지 않았다.

### 작성 세션 의견

라운드 1~3의 판정과 이견은 없다. 라운드 1의 회귀는 원본 skill 저장소만 보면 없던 기능이지만, 원본이 운영되던 작업 폴더 규칙을 기준으로 하면 타당한 지적이라 고쳤다. 라운드 3은 원본의 `git checkout -- <경로>`가 HEAD가 아닌 index를 복원한다는 점을 확인했다. 5f84cc1에서 비교·복원 기준을 index로 바꾸고 추출 실패 시 원래 파일을 덮기 전에 멈추도록 했다.

라운드 4는 index·누락 파일 처리를 정적으로 확인했고 확정 회귀를 찾지 못했다. 다만 원래 인계의 명시적 차이 4개에 보존·질문 분기가 없다는 이유로 전체 분류를 판정 불가로 남겼다. 작성 세션은 이 분류 해석에 이견이 있다. 보관본·미커밋 수정·project.json 보존과 모호할 때 질문은 이미 라운드 2에서 엄격화로 수용한 절차다([경우별 대조와 차이 목록](dryrun/round2.md)). 이번 인계도 관찰 1의 미추적 보관본 사용과 관찰 3의 질문 분기를 명시적으로 허용했다. 따라서 기존 보존 절차와 이번 관찰 반영은 승인 범위의 엄격화로 본다. 누락 원본·불명 규격의 사전 중단도 이 보존 목표를 따른다. 독립 판정 원문은 수정하지 않았으며, 독립적인 전체 수용 분류를 닫으려면 이 수용 기준을 명세에 명문화한 뒤 다시 분류받아야 한다.

라운드 2의 관찰은 7f669d7과 5f84cc1에서 다음과 같이 처리했다. 엔진 이력 목록을 새로 관리하지 않고, 현재 엔진과 다른 파일은 diff와 제작노트로 판별한 뒤 불명확하면 질문하는 분기를 택했다. 설치본에 Git 이력이 없어도 같은 절차를 쓸 수 있다.

| 관찰 | 반영 | 근거 |
| --- | --- | --- |
| 1. 미추적 엔진 파일 | 반영 | `??`와 index에 없는 파일은 Git 밖과 같이 보관본을 쓴다. 이 파일에 Git 버전을 추출하는 명령을 쓰지 않는다. 5f84cc1에서 새로 stage한 파일도 index 기준으로 구분했다 |
| 2. 이미 덮인 project.json의 HEAD 분기 | 미반영 | 기본값과 같다는 사실만으로 이전 덮어쓰기를 증명할 수 없다. 자동으로 HEAD를 고르면 의도한 미커밋 규격 변경을 잃을 수 있다. 실행 직전 보관본을 유지한다. 이미 덮인 원래 메타데이터는 자동 복원하지 못한다 |
| 3. 엔진 자산 변경 뒤 비교 기준 | 반영 | 현재 최신 엔진과 다르다는 이유만으로 미커밋 수정으로 분류하지 않는다. 이전 엔진의 덮어쓰기가 확인되면 Git 버전, 의도한 수정이면 보관본, 판단이 안 되면 한 번 질문한다. Git 버전은 5f84cc1에서 index로 고쳤다 |
| 4. revise-video 진입 확인 방법 | 반영 | 재렌더 전에 파일 존재·경로 한정 Git 상태·index diff·현재 엔진과의 cmp·제작노트를 확인한다. 상태가 불명확해도 복원 분기로 들어간다 |
| 5. 보관 폴더의 커밋 혼입 | 반영 | 복원 뒤 Git 상태는 처음과 같은 세 경로로 한정한다. `.restore/`를 프로젝트 커밋에 넣지 않도록 명시했다 |

## 하지 않은 것

- 실제 영상·음악 제작, 렌더, TTS·효과음·이미지 생성, 도메인 스크립트 실행(인계 금지선).
- 내부 검증 skill(`verify-<skillset>`) 작성과 새 모델 세션의 경로 시험. 실제 제작·유료 호출이 금지됐고 경로 시험 예산이 승인되지 않았다. 닫을 조건은 DESIGN에 있다.
- GitHub 형식 설치(`npx skills add ynginkim/motion-graphic-skills`)와 앱 메뉴 표시 확인.
