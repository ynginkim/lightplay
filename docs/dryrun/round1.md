# dry-run 판정 (라운드 1)
- 판정자: Claude Opus 5.5 (claude-opus-5-5)
- 원본: 374df70, 대상: 9028c20, op55: 828990b
- 실행하지 않은 것: 도메인 스크립트 전부(preflight, new_project, narrate, timeline, render, mix, finish, qa_check, cleanup, motion_check, contact_sheet, eleven, sfx_library, op55 render/verify/setup/preview 포함, `--help` 포함). 실행한 것은 `git show`, `git ls-tree`, `git diff`, `grep`, `sed -n`, `cat -n`, `diff` 같은 읽기 전용 명령뿐이다.

판정 규칙: 시나리오 판정은 차이 항목 가운데 가장 나쁜 것으로 정했다(회귀 > 판정 불가 > 의도된 차이 > 같음). 허용 목록에 없는 차이라도 원본보다 엄격하거나 동등하면 회귀로 세지 않고 "엄격화" 또는 "동등"으로 따로 적었다.

## 공통 사전 확인

- **스크립트와 자원은 바이트까지 같다.** `374df70:scripts/*`, `374df70:assets/*`의 모든 파일이 `skills/resolve-showreel-tools/scripts|assets/*`와 같다(`diff -q` 결과 차이 0건). 따라서 명령의 동작(인자, 출력 파일, 종료 코드)은 경로만 빼면 양쪽이 같다.
- **references는 내용이 같다.** 8개 파일을 비교한 결과 차이는 `scripts/x.py` → `$S/x.py` 경로 표기, 대시(—) → 콜론 같은 문장 부호, "SKILL.md 7단계" → "build-video-scenes의 스타일 프레임" 같은 상호 참조뿐이다. 규칙, 수치, 표는 바뀌지 않았다.
- **원본 SKILL.md의 "자주 생기는 문제" 17행**(374df70:SKILL.md:277-294)은 모두 대상 leaf로 옮겨졌고 빠진 행이 없다(plan-video:69, prepare-video-audio:89-92, build-video-scenes:69-74, deliver-video:107-111).
- **원본 "지킬 것" 6항**(374df70:SKILL.md:268-273)도 모두 어느 한 leaf의 "직접 불러도 지킬 것"에 있다(plan-video:15-17, prepare-video-audio:15-16, build-video-scenes:15-18, critique-video:16).

## 요약 표

| # | 시나리오 | 판정 | 핵심 근거 |
| --- | --- | --- | --- |
| 1 | 새 영상, 나레이션 없음 | 의도된 차이 | 0~11단계가 create-video 1~7단계에 같은 순서로 대응한다(374df70:SKILL.md:54-58 ↔ skills/showreel-mode/playbooks/create-video.md:13-25). 바뀐 것은 S·O 경로와 `OP55_SCRIPTS`뿐이고(resolve-showreel-tools/SKILL.md:31), 그 밖의 차이는 엄격화 또는 동등이다 |
| 2 | 새 영상, VO 있음 | 의도된 차이 | narrate·op55 빈틈 재렌더·`--mix`·리버브 금지·STT 두 번 규칙이 같다. `--mix`에 `SHOWREEL_SCRIPTS`와 `--mix-py`가 붙은 것은 허용된 차이다(374df70:SKILL.md:144 ↔ prepare-video-audio/SKILL.md:42) |
| 3 | VO gain·리버브만 수정 | 의도된 차이 | 양쪽 모두 믹스 → 마감만 다시 하고 영상은 다시 렌더하지 않는다(374df70:SKILL.md:235 ↔ revise-video.md:18). 대상은 입력과 같은 출력 이름을 막고 새 파일을 검수하는 단계를 더했다(엄격화) |
| 4 | 음악 교체(hit·energy·cue 소비 장면 있음) | 의도된 차이 | 원본은 격자만 같으면 영상을 재사용한다(374df70:SKILL.md:149). 대상은 hit·에너지 곡선·큐·크레딧까지 비교해 바뀌면 그 장면을 다시 렌더한다(prepare-video-audio/SKILL.md:74-83, revise-video.md:19). 엄격화다 |
| 5 | 9:16으로 수정 | 의도된 차이 | 안전 영역과 fx.js 회피 규칙이 같다(374df70:SKILL.md:293 ↔ build-video-scenes/SKILL.md:63,74). 대상은 자동 크롭 금지, 파생 프로젝트, 오디오 재사용 조건을 더했다(엄격화) |
| 6 | 납품 뒤 정리 | 의도된 차이 | 등록 → 목록 → `--apply` 순서가 같다(374df70:SKILL.md:258-264 ↔ deliver-video/SKILL.md:89-101). 대상은 삭제 승인을 skill 안에 명시하고 `--trash`만 주면 아무것도 옮기지 않는다는 점을 바로잡았다(엄격화) |
| 7 | 옛 프로젝트 폰트 재준비 + engine.js/fx.js 복원 | **회귀(경미, 조건부)** | 주 경로는 엄격화다(보관 → 원래 규격으로 실행 → 복원 → cmp). 단, 작업 폴더 규칙의 `git checkout`(video-creator/CLAUDE.md:32)이 하던 "그 영상 때 버전으로 되돌리기"를 대상은 실행 직전 디스크 상태로 되돌리기로 바꿨다(resolve-showreel-tools/SKILL.md:58,65). 그래서 실행 전부터 엔진이 HEAD와 다르면 복원하지 못한다 |
| 8 | leaf 직접 호출(prepare-video-audio, deliver-video) | 의도된 차이 | 두 leaf 모두 첫 줄에서 adapter를 Read하고 비용·라이선스·삭제 제약을 "직접 불러도 지킬 것"에 둔다(prepare-video-audio/SKILL.md:9,15-19; deliver-video/SKILL.md:9,15-19). 원본 SKILL.md의 해당 제약은 빠짐없이 있다. 하드 제약이 아닌 관찰 2건은 따로 적었다 |

## 시나리오별 상세

### 1. 새 영상, 나레이션 없음

**읽는 파일과 순서**

| 원본 | 대상 |
| --- | --- |
| `SKILL.md`(전체, 기준표·기본값·0~11단계 포함) | `showreel-mode/SKILL.md` → `playbooks/create-video.md`(끝까지 읽고 1~7단계를 todo로 복사, showreel-mode/SKILL.md:43) |
| 1단계 `references/brief.md` | 1단계 `resolve-showreel-tools/SKILL.md` → `plan-video/SKILL.md`의 "요청 읽기" → `brief.md` (create-video.md:13) |
| 2단계 `brief.md` "콘셉트 만들기", `design.md`, `story.md` "쇼릴" | 2단계 plan-video "콘셉트·조사·구성" → 같은 references(create-video.md:15, plan-video/SKILL.md:30-58) |
| 5단계 op55 skill 호출, `references/audio.md` | 3단계 `prepare-video-audio/SKILL.md` → `$O/../SKILL.md`, `showreel.md`, `audio.md`(prepare-video-audio/SKILL.md:25,33) |
| 6~8단계 `images.md`, `design.md`, `engine.md`, `techniques.md` | 4단계 `build-video-scenes/SKILL.md` → 같은 references(create-video.md:19) |
| 9단계 `qa.md` "비평" | 5단계 `critique-video/SKILL.md` → `qa.md`(create-video.md:21) |
| 10~11단계 `qa.md` "납품"·"납품 뒤 정리" | 6~7단계 `deliver-video/SKILL.md` → `qa.md`(create-video.md:23-25) |

**명령·인자·env**: preflight → new_project(`--ratio 16:9 --duration 60`) → op55 `render.mjs`/`verify.py --waveform-png` → (sfx_library find/use, eleven sfx) → `timeline.py --music-analysis` → render 스틸·초안·contact_sheet·motion_check → 최종 `render.mjs --sub 4`(또는 render_pieces) → motion_check → mix → finish → qa_check `--stt` → sfx_library add → cleanup(목록). 인자는 양쪽이 같다(374df70:SKILL.md:69,101,140-143,194-200,214-217,240,261-263 ↔ resolve-showreel-tools/SKILL.md:31,45; prepare-video-audio/SKILL.md:38-41; critique-video/SKILL.md:24-30; deliver-video/SKILL.md:26-36,68,92-94). 나레이션이 없으면 narrate는 건너뛰고 `--mix` 검증은 "나레이션이 생긴 뒤"라 하지 않는다. 이 점도 양쪽이 같다(374df70:SKILL.md:122,144 ↔ plan-video/SKILL.md:56, prepare-video-audio/SKILL.md:42).

**파일·필드**: `concept.md`, `research/`, `storyboard.md`, `script.json`(`lines: []`, `scenes`, `sfx`, `music.file=audio/music/music.wav`), `audio/music/{score.mjs,music.wav,analysis.json}`, `timeline.json`, `reel/timeline.js`, `qa/critique_NN.md`, `qa/qa_report.md`, `out/<제목>_<길이>s*`. 같다. 대상은 `analysis.json`의 `bpm`·`beats`·`downbeats`·`hits` 유효성을 받을 때 확인하라고 더했다(prepare-video-audio/SKILL.md:59; contract.md:77).

**사람 확인·비용·승인**: 질문은 1단계에서 사용자만 아는 사실만 묻고, 콘셉트는 알리기만 하고 확인을 기다리지 않는다. 같다(374df70:SKILL.md:60,82-84,94 ↔ showreel-mode/SKILL.md:30, plan-video/SKILL.md:24-26,36). 청취 요청도 같다(374df70:SKILL.md:252 ↔ showreel-mode/SKILL.md:22-24, deliver-video/SKILL.md:83). 비용 항목(codex 이미지, ElevenLabs 효과음)도 같다.

**hard constraint**: 작업 위치, 섬광, 실존 인물·로고, 출처 있는 숫자, BGM 코드 전용이 모두 유지된다(공통 사전 확인 참조).

**차이 목록**
| 차이 | 근거 | 분류 |
| --- | --- | --- |
| 진입 `/showreel` → `showreel-mode` + playbook 선택 | 374df70:SKILL.md:2 ↔ showreel-mode/SKILL.md:2,36-39 | 의도된 차이 |
| S가 adapter의 실제 경로, preflight에 `OP55_SCRIPTS=$O` | 374df70:SKILL.md:64,69 ↔ resolve-showreel-tools/SKILL.md:15-22,31 | 의도된 차이 |
| op55를 Skill로 "불러" 따르지 않고 문서(`$O/../SKILL.md`, `showreel.md`)를 Read해서 따름. 같은 문서를 읽고, op55 문서의 `$S`가 여기의 `$O`라는 점도 명시함 | 374df70:SKILL.md:128 ↔ prepare-video-audio/SKILL.md:25, showreel-mode/SKILL.md:53 | 동등(읽는 내용이 같고 변수 충돌을 명시함) |
| preflight에 나온 op55 경로가 O와 같은지 확인 | resolve-showreel-tools/SKILL.md:34 | 엄격화 |
| `analysis.json` 유효성 확인, op55 `verify.py`가 실패해도 종료 코드가 바뀌지 않는다는 주의 | prepare-video-audio/SKILL.md:57,59 (op55 verify.py에서 확인) | 엄격화 |
| playbook 단계를 todo로 복사하고 skip한 단계에 이유를 남김 | showreel-mode/SKILL.md:43 | 엄격화(절차 기록) |
| 맥락 없는 비평 agent에 의도·이전 판정을 주지 않음 | 374df70:SKILL.md:205 ↔ critique-video/SKILL.md:39 | 엄격화 |
| 정리 `--apply`는 사용자 확인 뒤에만 함(시나리오 6) | 374df70:SKILL.md:256 ↔ create-video.md:25 | 엄격화 |
| 정리되지 않은 이전 프로젝트나 디스크 부족은 "그 폴더의 정책"을 따름. 원본 skill에는 없고 작업 폴더 규칙에 있음 | video-creator/CLAUDE.md:64-65 ↔ create-video.md:13 | 동등(작업 폴더 정책에 맡김) |
| 결과물 기준표·기술 기본값·작업 위치가 진입 문서에서 `contract.md`로 옮겨짐. "Read" 지시는 없고 포인터만 있음 | 374df70:SKILL.md:8-50 ↔ showreel-mode/SKILL.md:26,32; plan-video/SKILL.md:11 | 동등(관찰): showreel-mode/SKILL.md:32가 기본값을 "쓴다"고 지시하므로 요청에 값이 없으면 contract를 읽게 된다. 숫자 기본값은 adapter 명령(:45), mix.py 기본값, audio.md 보이스 표(:39)에도 있다. 기준표 자체는 contract.md에만 있다 |

판정: **의도된 차이**

### 2. 새 영상, VO 있음

시나리오 1의 흐름에 다음이 더해진다.

| 항목 | 원본 | 대상 | 분류 |
| --- | --- | --- | --- |
| ElevenLabs 키가 없을 때 안내, 보이스가 막힐 때 `eleven.py voices --lang ko` | 374df70:SKILL.md:75-76 | resolve-showreel-tools/SKILL.md:37-38 | 같음 |
| 보이스 기본(Marcus, multilingual_v2, 0.45/0.8/0.4) | 374df70:SKILL.md:40 | contract.md:33, prepare-video-audio/references/audio.md:39 | 같음 |
| 원고: `text`/`tts` 분리, `cues`, 60초에 255자 이하, 요일 대조 | 374df70:SKILL.md:123-124 | plan-video/SKILL.md:57-58 | 같음 |
| `narrate.py --stt`, ✗ 줄 재생성, 바뀐 줄만 재생성, `takes` 제한 | 374df70:SKILL.md:138,160,272 | prepare-video-audio/SKILL.md:16,36,72 | 같음 |
| 나레이션 빈틈을 악보에 옮겨 적고 재렌더 | 374df70:SKILL.md:133 | prepare-video-audio/SKILL.md:31 | 같음 |
| op55 `verify.py --mix`: 원본은 `--mix-py` 없이 실행해 op55가 `.claude/skills/showreel/scripts/mix.py`를 찾음 | 374df70:SKILL.md:144; op55 828990b:skills/op55/scripts/verify.py:330-338 | `SHOWREEL_SCRIPTS=$S … --mix-py $S/mix.py`(prepare-video-audio/SKILL.md:42). 대상 폴더 이름(resolve-showreel-tools)은 op55의 대체 탐색에 걸리지 않으므로 명시가 필요하다 | 의도된 차이 |
| "showreel mix.py not found"나 빈 표를 미측정으로 처리 | 없음 | prepare-video-audio/SKILL.md:58 (verify.py:345의 메시지와 일치) | 엄격화 |
| 믹스: 리버브 금지, `--hall 0.04~0.08`, "말 끝 잔향" ✓, 줄별 6dB ✗ 처리 | 374df70:SKILL.md:233-235 | deliver-video/SKILL.md:50-52 | 같음 |
| 마감 SRT, `qa_check --stt`, STT가 한 번만 틀리면 한 번 더 | 374df70:SKILL.md:216-217,240-243 | deliver-video/SKILL.md:28-29,68-71 | 같음 |
| 비용: 나레이션 크레딧(ElevenLabs) | 374df70:SKILL.md:272 | prepare-video-audio/SKILL.md:16, resolve-showreel-tools/SKILL.md:76 | 같음 |

판정: **의도된 차이**

### 3. 기존 프로젝트에서 VO gain이나 리버브만 수정

**원본 흐름**: SKILL.md 전체 → 10단계의 "오디오만 고칠 때는 영상을 다시 렌더하지 않고 `mix.py`와 `finish.py`만"(374df70:SKILL.md:235,283) → `mix.py <timeline> [--hall …|--vo-db …]` → `finish.py --video out/video.mp4 …`(374df70:SKILL.md:216) → 11단계 qa_check. 정리된 프로젝트에서 `out/video.mp4`가 없을 때 원본에 있는 근거는 qa.md의 "마스터의 영상 스트림이 무음 렌더와 같아서 소리만 다시 입힐 때도 이 파일로 충분하다"(374df70:references/qa.md:181)뿐이다. 출력 이름 충돌에 대한 주의는 없다.

**대상 흐름**: showreel-mode → revise-video.md(showreel-mode/SKILL.md:39) → 1단계: adapter Read, `OP55_SCRIPTS=$O preflight`, `제작노트.md`·`PAUSE.md`·`script.json`·`timeline.json`·`qa/*`·`out/` 읽기(revise-video.md:11) → 2단계 표의 "gain, 덕킹, 리버브만" 행: 믹스 → 마감 → 완성본 검수, 영상 재렌더 없음(revise-video.md:18) → 3단계 deliver-video의 "오디오만 다시 마감"(revise-video.md:28; deliver-video/SKILL.md:54-61): mix.py → `out/video.mp4`가 있으면 finish 그대로, 없으면 마스터를 `--video`로 쓰고 `--name "<제목>_<길이>s_r2"` → 새 파일로 qa_check → 5단계 보고, 기존 납품본 교체 여부는 사용자가 정함(revise-video.md:34; deliver-video/SKILL.md:61).

**차이 목록**
| 차이 | 근거 | 분류 |
| --- | --- | --- |
| S 경로, preflight `OP55_SCRIPTS` | resolve-showreel-tools/SKILL.md:31 | 의도된 차이 |
| 입력과 같은 이름으로 마감하지 않음(`_r2`), 새 검수가 끝날 때까지 기존 마스터 보존 | deliver-video/SKILL.md:18,60; revise-video.md:3 | 엄격화. 원본에서 마스터를 `--video`로 쓰고 같은 `--name`을 주면, finish.py가 읽는 중인 파일에 마스터를 다시 쓴다(374df70:scripts/finish.py:8, 출력 `<name>.mp4`) |
| 수정 뒤 새 파일로 qa_check를 반드시 실행 | deliver-video/SKILL.md:61 vs 374df70:references/qa.md:161("mix.py → finish.py"까지만) | 엄격화 |
| 기존 납품본을 교체할지 사용자에게 물음, 제작노트 재생성 명령 갱신 | revise-video.md:34 | 엄격화(새 사람 확인 지점이며 비용은 없음) |
| 기존 기록을 먼저 읽고 preflight를 다시 실행 | revise-video.md:11 | 엄격화(비용 없음) |

**공통 관찰(차이 아님)**: 줄별 `gain_db`를 `script.json`에서 바꾸면 `timeline.py`가 이 값을 `timeline.json`으로 옮기므로(374df70:scripts/timeline.py:165) `timeline.py`를 다시 실행해야 믹스에 반영된다. 양쪽 문서 모두 "믹스 → 마감"만 적고 이 단계를 적지 않았다(374df70:SKILL.md:235,284 ↔ revise-video.md:18). `--vo-db` 옵션으로 고치면 이 단계가 필요 없다. 양쪽이 같으므로 회귀가 아니다.

판정: **의도된 차이**

### 4. 음악 교체(hit·energy·cue를 소비하는 장면 있음)

**원본 흐름**: op55 skill → 새 `score.mjs` 렌더·검증 → "박 격자(BPM·첫 다운비트)를 바꾸지 않으면 화면은 다시 렌더하지 않아도 된다. `mix.py`와 `finish.py`만"(374df70:SKILL.md:149). op55는 "옛 grid를 복사하고 새 beats가 옛 큐와 1ms 안에서 같은지 확인한 뒤 re-mix·re-finish만"이라고 한다(op55 828990b:references/showreel.md:25,30). `music.hitN` 번호가 밀린다는 주의는 장면을 만들 때만 있다(374df70:SKILL.md:150). 교체할 때 hit·에너지 곡선·크레딧을 비교하는 단계는 없다. `timeline.py`를 다시 실행하는지도 명시하지 않았다.

**대상 흐름**: revise-video.md 2단계 "음악 교체·편곡(격자 유지)" 행: op55 렌더·검증 → `timeline.py` → 소비값 비교 → 믹스 → 마감 → 검수. 박·다운비트·`music.start`·장면이 쓰는 큐·`music.hitN`·음악 에너지 곡선이 같거나 그 값을 쓰는 장면이 없을 때만 영상을 재사용한다(revise-video.md:19,29). prepare-video-audio의 "음악 교체": `timeline.json`·`reel/timeline.js`를 `.restore/<시각>/`에 보관하고, `music.meta.json`의 grid 또는 `analysis.json`에서 격자를 복구한 뒤 렌더·검증·`timeline.py`를 거쳐 비교하고, 바뀐 값과 그 값을 쓰는 장면 목록을 돌려준다(prepare-video-audio/SKILL.md:74-83). 화면 크레딧 문구가 바뀌면 그 장면을 다시 렌더한다(revise-video.md:20).

**차이 목록**
| 차이 | 근거 | 분류 |
| --- | --- | --- |
| 재사용 판단 기준이 "격자 같음"에서 "화면이 소비하는 값(hit·에너지·큐·크레딧) 같음"으로 바뀜 | 374df70:SKILL.md:149 ↔ prepare-video-audio/SKILL.md:47,81; principle-stable-cues-late-surfaces/SKILL.md:11 | 엄격화. 이 시나리오처럼 hit이나 에너지를 소비하는 장면이 있으면 원본은 화면과 음악이 어긋난 영상을 재사용하고, 대상은 그 장면을 다시 렌더한다. 음악 에너지 곡선은 `timeline.py`가 WAV에서 다시 계산하므로(contract.md:74) 격자가 같아도 바뀔 수 있다 |
| 교체 전 타임라인 보관(`.restore/`) | prepare-video-audio/SKILL.md:78 | 엄격화 |
| `timeline.py` 재실행을 명시 | prepare-video-audio/SKILL.md:80 | 엄격화(원본은 명시하지 않음) |
| 박자(beatsPerBar)가 불명확할 때만 사용자에게 묻는 지점이 새로 생김 | prepare-video-audio/SKILL.md:79 | 엄격화(좁은 조건의 새 질문 지점이며 기능 손실은 없음) |
| `--mix` 검증에 `SHOWREEL_SCRIPTS`·`--mix-py` | prepare-video-audio/SKILL.md:42 | 의도된 차이 |
| 비용: 음악은 API 비용 없음, 장면 재렌더 시간은 늘 수 있음(필요할 때만) | resolve-showreel-tools/SKILL.md:77; revise-video.md:13 | 엄격화 |

판정: **의도된 차이**

### 5. 9:16 규격으로 수정

**원본 흐름**: 원본에는 수정 경로가 따로 없다. 근거가 되는 것은 기본값의 "릴스·쇼츠면 9:16 1080×1920"(374df70:SKILL.md:39), `new_project.py --ratio`(374df70:SKILL.md:101), fx.js의 세로 회피 영역 위 250px·아래 420px(374df70:SKILL.md:293), design.md "레이아웃과 안전 영역"(374df70:references/design.md:112-127)이다. 장면 수정 뒤 진행은 10~11단계(전체 렌더 → mix → finish → qa_check)다. 기존 폴더에서 규격을 바꾸려고 `new_project.py --ratio 9:16`을 다시 실행하면 engine.js·fx.js·project.json을 덮어쓴다(374df70:scripts/new_project.py:8-9,186-202). 원본에는 이를 막는 문장이 없다.

**대상 흐름**: revise-video.md 2단계 "화면비·규격" 행: 레이아웃·안전 영역·장면 → 전체 렌더 → 포스터 → 검수. 음악·나레이션 길이가 같으면 오디오를 재사용하고, 자동 크롭으로 품질을 대신하지 않는다(revise-video.md:23). 기존 규격도 계속 다시 렌더해야 하면 파생 프로젝트를 만들고 유료 오디오를 복사하며, 파일 이름에 규격을 붙인다(revise-video.md:30). build-video-scenes "고칠 때": `REEL.config` 크기를 바꾸고 design.md의 안전 영역을 따르며 fx.js 회피 영역을 비운다(build-video-scenes/SKILL.md:63,74). 렌더·믹스·마감은 deliver-video를 따른다(revise-video.md:26). 정리된 프로젝트에는 `audio/mix.wav`가 없을 수 있다는 경고도 있다(revise-video.md:11).

**차이 목록**
| 차이 | 근거 | 분류 |
| --- | --- | --- |
| S 경로 | — | 의도된 차이 |
| 자동 크롭 금지, `REEL.config` 변경 명시 | build-video-scenes/SKILL.md:63; revise-video.md:23 | 엄격화 |
| 파생 프로젝트, 규격 접미사, 유료 오디오 복사 재사용 | revise-video.md:30 | 엄격화(원본 납품본 보호) |
| 안전 영역 수치와 fx.js 자동 회피 | 374df70:SKILL.md:293 ↔ build-video-scenes/SKILL.md:74 | 같음 |
| 표의 연쇄에 "믹스"가 따로 적혀 있지 않음. 오디오 재사용이라 적었고, `mix.wav`가 없을 수 있다는 경고(:11)와 deliver-video 위임(:26)이 있음 | revise-video.md:23 | 동등(관찰): 마감에 `--audio`가 필요하므로 정리된 프로젝트에서는 mix.py를 다시 실행하게 된다 |

판정: **의도된 차이**

### 6. 납품 뒤 정리

**원본 흐름**: 납품 보고 → "지울 목록부터 본 뒤 정리한다" → `sfx_library.py add` → `cleanup.py`(목록) → `cleanup.py --apply`(`--trash`면 휴지통)(374df70:SKILL.md:256-264; 374df70:references/qa.md:175-194). skill 안에는 "사용자가 확인한 뒤에만 지운다"는 문장이 없다. 이 조건은 작업 폴더 규칙에만 있다(video-creator/CLAUDE.md:89). 그 규칙의 "`--trash`로 휴지통에 옮긴다"는 표현은 실제 동작과 다르다. `--trash`만 주면 목록만 출력한다(374df70:scripts/cleanup.py:93-94).

**대상 흐름**: create-video 7단계: 정리 목록과 합계를 보고에 붙이고, 지우는 일은 사용자가 영상을 확인하고 끝났다고 한 뒤에만 한다(create-video.md:25). deliver-video "납품 뒤 정리": add → 목록 → 사용자 확인 뒤 `--apply`, 망설여지면 `--apply --trash`. `--trash`만 주면 아무것도 옮기지 않고, 납품 완료를 삭제 승인으로 보지 않으며, 정리 뒤 제작노트에 한 줄 남긴다(deliver-video/SKILL.md:89-99). 안전장치(`--force`)를 끄는 옵션은 일반 절차로 쓰지 않는다(deliver-video/SKILL.md:101). 지우지 않을 것도 적었다(deliver-video/SKILL.md:17).

**차이 목록**
| 차이 | 근거 | 분류 |
| --- | --- | --- |
| S 경로 | — | 의도된 차이 |
| 삭제 승인 조건을 skill 안에 명시 | 374df70:SKILL.md:256 ↔ deliver-video/SKILL.md:17,98 | 엄격화(작업 폴더 규칙 CLAUDE.md:89와 같은 수준이고, 원본 skill만 놓고 보면 더 엄격함) |
| `--trash` 단독 사용 오해를 바로잡음 | video-creator/CLAUDE.md:89 ↔ deliver-video/SKILL.md:98 (cleanup.py:93-94와 일치) | 엄격화 |
| `--force` 금지 | deliver-video/SKILL.md:101 | 엄격화 |
| 남길 것과 지울 것 표 | 374df70:references/qa.md:179-194 ↔ critique-video/references/qa.md(같은 표, 경로 표기만 다름) | 같음 |
| 정리 뒤 프로젝트 커밋(작업 폴더 규칙 CLAUDE.md:24)은 양쪽 skill 모두 다루지 않음 | — | 같음(작업 폴더 규칙) |

판정: **의도된 차이**

### 7. 옛 프로젝트의 폰트 재준비와 engine.js/fx.js 복원

**원본 skill**: 복원 절차가 없다. 문서에 있는 명령은 `new_project.py <프로젝트> --ratio 16:9 --duration 60 [--fonts …]`와 "다시 실행해도 유지된다"(374df70:SKILL.md:101-104)뿐이다. 이 명령을 기존 폴더에 실행하면 engine.js·fx.js를 최신으로, project.json을 인자 값으로 덮어쓴다(374df70:scripts/new_project.py:8-9,186-187,201-202).

**원본이 운영되던 작업 폴더 규칙**(skill 저장소 밖): ① `new_project.py <프로젝트>`(인자 기본값, 그래서 project.json이 16:9·60초·30fps로 덮어써짐) ② `git checkout -- reel/engine.js reel/fx.js`로 "그 영상 때 버전"으로 되돌림 ③ 음악은 `node $O/render.mjs`(video-creator/CLAUDE.md:30-33).

**대상**: revise-video 1단계에서 "엔진·폰트가 그 영상 때와 다르거나 없으면" adapter의 "옛 프로젝트 복원"을 실행한다(revise-video.md:11). ① `git -C <프로젝트> status --short -- reel/engine.js reel/fx.js project.json`을 기록하고 세 파일을 `.restore/<시각>/`에 복사 ② project.json의 ratio·duration·fps를 넘겨 `new_project.py` 실행, `--force-engine` 금지 ③ 보관본을 제자리로 복사, `cmp`로 확인, 처음에 깨끗했다면 `git status`가 다시 깨끗한지 확인, `git checkout` 금지 ④ 음악은 `node $O/render.mjs`(resolve-showreel-tools/SKILL.md:54-68).

**경우별 대조**
| 실행 전 상태 | 작업 폴더 규칙(원본 운영) | 대상 | 분류 |
| --- | --- | --- | --- |
| Git 깨끗함(보통의 경우) | engine/fx = HEAD, project.json은 기본값으로 덮어써짐 | engine/fx = HEAD(보관본 = HEAD), project.json도 원래 값 | 엄격화 |
| engine/fx에 의도한 미커밋 수정이 있음 | checkout이 수정을 지움 | 보존 | 엄격화 |
| Git 저장소가 아님 | checkout 실패 | 보관본으로 복원 | 엄격화 |
| **이전 세션이 복원 없이 new_project를 실행해 engine/fx가 이미 최신으로 덮인 상태(HEAD와 다름)** | checkout이 HEAD, 곧 그 영상 때 버전으로 되돌림 | 보관본(이미 최신)을 다시 놓는다. `git status`는 실행 전후 모두 dirty이고, 결과로 "Git 상태 전후"를 돌려줄 뿐 이 경우의 처리 규칙이 없다(resolve-showreel-tools/SKILL.md:65,68) | **회귀** |

**그 밖의 차이**
| 차이 | 근거 | 분류 |
| --- | --- | --- |
| 원래 규격 값을 넘김 | resolve-showreel-tools/SKILL.md:59-63 ↔ CLAUDE.md:31 | 엄격화 |
| 음악 재렌더 명령 | CLAUDE.md:33 ↔ resolve-showreel-tools/SKILL.md:66 | 같음(O 경로는 의도된 차이) |
| 작업 폴더 규칙(`git checkout`)과 대상 skill(`git checkout` 금지)이 같은 작업 폴더에서 충돌함. 어느 쪽이 먼저인지 정한 문장이 없음(showreel-mode/SKILL.md:32는 기술 값에만 적용됨) | CLAUDE.md:32 ↔ resolve-showreel-tools/SKILL.md:65 | 관찰(판정에 포함: 위 회귀와 같은 원인) |

판정: **회귀(경미, 조건부)**. 원본 skill만 기준으로 하면 대상이 기능을 더한 것이다. 원본 운영 기준(skill + 작업 폴더 CLAUDE.md)으로 보면 "그 영상 때 버전으로 되돌리기"라는 목표(CLAUDE.md:32; 대상도 revise-video.md:11에서 같은 목표를 적음)를 실행 전부터 엔진이 HEAD와 다른 경우에는 이루지 못한다.

### 8. playbook 없이 leaf를 직접 불렀을 때 hard constraint 유지

비교 기준: 원본은 `SKILL.md` 하나를 읽은 상태다. 대상은 leaf SKILL.md와, 그 leaf 첫 줄의 `Read ../resolve-showreel-tools/SKILL.md`로 읽게 되는 adapter다.

**prepare-video-audio 직접 호출**
| 원본 제약 | 원본 근거 | 대상 근거 | 결과 |
| --- | --- | --- | --- |
| BGM은 코드로만. 외부 음원·루프·음악 생성 서비스(ElevenLabs Music) 금지 | 374df70:SKILL.md:41,271 | prepare-video-audio/SKILL.md:15 | 유지. "샘플" 금지 문구는 "op55가 승인한 사운드뱅크 샘플은 op55 규칙 안에서"로 좁혀졌다. 원본도 같은 문서에서 op55 실제 악기 샘플을 쓰라고 하므로(374df70:SKILL.md:41,131) 원본 안의 모순을 정리한 것이다. 동등 |
| ElevenLabs 크레딧 절약, 바뀐 줄만, `takes` 제한 | 374df70:SKILL.md:272 | :16 | 유지(효과음 라이브러리 우선도 하드 목록에 들어가 엄격화) |
| `music_tools.py analyze` 금지, render가 쓴 `analysis.json` 사용 | 374df70:SKILL.md:148 | :17 | 유지 |
| op55 크레딧을 영상 크레딧과 보고에 넣기 | 374df70:SKILL.md:153 | :18,51 | 유지 |
| 작업 위치(프로젝트 폴더, /tmp 금지) | 374df70:SKILL.md:48 | :19 | 유지(동등) |
| 청취 요청 | 374df70:SKILL.md:153 | :51 | 유지 |
| 키 없음, 보이스 막힘 대체 경로 | 374df70:SKILL.md:75-76 | adapter:37-38 | 유지 |

**deliver-video 직접 호출**
| 원본 제약 | 원본 근거 | 대상 근거 | 결과 |
| --- | --- | --- | --- |
| 최종 렌더 뒤 motion_check 재실행 | 374df70:SKILL.md:227 | deliver-video/SKILL.md:15,39 | 유지 |
| 청취 요청 | 374df70:SKILL.md:252 | :16,83 | 유지 |
| 삭제는 목록부터 | 374df70:SKILL.md:256-263 | :17,97-101 | 유지하고 엄격화(사용자 확인, `--force` 금지, 지우지 않을 것 명시) |
| 나레이션 리버브 금지, 말 끝 잔향 ✓ | 374df70:SKILL.md:233 | :50 | 유지 |
| "고칠 것"을 모두 처리하고 최종 시트를 Read로 확인 | 374df70:SKILL.md:243 | :71 | 유지 |
| 납품 보고 필수 항목(절대 경로, 공개 전 확인, 재생성 명령 등) | 374df70:SKILL.md:245-252 | :75-83 | 유지(op55 크레딧 항목이 더해짐) |
| 작업 위치 | 374df70:SKILL.md:48 | :19 | 유지 |
| 출력 이름을 입력과 같게 두지 않기, 기존 마스터 보존 | 없음 | :18 | 엄격화 |

**관찰(하드 제약이 아니라 회귀로 세지 않음)**
- prepare-video-audio를 직접 부르면 나레이션 255자 상한이 본문에 없고 plan-video를 가리키는 포인터만 있다(prepare-video-audio/SKILL.md:72 ↔ 374df70:SKILL.md:123,281). 길이 초과는 `timeline.py`가 ✗로 막는다(prepare-video-audio/SKILL.md:60). 비용·라이선스·삭제 제약이 아니다.
- deliver-video를 직접 부르면 "모든 구간 유지 + 맥락 없는 비평 1회"가 입력 전제로만 적혀 있고 확인 단계가 없다(deliver-video/SKILL.md:11 ↔ 374df70:SKILL.md:205). 대상의 설계(반복과 중단은 playbook이 정함, showreel-mode/SKILL.md:9)에서 나온 결과이며 비용·라이선스·삭제 제약이 아니다.
- 나머지 leaf도 원본 "지킬 것"을 모두 가진다. 실존 인물 얼굴은 build-video-scenes/SKILL.md:15, 로고는 plan-video/SKILL.md:17과 build-video-scenes/SKILL.md:16, 숫자 출처는 plan-video/SKILL.md:16과 build-video-scenes/SKILL.md:17, 섬광은 build-video-scenes/SKILL.md:18과 critique-video/SKILL.md:16에 있다.

판정: **의도된 차이**

## 회귀 목록

1. **[시나리오 7] 실행 전부터 엔진이 HEAD와 다를 때 "그 영상 때 버전"으로 복원하지 못함(경미, 조건부).**
   - 원본 운영: video-creator/CLAUDE.md:32 `git checkout -- <프로젝트>/reel/engine.js <프로젝트>/reel/fx.js`
   - 대상: skills/resolve-showreel-tools/SKILL.md:58(실행 직전 디스크 상태를 보관), :65(보관본으로 복원, `git checkout` 금지, 처음에 깨끗했을 때만 결과를 검증)
   - 발생 조건: 프로젝트가 Git 안에 있고, 복원 전 `git status --short`에 engine.js 또는 fx.js가 수정됨으로 나온다(예: 이전 세션이 복원 없이 `new_project.py`를 실행함).
   - 영향: 옛 영상과 다른 엔진으로 다시 렌더한다. 원본 skill만 기준으로 하면 회귀가 아니다(원본 skill에는 이 기능이 없음).
   - 닫는 방법의 예: adapter 1단계에서 실행 전 상태가 dirty면 `git diff HEAD -- reel/engine.js reel/fx.js`를 보고, HEAD 버전(`git show HEAD:<경로>`)과 디스크 버전 가운데 무엇이 그 영상 때 것인지 정한 뒤 진행하는 분기를 둔다. 작업 폴더 CLAUDE.md:30-33과의 우선순위도 함께 정한다.

## 판정 불가와 닫을 조건

없음. 모든 시나리오를 정적 추적만으로 판정했다. 동작에 기대는 관찰 두 가지는 판정을 바꾸지 않았지만, 다음 라운드에서 확인할 만하다.

- contract.md에는 Read 지시가 없고 포인터만 있다(시나리오 1·2). 요청에 기술 값이 없으면 showreel-mode/SKILL.md:32가 contract.md를 읽게 만든다고 보고 동등으로 판정했다. 요청에 길이·규격이 모두 있으면 결과물 기준표(contract.md:5-24)를 읽지 않고 진행할 수 있다. create-video 1단계나 plan-video "콘셉트"에 `Read ../resolve-showreel-tools/references/contract.md`를 명시하거나, 실행 기록에서 읽혔음을 확인하면 이 관찰을 닫을 수 있다.
- 줄별 `gain_db` 수정에 `timeline.py` 재실행이 필요하다는 점이 양쪽 문서에 모두 없다(시나리오 3). 양쪽이 같아 회귀는 아니고, 원본 문서에도 있는 공백이다.
