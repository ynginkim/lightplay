# Lightplay 설계

Status: implemented. 구조·설치·정적 흐름은 검증했고 실제 제작 품질은 unverified다(아래 "검증 기록"과 "확인하지 못한 것").

한 줄 철학: 주제에서 콘셉트를 세우고, 화면은 렌더한 증거로 판정하며, 오디오와 화면은 이름 붙은 큐로 묶어 늦은 수정을 싸게 만든다.

이 저장소는 showreel 단일 skill(`307b3fd8407feca15c7bd74a089276e8002b204c`, 이 저장소 첫 커밋 `374df70`)을 meta-harness 구조의 skillset으로 옮긴 것이다. 설계 원안은 meta-harness 저장소의 `examples/showreel/plan.md` 1~7절이며, 아래 "이번 결정으로 대체"에 적은 것만 바꿨다.

저장소 이름은 `motion-graphic-skills`에서 `lightplay`로 바뀌었다. 당시를 적은 기록(결정 표, dry-run 기록, 검증 기록의 실행 링크)은 옛 이름을 그대로 둔다.

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
| leaf | `prepare-video-audio` | 음악 경로 선택·나레이션·효과음·타임라인 | `SKILL.md:126-160`, `references/audio.md` |
| leaf | `build-video-scenes` | 이미지·스타일 프레임·장면 코드 | `SKILL.md:162-189`, `references/{images,design,engine,techniques}.md` |
| leaf | `critique-video` | 초안 렌더·시트·움직임 검사·비평 반복 | `SKILL.md:191-209`, `references/qa.md:12-103` |
| leaf | `deliver-video` | 최종·조각 렌더, 믹스, 마감, 자동 검수, 납품 보고, 정리 | `SKILL.md:211-264`, `references/qa.md:104-194` |
| principle | `principle-concept-before-template` | 화면을 도구 목록이 아니라 주제에서 고름 | `SKILL.md:27-31,86-94`, `references/design.md:15-43` |
| principle | `principle-judge-rendered-evidence` | 코드·종료 코드가 아니라 렌더한 프레임·수치 표·외부 비평으로 판정 | `SKILL.md:203-207`, `references/qa.md:23,33-55` |
| principle | `principle-stable-cues-late-surfaces` | 큐·격자를 고정해 표면 수정을 싸게, 소비값이 바뀌면 다시 렌더 | `SKILL.md:147-150,185`, `references/engine.md:35-36,66-67` |

기각한 후보와 대체 위치:

- 조사·브리프·스토리보드 leaf 분리: 독립 직접 호출 사례가 없다. `plan-video`의 references로 충분하다.
- 음악 작곡 leaf·작곡 mode: op55를 쓸 때는 그 설치본이 소유한다. 대안은 기존 ElevenLabs·합성 helper를 재사용하며 별도 음악 mode를 만들지 않는다.
- 비평 mode: 사람의 역할 전환이 없다. 독립 비평은 `critique-video`의 단계다.
- 규격 파생 playbook: 반복되는 독립 흐름이 확인되기 전까지 `revise-video`의 분기다.
- 운영 adapter(resolve-capability): 운영 어휘는 하위 agent, 백그라운드 실행 둘이다. 셋 이상이 필요해지면 검토한다.

## 파일 경계와 op55

- 실행 자원(`scripts/`, `assets/`)은 `resolve-showreel-tools`가 원래 상대 배치(`scripts/../assets`) 그대로 한 벌 소유한다. 다른 leaf는 제목 바로 아래 `Read ../resolve-showreel-tools/SKILL.md`로 adapter를 읽고 그 경로를 쓴다.
- 기술별 reference는 담당 leaf가 소유한다. 다른 leaf가 필요하면 그 경로를 읽는다(`qa.md`는 critique-video, 믹스 기준이 든 `audio.md`는 prepare-video-audio).
- op55 지원 기준은 0.2.0 이상과 resolve-op55-tools 구조다. 0.2.0은 아직 릴리스 전이며 태그가 예정돼 있다. 현재 main의 같은 구조처럼 버전 정보를 제공하지 않는 설치본은 실제 경로와 "버전 미확인"을 기록한다. 버전 숫자로 실행을 차단하지 않고 실제 파일의 수락 기준으로 판정한다.
- 공유 계약(결과물 기준, 기술 기본값, 작업 위치, 프로젝트 파일, 음악 경계 필드)은 `resolve-showreel-tools/references/contract.md` 한 곳에 둔다.
- 최초 이식의 정적 dry-run은 op55 `828990bb00ed1b887bb29d79710006c3c4bec526`을 기준으로 했다. 현재 실행은 특정 커밋을 요구하지 않고 설치된 op55 문서·도구·파일 계약을 확인한다. 사용 경로와 확인 가능한 버전은 제작노트에 남긴다.
- 음악은 op55 기본, 선택한 ElevenLabs Music BYOK, 내장 합성 fallback의 세 경로다. 선택·실패·수락 기준은 `skills/prepare-video-audio/references/music.md`가 소유한다. 공통 계약은 음악 파일·analysis와 출처다. 악보·op55 meta는 op55에만 요구한다. 옛 단일 skill 문서 경로를 허용하던 transition 두 건은 제거했다.
- 스크립트 이동 뒤 예전 설치 경로 탐색에 기대지 않는다. adapter가 `S`(이 skillset의 scripts)와 `O`(op55 scripts)의 실제 절대 경로를 확인하고, 환경 점검에 `OP55_SCRIPTS`를 명시한다. 나레이션 대 배경 검사는 MGS의 `mix.py`가 소유하며 op55에 믹서 경로나 타임라인을 전달하지 않는다. 전역 env와 사용자 설정은 바꾸지 않는다.

## 이식 결과

이 절의 바이트 대조 표는 최초 이식 시점의 기록이다. 이후 음악 경로 변경과 현재 검증은 [음악 검증 기록](docs/music-validation.md)에 있다.

원본 `SKILL.md`의 0~11단계와 지킬 것·자주 생기는 문제·참조 표는 [이식 장부](docs/migration.md)의 A01~A28로 모두 새 위치에 옮겼다. references 8개, scripts 22개, assets 5개를 담당 skill로 옮겼고 `migration.pending`은 0건이다. 원본 명령 35개는 [명령 스냅샷](docs/command-snapshot.md)에 보존했다. 현재 `command_snapshots`는 활성 명령 30개를 대조한다. op55 전용 명령 5개는 설치본의 현재 문서·도구 경로로 확인하므로 고정 문자열 검사를 종료했다.

| 대상 | 결과 |
| --- | --- |
| scripts 22개, assets 5개, references/design.md (모두 28개) | `374df70`과 바이트가 같다 |
| references 7개 | 경로 문장과 검사기 표기만 바꿨다(줄 목록은 이식 장부). 인계 조건 "원본 바이트 유지, 경로 문장만 다시 씀"과 다른 점은 검사기 표기 13줄(긴 대시 10줄, API 경로 2줄, 인라인 `/tmp` 1줄)이다. 구조 검사기의 LONG_DASH·REF 규칙을 우회하지 않으려고 뜻을 바꾸지 않는 문장부호·표기만 고쳤다 |

## 이번 결정으로 대체

| ID | 원안(plan.md) | 이번 결정 |
| --- | --- | --- |
| Q3 | upstream report-only 추적(plan §8의 4단계) | 추적 종료. 기준 커밋 `307b3fd`와 MIT 라이선스만 기록한다. `tools/sync.sh`와 report-only 구성은 만들지 않는다 |
| Q7 | meta-harness 작업명, 로컬·push 없음 | 저장소 `ynginkim/motion-graphic-skills`(비공개)로 시작해 `lightplay`로 이름을 바꿨다. mode 이름은 `showreel-mode`. 2026-11-26 사용자 결정으로 공개 |
| Q2 | op55 leaf 호출 | op55는 실행 시 설치본 문서·도구 경로로 연결. 2026-10-25 음악 경로 정책으로 옛 transition 종료 |
| 라이선스 | 해당 없음 | `LICENSE`에 원 저작권 줄을 유지하고 본인 줄 추가. `resolve-showreel-tools/LICENSE` 사본을 `copies`로 바이트 대조 |
| 커밋 | 격리 브랜치 | `main`에서 직접, 단계마다 검사 통과 뒤 커밋·push. force push·PR 없음 |
| 음악 재생성 뒤 화면 재사용 | 원본 `SKILL.md:149` "박 격자가 같으면 화면 재렌더 불필요" | 격자에 더해 화면이 소비하는 큐·히트·음악 에너지 곡선·크레딧 문구를 비교해 정함(plan §3, artifact-graph). `timeline.py`가 WAV에서 에너지 곡선을 다시 계산하기 때문 |
| 정리 | 원본 `SKILL.md:256` "지울 목록부터 본 뒤 정리" | 목록과 합계를 납품 보고에 붙이고, 사용자가 끝났다고 확인한 뒤에만 `--apply`(plan §2·§4, video-creator `CLAUDE.md` "납품 뒤 정리"). 2026-11-13부터 `--apply`는 "다시 안 쓸 것"만 휴지통으로 옮기고, "후속 작업용"(무음 렌더·조각·음악 스템·녹음 원본)은 `--followup`, 영구 삭제는 `--delete`를 더할 때만 한다. 최종 믹스는 후보에서 뺐다 |

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
| S6 명령 스냅샷 대조 | 적용. 역사적 명령 35개 중 활성 명령 30개와 대조. 도메인 스크립트 help는 실행 금지라 기록하지 않음 |
| S7 install smoke | 적용 |
| S8 진입 정책 | 적용 |
| S9 색인 밖 principle 사용 | 적용 |
| S10 미확인 닫을 조건 | 적용 |
| S11 생성 문서·링크 드리프트 | 적용 |
| S12 push CI | 적용 |

## 검증 기록

자세한 표와 판정 원문은 [검증 기록](docs/validation.md)에 있다.

| 층 | 결과 | 근거와 한계 |
| --- | --- | --- |
| 구조 | PASS | `check.py` 오류·경고 0, `selftest.py` 49개, 조건부 검사 오류 주입 5건 실패 확인 |
| 설치 | PASS(로컬 경로) | 임시 Git 폴더에 `npx skills add` 복사 설치, 10개 skill, 두 하네스 경로에서 playbook·참조 130개 열람. GitHub 형식 설치는 미확인 |
| CI | PASS(9028c20, a723dde), FAIL(dd967a3) | 골격 커밋은 원본 루트 `SKILL.md`가 남아 설치기가 skill 하나로 설치해 실패. 이후 해소 |
| 정적 dry-run | 확정 회귀 0, 시나리오 7 전체 분류는 판정 불가 | 별도 판정자 4라운드. 라운드 3에서 발견한 index·HEAD 혼동 회귀를 5f84cc1에서 고쳤다. 라운드 4는 회귀를 찾지 못했으나 보존·질문 분기의 수용 분류를 미확정으로 남겼다. 판정 원문은 내부 기록이라 저장소 밖에 둔다 |
| 실제 제작·청취 | unverified | 이번 범위에서 실행 금지 |

## 이름

mode 이름은 `showreel-mode`로 확정했다(2026-10-24 사용자 결정). 같은 프로젝트에 설치되는 skill끼리 이름이 겹치지 않는지만 보면 되므로 저장소 검색은 하지 않았다.

| 후보 | 뜻 | 아쉬운 점 |
| --- | --- | --- |
| `showreel-mode`(확정) | 출발한 skill과 이어지고 기존 사용자가 알아봄 | 쇼릴 말고 홍보·교육 영상도 만드는데 이름이 좁아 보임. 예전 `showreel` skill과 함께 설치하면 같은 요청을 두고 경쟁 |
| `motion-graphic-mode` | 저장소 이름과 같고 범위를 그대로 말함 | 길다 |
| `motion-video-mode` | 코드로 만드는 영상 전반 | 실사 편집까지 하는 것처럼 읽힐 수 있음 |

## 기본값과 사용자 결정

| ID | 값 | 적용 범위 |
| --- | --- | --- |
| Q1 | `showreel-mode`만 자연어 진입 | 이 저장소 |
| Q2 | op55 독립, 런타임 문서·파일 계약 확인 | 기본 음악 경로. 특정 커밋은 실행 조건이 아님 |
| 음악 경로 | op55 기본, ElevenLabs Music BYOK 선택, 내장 합성 fallback | 2026-10-25 사용자 결정. Suno 제외, 외부 Music 금지 정책 대체 |
| Q4 | 도메인 adapter + 하네스 중립 운영 문장 | 운영 어휘 3개 이상이면 재검토 |
| Q5 | 새 제작·수정 2 playbook | 오디오 교체·규격 변경은 수정 분기 |
| 공개 | 2026-11-26 사용자 결정으로 공개. 비공개 작업 폴더를 인용하는 dry-run 판정 원문은 저장소에서 뺐다 | 이 저장소 |
| 제작 테스트 위치 | video-creator가 아닌 새 빈 작업 폴더. 예산 때문에 30초 영상으로 시작(2026-10-24 사용자 결정) | 첫 실제 제작 검증 |
| 라운드 2 관찰 | 관찰 1·3·4·5 반영, 2는 보관본 유지. 시나리오 7을 라운드 3·4에서 독립 재판정(2026-10-25) | 복원 분기. 이유와 판정 결과는 [검증 기록](docs/validation.md) |
| Q6 | 성공 경험과 피드백 수확은 사용자가 부를 때만 | 같은 문제가 두 번이면 그 일을 맡은 leaf의 reference에 기록(원본 video-creator 규칙) |

## 확인하지 못한 것

| 항목 | 상태 | 닫을 조건 |
| --- | --- | --- |
| 실제 영상·음악 품질 | unverified | 승인된 제작 위치에서 새 영상과 수정 사례를 만들고 사용자가 전체 시청·청취 |
| 앱 메뉴 표시와 자연어 진입 | unverified | 설치본을 새 Claude Code·Codex 세션에서 열어 mode 진입과 leaf 명시 호출 확인 |
| op55 leaf 변환 | 정렬함 | 설치본 문서로 경로·명령을 확인하는 방식으로 변경하고 옛 transition 두 건 삭제 |
| 음악 세 경로 실제 품질 | 일부 확인, 외부 호출·청취 unverified | 발견·BYOK 경계·합성 pipeline 테스트와 별개로 실제 op55·ElevenLabs 음악 및 사용자의 전체 청취 확인 |
| GitHub 형식 설치 | unverified | 공개 전환 뒤 빈 Git 프로젝트에서 `npx skills add ynginkim/lightplay -a claude-code -a codex`를 실행하고 10개 설치·형제 참조 확인 |
| 새 세션 경로 시험(진입·원문 todo·leaf 직접 호출) | unverified | 경로 시험 예산이 승인되면 내부 검증 skill을 만들고 새 Claude·Codex 세션 각 1회로 mode 진입, playbook Read, 원문 단계 todo, leaf 직접 호출의 제약 유지를 확인 |
| 복원 보존·질문 분기의 수용 분류 | 독립 판정 불가(라운드 4) | 기존 엄격화와 이번 인계가 허용한 차이를 수용 기준으로 명문화한 뒤 독립 판정 |
| 옛 프로젝트의 실제 복원·폰트 로딩 | unverified | 승인된 실행에서 미추적·staged·누락 파일과 이전 엔진 덮어쓰기를 판별하고 선택 원본과 cmp. 폰트 로그·프레임·보관 폴더의 커밋 제외를 확인 |
| 원본 엔진·과거 메타데이터의 정보 부재 | 프로젝트별 미확인 | Git·보관본·제작노트·장면 설정 또는 사용자 확인으로 원래 값을 확보. 확인하지 못한 정보를 복원 완료로 보고하지 않음 |
