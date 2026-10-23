# motion-graphic-skills 설계

Status: draft. 이식을 마쳤고 설치 smoke·dry-run·CI 결과는 다음 커밋에서 반영한다.

한 줄 철학: 주제에서 콘셉트를 세우고, 화면은 렌더한 증거로 판정하며, 오디오와 화면은 이름 붙은 큐로 묶어 늦은 수정을 싸게 만든다.

이 저장소는 showreel 단일 skill(`307b3fd8407feca15c7bd74a089276e8002b204c`, 이 저장소 첫 커밋 `374df70`)을 meta-harness 구조의 skillset으로 옮긴 것이다. 설계 원안은 meta-harness 저장소의 `examples/showreel/plan.md` 1~7절이며, 아래 "이번 결정으로 대체"에 적은 것만 바꿨다.

## 범위

코드(DOM·캔버스·WebGL·3D)로 렌더하는 한국어 모션그래픽 영상을 콘셉트부터 납품까지 만들고, 만든 영상을 피드백대로 고친다. 실사 촬영본 컷 편집, 파일 자르기·변환만 하는 일, Sora·Veo 같은 생성형 비디오 모델 호출, 슬라이드·PDF만 만드는 일은 범위가 아니다(원본 `SKILL.md:3`).

## 결과물과 판정

| 구분 | 계약 |
| --- | --- |
| 납품 파일 | `out/<제목>_<길이>s.mp4`, `_공유용.mp4`, `_포스터.jpg`, 나레이션이 있으면 `.srt`, 프로젝트 루트 `제작노트.md` |
| 재현 근거 | `concept.md`, `storyboard.md`, `research/`, `script.json`, `timeline.json`, `reel/`, `assets/`, 오디오 원본, `qa/critique_NN.md`, `qa/qa_report.md`, `qa/final_sheet*.png` |
| 에이전트 완료 | 납품 파일 존재·규격, 구간별 비평이 모두 "유지", 최종 시트 열람, 수치 보고의 "고칠 것" 처리, 출처·크레딧·재생성 명령·대체 경로·사람 확인 요청 |
| 사람 판정 | 전체 연속 시청(리듬·가독성·의도 전달), 스피커·이어폰 청취(음질·대사·취향) |
| 납품 요청 문장 | "위 마스터 파일을 처음부터 끝까지 보고, 스피커나 이어폰으로 소리도 확인해 주세요. 저는 프레임과 수치·STT로 확인했으며 직접 청취하지 않았습니다." 끝내지 못한 항목은 따로 적는다 |
| 재개 상태 | 프로젝트 `PAUSE.md`(끝난 것, 진행 중, 다시 시작하는 순서) |

출처: 원본 `SKILL.md:43,203,243-252`, `references/qa.md:117-173`. 모션·QA 스크립트의 정상 종료만으로 완료라고 쓰지 않는다. 사람이 감독 역할을 유지하므로 비평용 mode를 따로 두지 않고, 기존의 맥락 없는 독립 비평을 critique-video 안에 보존한다(`SKILL.md:205`).

## 구성

| 요소 | 이름 | 채택 이유 | 원본 출처 |
| --- | --- | --- | --- |
| mode | `showreel-mode` | 자연어 진입, 브리프, 결과물·완료·사람 판정, playbook 선택, 진행 장부 | `SKILL.md:1-64` |
| playbook | `create-video` | 새 프로젝트: 0~11단계 전체 | `SKILL.md:52-264` |
| playbook | `revise-video` | 기존 프로젝트와 피드백: 출발 상태와 무효화 범위가 다름 | `SKILL.md:149,160,235,283`, `references/qa.md:159-162` |
| adapter | `resolve-showreel-tools` | 스크립트·엔진 자원 한 벌 소유, `S`·`O` 경로 해석, 점검, 새 프로젝트·옛 프로젝트 복원 분기, 공유 계약 | `SKILL.md:64-76,98-106`, `scripts/preflight.py:20-27` |
| leaf | `plan-video` | 요청 읽기·콘셉트·조사·구성·원고 | `SKILL.md:78-124`, `references/brief.md`, `story.md` |
| leaf | `prepare-video-audio` | op55 음악·나레이션·효과음·타임라인 | `SKILL.md:126-160`, `references/audio.md` |
| leaf | `build-video-scenes` | 이미지·스타일 프레임·장면 코드 | `SKILL.md:162-189`, `references/{images,design,engine,techniques}.md` |
| leaf | `critique-video` | 초안 렌더·시트·움직임 검사·비평 반복 | `SKILL.md:191-209`, `references/qa.md:12-103` |
| leaf | `deliver-video` | 최종·조각 렌더, 믹스, 마감, 자동 검수, 납품 보고, 정리 | `SKILL.md:211-264`, `references/qa.md:104-194` |
| principle | `principle-concept-before-template` | 화면을 도구 목록이 아니라 주제에서 고름 | `SKILL.md:27-31,86-94`, `references/design.md:15-43` |
| principle | `principle-judge-rendered-evidence` | 코드·종료 코드가 아니라 렌더한 프레임·수치 표·외부 비평으로 판정 | `SKILL.md:203-207`, `references/qa.md:23,33-55` |
| principle | `principle-stable-cues-late-surfaces` | 큐·격자를 고정해 표면 수정을 싸게, 소비값이 바뀌면 다시 렌더 | `SKILL.md:147-150,185`, `references/engine.md:35-36,66-67` |

기각한 후보와 대체 위치:

- 조사·브리프·스토리보드 leaf 분리: 독립 직접 호출 사례가 없다. `plan-video`의 references로 충분하다.
- 음악 작곡 leaf·작곡 mode: op55가 소유한다(BGM 이관은 `CUSTOM.md:63`에서 이미 끝남). showreel은 op55를 중첩 호출하지 않는다.
- 비평 mode: 사람의 역할 전환이 없다. 독립 비평은 `critique-video`의 단계다.
- 규격 파생 playbook: 반복되는 독립 흐름이 확인되기 전까지 `revise-video`의 분기다.
- 운영 adapter(resolve-capability): 운영 어휘는 하위 agent, 백그라운드 실행 둘이다. 셋 이상이 필요해지면 검토한다.

## 파일 경계와 op55

- 실행 자원(`scripts/`, `assets/`)은 `resolve-showreel-tools`가 원래 상대 배치(`scripts/../assets`) 그대로 한 벌 소유한다. 다른 leaf는 제목 바로 아래 `Read ../resolve-showreel-tools/SKILL.md`로 adapter를 읽고 그 경로를 쓴다.
- 기술별 reference는 담당 leaf가 소유한다. 다른 leaf가 필요하면 그 경로를 읽는다(`qa.md`는 critique-video, 믹스 기준이 든 `audio.md`는 prepare-video-audio).
- 공유 계약(결과물 기준, 기술 기본값, 작업 위치, 프로젝트 파일, op55 경계 필드)은 `resolve-showreel-tools/references/contract.md` 한 곳에 둔다.
- **op55 기준 커밋은 `828990bb00ed1b887bb29d79710006c3c4bec526`이다.** 이번 이식의 파일 계약·경로·transition·dry-run 판정은 모두 이 커밋의 op55(`git show 828990b:<path>`)를 기준으로 한다. 이후 op55 커밋은 따라가지 않는다.
- op55는 독립 skillset이다. showreel은 op55의 파일 계약(`score.mjs`, `music.wav`, `analysis.json`, `music.meta.json`)과 op55 문서로만 연결한다. op55는 아직 skill 하나라서 현재 op55 `SKILL.md`를 읽는다. 이 경로는 `skillset.json`의 `portability.transitions`에 "op55가 leaf로 변환됨"을 닫을 조건으로 등록한다.
- 스크립트 이동 뒤 예전 설치 경로 탐색에 기대지 않는다. adapter가 `S`(이 skillset의 scripts)와 `O`(op55 scripts)의 실제 절대 경로를 확인하고, 자식 명령에 `OP55_SCRIPTS`, `SHOWREEL_SCRIPTS`, `--mix-py`를 명시한다. 전역 env와 사용자 설정은 바꾸지 않는다.

## 이식 결과

원본 `SKILL.md`의 0~11단계와 지킬 것·자주 생기는 문제·참조 표는 [이식 장부](docs/migration.md)의 A01~A28로 모두 새 위치에 옮겼다. references 8개, scripts 22개, assets 5개를 담당 skill로 옮겼고 `migration.pending`은 0건이다. 원본 명령 35개는 [명령 스냅샷](docs/command-snapshot.md)과 각 leaf에 같은 문자열로 남아 있고 `command_snapshots`가 이를 검사한다.

| 대상 | 결과 |
| --- | --- |
| scripts 22개, assets 5개, references/design.md (모두 28개) | `374df70`과 바이트가 같다 |
| references 7개 | 경로 문장과 검사기 표기만 바꿨다(줄 목록은 이식 장부). 인계 조건 "원본 바이트 유지, 경로 문장만 다시 씀"과 다른 점은 검사기 표기 13줄(긴 대시 10줄, API 경로 2줄, 인라인 `/tmp` 1줄)이다. 구조 검사기의 LONG_DASH·REF 규칙을 우회하지 않으려고 뜻을 바꾸지 않는 문장부호·표기만 고쳤다 |

## 이번 결정으로 대체

| ID | 원안(plan.md) | 이번 결정 |
| --- | --- | --- |
| Q3 | upstream report-only 추적(plan §8의 4단계) | 추적 종료. 기준 커밋 `307b3fd`와 MIT 라이선스만 기록한다. `tools/sync.sh`와 report-only 구성은 만들지 않는다 |
| Q7 | meta-harness 작업명, 로컬·push 없음 | 저장소 `ynginkim/motion-graphic-skills`(비공개). mode 이름은 일단 `showreel-mode`. 공개는 검증 뒤 사용자 결정 |
| Q2 | op55 leaf 호출 | op55가 아직 skill 하나이므로 현재 op55 skill 경로를 쓰고 transition을 등록 |
| 라이선스 | 해당 없음 | `LICENSE`에 원 저작권 줄을 유지하고 본인 줄 추가. `resolve-showreel-tools/LICENSE` 사본을 `copies`로 바이트 대조 |
| 커밋 | 격리 브랜치 | `main`에서 직접, 단계마다 검사 통과 뒤 커밋·push. force push·PR 없음 |
| 음악 재생성 뒤 화면 재사용 | 원본 `SKILL.md:149` "박 격자가 같으면 화면 재렌더 불필요" | 격자에 더해 화면이 소비하는 큐·히트·음악 에너지 곡선·크레딧 문구를 비교해 정함(plan §3, artifact-graph). `timeline.py`가 WAV에서 에너지 곡선을 다시 계산하기 때문 |
| 정리 | 원본 `SKILL.md:256` "지울 목록부터 본 뒤 정리" | 목록과 합계를 납품 보고에 붙이고, 사용자가 끝났다고 확인한 뒤에만 `--apply` 또는 `--apply --trash`(plan §2·§4, video-creator `CLAUDE.md` "납품 뒤 정리") |

## 진입 정책과 언어

name은 영어 kebab-case, description·본문·default_prompt는 한국어다. 식별자와 API는 원어를 유지한다. `showreel-mode`만 자연어로 진입한다(Claude `disable-model-invocation: false`, Codex `policy.allow_implicit_invocation: true`). leaf와 principle은 명시 호출이다.

<!-- skillset:policy:start -->
| mode | 자연어 자동 호출 |
| --- | --- |
| `showreel-mode` | `true` |

leaf skill과 principle의 자동 호출은 `false`다.
<!-- skillset:policy:end -->

## 구조 검사

| 검사 | 이 저장소 |
| --- | --- |
| S1 참조·frontmatter·색인·언어·오류 주입 | 적용 |
| S2 설치 경계·등록된 사본 diff | 적용. `LICENSE` 사본 |
| S3 adapter 소비 leaf의 제목 직후 포인터 | 적용. 작업 leaf 5개 |
| S4 제품명 lint·경로별 예외·transition | 적용. 예전 설치 경로·동기화·중첩 호출 문구 |
| S5 이전 장부 prune | 적용 |
| S6 명령 스냅샷 대조 | 적용. 원본 `SKILL.md`의 명령 문자열 35개와 대조. 도메인 스크립트 help는 실행 금지라 기록하지 않음 |
| S7 install smoke | 적용 |
| S8 진입 정책 | 적용 |
| S9 색인 밖 principle 사용 | 적용 |
| S10 미확인 닫을 조건 | 적용 |
| S11 생성 문서·링크 드리프트 | 적용 |
| S12 push CI | 적용 |

## 기본값과 사용자 결정

| ID | 값 | 적용 범위 |
| --- | --- | --- |
| Q1 | `showreel-mode`만 자연어 진입 | 이 저장소 |
| Q2 | op55 독립, 파일 계약과 op55 문서로 연결 | transition 종료 전까지 현재 op55 skill 경로 |
| Q4 | 도메인 adapter + 하네스 중립 운영 문장 | 운영 어휘 3개 이상이면 재검토 |
| Q5 | 새 제작·수정 2 playbook | 오디오 교체·규격 변경은 수정 분기 |
| Q6 | 성공 경험과 피드백 수확은 사용자가 부를 때만 | 같은 문제가 두 번이면 그 일을 맡은 leaf의 reference에 기록(원본 video-creator 규칙) |

## 확인하지 못한 것

| 항목 | 상태 | 닫을 조건 |
| --- | --- | --- |
| 실제 영상·음악 품질 | unverified | 승인된 제작 위치에서 새 영상과 수정 사례를 만들고 사용자가 전체 시청·청취 |
| 앱 메뉴 표시와 자연어 진입 | unverified | 설치본을 새 Claude Code·Codex 세션에서 열어 mode 진입과 leaf 명시 호출 확인 |
| op55 leaf 변환 | 대기 | op55가 op55-compose·op55-render·op55-verify·resolve-op55-tools로 변환되면 prepare-video-audio와 adapter의 op55 경로를 바꾸고 transition 삭제 |
| op55 변경 후 재정렬 | 대기 | op55 변경 작업(leaf 변환 포함)이 끝난 뒤 새 HEAD의 파일 계약·leaf 이름을 기준 커밋 `828990b`와 대조하고 transition을 닫거나 갱신 |
| 이식·검증 결과 | 진행 중 | 이식 커밋, install smoke, dry-run, Actions 결과를 이 문서에 반영 |
