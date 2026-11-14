---
name: prepare-video-audio
description: "op55 기본, ElevenLabs Music BYOK 선택, 내장 합성 fallback으로 음악과 나레이션·효과음을 준비하고 타임라인을 만든다. 음악 교체와 나레이션 수정에도 쓴다."
disable-model-invocation: true
---

# 음악·나레이션·효과음과 타임라인

Read ../resolve-showreel-tools/SKILL.md

입력은 `concept.md`, `script.json`, 프로젝트 폴더, adapter가 확인한 `S`와 선택한 음악 경로다. op55를 쓰면 `O`도 확인한다. 결과는 음악 파일·`analysis.json`, 제공자별 원본, `audio/vo/`, `audio/sfx/`, `timeline.json`, `reel/timeline.js`와 검사 표·크레딧이다. 다음 단계와 반복 여부는 이 skill을 부른 playbook이 정한다. 음악 파일 계약은 `../resolve-showreel-tools/references/contract.md`의 "음악 경계"에 있다.

## 직접 불러도 지킬 것

- 음악 경로는 `references/music.md`를 따른다. op55가 기본이고, 사용자가 선택한 ElevenLabs Music은 BYOK로 쓴다. 둘 다 실패하거나 사용 불가하면 내장 합성을 쓴다. 임의 외부 음원·루프·샘플은 가져오지 않는다. op55 사운드뱅크는 그 설치본의 규칙을 따른다.
- ElevenLabs 크레딧을 아낀다. 바뀐 줄만 다시 만들고, `takes`는 고유명사·숫자 줄에만 쓴다. 효과음은 공용 라이브러리에서 먼저 찾는다.
- op55의 정확한 `analysis.json`은 그대로 쓴다. API·내장 합성은 최종 음악을 분석해 만든다. 두 종류의 격자 정확도를 혼동하지 않는다.
- 실제 제공자·설정·전환 이유와 출처·크레딧을 기록한다. op55의 meta는 op55 결과에만 적용한다. API 키를 대화·로그·커밋에 남기지 않는다.
- 모든 작업 파일은 프로젝트 폴더 안에 둔다. 나레이션·효과음 원본 클립과 사용자 녹음 원본은 고치지 않고 믹서에서 처리한다.

## 순서

원래 5단계다. 화면의 시각은 음악 박·히트와 나레이션 단어에서 정해지므로 오디오를 먼저 확정한다. 쇼릴은 음악이 편집의 기준이다. **principle-stable-cues-late-surfaces**를 적용한다.

Read references/music.md. 음악 경로를 정하고 해당 절차로 음악과 분석 파일을 만든다. op55는 설치본의 현재 문서·경로를 확인한다. ElevenLabs를 선택하면 Read references/elevenlabs-music.md. 키 설정이나 op55 설치가 필요하면 그 안내에 따라 사용자에게 확인한다. 이미 승인한 API 사용 범위는 다시 묻지 않는다.

1. 길이·구간·강세와 나레이션 구간을 정한다. op55는 악보의 정확한 격자를 쓰고, API·내장 합성은 결과 분석을 보고 장면 기준점을 정한다.
2. 음악 파일을 검수하고 `script.json`의 `music.file`에 실제 경로를, `music.provider`에 실제 제공자를 적는다. 기본 파일은 `audio/music/music.wav`다. 수정 작업은 새 폴더에서 만들어 기존 음악을 보존한다.
3. 필요한 나레이션·효과음을 만든 뒤 타임라인을 생성한다. op55는 배치된 나레이션 빈틈을 악보에 반영해 다시 렌더한다. API·내장 합성은 먼저 믹스의 gain·덕킹·자동화로 대사 공간을 확보하고 재생성은 승인된 범위에서만 한다.

나레이션·효과음 기준은 `references/audio.md`에 있다. 사용자가 직접 녹음한 나레이션이면 `narrate.py` 대신 `references/audio.md`의 "사용자가 녹음한 나레이션"대로 `vo_split.py`로 줄을 나누고, 줄 길이 대 장면 표로 길이 안을 사용자와 정한다.

```bash
python3 $S/narrate.py <프로젝트>/script.json --stt            # 나레이션이 있을 때. ✗ 줄은 고쳐서 다시
python3 $S/eleven.py sfx-kit <프로젝트>/audio/sfx --names impact,riser   # 범용 프리셋이 필요한 곳만(합성: synth_music.py sfx). 구간 재질에 맞는 소리는 eleven.py sfx "prompt"
python3 $S/timeline.py <프로젝트>/script.json --music-analysis audio/music/analysis.json
python3 $S/mix.py <프로젝트>/timeline.json --verified-music <검수한-WAV>
```

- op55는 악보 격자에 구간 경계·큰 히트를 맞춘다. API·내장 합성의 분석이 불확실하면 확인한 시각과 장면 큐를 쓴다. 근거 없이 4박자나 정확한 다운비트를 가정하지 않는다.
- 음악을 다시 만들어도 박 격자(BPM·첫 다운비트)와 화면이 쓰는 큐·히트·음악 에너지 곡선이 그대로면 화면은 다시 렌더하지 않아도 된다. 이때는 deliver-video의 믹스와 마감만 다시 한다. 판단은 아래 "음악 교체"의 비교로 한다.
- op55의 정확한 격자를 쓰면 장면 경계는 `music.hitN`보다 `barN` 큐에 건다. 악보에 섹션이나 강세를 더하거나 빼면 `hitN` 번호가 밀린다. 내장 합성은 spec의 섹션·강세 시각을 초 단위 장면 큐로 쓴다. API는 실제 파일에서 확인한 기준점을 쓴다. 추정 `barN` 번호를 spec의 마디 번호와 같다고 보지 않는다.
- 통과 기준은 제공자별 검수와 공통 믹스·최종 QA다. op55의 강세·격자 검사를 API 음악에도 통과했다고 쓰지 않는다. 나레이션이 있으면 줄별 나레이션 대 배경 표를 읽는다.
- 납품 보고에 실제 음악 제공자·fallback 이유·검사 결과·출처와 크레딧을 적고, 사용자에게 전체 청취를 요청한다.

## 검사 결과 읽기

**principle-judge-rendered-evidence**를 적용한다. 스크립트가 정상 종료해도 표를 읽는다.

- op55는 설치본의 검수 계약을 확인한다. 현재 알려진 `verify.py`는 실패 항목이 있어도 종료 코드를 바꾸지 않는다. ✓·✗·△ 줄과 그림(PNG)을 Read로 본다.
- 음악 경로 세 가지 모두 이 skillset의 `mix.py`로 나레이션 대 배경을 판정한다. `--verified-music`에는 이번에 검수한 WAV 경로를 넘긴다. 타임라인의 음악과 다른 파일이면 믹서가 쓰기 전에 중단한다. 믹스 실패·빈 표·누락 줄은 미측정이다. 나레이션이 없으면 그 사유를 기록하고 해당 검사를 완료 조건에서 제외한다. 나레이션이 있으면 모든 줄을 측정하기 전에는 마감하지 않는다.
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

이미 만든 영상의 음악을 바꿀 때 쓴다. 기존 제공자와 소비값을 확인하고 `references/music.md`로 새 경로를 정한다. 제공자를 바꾸어도 기존 음악과 유료 원본은 새 검수가 끝날 때까지 보존한다.

1. 기존 `timeline.json`과 `reel/timeline.js`를 `<프로젝트>/.restore/<YYYYmmdd-HHMMSS>/`에 복사해 둔다.
2. op55를 쓰면 영상이 이미 쓰는 격자를 새 악보에 옮긴다. 기존 op55 음악의 meta가 있으면 grid를 쓰고, 없으면 기존 분석·큐와 원본 자료에서 복구한다. 박자(마디당 박 수)는 분석 파일에 없으니 불명확하면 확인한다. API·내장 합성이 기존 격자를 유지한다고 보장하지 않는다.
3. 새 폴더에 음악을 생성·검수하고 해당 파일의 분석으로 `timeline.py`를 다시 실행한다. 새 음악의 제공자와 크레딧을 기록한다. 이전 op55 meta를 새 음악에 적용하지 않는다.
4. 보관본과 새 타임라인을 비교한다. 박·다운비트·`music.start`(1ms 안), 장면이 쓰는 `barN`·`music.hitN` 큐, `reel/timeline.js`의 음악 에너지 곡선, 크레딧 문구를 본다. 바뀐 값과 그 값을 쓰는 장면 목록을 돌려준다.

영상 재사용 여부는 이 목록으로 playbook이 정한다. 변경된 음악이면 믹스·마감·검수는 늘 다시 한다.

## 자주 생기는 문제

| 증상 | 조치 |
| --- | --- |
| 이름·숫자를 잘못 읽음(이훈희→이후니, 2026→2025) | 발음 표기 수정 → 쉼표로 끊기("이공, 이육") → `takes` 3~5 → 모델 `eleven_v3`로 그 줄만 교체 |
| 오류 JSON이 mp3로 저장됨 | `eleven.py`가 막는다. 직접 curl을 쓰지 말고 스크립트를 쓴다 |
| Python에서 ElevenLabs 호출 시 SSL 오류 | 검증을 끄지 않는다. `eleven.py`는 curl을 쓰므로 이 문제가 없다 |
| 음악 박과 화면 박이 어긋남 | op55는 악보에서 쓴 분석을 그대로 썼는지 확인한다. API·내장 합성은 최종 파일을 분석했는지 보고, 추정 격자가 불확실하면 확인한 시각으로 장면을 맞춘다 |

## references

| 파일 | 언제 읽나 |
| --- | --- |
| `references/audio.md` | 보이스·나레이션 생성과 발음 검증, 사용자가 녹음한 나레이션(원고 형식·줄 나누기·길이 맞추기), 효과음, 믹스 기준 |
| `references/music.md` | 음악 경로 선택, op55 런타임 문서 확인, 공통 spec, 내장 합성, 파일 수락 기준 |
| `references/elevenlabs-music.md` | Music API BYOK 설정, 생성·보정·분석, 실패 처리 |
