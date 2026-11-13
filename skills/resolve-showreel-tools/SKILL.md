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
- **O**: op55를 쓸 때만 확인하는 scripts 절대 경로다. `preflight.py`는 `OP55_SCRIPTS`, 이 skill 옆, 작업 폴더와 상위 폴더의 `.claude/skills`·`.agents/skills`, 두 하네스의 홈 설치 순서로 찾는다. 각 위치에서 `resolve-op55-tools/scripts`만 확인한다. 옛 `op55/scripts` 배치는 사용하지 않는다. 이는 발견을 위한 후보이며 특정 커밋을 요구하지 않는다.
- 지정한 `OP55_SCRIPTS`가 유효하지 않으면 다른 엔진으로 자동 대체하지 않는다. 설치본의 현재 문서·도구 위치를 읽고 `O`를 정한다. preflight가 찾지 못하면 사용자에게 설치 경로를 묻거나 설치를 안내한다. 음악 경로 선택은 prepare-video-audio가 맡는다. op55가 없어도 이 skillset의 다른 음악 경로를 쓸 수 있다.
- 셸 변수는 명령 사이에 남지 않는다. 명령마다 확인한 절대 경로를 그대로 쓰거나 같은 명령 줄 앞에 `S=… O=…`를 붙인다. leaf 문서의 `$S`, `$O`는 이 두 값을 뜻한다.
- 환경 점검에 확인한 `OP55_SCRIPTS`를 명시한다. 나레이션 대 배경 검사는 이 skillset의 `mix.py`가 소유한다. op55에는 영상 믹서 경로나 타임라인을 넘기지 않는다. 전역 환경 변수와 사용자 설정은 바꾸지 않는다.
- 설치 안내는 `npx skills@1.7.4 add ynginkim/op55 -a claude-code -a codex`다. 옛 사본은 새 설치 후 `npx skills@1.7.4 remove op55`로 지우도록 안내한다. 전역 사본이면 `-g`를 붙인다. 제거를 자동 실행하지 않는다. 설치·사운드뱅크 다운로드는 사용자가 선택한다. 뱅크가 없어도 합성 악보만 쓸 수 있는지는 설치본 문서로 확인한다. 설치 경로·명령·버전은 prepare-video-audio가 읽는 현재 op55 문서가 정한다.

## 환경 점검

원래 0단계다.

```bash
OP55_SCRIPTS=$O python3 $S/preflight.py
```

op55를 사용할 때는 위 명령에 `OP55_SCRIPTS`를 전달한다. op55를 사용하지 않으면 이 환경변수 없이 같은 점검을 실행한다. 결과의 "쓸 수 있는 경로"를 돌려준다. `caps.music`은 발견한 scripts 경로 또는 null이다. 경로 발견은 문서·뱅크·음악 품질 확인을 뜻하지 않는다. `caps.op55_version`은 도구 skill의 metadata.version, 없으면 `render.mjs --version`에서 읽은 버전 또는 null이다. null이면 실제 경로와 "버전 미확인"을 제작노트에 남긴다. 버전 숫자로 실행을 막지 않고 실제 산출물의 수락 기준으로 판정한다. `caps.music_api`는 키 없음·Free 플랜이면 false, 키가 있지만 Music 사용 가능 여부가 미확인이면 null이다. TTS 조회 권한 부족으로 Music 키까지 무효라고 판단하지 않는다.

- **codex CLI나 이미지 스킬이 없을 때**: codex-image·photoreal·codex-cli 스킬은 https://github.com/revfactory/skills 에 있다. 출력된 설치 명령을 사용자에게 안내한다. 설치하지 않으면 코드로 그린 그래픽과 사용자 제공 사진으로 구성한다. 사용자가 "realphoto"라고 부르는 스킬의 실제 이름은 `photoreal`이다.
- **ElevenLabs 키가 없을 때**: 나레이션이나 선택한 Music API에 키가 필요하면 발급·로컬 설정 절차를 안내한다. 키를 받기 전에는 op55 또는 내장 합성·화면 제작을 진행할 수 있다. TTS용 키의 Music 권한은 별도로 확인한다. 키 원문은 받거나 출력하지 않는다.
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

이미 만든 프로젝트를 다시 렌더하기 전에 엔진을 복원하거나 폰트를 다시 준비해야 할 때 쓴다. `new_project.py`를 기존 폴더에 다시 실행하면 `scenes.js`·`index.html`은 그대로 두지만 `reel/engine.js`·`reel/fx.js`를 이 skillset의 최신 엔진으로, `project.json`을 명령의 인자 값(기본 16:9·60초·30fps)으로 덮어쓴다. 그래서 순서를 지킨다.

1. 보관: 세 파일 중 존재하는 파일을 `<프로젝트>/.restore/<YYYYmmdd-HHMMSS>/`에 복사하고 없는 파일을 기록한다. 프로젝트가 Git 저장소 안이면 `git -C <프로젝트> status --short -- reel/engine.js reel/fx.js project.json`의 출력도 기록한다.
2. 되돌릴 버전 정하기: 목표는 그 영상을 만들 때의 엔진이다. 파일마다 다음으로 정한다.
   - Git 저장소 밖이거나 파일이 미추적(`??`) 또는 index에 없으면 보관본(지금 디스크의 파일)을 쓴다. 보관본도 없으면 원본 파일을 요청하고 멈춘다.
   - index에 있는 `engine.js`나 `fx.js`는 `git -C <프로젝트> diff -- reel/engine.js reel/fx.js`로 비교한다. 차이가 없으면 보관본, 디스크에 파일이 없으면 index 버전을 쓴다. 그 밖에는 디스크 파일을 이 skillset의 최신 엔진(`$S/../assets/engine/`의 같은 이름 파일)과 `cmp`로 비교한다. 최신 엔진과 같으면 이전에 복원 없이 `new_project.py`가 덮어쓴 것이므로 index 버전을 쓴다. 최신 엔진과 다르면 diff와 제작노트로 이전 엔진이 덮어쓴 것인지, 그 영상을 위해 고친 미커밋 수정인지 확인한다. 전자는 index, 후자는 보관본을 쓴다.
   - 어느 쪽인지 판단할 수 없으면 사용자에게 두 버전의 차이를 보여 주고 한 번 묻는다. 현재 최신 엔진과 다르다는 이유만으로 미커밋 수정으로 분류하지 않는다.
   - index는 `git checkout -- <파일>`이 복원하는 스테이징 버전이다. 고른 index 버전은 폰트 준비 전에 `git -C <프로젝트> show :<저장소 기준 경로> > <보관 폴더>/index-<파일 이름>`으로 따로 추출한다. 실패하면 멈춘다. HEAD와 다를 수 있으므로 HEAD로 대신하지 않는다.
3. 폰트 준비: `project.json`의 ratio·duration·fps를 읽어 같은 값을 넘긴다. 파일이 없으면 제작노트와 `reel/scenes.js`의 `REEL.config`에서 원래 규격을 확인한다. 확인할 수 없으면 사용자에게 묻고 값이 정해질 때까지 멈춘다. `--force-engine`은 쓰지 않는다.

   ```bash
   python3 $S/new_project.py <프로젝트> --ratio <원래 ratio> --duration <원래 duration> --fps <원래 fps>
   ```

4. 엔진 복원: 2단계에서 고른 보관본이나 추출한 index 파일을 원래 자리에 복사한다. 놓은 파일이 고른 원본과 바이트가 같은지 `cmp`로 확인한다. `project.json`은 보관본이 있으면 늘 보관본으로 되돌린다. 없으면 3단계에서 확인한 규격으로 생성된 파일을 유지하고, 확인하지 못한 과거 메타데이터를 복원했다고 보고하지 않는다. 1단계에서 Git 상태가 깨끗했다면 같은 세 경로로 한정한 `git -C <프로젝트> status --short -- reel/engine.js reel/fx.js project.json`도 다시 깨끗해야 한다. `.restore/`는 프로젝트 커밋에 넣지 않는다. 미커밋 수정이 함께 사라질 수 있으므로 `git checkout`으로 되돌리지 않는다. 작업 폴더 규칙이 이 자리에서 `git checkout`을 지시하더라도 이 단계가 같은 목표(그 영상 때 엔진)를 대신한다.
5. 음악도 다시 만들어야 하면 prepare-video-audio의 "음악 교체"로 간다. 이전 음악 제공자와 엔진·악보·분석을 확인한다. 현재 설치본이 과거와 같은 바이트를 만든다고 가정하지 않는다.

결과로 보관 폴더 경로, 파일마다 고른 버전과 이유, `cmp` 결과, Git 상태 전후를 돌려준다.

## 외부 도구와 비용

| 도구 | 쓰는 leaf | 확인과 비용 |
| --- | --- | --- |
| Node 18 이상, 시스템 Chrome, playwright-core | build-video-scenes, critique-video, deliver-video | `preflight.py`. 렌더 시간은 영상 길이에 비례 |
| ffmpeg, Python numpy·Pillow | 모든 검사·믹스·마감 | `preflight.py` |
| ElevenLabs(나레이션·효과음) | prepare-video-audio | 키는 `eleven.py check`. 크레딧이 든다. 음악 API는 아래 ElevenLabs Music 행을 따른다 |
| op55와 필요한 사운드뱅크 | prepare-video-audio | 기본 음악 경로. 음악 생성 API 비용 없음. 필요한 뱅크의 다운로드와 디스크 |
| ElevenLabs Music | prepare-video-audio | 선택 경로. 사용자 BYOK와 Music 권한·유료 크레딧 필요 |
| 내장 synth_music.py | prepare-video-audio | 앞선 두 경로가 실패하거나 사용 불가할 때. ffmpeg·numpy, 외부 음악 API 비용 없음 |
| codex CLI, codex-image·photoreal 스킬 | build-video-scenes | 사용자 전역 설치(홈의 .claude/skills). 이미지당 약 1분, 플랜 사용량 차감 |
| swiftc(macOS) | build-video-scenes(누끼) | 없으면 누끼 없이 진행 |
| 공용 효과음 라이브러리 | prepare-video-audio, deliver-video | `sfx_library.py`가 `--lib`, 환경 변수 `SHOWREEL_SFX_LIBRARY`, `$CLAUDE_PROJECT_DIR/sfx-library` 순으로 찾는다. 셋 다 없으면 위치를 모른다며 멈춘다. 이때는 `sfx_library.py --lib <작업 폴더>/sfx-library find 종이`처럼 하위 명령 앞에 `--lib`를 붙인다 |
| `asset_qa.py` | 에셋 프레임 폴더 검수 | `players` `routes` `loop` `ink` `motion` `markers` `themes` `sheet` `report`. numpy·Pillow. 판정은 그림 영역의 최악 프레임으로 한다. 플레이어 비교는 32 초과 화소 5% 초과 ✗, 1.5% 또는 평균 5.0 초과 △. 경로 비교는 20% 초과 ✗, 평균 12.0 또는 가장자리 채도 차이 0.01 초과 △. 두 폴더의 배경색이 24 넘게 다르면 ✗. 마커의 진입 경계는 구간 앞 12스텝, 루프 이음새는 구간 전체에서 움직이는 스텝의 변화에 대한 비로 1.5 이하 ✓, 3.0 이하 △, 3.0 초과 ✗(구간 프레임이 모자라면 절대 차이 1.0·3.0). 루프는 비 1.5 초과 ✗. ✗는 종료 코드 1, 도구 오류는 2. 1080p 480프레임 `report`는 10코어에서 44~63초(부하 평균 12~18에서 3회 잰 값) |
| `encode_asset.py` | 에셋 프레임 폴더 인코딩 | GIF(폭 480, 50fps 이하, 지연은 20 ms 이상이고 누적 반올림이라 길이가 10 ms 안에서 맞는다. 알파 없는 GIF는 ffmpeg 팔레트로, 알파 GIF만 Pillow로 만든다)·VP9 WebM(알파)·APNG·MP4. WebM·MP4는 BT.709 행렬·원색, sRGB 곡선으로 태그한다. 프레임 번호가 끊기면 거부한다. 오류는 종료 코드 2. ffmpeg. 1080p 480프레임 WebM은 10코어에서 28~33초(같은 부하) |

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

공유 계약(결과물 기준, 기술 기본값, 작업 위치, 프로젝트 파일, 음악 경계)은 `references/contract.md`에 있다.
