---
name: prepare-video-audio
description: "op55로 음악을 만들고 나레이션·효과음을 준비해 timeline.json과 reel/timeline.js를 만드는 기술. 음악 교체와 나레이션 수정에도 쓴다."
disable-model-invocation: true
---

# 음악·나레이션·효과음과 타임라인

Read ../resolve-showreel-tools/SKILL.md

입력은 `concept.md`, `script.json`, 프로젝트 폴더, adapter가 확인한 `S`·`O`다. 결과는 `audio/music/`의 op55 산출물(`score.mjs`, `music.wav`, `analysis.json`, `music.meta.json`), `audio/vo/`, `audio/sfx/`, `timeline.json`, `reel/timeline.js`와 각 검사의 ✓·✗ 표, 크레딧 문구다. 다음 단계와 반복 여부는 이 skill을 부른 playbook이 정한다. 음악 파일 계약은 `../resolve-showreel-tools/references/contract.md`의 "op55 경계"에 있다.

## 직접 불러도 지킬 것

- BGM은 코드로만 만든다. 외부 음원·루프나 음악 생성 서비스(ElevenLabs Music 포함)를 쓰지 않는다. op55가 승인한 사운드뱅크의 악기 샘플은 op55 규칙 안에서 쓴다.
- ElevenLabs 크레딧을 아낀다. 바뀐 줄만 다시 만들고, `takes`는 고유명사·숫자 줄에만 쓴다. 효과음은 공용 라이브러리에서 먼저 찾는다.
- op55 렌더가 쓴 `analysis.json`을 그대로 `timeline.py`에 준다. `music_tools.py analyze`로 박을 다시 읽지 않는다.
- `music.meta.json`의 `credits`에 문구가 있으면 영상 크레딧과 납품 보고로 넘긴다.
- 모든 작업 파일은 프로젝트 폴더 안에 둔다. 나레이션·효과음 원본 클립은 고치지 않고 믹서에서 처리한다.

## 순서

원래 5단계다. 화면의 시각은 음악 박·히트와 나레이션 단어에서 정해지므로 오디오를 먼저 확정한다. 쇼릴은 음악이 편집의 기준이다. **principle-stable-cues-late-surfaces**를 적용한다.

음악은 op55로 Claude가 직접 작곡한다. op55 문서(`$O/../SKILL.md`와 그 references, 특히 showreel 연결을 다룬 `showreel.md`)를 읽고 그 절차(큐 시트 → 격자 → `score.mjs` → 렌더 → 검증)를 따른다. op55 문서의 `$S`는 여기의 `$O`다. op55의 진입 skill을 이 작업 안에서 따로 진행 방식으로 부르지 않고, 문서와 파일 계약으로만 쓴다. 순서는 이렇다.

1. op55 예시(`$O/examples/`: starter 합성, eroica 샘플 오케스트라, pstack-harness 300초 설명 영상)에서 가까운 것을 `audio/music/score.mjs`로 복사한다.
2. 박 격자를 먼저 정한다.
3. `concept.md`의 구간대로 섹션·에너지·강세를 악보에 적는다. 구간마다 악기·질감은 아트 디렉션에 맞춘다. 합성 악기·실제 악기 샘플·혼합 중 무엇을 쓸지는 op55의 팔레트 표를 따른다. `spec.json`은 쓰지 않는다.
4. `script.json`의 `music.file`은 `audio/music/music.wav`로 둔다.
5. 나레이션을 배치한 뒤 나레이션 빈틈을 악보에 옮겨 적고 다시 렌더한다.

나레이션·효과음 기준은 `references/audio.md`에 있다.

```bash
python3 $S/narrate.py <프로젝트>/script.json --stt            # 나레이션이 있을 때. ✗ 줄은 고쳐서 다시
# 음악(op55): score.mjs를 쓰고 렌더한다. analysis.json은 악보의 정확한 격자로 함께 쓰인다
node $O/render.mjs --score <프로젝트>/audio/music/score.mjs --out <프로젝트>/audio/music/music.wav --analysis <프로젝트>/audio/music/analysis.json
python3 $O/verify.py <프로젝트>/audio/music/music.wav --analysis <프로젝트>/audio/music/analysis.json --waveform-png   # 음량·섹션 에너지·핵심 히트 정렬
python3 $S/eleven.py sfx-kit <프로젝트>/audio/sfx --names impact,riser   # 범용 프리셋이 필요한 곳만(합성: synth_music.py sfx). 구간 재질에 맞는 소리는 eleven.py sfx "prompt"
python3 $S/timeline.py <프로젝트>/script.json --music-analysis audio/music/analysis.json
SHOWREEL_SCRIPTS=$S python3 $O/verify.py <프로젝트>/audio/music/music.wav --analysis <프로젝트>/audio/music/analysis.json --mix <프로젝트>/timeline.json --mix-py $S/mix.py   # 나레이션이 생긴 뒤: 줄마다 나레이션 대 배경 ✓
```

- 음악 섹션은 4마디 단위로 잡고, 구간 경계·큰 히트는 다운비트에 둔다. 악보가 격자를 정하므로 드롭·히트를 원하는 시각에 바로 둘 수 있다.
- `music_tools.py analyze`로 박을 다시 읽지 않는다. 정확한 격자의 곡도 템포를 약간 틀리게 읽어 5분 끝에서 70ms쯤 어긋난다. `render.mjs`가 쓴 `analysis.json`을 그대로 `timeline.py`에 준다.
- 음악을 다시 만들어도 박 격자(BPM·첫 다운비트)와 화면이 쓰는 큐·히트·음악 에너지 곡선이 그대로면 화면은 다시 렌더하지 않아도 된다. 이때는 deliver-video의 믹스와 마감만 다시 한다. 판단은 아래 "음악 교체"의 비교로 한다.
- 장면 경계는 `music.hitN`보다 `barN` 큐에 건다. 악보에 섹션이나 강세를 더하거나 빼면 `hitN` 번호가 밀린다.
- 통과 기준: 나레이션 줄이 모두 ✓이고, 가장 큰 강세가 든 마디가 곡에서 가장 크다.
- 필요한 것: Node 18 이상(npm 패키지 없음), op55 사운드뱅크(`setup.mjs`, 88MB). `verify.py`는 ffmpeg와 numpy를 쓴다.
- 납품 보고에 음악은 op55로 작곡했다고 적고, 사용자에게 직접 들어 봐 달라고 한다. `music.meta.json`의 `credits`에 크레딧 문구가 있으면 영상 크레딧에 넣는다.

## 검사 결과 읽기

**principle-judge-rendered-evidence**를 적용한다. 스크립트가 정상 종료해도 표를 읽는다.

- op55 `verify.py`는 실패 항목이 있어도 종료 코드를 바꾸지 않는다. ✓·✗·△ 줄과 그림(PNG)을 Read로 본다.
- `--mix` 결과에 "showreel mix.py not found"가 나오거나 줄별 표가 비었으면 나레이션 대 배경은 미측정이다. `--mix-py` 경로를 확인하고 다시 돌린다.
- 음악을 받을 때 `analysis.json`이 있고 유효한 JSON이며 `bpm` 수와 `beats`·`downbeats`·`hits` 배열이 있는지, 길이와 경로가 이 프로젝트의 것인지 확인한다. 어긋나면 타임라인을 만들지 않고 원인을 돌려준다.
- `timeline.py`는 겹침·길이 초과·큐 누락을 ✗로 알려 주고 실패로 끝난다. 음악·효과음 파일이 없다는 줄은 경고라서 실패로 끝나지 않을 수 있으니 경고 줄도 읽는다.

## 효과음

- 효과음은 화면의 움직임마다 맞춰 설계한다. 프리셋 이름만 고르지 말고 `eleven.py sfx "prompt"`로 구간의 재질(종이, 유리, 액체, 전자음)에 맞는 소리를 만든다.
- 새로 만들기 전에 공용 효과음 라이브러리에서 찾는다.
  - `python3 $S/sfx_library.py find 종이`로 찾고, `python3 $S/sfx_library.py use <이름…> --to <프로젝트>`로 복사한다.
  - 라이브러리 위치를 찾는 순서는 resolve-showreel-tools의 도구 표에 있다. 환경 변수가 없는 셸에서는 하위 명령 앞에 `--lib`를 붙인다.
  - 맞는 소리가 없을 때만 새로 만든다. 새로 만든 소리는 `audio/sfx/list.tsv`에 `이름<TAB>길이<TAB>프롬프트`를 한 줄 남긴다. 라이브러리가 이 파일에서 프롬프트를 읽는다.

## 타임라인

`timeline.py`가 `timeline.json`(믹서·검수용)과 `reel/timeline.js`(화면용 큐·단어 시각·소리 크기 곡선)를 만든다. 겹침·길이 초과·큐 누락이 있으면 ✗로 알려 주므로 모두 고친 뒤 장면을 만든다. 나레이션 문구나 시각을 바꿀 때는 `script.json`만 고치고 `narrate.py`(바뀐 줄만 다시 생성)와 `timeline.py`를 다시 실행한다. 나레이션이 목표 길이를 넘기면 plan-video의 "자주 생기는 문제"대로 원고를 줄인다.

## 음악 교체

이미 만든 영상의 음악을 바꿀 때 쓴다. op55의 `showreel.md` "Replacing the music of a finished video"를 따른다.

1. 기존 `timeline.json`과 `reel/timeline.js`를 `<프로젝트>/.restore/<YYYYmmdd-HHMMSS>/`에 복사해 둔다.
2. 영상이 이미 쓰는 격자를 새 악보에 옮긴다. `music.meta.json`이 있으면 그 grid를 쓰고, 없으면 기존 `analysis.json`의 박 간격·첫 박·첫 다운비트에서 복구한다. 박자(마디당 박 수)는 `analysis.json`에 없으니 큐 시트·원래 악보에서 확인하고, 그래도 불명확할 때만 사용자에게 묻는다.
3. 새 악보를 렌더·검증하고 `timeline.py`를 다시 실행한다.
4. 보관본과 새 타임라인을 비교한다. 박·다운비트·`music.start`(1ms 안), 장면이 쓰는 `barN`·`music.hitN` 큐, `reel/timeline.js`의 음악 에너지 곡선, 크레딧 문구를 본다. 바뀐 값과 그 값을 쓰는 장면 목록을 돌려준다.

영상 재사용 여부는 이 목록으로 playbook이 정한다. 변경된 음악이면 믹스·마감·검수는 늘 다시 한다.

## 자주 생기는 문제

| 증상 | 조치 |
| --- | --- |
| 이름·숫자를 잘못 읽음(이훈희→이후니, 2026→2025) | 발음 표기 수정 → 쉼표로 끊기("이공, 이육") → `takes` 3~5 → 모델 `eleven_v3`로 그 줄만 교체 |
| 오류 JSON이 mp3로 저장됨 | `eleven.py`가 막는다. 직접 curl을 쓰지 말고 스크립트를 쓴다 |
| Python에서 ElevenLabs 호출 시 SSL 오류 | 검증을 끄지 않는다. `eleven.py`는 curl을 쓰므로 이 문제가 없다 |
| 음악 박과 화면 박이 어긋남 | `timeline.py`에 `render.mjs`가 쓴 `analysis.json`을 줬는지 확인한다. `music_tools.py analyze`로 다시 읽은 박을 쓰면 곡 끝으로 갈수록 어긋난다 |

## references

| 파일 | 언제 읽나 |
| --- | --- |
| `references/audio.md` | 보이스·모델·설정, ElevenLabs 키·플랜, 나레이션 생성과 발음 검증, 효과음, 믹스 기준. "음악" 절의 ElevenLabs Music과 `synth_music.py` 음악 경로는 업스트림 원문 보관이라 쓰지 않는다(효과음 합성은 쓴다) |
| op55 문서(`$O/../SKILL.md`, `references/`) | BGM 작곡(박 격자, 악보 API, 영상용 편곡, 렌더, 검증, showreel 연결) |
