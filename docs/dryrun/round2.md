# dry-run 판정 (라운드 2, 시나리오 7)
- 판정자: Claude Opus 5.5 (claude-opus-5-5)
- 원본: 374df70(+ video-creator/CLAUDE.md), 대상: a723dde, op55: 828990b
- 실행하지 않은 것: 도메인 스크립트 전부(new_project, preflight, render, timeline, mix, finish, qa_check, cleanup, op55 scripts, `--help` 포함). 읽기 전용 확인으로 `git show`·`git diff`·`git status --short`·`git cat-file -e`·`cmp`·`grep`·`cat`만 썼다.

## 판정
| # | 시나리오 | 판정 | 핵심 근거 |
| --- | --- | --- | --- |
| 7 | 옛 프로젝트 폰트 재준비 + engine.js/fx.js 복원 | **의도된 차이** | 라운드 1의 회귀(이미 덮인 엔진을 되돌리지 못함)는 닫혔다. 이제 디스크 엔진이 최신 엔진과 같으면 HEAD 버전을 놓는다(resolve-showreel-tools/SKILL.md:61,69). 원본 운영 규칙의 `git checkout`(CLAUDE.md:32)과 같은 결과다. 나머지 경우(깨끗함, Git 밖, 의도한 미커밋 수정)는 같거나 더 엄격하다. 남은 차이는 진입·경로·`OP55_SCRIPTS`(의도된 차이)와 엄격화뿐이다. 판정을 바꾸지 않는 관찰이 4건 있다(아래) |

## 상세

### 읽는 파일과 순서
| 원본 | 대상 |
| --- | --- |
| `/showreel` 진입, `SKILL.md`. 옛 프로젝트 복원 절차는 skill에 없다. 관련 문서는 `new_project.py` 명령과 "다시 실행해도 유지된다"(374df70:SKILL.md:98-104), "engine.js 고치지 않는다 — new_project.py 가 최신으로 덮어쓴다"(374df70:references/engine.md:21)뿐이다 | `showreel-mode/SKILL.md` → 진행 방식 표에서 `playbooks/revise-video.md`를 고른다(showreel-mode/SKILL.md:39). 끝까지 읽고 번호 단계를 todo로 복사한다(:43) |
| 작업 폴더 규칙 `video-creator/CLAUDE.md:30-33`(세션에 자동으로 실린다). S는 CLAUDE.md:37, O는 CLAUDE.md:46 | revise-video 1단계에서 Read `../resolve-showreel-tools/SKILL.md`, S·O를 확인하고 환경 점검을 한 뒤 제작노트·PAUSE·script·timeline·qa·out을 읽는다. 다시 렌더해야 하는데 엔진·폰트가 그 영상 때와 다르거나 없으면 adapter의 "옛 프로젝트 복원"(resolve-showreel-tools/SKILL.md:54-72)을 먼저 한다(revise-video.md:11) |
| — | 같은 문서 1~5단계 순서. 판단이 서지 않을 때 제작노트를 근거로 쓴다(:62) |

### 명령·인자·env
| 단계 | 원본(CLAUDE.md) | 대상(resolve-showreel-tools/SKILL.md) |
| --- | --- | --- |
| 점검 | 없음 | `OP55_SCRIPTS=$O python3 $S/preflight.py`(:31). revise-video.md:11. 의도된 차이 + 엄격화 |
| 보관 | 없음 | 세 파일을 `<프로젝트>/.restore/<YYYYmmdd-HHMMSS>/`에 복사. Git 안이면 `git -C <프로젝트> status --short -- reel/engine.js reel/fx.js project.json`(:58) |
| 판정 | 없음 | M이면 `git -C <프로젝트> diff HEAD -- reel/engine.js reel/fx.js`, 디스크 파일과 `$S/../assets/engine/<같은 이름>`을 `cmp`(:61) |
| 폰트 | `python3 $S/new_project.py <프로젝트>`. 인자는 기본값 16:9·60·30(:31) | `python3 $S/new_project.py <프로젝트> --ratio <원래> --duration <원래> --fps <원래>`. `--force-engine` 금지(:63-67) |
| 엔진 | `git checkout -- <프로젝트>/reel/engine.js <프로젝트>/reel/fx.js`(:32) | 고른 버전을 놓는다. 보관본은 `cp`, HEAD는 `git -C <프로젝트> show HEAD:<저장소 기준 경로> > <파일>`. 이어서 `cmp`, `project.json`은 보관본으로, 처음에 깨끗했으면 `git status` 재확인, `git checkout` 금지(:69) |
| 음악 | `node $O/render.mjs`(:33) | `node $O/render.mjs`(:70). op55 828990b에 `skills/op55/scripts/render.mjs`가 있음을 확인 |
| env | S·O를 `$CLAUDE_PROJECT_DIR` 기준으로 고정(CLAUDE.md:37,46) | S는 adapter의 실제 경로, O는 `OP55_SCRIPTS`부터 찾는다(:15-22). 의도된 차이 |

`new_project.py`는 두 커밋에서 바이트가 같다(374df70:scripts/new_project.py ↔ skills/resolve-showreel-tools/scripts/new_project.py, diff 없음). 엔진 자산 4개도 같다. 기존 폴더에 실행하면 engine.js·fx.js를 늘 최신으로 덮고(:186-187), `_example_scenes.js`를 덮고(:190), project.json을 인자 값으로 덮는다(:201-202). index.html·scenes.js·timeline.js는 없을 때만 만들고(:188-197), 폰트는 없는 것만 받으며 `.extra_fonts`는 유지한다(:128-138). 양쪽에서 동작이 같다.

### 생기는 파일과 소비하는 필드
- 양쪽 공통: `reel/fonts/*`, `fonts.css`, `.google.css`, `.extra_fonts`, `_example_scenes.js`(덮어씀), 필요하면 `$S/node_modules`.
- 대상에만: `<프로젝트>/.restore/<시각>/{engine.js,fx.js,project.json}`. 소비하는 필드는 `project.json`의 `ratio`·`duration`·`fps`이고 3단계 인자로 쓴다. 원본은 project.json을 읽지 않고 기본값으로 덮는다.
- `project.json`을 읽는 스크립트는 없다(대상 scripts에서 grep. new_project.py:202에서 쓰기만 한다). 실제 규격은 `scenes.js`의 `REEL.config`에 있고, 이 파일은 양쪽 모두 덮어쓰지 않는다. 그래서 project.json 차이는 메타데이터 보존의 차이다.

### 사람 확인·비용·승인
- 원본: 확인 문장이 없다. 비용은 폰트·npm 네트워크뿐이다(유료 API 없음).
- 대상: 2단계에서 diff와 제작노트로도 판단할 수 없을 때만 "두 버전의 차이를 보여 주고 한 번 묻는다"(:62). 그 밖에는 묻지 않는다. 비용은 원본과 같다. adapter는 "렌더·유료 호출·삭제를 하지 않는다"(:9). 음악 렌더(:70)는 호출자가 할 일을 안내하는 것이고, op55 렌더는 로컬에서 하며 유료가 아니다.
- 분류: 질문은 판단할 수 없는 경우로 한정한 추가 확인 지점이다. 브리프의 "처음 한 번만 묻는다"(showreel-mode/SKILL.md:30)는 제작 흐름의 규칙이고, 이 질문은 수정 흐름의 모호한 상태를 해소하는 것이다. 엄격화로 본다.

### hard constraint
| 제약 | 원본 | 대상 | 분류 |
| --- | --- | --- | --- |
| 작업 파일은 프로젝트 안, `/tmp` 금지 | CLAUDE.md:17 | `.restore/`를 프로젝트 안에 둠(:58), showreel-mode/SKILL.md:54 | 같음 |
| engine.js를 고치지 않는다 | 374df70:references/engine.md:21 | build-video-scenes/references/engine.md:21 | 같음 |
| index.html·scenes.js 보존 | new_project 기본 동작 | `--force-engine` 금지를 명시(:63) | 엄격화 |
| 미커밋 수정 보존 | 없음(checkout이 지움) | `git checkout` 금지, 보관본 선택(:61,69) | 엄격화 |
| 원래 규격 유지 | 없음(project.json이 기본값으로 덮임) | 원래 ratio·duration·fps를 넘기고 project.json을 복원(:63,69) | 엄격화 |
| 작업 폴더 규칙과의 우선순위 | — | "작업 폴더 규칙이 `git checkout`을 지시하더라도 이 단계가 같은 목표를 대신한다"(:69) | 라운드 1 관찰을 닫음 |

### 경우별 대조표
기호: E0 = 그 영상 때 엔진(HEAD 또는 그 영상을 위해 고친 파일), L = 최신 엔진(`$S/../assets/engine`).

| # | 실행 전 상태 | 원본 운영(new_project → checkout) | 대상(:58-69) | 분류 |
| --- | --- | --- | --- | --- |
| a | Git 추적, 깨끗함(디스크 = HEAD = E0) | engine/fx = HEAD. project.json은 16:9·60·30으로 덮이고 남는다 | 상태가 깨끗해 보관본(= HEAD)을 놓고 cmp. project.json도 원래 값. `git status`는 다시 깨끗함 | 엄격화(엔진 결과는 같고 project.json은 보존) |
| b | Git 저장소 밖 | checkout 실패("not a git repository"). 엔진은 L로 남음 | 보관본(디스크 = E0)으로 복원 | 엄격화 |
| b' | 저장소 안이지만 추적 안 됨(`??`). video-creator의 실제 상태다: `projects/` 전체가 미추적이고 두 프로젝트 모두 `?? reel/engine.js` 등으로 나옴 | checkout 실패("pathspec did not match"). 엔진은 L로 남음 | 2단계 규칙이 `??`를 직접 다루지 않는다. "Git 저장소가 아니면"에 준해 보관본을 쓰거나 :62에 따라 한 번 묻는다. 어느 쪽이든 원본 이상이다 | 엄격화(관찰 1) |
| c | Git 추적, engine/fx에 의도한 미커밋 수정(디스크 ≠ HEAD, ≠ L) | checkout이 수정을 지우고 HEAD를 놓음 | cmp 결과 L과 다르므로 보관본(수정본) 유지(:61) | 엄격화 |
| c' | 섞인 경우(engine.js = L로 덮임, fx.js에 의도한 수정) | 둘 다 HEAD. fx 수정이 사라짐 | 파일마다 정한다(:59). engine은 HEAD, fx는 보관본 | 엄격화 |
| d | Git 추적, 이전 세션이 복원 없이 new_project를 실행해 엔진이 L로 덮임(디스크 = L ≠ HEAD) | checkout으로 HEAD(E0) | status M → diff → `cmp` = L이므로 HEAD 버전을 `git show HEAD:… >`로 놓고 cmp(:61,69) | **같음**(라운드 1 회귀가 닫힘) |
| d-pj | d와 같은데 이전 세션이 CLAUDE.md:31대로 인자 없이 실행해 project.json도 기본값으로 덮인 경우 | project.json은 기본값으로 남음 | 보관본(= 기본값)으로 되돌리고, 3단계도 그 기본값을 넘김. HEAD의 project.json은 쓰지 않음(:69 "늘 보관본") | 같음(둘 다 원래 값을 잃음. 관찰 2) |
| d-b | Git 밖이거나 미추적인데 이전 세션이 L로 덮은 경우 | checkout 실패, L | 보관본(= L) | 같음(되돌릴 원본이 양쪽 모두 없음) |
| e | Git 추적, 덮은 엔진을 HEAD에 이미 커밋함 | HEAD(= L) | 깨끗하므로 보관본(= L) | 같음(양쪽 모두 E0를 잃음) |

### 차이 목록과 분류
| 차이 | 근거 | 분류 |
| --- | --- | --- |
| 진입 `/showreel` → `showreel-mode` → revise-video | 374df70:SKILL.md:2 ↔ showreel-mode/SKILL.md:2,39; revise-video.md:11 | 의도된 차이 |
| S·O가 adapter의 실제 경로, preflight에 `OP55_SCRIPTS=$O` | CLAUDE.md:37,46 ↔ resolve-showreel-tools/SKILL.md:15-22,31 | 의도된 차이 |
| 복원 전 환경 점검 | revise-video.md:11 | 엄격화 |
| 실행 전 보관과 Git 상태 기록 | resolve-showreel-tools/SKILL.md:58 | 엄격화 |
| 파일마다 버전을 정하는 규칙(깨끗함/Git 밖 → 보관본, M이고 = L → HEAD, M이고 ≠ L → 보관본, 판단 불가 → 한 번 묻기) | :59-62 ↔ CLAUDE.md:32 | 엄격화. 경우 d에서는 같음 |
| 원래 ratio·duration·fps 전달, `--force-engine` 금지 | :63-67 ↔ CLAUDE.md:31 | 엄격화 |
| `git checkout` 대신 놓기와 `cmp` 검증, project.json 복원, 작업 폴더 규칙보다 이 단계가 먼저임을 명시 | :69 ↔ CLAUDE.md:32 | 엄격화. 우선순위 문장이 라운드 1 관찰을 닫음 |
| 결과 보고(보관 경로, 파일별 선택과 이유, cmp, Git 전후) | :72 | 엄격화 |
| 음악 재렌더 명령 | CLAUDE.md:33 ↔ :70 | 같음(O 경로는 의도된 차이) |
| upstream sync·`tools/sync.sh` 없음 | CLAUDE.md:38-45 | 의도된 차이 |

### 판정을 바꾸지 않는 관찰
1. **미추적(`??`) 상태가 2단계 규칙에 이름으로 없다.** video-creator의 실제 두 프로젝트가 이 상태다(`git -C projects/<p> status --short` → `?? project.json`, `?? reel/engine.js`, `?? reel/fx.js`. 디스크 엔진은 L과 cmp가 같음). 규칙(:60-62)은 "깨끗함/Git 밖"과 "수정됨"만 적는다. `??`를 "수정됨"으로 잘못 읽으면 cmp = L이라 HEAD를 고르고, `git show HEAD:… > 파일`이 실패하면서 리다이렉트가 파일을 0바이트로 만든다. 4단계 `cmp`와 1단계 보관본이 있어 복구할 수 있고, 원본(checkout 실패 → L)보다 나쁘지 않다. "추적되지 않으면 Git 밖과 같이 보관본"이라는 한 줄을 더하면 닫힌다.
2. **project.json이 이미 덮였을 때는 HEAD 분기가 없다(:69 "늘 보관본").** 원본도 같은 값을 잃으므로 회귀는 아니다. 이 파일을 읽는 스크립트가 없어 영향은 메타데이터에 그친다. 추적되고 M이면 engine/fx처럼 HEAD와 비교하는 분기를 둘 수 있다.
3. **"최신 엔진"을 현재 skillset 기준으로만 비교한다(:61).** 엔진이 바뀐 뒤에는 예전 L(덮어쓴 그때의 최신)이 현재 L과 달라진다. 그러면 덮인 파일을 "의도한 미커밋 수정"으로 분류해 보관본을 유지하고, checkout(HEAD)과 결과가 갈린다. 고정 커밋에서는 이런 일이 생기지 않는다. 엔진이 마지막으로 바뀐 날은 2026-10-12(showreel 6452122)이고, 작업 폴더의 첫 프로젝트는 2026-10-21에 만들어졌다. video-creator의 showreel HEAD, 설치본 `.claude/skills/showreel/assets/engine`, 대상 assets의 engine.js·fx.js는 모두 바이트가 같다. 앞으로 엔진을 바꿀 때는 이 비교를 "알려진 엔진 버전들 중 하나와 같은지"로 넓히거나, :62의 질문 분기로 보내야 한다.
4. **진입 조건을 확인하는 방법이 적혀 있지 않다(revise-video.md:11 "엔진·폰트가 그 영상 때와 다르거나 없으면").** 폰트는 남아 있고 엔진만 이전 세션에 덮인 경우(d), 에이전트가 엔진 차이를 확인하지 않으면 복원 분기에 들어가지 않을 수 있다. 원본 규칙(CLAUDE.md:30)도 "폰트를 먼저 받는다"는 틀로 적혀 있어, 폰트가 있으면 건너뛸 여지가 같다. 그래서 동등으로 본다. revise-video.md:11에 "엔진 차이는 `git status --short`나 `$S/../assets/engine`과의 `cmp`로 확인한다"를 더하면 강해진다.
5. (사소) 4단계의 "`git status`도 다시 깨끗해야 한다"는 1단계와 같은 경로 한정으로 읽어야 한다. `.restore/`는 `.gitignore`에 없어(video-creator/.gitignore 확인) 경로를 한정하지 않은 `git status`에는 `??`로 나온다. 프로젝트를 커밋할 때(CLAUDE.md:24) 함께 들어갈 수 있다. 작은 텍스트 파일 세 개라 영향은 작다.

## 회귀 목록
없음. 라운드 1의 회귀 1건(시나리오 7, 실행 전부터 엔진이 HEAD와 다를 때 되돌리지 못함, docs/dryrun/round1.md:220-225)은 a723dde에서 닫혔다(resolve-showreel-tools/SKILL.md:59-62,69. 경우 d에서 원본과 같은 HEAD를 놓는다).

## 판정 불가와 닫을 조건
없음. 모든 경우를 정적 추적으로 판정했다. 관찰 3(엔진이 바뀐 뒤의 비교 기준)은 고정 커밋에서 생길 수 없음을 커밋 날짜와 바이트 비교로 확인했다. 다음에 엔진 자산을 바꾸는 커밋에서는 다시 확인해야 한다.
