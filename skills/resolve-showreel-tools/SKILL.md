---
name: resolve-showreel-tools
description: "showreel 스크립트·엔진 자원의 실제 경로(S)와 op55 경로(O)를 확인하고, 환경 점검·새 프로젝트·옛 프로젝트 복원 명령과 공유 계약을 제공하는 도메인 adapter."
disable-model-invocation: true
---

# showreel 도구 경로와 공유 계약

입력은 작업 폴더와(있으면) 프로젝트 폴더다. 결과는 `S`·`O`의 실제 절대 경로, 환경 점검의 "쓸 수 있는 경로"와 없는 도구의 설치 안내, 만든 프로젝트 경로 또는 복원 결과다. 다른 leaf는 제목 바로 아래에서 이 파일을 읽고 여기서 정한 경로로 명령을 실행한다. 이 skill은 렌더·유료 호출·삭제를 하지 않는다.

이 폴더가 실행 자원을 한 벌 소유한다. 스크립트는 이 폴더의 scripts, 엔진 템플릿과 효과음 프리셋은 그 옆의 assets다. 두 폴더의 상대 배치를 바꾸지 않는다(`new_project.py`, `eleven.py`, `sfx_library.py`가 scripts의 부모에서 assets를 찾는다). 라이선스는 이 폴더의 LICENSE(MIT)다.

## S와 O

- **S**: 이 SKILL.md를 연 실제 경로의 폴더 안 scripts 폴더의 절대 경로다. `test -f "$S/preflight.py"`로 확인한다.
- **O**: op55의 scripts 폴더다. 아래 순서로 보고 `render.mjs`가 있는 첫 폴더를 쓴다. 이 순서는 `preflight.py`가 op55를 찾는 순서와 같다.
  1. 환경 변수 `OP55_SCRIPTS`
  2. 이 skill 옆에 설치된 op55: `$S/../../op55/scripts`
  3. 작업 폴더와 그 위쪽 폴더의 `.claude/skills/op55/scripts`, `.agents/skills/op55/scripts`
  4. 사용자 홈의 .claude/skills/op55/scripts
- 셸 변수는 명령 사이에 남지 않는다. 명령마다 확인한 절대 경로를 그대로 쓰거나 같은 명령 줄 앞에 `S=… O=…`를 붙인다. leaf 문서의 `$S`, `$O`는 이 두 값을 뜻한다.
- 자식 명령에 경로를 명시한다. 환경 점검에는 `OP55_SCRIPTS`를, op55의 test mix에는 `SHOWREEL_SCRIPTS`와 `--mix-py`를 넘긴다. 예전 설치 위치를 찾는 스크립트 안의 대체 탐색에 기대지 않는다. 전역 환경 변수와 사용자 설정은 바꾸지 않는다.
- op55는 기준 커밋에서 skill 하나다. op55 문서는 O의 부모 폴더의 SKILL.md(`$O/../SKILL.md`)와 그 references다. op55 문서의 `$S`는 op55의 scripts, 곧 여기의 `O`다.
- O를 찾지 못하면 `npx skills add ynginkim/op55 -a claude-code`로 설치하라고 안내한다. 사운드뱅크는 `node $O/setup.mjs`로 받는다(기본 88MB, 사용자 홈의 .cache/op55/banks).

## 환경 점검

원래 0단계다.

```bash
OP55_SCRIPTS=$O python3 $S/preflight.py
```

결과의 "쓸 수 있는 경로"를 돌려주고, 표의 BGM 스킬(op55) 경로가 위에서 정한 O와 같은지 확인한다.

- **codex CLI나 이미지 스킬이 없을 때**: codex-image·photoreal·codex-cli 스킬은 https://github.com/revfactory/skills 에 있다. 출력된 설치 명령을 사용자에게 안내한다. 설치하지 않으면 코드로 그린 그래픽과 사용자 제공 사진으로 구성한다. 사용자가 "realphoto"라고 부르는 스킬의 실제 이름은 `photoreal`이다.
- **ElevenLabs 키가 없을 때**: 나레이션이 필요한 요청이면 `preflight.py`가 출력하는 키 발급 절차를 안내하고, 키를 받기 전까지 음악·화면 버전으로 진행할 수 있다고 알린다. 음악은 op55로 작곡하므로 키와 관계없다.
- **고른 보이스가 막힐 때**(Free 플랜은 라이브러리 보이스를 쓸 수 없다): `python3 $S/eleven.py voices --lang ko`로 쓸 수 있는 보이스를 고르거나 플랜 업그레이드를 안내한다.

## 새 프로젝트

원래 3단계 앞부분이다. 폴더 구조, 엔진, 한글 폰트, 렌더러 의존성이 한 번에 준비된다.

```bash
python3 $S/new_project.py <프로젝트> --ratio 16:9 --duration 60 [--fonts "Hahmlet:wght@300;900"]
```

기본 서체 세트 밖의 Google Fonts 한글 서체는 `--fonts`로 더한다(여러 번 쓸 수 있고, 다시 실행해도 유지된다).

`reel/scenes.js`는 빈 장면 파일로 생긴다. API 사용 예시는 `reel/_example_scenes.js`에 있다. 예시의 화면을 출발점으로 삼지 말고 콘셉트에서 새로 쓴다.

렌더러 의존성(playwright-core)이 없으면 `new_project.py`가 S 폴더 안에서 `npm install`을 실행한다. 네트워크가 필요하고 설치본 폴더 안에 `node_modules`가 생긴다. 폰트는 로컬에 있으면 복사하고 없으면 내려받는다(모두 SIL OFL).

## 옛 프로젝트 복원

이미 만든 프로젝트를 다시 렌더하기 전에 폰트를 다시 준비해야 할 때 쓴다. `new_project.py`를 기존 폴더에 다시 실행하면 `scenes.js`·`index.html`은 그대로 두지만 `reel/engine.js`·`reel/fx.js`를 이 skillset의 최신 엔진으로, `project.json`을 명령의 인자 값(기본 16:9·60초·30fps)으로 덮어쓴다. 그래서 순서를 지킨다.

1. 보관: 프로젝트가 Git 저장소 안이면 `git -C <프로젝트> status --short -- reel/engine.js reel/fx.js project.json`의 출력을 기록한다. 세 파일을 `<프로젝트>/.restore/<YYYYmmdd-HHMMSS>/`에 복사한다.
2. 폰트 준비: `project.json`의 ratio·duration·fps를 읽어 같은 값을 넘긴다. `--force-engine`은 쓰지 않는다.

   ```bash
   python3 $S/new_project.py <프로젝트> --ratio <원래 ratio> --duration <원래 duration> --fps <원래 fps>
   ```

3. 엔진 복원: 보관한 세 파일을 원래 자리로 복사하고 `cmp`로 보관본과 바이트가 같은지 확인한다. 1단계에서 Git 상태가 깨끗했다면 `git status`도 다시 깨끗해야 한다. 미커밋 수정을 잃을 수 있으므로 `git checkout`으로 되돌리지 않는다.
4. 음악을 다시 렌더해야 하면 `node $O/render.mjs`로 렌더한다. 2026-10-23 이전 프로젝트의 제작노트에 있는 예전 showreel 안의 BGM 렌더 명령과 같은 엔진이고 같은 바이트가 나온다(video-creator의 pstack-harness, 2026-10-23-agent-skills에서 확인된 기록).

결과로 보관 폴더 경로, 세 파일의 `cmp` 결과, Git 상태 전후를 돌려준다.

## 외부 도구와 비용

| 도구 | 쓰는 leaf | 확인과 비용 |
| --- | --- | --- |
| Node 18 이상, 시스템 Chrome, playwright-core | build-video-scenes, critique-video, deliver-video | `preflight.py`. 렌더 시간은 영상 길이에 비례 |
| ffmpeg, Python numpy·Pillow | 모든 검사·믹스·마감 | `preflight.py` |
| ElevenLabs(나레이션·효과음) | prepare-video-audio | 키는 `eleven.py check`. 크레딧이 든다. 음악에는 쓰지 않는다 |
| op55와 사운드뱅크 | prepare-video-audio | 음악 생성 API 비용 없음. 첫 사운드뱅크 다운로드와 디스크 |
| codex CLI, codex-image·photoreal 스킬 | build-video-scenes | 사용자 전역 설치(홈의 .claude/skills). 이미지당 약 1분, 플랜 사용량 차감 |
| swiftc(macOS) | build-video-scenes(누끼) | 없으면 누끼 없이 진행 |
| 공용 효과음 라이브러리 | prepare-video-audio, deliver-video | 환경 변수 `SHOWREEL_SFX_LIBRARY`, 없으면 `<작업 폴더>/sfx-library` |

## 자료 위치

references 문서는 서로를 파일 이름만으로 부른다(예: "`design.md`의 뻔한 화면"). 이름을 만나면 아래 경로에서 읽는다. 각 파일은 그 기술을 맡은 leaf가 소유한다.

| 이름 | 경로 |
| --- | --- |
| `brief.md` | `../plan-video/references/brief.md` |
| `story.md` | `../plan-video/references/story.md` |
| `audio.md` | `../prepare-video-audio/references/audio.md` |
| `images.md` | `../build-video-scenes/references/images.md` |
| `design.md` | `../build-video-scenes/references/design.md` |
| `engine.md` | `../build-video-scenes/references/engine.md` |
| `techniques.md` | `../build-video-scenes/references/techniques.md` |
| `qa.md` | `../critique-video/references/qa.md` |
| `contract.md` | `references/contract.md`(이 폴더) |

`concept.md`, `research.md`, `storyboard.md`, `timeline.json`처럼 프로젝트 파일 이름은 프로젝트 폴더 안의 파일이다. 스크립트 이름(`timeline.py` 등)은 `$S` 안의 파일이다.

공유 계약(결과물 기준, 기술 기본값, 작업 위치, 프로젝트 파일, op55 경계)은 `references/contract.md`에 있다.
