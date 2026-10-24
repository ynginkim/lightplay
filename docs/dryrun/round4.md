# 정적 dry-run round 4: 시나리오 7

## 판정자와 범위

| 항목 | 내용 |
| --- | --- |
| 판정자 | `round4_judge`. 구현과 수정에 참여하지 않은 독립 판정자 |
| 시나리오 | 7. 옛 프로젝트의 폰트 재준비와 `engine.js`·`fx.js` 복원 |
| 원본 | `374df70` |
| 대상 | `5f84cc13f8e7695802d2717dd4db4a2a146ce3e9` |
| op55 기준 | `828990bb00ed1b887bb29d79710006c3c4bec526` |
| 원본 운영 규칙 | `/Users/fluentt/Documents/video-creator/CLAUDE.md`. 지정된 파일을 읽기만 했다 |
| 명세 | `/Users/fluentt/Documents/motion-graphic-skills/.work/HANDOFF.md` 6절과 7절 |
| 조사 방식 | 고정 커밋의 `git show`, `git ls-tree`, `git grep`, `git rev-parse`와 파일 읽기 |
| 실행 금지 범위 | 도메인 스크립트와 `--help`, 영상·음악 생성, 유료 호출, 설치, 파일 변경, Git 상태 변경 |
| 보고서 작성 | 파일을 쓰지 않았다. 이 문서 원문만 반환한다 |

과거 판정은 읽지 않았다. 작성 세션의 수정 의도도 판정 근거로 쓰지 않았다.

아래 원본 경로는 `374df70`, 대상 경로는 대상 커밋 기준이다. `CLAUDE.md`만 지정된 외부 작업 폴더의 현재 파일이다.

경로를 줄여 쓸 때 다음 이름을 사용한다.

| 이름 | 대상 파일 |
| --- | --- |
| adapter | `skills/resolve-showreel-tools/SKILL.md` |
| revise | `skills/showreel-mode/playbooks/revise-video.md` |
| mode | `skills/showreel-mode/SKILL.md` |
| contract | `skills/resolve-showreel-tools/references/contract.md` |
| 대상 스크립트 | `skills/resolve-showreel-tools/scripts/` |
| 대상 엔진 | `skills/resolve-showreel-tools/assets/engine/` |

## 판정표

시나리오 전체 판정은 **판정 불가**다. 원본의 index 복원 경로는 대상에서도 유지된다. 정적으로 확인된 회귀는 없다. 다만 대상이 추가한 보존·질문 분기는 명세에 열거된 의도된 차이 밖에 있다. 이 분기의 수용 여부는 별도로 남긴다.

| 대조 항목 | 판정 | 원본 근거 | 대상 근거 |
| --- | --- | --- | --- |
| 진입과 스크립트 실제 경로 | 의도된 차이 | `SKILL.md:64-69` | `mode:34-43`, `adapter:13-22` |
| 폰트 준비 스크립트와 엔진 템플릿 | 같음 | `scripts/new_project.py:171-202`, `assets/engine/engine.js`, `assets/engine/fx.js` | 같은 줄의 대상 스크립트와 대상 엔진. Git blob 동일 |
| 추적 파일을 index 버전으로 복원 | 같음 | `CLAUDE.md:30-32` | `adapter:59-70` |
| staged 버전과 HEAD의 구분 | 같음 | `CLAUDE.md:32`의 `git checkout --` | `adapter:63`에서 stage 0 index를 추출하며 HEAD 대체 금지 |
| 작업트리의 최신 엔진 덮어쓰기 판별 | 같음 | `CLAUDE.md:31-32`, `scripts/new_project.py:186-187` | `revise:11`, `adapter:61-63` |
| 확인된 미커밋 수정 보존 | 판정 불가 | 원본은 index 복원. `CLAUDE.md:32` | 보관본을 선택. `adapter:61-62` |
| Git 밖·미추적 파일 복원 | 판정 불가 | 원본 명령의 적용 전제에 맞지 않는다. `CLAUDE.md:32` | 보관본 사용 또는 사전 중단. `adapter:60` |
| `project.json` 보존 | 판정 불가 | 기본 인자로 새 파일을 쓴다. `CLAUDE.md:31`, `scripts/new_project.py:174-176,201-202` | 원래 규격 전달 후 보관본 복원. `adapter:64-70` |
| 추가 사람 확인과 중단 | 판정 불가 | 복원 단계의 추가 질문이 없다. `CLAUDE.md:30-33`, `SKILL.md:60` | 버전·규격을 모르면 질문하고 중단. `adapter:60-64` |
| 필요할 때 op55로 음악 재렌더 | 같음 | `CLAUDE.md:33`, `SKILL.md:140` | `adapter:71`, `skills/prepare-video-audio/SKILL.md:38` |
| 실제 프로젝트의 복원 결과 | 판정 불가 | 프로젝트별 HEAD·index·파일·제작노트 미제공 | 같은 자료가 필요하며 런타임도 실행하지 않음 |

## 읽는 파일과 순서

### 원본 흐름

1. `CLAUDE.md:30-33`의 옛 프로젝트 재렌더 절차를 적용한다.
2. `SKILL.md:64-76`에서 `S`와 환경 점검 절차를 확인한다.
3. `scripts/new_project.py`를 기존 프로젝트에 실행한다.
4. `CLAUDE.md:32`의 명령으로 두 엔진을 index 버전으로 복원한다.
5. 음악 재렌더가 필요하면 `CLAUDE.md:33`의 op55 경로를 따른다.
6. 장면 변경을 동반하면 `SKILL.md:179-185`에 따라 `references/engine.md`, `references/design.md`, 필요 기법의 `references/techniques.md`를 읽는다.
7. 재렌더와 납품까지 진행하면 `SKILL.md:191-252` 및 `references/qa.md`의 절차를 따른다.

원본 운영 규칙에는 복원 전 `project.json`, 엔진 diff, 제작노트를 읽는 별도 단계가 없다. 엔진 복원 명령은 두 파일을 index 내용으로 되돌린다.

### 대상 흐름

1. `mode:34-43`에서 기존 프로젝트 수정용 `revise-video.md`를 선택한다.
2. `revise:11`에서 adapter를 읽고 `S`·`O`와 환경을 확인한다.
3. 프로젝트의 `제작노트.md`, `PAUSE.md`, `script.json`, `timeline.json`, 검수 기록과 납품본을 읽는다.
4. 장면 재렌더가 필요하면 엔진 존재와 Git 상태를 확인한다. index diff, 현재 템플릿과의 `cmp`, 제작노트로 상태를 판별한다.
5. 엔진·폰트가 다르거나 없거나 상태가 불명확하면 `adapter:54-73`의 복원 분기를 먼저 따른다.
6. 파일 보관과 버전 선택을 마친 뒤 `project.json` 또는 제작노트·`REEL.config`에서 규격을 확인한다.
7. 폰트를 준비한 뒤 선택한 엔진과 원래 메타데이터를 복원한다.
8. 장면 변경·검수·납품이 필요하면 `revise:26-34`가 해당 leaf로 연결한다.

대상은 원본의 폰트 준비보다 앞에 보관과 버전 선택을 넣었다. `revise:11`과 adapter의 복원 분기가 연결되므로, 상태를 판별할 수 없는 엔진을 그대로 재렌더하는 경로를 지시하지 않는다.

## 명령·인자·환경 변수

이 절의 명령은 문서와 코드에서 추출한 실행 예정 명령이다. 이번 판정에서는 실행하지 않았다.

| 목적 | 원본 | 대상 |
| --- | --- | --- |
| 도구 경로 | `S=<showreel 스킬 폴더>/scripts` | 열린 adapter의 실제 폴더에서 `S` 결정. `O`는 `OP55_SCRIPTS`부터 탐색 |
| 환경 점검 | `python3 $S/preflight.py` | `OP55_SCRIPTS=$O python3 $S/preflight.py` |
| 복원 전 상태 | 별도 명령 없음 | `git -C <프로젝트> status --short -- reel/engine.js reel/fx.js project.json` |
| 작업트리 비교 | 별도 명령 없음 | `git -C <프로젝트> diff -- reel/engine.js reel/fx.js` |
| 템플릿 비교 | 별도 명령 없음 | 디스크 파일과 `$S/../assets/engine/`의 같은 파일을 `cmp` |
| index 확보 | 폰트 준비 뒤 `git checkout --`가 index를 사용 | 폰트 준비 전에 `git -C <프로젝트> show :<저장소 기준 경로>`로 선택한 index 파일 추출 |
| 폰트 준비 | `python3 $S/new_project.py <프로젝트>` | `python3 $S/new_project.py <프로젝트> --ratio <원래 ratio> --duration <원래 duration> --fps <원래 fps>` |
| 엔진 복원 | `git checkout -- <프로젝트>/reel/engine.js <프로젝트>/reel/fx.js` | 선택한 보관본 또는 추출한 index 파일을 복사하고 `cmp` |
| 메타데이터 복원 | 없음 | 보관한 `project.json`이 있으면 그 파일로 복원 |
| 복원 후 상태 | 별도 명령 없음 | 복원 전 깨끗했던 세 경로는 복원 후에도 깨끗한지 확인 |
| 필요한 음악 렌더 | `node $O/render.mjs` | `node $O/render.mjs` |

근거는 원본 `SKILL.md:64-69`, `CLAUDE.md:30-33`과 대상 `adapter:13-34,58-73`이다.

대상은 `--force-engine`을 금지한다. 해당 옵션은 양쪽의 동일한 스크립트에서 기존 `index.html`과 `scenes.js`까지 덮어쓰게 한다. 근거는 `adapter:64`와 양쪽 `new_project.py:177,188-197`이다.

음악을 실제로 다시 만들 때의 구체적인 명령은 양쪽 모두 다음 계약을 사용한다.

```bash
node $O/render.mjs --score <프로젝트>/audio/music/score.mjs --out <프로젝트>/audio/music/music.wav --analysis <프로젝트>/audio/music/analysis.json
```

근거는 원본 `SKILL.md:140`, 대상 `skills/prepare-video-audio/SKILL.md:38`, 고정 op55의 `skills/op55/SKILL.md:39-42`다. 단순 폰트·엔진 복원만으로 이 명령을 반드시 실행하라고 읽을 근거는 없다.

나레이션 test mix까지 필요하면 대상은 `SHOWREEL_SCRIPTS=$S`와 `--mix-py $S/mix.py`를 명시한다. 이는 지정된 의도된 차이다. 근거는 원본 `SKILL.md:144`, 대상 `skills/prepare-video-audio/SKILL.md:42`, 고정 op55의 `skills/op55/references/showreel.md:25-26`이다.

### 숨은 설치와 외부 접근

양쪽 `new_project.py`는 다음 동작도 수행한다.

- 폰트가 로컬에 없으면 `curl`로 받는다. `new_project.py:57-64,91-158`.
- 추가 폰트 목록은 `reel/fonts/.extra_fonts`에서 읽는다. `new_project.py:127-138`.
- `playwright-core`가 없으면 스크립트 폴더에서 `npm install --no-audit --no-fund --silent`를 실행한다. `new_project.py:162-168`.

`preflight.py`도 단순 파일 검사만 하지 않는다. op55 setup 확인과 Codex 로그인 상태 명령을 부르고, 키가 있으면 ElevenLabs 조회 요청을 보낸다. 양쪽의 동일한 `preflight.py:71-112`가 근거다.

이번 판정에서는 이 스크립트를 하나도 실행하지 않았다.

## 생성 파일과 소비 필드

| 파일 | 양쪽 스크립트의 동작 | 소비하는 곳 | 대상 복원 절차 |
| --- | --- | --- | --- |
| `reel/engine.js`, `reel/fx.js` | 템플릿을 매번 복사 | `index.html`의 script 태그 | 선택한 과거 파일로 다시 복원 |
| `reel/index.html` | 없거나 `--force-engine`일 때 생성 | 렌더러가 여는 페이지 | 기존 파일은 유지 |
| `reel/scenes.js` | 없거나 `--force-engine`일 때 stub 생성 | 엔진 설정과 장면 | 기존 파일은 유지 |
| `reel/_example_scenes.js` | 매번 예시 파일 복사 | API 예시 | 별도 복원 대상에 포함하지 않음 |
| `reel/timeline.js` | 없으면 빈 TL 생성 | 페이지와 장면 코드 | 원래 타임라인 재생성을 대신하지 않음 |
| `reel/fonts/*` | 폰트 준비와 CSS 재작성 | `fonts/fonts.css`, 브라우저 폰트 로딩 | 준비된 결과 유지 |
| `project.json` | `ratio`, `width`, `height`, `fps`, `duration`으로 매번 재작성 | 프로젝트 규격 기록, 대상의 복원 입력 | 기존 파일이 있으면 바이트 보존 |
| `.restore/<시각>/` | 원본에는 없음 | 복원본·index 추출본·상태 기록 | 대상이 추가하며 프로젝트 커밋에서 제외 |

스크립트 동작 근거는 양쪽 `new_project.py:181-202`다. 대상 복원 근거는 `adapter:58-73`이다.

페이지는 `fonts/fonts.css`와 `timeline.js`, `engine.js`, `fx.js`, `scenes.js`를 읽는다. 원본 `assets/engine/index.html:6-7,44-47`과 대상의 동일 파일이 근거다.

엔진은 `REEL.config`에서 길이·프레임률·크기를 받는다. 로딩된 폰트와 설정을 `window.__meta`로 제공한다. 렌더러는 이 값을 읽는다. `project.json`을 복원했다는 사실만으로 페이지 설정과 폰트 로딩까지 확인된 것은 아니다.

근거는 원본 `assets/engine/engine.js:248,321-346,412`, `scripts/render.mjs:152-154,184-186`이다. 대상 엔진과 렌더러는 각각 원본과 Git blob이 같다.

### 바이트 보존 확인

다음 파일은 `git rev-parse <커밋>:<경로>`로 같은 Git blob임을 확인했다.

| 파일 | 원본과 대상의 blob |
| --- | --- |
| `new_project.py` | `ae2acc32fb38f41469e1b7677d7e287d9e967a01` |
| `engine.js` | `7ede8bfc398b4c4c1d7cf531c6a94d7b11a3b33a` |
| `fx.js` | `af5b939346d4f53fbfabf0609ef5383ae2bb911a` |
| `index.html` | `c9d809aebd2f8ab0b7c7192737d5a69adfce5077` |
| 엔진 예시 `scenes.js` | `951d8ad7c452503510d94b94ae2fe287cb020f1d` |
| `preflight.py` | `b28599784b167347e691b402a4cb8591fe03e040` |
| `render.mjs` | `d2c6af89a649dbaf90fa2e93fc94faa2fdb62171` |

## 사람 확인·비용·승인

| 지점 | 원본 | 대상 | 판정 |
| --- | --- | --- | --- |
| 복원할 엔진 선택 | index 버전을 바로 사용. `CLAUDE.md:32` | 판단이 모호하면 두 버전을 보여 주고 한 번 질문. `adapter:62` | 추가 질문의 수용 분류는 판정 불가 |
| 원본 파일 없음 | 별도 사전 중단 절차 없음. `CLAUDE.md:30-32` | 보관본과 index가 없으면 원본을 요청하고 중단. `adapter:60` | 추가 안전 분기 |
| 규격 확인 불가 | 명령 기본값 사용. `CLAUDE.md:31`, 원본 `new_project.py:174-176` | 원래 값을 질문하고 결정 전 중단. `adapter:64` | 추가 질문의 수용 분류는 판정 불가 |
| 폰트 준비 | 로컬 복사 또는 다운로드. 원본 `new_project.py:91-158` | 같은 코드. `adapter:52`에도 명시 | 같음 |
| 렌더러 의존성 | 없으면 자동 npm 설치. 원본 `new_project.py:162-168` | 같은 코드이며 `adapter:52`에 명시 | 같음 |
| 음악 비용 | op55. ElevenLabs Music 금지. 원본 `SKILL.md:41,128` | 같은 원칙. `adapter:81-82`, `contract:34` | 같음 |
| 완성 영상 확인 | 소리를 직접 들어 달라고 요청. 원본 `SKILL.md:245-252` | 영상 전체와 스피커·이어폰 확인 요청. `mode:22-24` | 사람 확인 유지 |
| 삭제 | 영상 확인 뒤 종료 의사를 받아 정리. `CLAUDE.md:86-90` | 납품 완료와 삭제 승인을 구분. `skills/deliver-video/SKILL.md:99-103` | 복원만으로 삭제 승인 없음 |

복원 분기 자체는 TTS·이미지·효과음 생성을 요구하지 않는다. 다운로드와 자동 설치 가능성은 남아 있다. 대상 `adapter:9`도 이 skill이 렌더·유료 호출·삭제를 하지 않는다고 명시한다.

## Hard constraint

| 제약 | 원본 근거 | 대상 근거 | 정적 결과 |
| --- | --- | --- | --- |
| 모든 작업 파일은 프로젝트 안 | `SKILL.md:46-50`, `CLAUDE.md:17` | `mode:54`, `contract:39-45`, `adapter:58` | 보관 위치도 프로젝트 안 |
| 기존 장면을 폰트 준비로 초기화하지 않음 | `new_project.py:188-197` | 같은 코드, `adapter:56,64` | `--force-engine` 없이 기존 장면 유지 |
| 그 영상 때 엔진으로 복원 | `CLAUDE.md:30-32` | `adapter:59-70` | index 복원과 모호한 버전의 확인 경로 존재 |
| HEAD로 index를 대체하지 않음 | `CLAUDE.md:32`의 index 복원 | `adapter:63` | staged 버전 보존 |
| 폰트 라이선스 | `new_project.py:12-15` | 같은 코드, `adapter:52` | 준비 코드 변경 없음 |
| 화면 결정성과 큐 사용 | `SKILL.md:183-186` | `skills/build-video-scenes/SKILL.md:50-53` | 재렌더·장면 변경 시 유지 |
| 음악 서비스 호출 금지 | `SKILL.md:41,271` | `skills/prepare-video-audio/SKILL.md:15` | 복원 과정에서 새 음악 서비스 경로 없음 |
| 종료 코드만으로 품질 완료를 선언하지 않음 | `SKILL.md:203-207,243` | `mode:26`, `skills/critique-video/SKILL.md:33-45` | 복원 완료와 영상 검수 구분 |
| 유료 원본과 기존 납품본 보존 | `CLAUDE.md:72-79` | `revise:3`, `skills/deliver-video/SKILL.md:17-18` | 복원 분기에서 삭제 지시 없음 |

## 경우별 대조표

다음 표는 엔진 파일 하나의 상태를 기준으로 한다. 두 엔진은 각자 판별한다. `project.json`은 별도 행에 적었다.

- `H`는 HEAD의 파일이다.
- `I`는 stage 0 index의 파일이다.
- `W`는 폰트 준비 전 작업트리 파일이다.
- `N`은 현재 skillset의 엔진 템플릿이다.
- `A`, `B`, `C`는 서로 다른 바이트를 뜻한다.
- `없음`은 해당 위치에 파일이나 index 항목이 없다는 뜻이다.

원본 공통 근거는 `CLAUDE.md:31-32`와 원본 `new_project.py:186-202`다. 대상 공통 근거는 `adapter:58-70`이다.

| 경우 | H·I·W 조합 | 원본 흐름 | 대상 흐름 | 판정과 근거 |
| --- | --- | --- | --- | --- |
| 깨끗한 과거 엔진 | `H=I=W=A`, `A≠N` | N으로 덮은 뒤 I=A 복원 | W=A 보관 후 복원 | 같음. `CLAUDE.md:32`, `adapter:61,70` |
| staged 수정 | `H=A`, `I=W=B` | I=B 복원 | diff가 없으므로 W=B 보관본 복원 | 같음. HEAD=A로 바꾸지 않음. `adapter:61,63` |
| 최신 엔진으로 미복원 덮어쓰기 | `H=I=A`, `W=N=B` | I=A 복원 | W와 N이 같으므로 I=A 추출·복원 | 같음. `adapter:61,63` |
| staged 수정 뒤 최신 엔진 덮어쓰기 | `H=A`, `I=B`, `W=N=C` | I=B 복원 | I=B 추출·복원 | 같음. `adapter:61,63` |
| 더 오래된 템플릿이 W를 덮음 | `I=A`, `W=B`, `B≠N` | I=A 복원 | diff·제작노트로 덮어쓰기를 확인하면 I=A 복원 | 같음. 프로젝트별 사실 확인 필요. `adapter:61-62` |
| 확인된 프로젝트 미커밋 수정 | `I=A`, `W=B`, `B≠N` | I=A 복원하여 W=B는 사라짐 | W=B 보관본 복원 | 판정 불가. 결과 차이가 확정되며 보존 분기 수용 여부가 필요. `adapter:61` |
| W의 출처 불명 | `I=A`, `W=B`, `B≠N` | I=A 복원 | 두 버전을 보여 주고 질문 | 판정 불가. 추가 질문과 중단. `adapter:62` |
| 추적 엔진이 디스크에서 누락 | `I=A`, `W=없음` | N 생성 뒤 I=A 복원 | 폰트 준비 전 I=A 추출 후 복원 | 같음. `adapter:61,63` |
| staged 신규 엔진 | `H=없음`, `I=W=B` | I=B 복원 | W=B 보관본 복원 | 같음. `adapter:61,63` |
| staged 삭제 후 디스크에 파일 존재 | `H=A`, `I=없음`, `W=A` | N으로 덮은 뒤 해당 경로의 index 복원 불가 | W=A 보관본 사용 | 판정 불가. 원본과 결과가 다름. `adapter:60` |
| 미추적 엔진 | `H=I=없음`, `W=A` | N으로 덮으며 index 복원 불가 | W=A 보관본 사용 | 판정 불가. 추가 안전 분기. `adapter:60` |
| Git 밖의 엔진 | Git 없음, `W=A` | N으로 덮으며 Git 복원 명령 실패 | W=A 보관본 사용 | 판정 불가. 추가 안전 분기. `adapter:60` |
| 복원할 엔진이 어디에도 없음 | `I=W=없음` | N 생성 뒤 과거 파일 복원 불가 | 원본을 요청하고 폰트 준비 전 중단 | 판정 불가. 추가 중단 분기. `adapter:60` |
| index가 충돌 상태 | stage 0 없음 | 원본 checkout으로 정상 복원 확정 불가 | 필요한 index 추출이 실패하면 중단 | 판정 불가. `adapter:63` |
| 두 엔진 상태가 서로 다름 | 예: engine은 staged, fx는 누락 | 두 경로를 한 명령으로 복원 | 파일마다 버전을 결정하고 확보 | 각 파일의 위 분기 적용. `adapter:59-63` |
| 기존 project.json 존재 | 기본값과 다른 규격·메타데이터 | 기본 규격의 JSON으로 덮음 | 원래 규격을 전달하고 기존 파일을 복원 | 판정 불가. 명세 밖 결과 차이. `adapter:64-70` |
| project.json 누락, 규격 확인 가능 | 제작노트·REEL.config 있음 | 기본 규격 JSON 생성 | 확인한 규격으로 생성. 과거 메타데이터 전체 복원은 주장하지 않음 | 판정 불가. `adapter:64,70` |
| project.json 누락, 규격도 불명 | 확인 자료 없음 | 기본 규격 JSON 생성 | 질문하고 값 확정 전 중단 | 판정 불가. 추가 중단 분기. `adapter:64` |
| scenes.js 또는 index.html 누락 | 장면 또는 페이지 파일 없음 | stub 또는 템플릿 생성 | 같은 스크립트가 생성 | 생성 동작은 같음. 과거 장면 복원 성공은 판정 불가. 양쪽 `new_project.py:188-197` |

작업트리가 최신 템플릿과 다르다는 사실만으로 미커밋 수정이라고 결론 내릴 수 없다. 대상은 `adapter:62`에서 이 추론을 금지한다. 과거 템플릿 덮어쓰기와 프로젝트 수정은 제작노트나 사람 확인으로 구분한다.

복원 전 상태가 깨끗했던 경우의 사후 확인은 세 경로로 한정된다. `.restore/`, 예시 파일, 폰트 파일을 포함한 프로젝트 전체가 깨끗하다고 선언하는 조건은 아니다. 근거는 `adapter:70`이다.

## 차이 목록과 분류

| 차이 | 분류 | 근거 |
| --- | --- | --- |
| `/showreel`에서 `showreel-mode`로 진입 변경 | 의도된 차이 | 명세 6절, 원본 `SKILL.md:1-3`, 대상 `mode:1-4` |
| adapter가 확인한 실제 S·O 사용 | 의도된 차이 | 명세 6절, 원본 `SKILL.md:64,128`, 대상 `adapter:13-24` |
| `OP55_SCRIPTS`, `SHOWREEL_SCRIPTS`, `--mix-py` 명시 | 의도된 차이 | 명세 6절, 대상 `adapter:22,31`, `skills/prepare-video-audio/SKILL.md:42` |
| upstream sync와 `tools/sync.sh` 없음 | 의도된 차이 | 명세 6절. 원본 운영 규칙 `CLAUDE.md:38-45`와 대상 커밋 트리 대조 |
| 보관 폴더와 파일별 선택 근거·cmp 결과 추가 | 판정 불가 | 원본 `CLAUDE.md:30-33`에 없는 산출물. 대상 `adapter:58-73` |
| 확인된 미커밋 수정과 Git 밖 파일 보존 | 판정 불가 | 원본 index 복원과 결과가 다름. 대상 `adapter:60-62` |
| 원래 project.json 보존과 규격 전달 | 판정 불가 | 원본 기본값 덮어쓰기와 다름. 대상 `adapter:64-70` |
| 모호한 버전·누락 원본·불명 규격에서 질문 또는 중단 | 판정 불가 | 원본 절차에 없는 확인 지점. 대상 `adapter:60-64` |

추가 분기는 파일 유실을 줄이는 방향이다. 하지만 명세에 열거된 차이만으로 이 분기의 수용 여부까지 확정하지 않았다. 판정자의 추정으로 의도된 차이 목록을 넓히지 않았다.

## 회귀 목록

정적으로 확정한 회귀는 없다.

특히 다음 결함은 대상 고정 커밋에서 확인되지 않았다.

- HEAD를 index 대신 사용하도록 지시하는 결함.
- 디스크에서 엔진이 사라졌을 때 복원 원본을 확보하지 못하는 결함.
- 현재 템플릿과 다르다는 이유만으로 W를 프로젝트 수정으로 분류하는 결함.
- 엔진 상태를 판단하지 못한 채 재렌더를 계속하도록 지시하는 결함.
- 기존 `project.json`을 보관하지 않고 기본값으로 확정하는 결함.

이는 문서와 코드의 정적 결과다. 실제 복원 성공이나 영상 품질 검증 결과는 포함하지 않는다.

## 판정 불가와 닫을 조건

### 명세상 분류

| 남은 항목 | 닫을 조건 |
| --- | --- |
| 보관·미커밋 수정 보존·Git 밖 복원·메타데이터 보존의 수용 여부 | 이 분기들을 의도된 차이로 인정하는 명세 또는 별도 수용 기준 |
| 추가 질문과 사전 중단의 수용 여부 | 복원 단계의 데이터 보호 질문을 허용하는 명시적 기준 |

이 두 항목은 런타임 미확인 때문에 남긴 것이 아니다. 고정 커밋에서 원본과 다른 지시가 확인되며, 제공된 예외 목록이 그 분류를 직접 정하지 않는다.

### 실제 프로젝트별 정보

| 남은 항목 | 닫을 조건 |
| --- | --- |
| 실제 엔진의 H·I·W와 원래 버전 | 해당 프로젝트의 읽기 전용 Git 상태·diff·버전 파일과 제작노트 |
| W가 이전 템플릿 덮어쓰기인지 의도한 수정인지 | 제작 기록, 보관본 또는 두 버전을 검토한 사람의 선택 |
| 누락된 project.json의 원래 규격 | 제작노트·원래 REEL.config 또는 사용자 확인 |
| 필요한 추가 폰트와 굵기 | 원래 fonts.css·`.extra_fonts`·장면 CSS·폰트 원본 |
| 원래 장면·페이지 파일이 누락된 경우 | 그 프로젝트의 원본 `scenes.js`, `index.html` 또는 보관본 |

### 런타임과 품질

| 남은 항목 | 닫을 조건 |
| --- | --- |
| 실제 다운로드·설치 성공 | 별도로 승인된 실행 환경에서 준비 결과 확인 |
| 선택한 엔진의 실제 복원 | 실행 후 선택 원본과 복원 파일의 cmp, 한정 경로의 Git 상태 확인 |
| 실제 폰트 로딩 | 승인된 렌더에서 폰트 로그와 프레임 확인 |
| 옛 영상의 재현 품질 | 해당 프로젝트의 렌더·검수와 사람 확인 |
| 예전 BGM과 op55의 실제 바이트 동일성 | 같은 악보·seed·사운드뱅크·환경을 사용한 별도 실행 증거 |

이번에는 도메인 실행, 설치, 파일 복원, 렌더와 청취를 확인하지 않았다.  
정적 회귀는 확인되지 않았으며, 명세 밖 안전 분기의 수용 분류와 실제 프로젝트별 복원 결과는 남아 있다.
