# dry-run 판정 (라운드 3, 시나리오 7)

## 판정자·기준·실행 금지 범위

- 판정자: 이식 수정에 참여하지 않은 별도 Codex 에이전트.
- 시나리오: 옛 프로젝트의 폰트 재준비와 `engine.js`·`fx.js` 복원.
- 원본 커밋: `374df70`.
- 원본 운영 규칙: `/Users/fluentt/Documents/video-creator/CLAUDE.md`. 이번 판정에서 읽은 현재 파일을 기준으로 한다. 이 파일은 원본 커밋에 고정된 자료가 아니다.
- 대상 커밋: `7f669d78cea93c9454fc44b0cd9f62ba8466f991`.
- op55 기준 커밋: `828990bb00ed1b887bb29d79710006c3c4bec526`.
- 명세: `/Users/fluentt/Documents/motion-graphic-skills/.work/HANDOFF.md` 6절·7절과 최신 인계 범위.
- 읽기 전용 셸·Git 명령만 사용했다. 파일 수정, Git 상태 변경, 설치, 영상·음악 생성, 유료 호출을 하지 않았다.
- 도메인 스크립트는 `--help`를 포함해 실행하지 않았다.
- `docs/dryrun/round2.md`는 문서 형식 확인에만 사용했다. 아래 판정은 원본과 대상의 직접 추적 결과다.

아래에서 원본 경로는 `374df70`의 경로다. 대상 경로는 대상 커밋의 경로다. `CLAUDE.md`는 위 절대 경로의 파일이다. 줄 범위는 해당 파일의 줄 번호다.

## 판정표

| 번호 | 시나리오 | 판정 | 근거 |
| --- | --- | --- | --- |
| 7 | 옛 프로젝트 폰트 재준비와 엔진 복원 | **회귀** | 폰트 준비 스크립트는 같다. 대상은 보관과 버전 판별을 추가했다. 그러나 원본의 `git checkout -- <경로>`는 index 버전을 복원하고, 대상은 디스크 엔진이 최신 템플릿과 같으면 HEAD 버전을 선택한다. index와 HEAD가 다른 경우 복원 결과가 달라진다. 원본 `CLAUDE.md:30-33`, 대상 `skills/resolve-showreel-tools/SKILL.md:58-69`. |

확인된 회귀는 1건이다. 파일 누락과 원본 정보 부재에는 판정 불가 항목이 남는다.

## 읽는 파일과 순서

| 단계 | 원본 | 대상 |
| --- | --- | --- |
| 진입 | `/showreel`로 `SKILL.md`를 읽는다. 스크립트 경로 정의와 환경 점검은 `SKILL.md:64-76`에 있다. 작업 폴더의 복원 순서는 `CLAUDE.md:30-33`에 있다. | `skills/showreel-mode/SKILL.md:34-43`에서 기존 프로젝트 수정용 `playbooks/revise-video.md`를 고르고 끝까지 읽는다. |
| 프로젝트 확인 | 복원 절차에서 프로젝트 상태를 먼저 조사하라는 별도 단계는 없다. | `skills/showreel-mode/playbooks/revise-video.md:11`에서 adapter를 읽고 S·O 및 환경을 확인한다. 이어 제작노트, PAUSE, script, timeline, 검수 기록과 납품본을 읽는다. |
| 복원 진입 | `CLAUDE.md:30-33`의 폰트 준비 → 엔진 복원 → 필요한 음악 렌더 순서다. | `revise-video.md:11`에서 엔진 존재, Git 상태, HEAD diff, 최신 템플릿과의 비교, 제작노트로 상태를 판별한다. 복원이 필요하면 adapter의 옛 프로젝트 복원 분기로 들어간다. |
| 복원 세부 순서 | `new_project.py` 실행 후 두 엔진 파일을 `git checkout`으로 되돌린다. | `skills/resolve-showreel-tools/SKILL.md:58-72`의 보관 → 파일별 버전 선택 → 기존 규격으로 폰트 준비 → 엔진·project.json 복원 → 결과 보고 순서다. |
| 장면 작업이 이어질 때 | `SKILL.md:179-185`에서 `references/engine.md`, `references/design.md`를 읽는다. | `revise-video.md:26`에서 `build-video-scenes`를 부른다. `skills/build-video-scenes/SKILL.md:48-53`에서 engine·design reference와 큐 규칙을 읽는다. |
| 검수·납품이 이어질 때 | `SKILL.md:191-217,243-252`에 따라 렌더·비평·검수·보고를 한다. | `revise-video.md:32-34`에서 critique-video와 deliver-video로 연결한다. |

폰트·엔진 복원만 요청됐다면 음악 생성, 이미지 생성, 나레이션 재생성을 필수 작업으로 추가할 근거는 없다.

## 명령·인자·env

아래 명령은 문서에서 추출한 실행 예정 명령이다. 이번 판정에서는 실행하지 않았다.

| 목적 | 원본 | 대상 |
| --- | --- | --- |
| S | `SKILL.md:64`의 skill base directory 아래 scripts. 작업 폴더에서는 `CLAUDE.md:37`의 `$CLAUDE_PROJECT_DIR/.claude/skills/showreel/scripts`. | `skills/resolve-showreel-tools/SKILL.md:15`의 실제 adapter 경로 아래 scripts. |
| O | `CLAUDE.md:46`의 작업 폴더 설정. | adapter `:16-24`에서 `OP55_SCRIPTS`부터 정해진 순서로 찾는다. op55 문서 안의 S는 이 O다. |
| 환경 점검 | `python3 $S/preflight.py`, `SKILL.md:68-70`. | `OP55_SCRIPTS=$O python3 $S/preflight.py`, adapter `:30-34`. |
| 사전 보관 | 별도 지시 없음. | engine.js·fx.js·project.json을 프로젝트 안 `.restore/<시각>/`에 복사한다. Git 안이면 세 경로의 `git -C <프로젝트> status --short -- ...` 출력을 기록한다. adapter `:58`. |
| 버전 판별 | 별도 지시 없음. | `git -C <프로젝트> diff HEAD -- reel/engine.js reel/fx.js`, 최신 템플릿과 `cmp`, 제작노트를 사용한다. adapter `:59-62`. |
| 폰트 준비 | `python3 $S/new_project.py <프로젝트>`, `CLAUDE.md:31`. 기본값은 16:9·60초·30fps다. `scripts/new_project.py:174-176`. | `python3 $S/new_project.py <프로젝트> --ratio <원래 ratio> --duration <원래 duration> --fps <원래 fps>`. `--force-engine`을 금지한다. adapter `:63-67`. |
| 엔진 복원 | `git checkout -- <프로젝트>/reel/engine.js <프로젝트>/reel/fx.js`, `CLAUDE.md:32`. tree-ish를 지정하지 않았으므로 index에서 작업트리로 복원한다. | 보관본 복사 또는 `git -C <프로젝트> show HEAD:<저장소 기준 경로> > <파일>`. 선택한 원본과 `cmp`한다. adapter `:69`. |
| 메타데이터 복원 | 별도 지시 없음. | `project.json`은 항상 보관본으로 복원한다. 처음에 세 경로가 깨끗했다면 복원 후에도 깨끗한지 확인한다. adapter `:69`. |
| 음악 재렌더 | 필요하면 `node $O/render.mjs`, `CLAUDE.md:33`. | 같은 명령을 필요할 때 안내한다. adapter `:70`. op55의 구체적인 악보·출력 인자는 기준 커밋 `skills/op55/SKILL.md:39-42`에 있다. |
| test mix env | 이 복원 절차에는 없다. | adapter `:22`의 `SHOWREEL_SCRIPTS`·`--mix-py`는 op55 test mix용이다. 이 시나리오에서 test mix를 호출하지 않으면 적용되지 않는다. |

셸 변수의 유지에 기대지 않고 명령마다 실제 절대 경로나 S·O를 지정하도록 한 변경은 adapter `:21-22`에 명시돼 있다.

## 생성 파일·소비 필드

`git diff`로 다음 원본과 대상 파일의 차이가 없음을 확인했다.

- `scripts/new_project.py`와 `skills/resolve-showreel-tools/scripts/new_project.py`.
- `assets/engine/engine.js`와 대상 adapter의 같은 자산.
- `assets/engine/fx.js`와 대상 adapter의 같은 자산.
- `scripts/render.mjs`와 대상 adapter의 같은 스크립트.

| 파일·필드 | 양쪽의 실제 스크립트 동작 | 대상의 추가 처리 |
| --- | --- | --- |
| `reel/engine.js`, `reel/fx.js` | 실행할 때마다 현재 템플릿으로 덮어쓴다. 양쪽 new_project.py `:186-187`. | 실행 전에 보관하고 선택한 버전으로 되돌린다. adapter `:58-69`. |
| `reel/index.html`, `reel/scenes.js` | `--force-engine`이 없으면 이미 있는 파일은 보존한다. new_project.py `:188-197`. | `--force-engine` 금지를 명시한다. adapter `:63`. |
| `reel/_example_scenes.js` | 실행할 때마다 템플릿 예시를 복사한다. new_project.py `:190`. | 별도 복원 대상은 아니다. |
| `reel/timeline.js` | 없을 때만 빈 `window.TL`을 만든다. new_project.py `:191-192`. | 기존 타임라인을 복원 과정에서 다시 만들라는 지시는 없다. |
| `reel/fonts/*` | 유효한 기존 폰트를 재사용한다. 로컬 폰트 복사와 다운로드를 수행한다. new_project.py `:75-153`. | 같은 스크립트를 사용한다. |
| `fonts/.google.css`, `.extra_fonts`, `fonts.css` | Google CSS를 캐시하고 추가 서체 목록을 재사용한다. 확보한 서체로 fonts.css를 작성한다. new_project.py `:117-158`. | 같은 스크립트를 사용한다. |
| `project.json` | `ratio`, `width`, `height`, `fps`, `duration`을 명령 인자로 다시 쓴다. new_project.py `:194-202`. | 기존 `ratio`·`duration`·`fps`를 인자로 소비하고, 실행 후 파일 전체를 보관본으로 돌린다. adapter `:63-69`. |
| `$S/node_modules` | playwright-core가 없으면 scripts 폴더에서 npm install을 실행한다. new_project.py `:162-168`. | adapter `:52`에서 이 부수 효과를 알린다. |
| `.restore/<시각>/` | 없음. | 세 파일과 판별 근거를 보관한다. 프로젝트 커밋에는 넣지 않는다. adapter `:58,69,72`. |

원본 `assets/engine/index.html:6-7,44-47`은 fonts.css와 timeline·engine·fx·scenes를 읽는다. 실제 장면 규격은 `REEL.config`에도 있다. new_project.py는 기존 scenes.js의 설정을 덮어쓰지 않는다(`:194-197`).

폰트 다운로드 실패가 곧 스크립트 실패를 뜻하지는 않는다. 대체 경로와 경고가 있다. 실제 로드 여부는 렌더 로그와 fonts.css에서 확인하도록 양쪽에 남아 있다. 원본 `SKILL.md:287`, 대상 `skills/build-video-scenes/SKILL.md:71`, 양쪽 render.mjs `:153-154`.

## 사람 확인·비용·승인

| 항목 | 원본 | 대상 | 분류 |
| --- | --- | --- | --- |
| 복원 버전 확인 | 별도 질문 없이 checkout한다. `CLAUDE.md:31-32`. | diff와 제작노트로도 판단할 수 없으면 두 버전의 차이를 보여 주고 한 번 묻는다. adapter `:62`. | 의도된 차이. 모호한 상태의 확인을 추가했다. |
| 폰트·의존성 비용 | 폰트 다운로드와 npm 설치가 발생할 수 있다. new_project.py `:57-64,162-168`. | 같은 코드다. 네트워크와 설치본 변경을 adapter `:52`에서 설명한다. | 같음. |
| 음악 비용 | op55로 로컬 렌더한다. `CLAUDE.md:33,53`. | adapter `:80-81`에 음악 생성 API 비용이 없다고 명시한다. | 같음. |
| 유료 원본 보존 | 이 복원 절차에는 재생성 지시가 없다. | revise-video `:3`에서 기존 마스터와 유료 원본을 새 검수 완료까지 보존한다. | 의도된 차이. 보존을 명시했다. |
| 완성 영상의 사람 확인 | `SKILL.md:252`에서 직접 청취를 요청한다. | mode `:22-24`, revise-video `:34`에서 전체 영상과 소리 확인을 요청한다. | 같음. 대상은 문장을 구체화했다. |
| 삭제 승인 | `CLAUDE.md:89`에서 사용자가 영상을 확인하고 끝났다고 한 뒤 정리한다. | revise-video `:34`와 deliver-video `:17`에서 납품과 삭제 승인을 구분한다. | 같음. |

대상 복원 과정의 버전 확인 질문은 안전하게 선택할 근거가 없을 때 필요하다. 다만 디스크가 최신 템플릿과 같은 경우에는 질문 전에 HEAD로 단정한다. 이 분기가 아래 회귀에 해당한다.

## hard constraint

| 제약 | 원본 근거 | 대상 근거 | 판정 |
| --- | --- | --- | --- |
| 작업 파일은 프로젝트 안에 둔다. 시스템 임시 폴더는 쓰지 않는다. | `SKILL.md:46-50`, `CLAUDE.md:17`. | adapter contract `:39-45`, 복원 보관 위치 `adapter:58`. | 같음. |
| 장면과 index.html을 폰트 준비 때문에 초기화하지 않는다. | new_project.py `:188-197`. | 같은 코드, adapter `:63`의 force-engine 금지. | 같음. |
| 그 영상 때 엔진으로 되돌린다. | `CLAUDE.md:30-32`. | adapter `:59-69`. | 일반적인 unstaged 상태는 유지한다. index와 HEAD가 다른 상태에는 회귀가 있다. |
| 엔진을 장면 작업 중 임의 수정하지 않는다. | `references/engine.md:21`. | `skills/build-video-scenes/references/engine.md:21`. | 같음. |
| 결정성과 큐 기반 시각을 유지한다. | `references/engine.md:32-38`. | 대상 engine reference `:32-38`. | 같음. |
| 미커밋 파일을 일괄 checkout으로 지우지 않는다. | 원본에는 별도 보존 규칙이 없다. | adapter `:61-69`. | 보관을 추가했다. staged 상태의 올바른 복원 선택은 닫히지 않았다. |
| 렌더 프레임과 검수 근거 없이 완료를 선언하지 않는다. | `SKILL.md:203-209,243`. | critique-video `:15-17,33-45`, mode `:26`. | 같음. |
| 음악 생성 서비스를 호출하지 않는다. | `SKILL.md:41,271`. | adapter contract `:34`, op55 기준 SKILL.md `:63`. | 같음. |

## 경우별 대조표

기호는 다음과 같다.

- H: Git HEAD의 엔진.
- I: Git index의 엔진.
- D: 실행 전 작업트리 엔진.
- L: 현재 skillset의 최신 엔진 템플릿.
- E: 그 영상을 만들 때 사용한 엔진.

파일별로 적용한다. engine.js와 fx.js의 상태가 서로 다를 수 있다.

| 경우 | 실행 전 상태 | 원본 결과 | 대상 결과 | 분류 |
| --- | --- | --- | --- | --- |
| A | Git 추적. D=I=H=E. | new_project 후 checkout으로 I=E를 복원한다. | 보관본 D=E를 복원한다. project.json도 보존한다. | 의도된 차이. 엔진 결과는 같고 메타데이터 보존을 추가했다. |
| B | Git 밖. D=E가 남아 있다. | 폰트 준비 후 checkout은 성공할 수 없다. 엔진은 L로 남는다. | 보관본 E를 복원한다. adapter `:60,69`. | 의도된 차이. 복원 가능한 범위를 넓혔다. |
| C | Git 안의 미추적 파일 또는 HEAD에 없는 파일. D=E가 남아 있다. | index에도 해당 경로가 없다면 checkout할 수 없다. | 보관본 E를 사용한다. adapter `:60`. | 의도된 차이. |
| D | D≠H이고 D≠L. 제작노트에서 D가 그 영상을 위한 미커밋 수정임을 확인한다. I=H. | checkout으로 H를 복원한다. 미커밋 수정은 작업트리에서 사라진다. | 보관본 D를 복원한다. adapter `:61`. | 의도된 차이. 미커밋 수정 보존을 추가했다. |
| E | I=H=E. 이전 실행으로 D=L≠H가 됐다. | checkout으로 E를 복원한다. | 최신 템플릿과 같음을 확인하고 HEAD E를 복원한다. adapter `:61,69`. | 같음. |
| F | I=H=E. 더 이전 템플릿이 덮여 D≠H이고 D≠현재 L이다. 제작노트에서 덮어쓰기임을 확인한다. | checkout으로 E를 복원한다. | diff와 제작노트로 덮어쓰기를 확인한 뒤 HEAD E를 복원한다. adapter `:61`. | 같음. |
| G | F와 같지만 덮어쓰기인지 의도한 수정인지 확인할 수 없다. | checkout으로 I를 복원한다. | 두 버전의 차이를 보여 주고 한 번 묻는다. adapter `:62`. | 판정 불가. 사용자의 버전 선택이 필요하다. |
| H | H≠I=E. E가 stage된 뒤 작업트리만 최신 템플릿으로 덮여 D=L이 됐다. | checkout으로 index의 E를 복원한다. | D=L이므로 HEAD H를 선택하고 복원한다. index의 E를 판별에 사용하지 않는다. adapter `:61,69`. | **회귀 R7-1**. |
| I | engine.js는 경우 E, fx.js는 경우 D다. | 두 파일 모두 index 버전으로 복원한다. | 파일마다 HEAD 또는 보관본을 선택한다. adapter `:59-61`. | 의도된 차이. 단, 각 파일의 index 상태에도 R7-1이 적용된다. |
| J | Git 추적 파일이 디스크에서 누락됐다. index에는 E가 있다. | new_project가 파일을 만든 뒤 checkout으로 E를 복원할 수 있다. | 첫 단계는 세 파일 복사를 요구한다. 누락 파일 보관과 복원 버전 선택의 예외가 명시돼 있지 않다. adapter `:58-60`. | 판정 불가. |
| K | Git 밖 또는 미추적 상태에서 이미 D=L로 덮였고 E의 사본이 없다. | E를 복원할 근거가 없다. | 보관본도 L이다. E를 복원할 근거가 없다. | 판정 불가. 양쪽의 공통 정보 부재다. |
| L | project.json은 이미 기본값으로 덮였다. 원래 값의 사본이 없다. | 기본값으로 다시 쓴다. | 현재 파일의 기본값을 읽고 보관본으로 돌린다. adapter `:63,69`. | 판정 불가. 원래 메타데이터의 복원을 증명할 수 없다. |

J는 진입 조건과 복원 절차 사이의 공백이다. revise-video `:11`은 파일이 없는 경우에도 복원 분기로 들어가도록 하지만, adapter에는 없는 파일을 어떻게 보관하고 복원할지 명확한 지시가 없다.

## 차이 목록·분류

| 차이 | 분류 | 근거 |
| --- | --- | --- |
| `/showreel`에서 `showreel-mode`로 진입 | 의도된 차이 | 원본 SKILL.md `:2`, 대상 mode `:2,34-43`. |
| adapter가 반환한 실제 S·O 사용 | 의도된 차이 | 원본 SKILL.md `:64`, 대상 adapter `:15-23`. |
| `OP55_SCRIPTS`, test mix의 `SHOWREEL_SCRIPTS`·`--mix-py` 명시 | 의도된 차이 | 원본 SKILL.md `:68-70`, 대상 adapter `:22,30-34`. |
| upstream sync와 tools/sync.sh 제거 | 의도된 차이 | 원본 CLAUDE.md `:38-43`에는 sync 흐름이 있다. 대상 커밋의 추적 파일 목록에는 tools/sync.sh가 없다. |
| 보관본·cmp·project.json 복원과 모호할 때 질문 추가 | 의도된 차이 | 원본 CLAUDE.md `:30-33`, 대상 adapter `:58-72`. |
| 폰트 준비 코드와 엔진 자산 | 같음 | 대응 파일의 Git diff가 비어 있다. |
| index를 복원하던 경로를 HEAD 고정 복원으로 변경 | 회귀 | 원본 CLAUDE.md `:32`, 대상 adapter `:61,69`. |
| 누락 파일과 원본 정보가 없는 상태의 복원 | 판정 불가 | 대상 revise-video `:11`, adapter `:58-69`. |

## 회귀 목록

### R7-1. stage된 원래 엔진을 두고 HEAD의 다른 엔진을 복원한다

원본 명령은 다음과 같다.

```bash
git checkout -- <프로젝트>/reel/engine.js <프로젝트>/reel/fx.js
```

tree-ish가 없으므로 index의 파일을 작업트리에 복원한다. 원본 근거는 `CLAUDE.md:32`다.

대상은 디스크 엔진이 최신 템플릿과 같으면 이전 덮어쓰기로 단정하고 HEAD를 선택한다(`skills/resolve-showreel-tools/SKILL.md:61`). 이후 `git show HEAD:<경로>`로 복원한다(`:69`).

다음 상태에서 결과가 달라진다.

```text
HEAD: 이전 엔진 H
index: 영상을 만들 때 사용한 엔진 E
작업트리: 이후 new_project가 덮어쓴 최신 엔진 L
H, E, L의 바이트가 서로 다름
```

원본은 E를 복원한다. 대상은 H를 복원한다. 대상의 `cmp`는 선택한 H와 비교하므로 이 잘못된 선택을 검출하지 못한다. index의 E 자체는 남지만, 다시 렌더할 작업트리에는 다른 엔진이 놓인다.

닫을 조건은 다음과 같다.

1. HEAD·index·작업트리의 차이를 구분한다.
2. index가 HEAD와 다르면 index도 복원 후보로 보관하고 판별한다.
3. 위 상태와 engine.js·fx.js가 서로 다른 상태를 독립 판정자가 다시 추적한다.
4. 선택한 엔진이 그 영상 때 버전이라는 근거와 파일별 바이트 대조를 남긴다.

이 회귀가 닫히기 전에는 시나리오 7의 회귀 0건을 선언할 수 없다.

## 판정 불가·닫을 조건

| 항목 | 이유 | 닫을 조건 |
| --- | --- | --- |
| 누락된 engine.js·fx.js·project.json | 대상 진입 조건에는 누락이 포함된다. 보관 단계에는 누락 예외가 없다. 원본은 index에 파일이 있으면 엔진 복원이 가능하다. | 존재하는 파일만 보관하는 규칙, 누락 기록, index·HEAD·외부 보관본의 선택 순서, 어느 원본도 없을 때의 중단 조건을 명시한다. |
| 이전 템플릿 덮어쓰기와 의도한 수정의 구분 | 바이트 차이만으로 변경 의도를 확정할 수 없다. 대상은 제작노트와 사용자 확인을 요구한다. | 해당 프로젝트의 제작노트나 사용자가 선택한 버전을 확보한다. adapter `:61-62`. |
| 원본 엔진 사본 자체가 없음 | Git·보관본 모두 없으면 양쪽 문서로 E를 재구성할 수 없다. | 영상을 만들 때의 엔진 사본이나 식별 가능한 커밋을 확보한다. |
| 원래 project.json 정보가 이미 사라짐 | 현재 파일을 보관하는 것만으로 과거 값을 복원할 수 없다. | Git·보관본·제작노트·장면 설정에서 원래 값을 확인한다. 확인할 수 없는 필드는 복원 완료로 보고하지 않는다. |
| 폰트의 실제 확보와 화면 동일성 | 정적 코드 일치가 다운로드 성공이나 렌더 결과를 증명하지 않는다. | 별도로 승인된 실행 환경에서 폰트 확보 결과, 로드 로그와 같은 시각의 프레임을 확인한다. |
| op55 재렌더의 실제 바이트 동일성 | 양쪽 문서에 동일성 기록이 있으나 이번에는 렌더하지 않았다. | 승인된 실행에서 원래 악보·뱅크·기준 엔진으로 재렌더하고 기존 WAV와 비교한다. |

도메인 실행과 실제 영상·음악 품질 확인은 하지 않았다. 남은 핵심 위험은 staged 엔진의 복원 버전을 잘못 선택해 다른 화면을 렌더하는 것이다.
