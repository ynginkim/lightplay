# 음악 생성 경로 선택

음악은 op55를 기본으로 만들고, 선택한 ElevenLabs Music BYOK를 대안으로 쓴다. 두 경로가 실패하거나 사용 불가하면 내장 합성으로 진행한다. Suno는 지원하지 않는다. 선택·전환 이유와 미완료 검사를 제작노트와 납품 보고에 남긴다.

| 경로 | 사용 조건 | 다음 행동 |
| --- | --- | --- |
| op55, 기본 | 설치본의 현재 문서·도구·필요한 뱅크를 확인함 | 그 문서에 따라 작곡·렌더·검수 |
| ElevenLabs Music, 선택 | 사용자가 Music API 사용을 선택했고 BYOK·권한·크레딧을 준비함 | Read references/elevenlabs-music.md |
| 내장 합성, fallback | 앞선 두 경로가 실패·거절·미설정 등으로 사용 불가 | 아래 spec과 합성 명령 사용 |

op55가 없으면 경로를 묻거나 설치 명령을 안내한다. 사용자가 설치하지 않겠다고 하면 ElevenLabs 설정 또는 내장 합성을 안내한다. 사용자가 처음부터 ElevenLabs를 선택하면 op55는 시도하지 않는다. 키를 제공하지 않거나 API 사용을 원하지 않으면 유료 생성 시도 없이 아래 실패 후 경로 선택을 따른다. 키가 있다는 사실은 Music API 사용 선택을 대신하지 않는다.

ElevenLabs가 실패하거나 사용 불가하면, 사용자가 op55를 허용했고 이번 작업에서 아직 실패하지 않은 사용 가능한 설치본이 있을 때 op55로 돌아간다. op55도 실패·미설치·거절 상태이면 내장 합성으로 간다. 사용자에게 경로·설치·API 선택이 필요하면 가능한 선택지를 한 번에 안내하고 이미 정한 답을 다시 묻지 않는다.

## op55 설치본 사용

1. adapter가 찾은 `O`와 설치된 op55 skill 목록을 확인한다. 기존 제작노트의 경로도 단서로 쓴다. 설치본의 도구 안내에서 작곡·렌더·검수 문서를 찾아 읽는다. 현재 이름의 예는 `resolve-op55-tools`, `op55-compose`, `op55-render`, `op55-verify`다. 이름·폴더·명령은 발견한 설치본 문서로 확정한다.
2. 이 skillset의 scripts는 `S`, op55 scripts는 `O`로 구분한다. op55 문서가 쓰는 변수는 그 문서 기준이다. 도구와 문서가 서로 다른 설치본이면 실행하지 않는다. 확인한 `O`를 `OP55_SCRIPTS`로 preflight에 전달한다.
3. 길이, `concept.md`의 구간·에너지·강세, 나레이션 시각·빈틈을 넘긴다. op55 문서에 따라 큐 시트·격자·악보를 만들고 렌더·검수한다. 이 작업 안에서 op55의 mode를 새 진행 관리자로 시작하지 않는다.
4. 생성한 `score.mjs`, `music.wav`, `analysis.json`, `music.meta.json`을 확인한다. 검수의 수치·그림을 읽는다. 현재 알려진 verify는 미달이어도 exit 0이므로 종료 코드만으로 성공을 정하지 않는다. 설치본의 실제 판정 계약을 확인한다.
5. 나레이션 배치 후 빈틈을 악보에 반영해 다시 렌더한다. 확인한 영상 믹서 경로를 `SHOWREEL_SCRIPTS`와 `--mix-py`로 명시한다. 해당 옵션의 지원 여부도 설치본 문서에서 확인한다.

op55가 쓴 정확한 `analysis.json`은 그대로 쓴다. `music_tools.py analyze`로 격자를 다시 추정하지 않는다. `music.meta.json`의 credits가 있으면 영상과 납품 보고로 전달한다. 설치본의 경로와 확인 가능한 버전·커밋을 제작노트에 기록한다. 복사 설치본에 Git 정보가 없으면 확인 날짜와 사용 문서·도구 경로를 남긴다. 한 제작 작업 도중 설치본을 갱신하지 않는다.

## API와 내장 합성이 공유하는 spec

op55에는 이 spec을 요구하지 않는다. 두 대안은 같은 `audio/music/spec.json`을 쓴다. 분위기·구간·강세는 콘셉트에서 정하고 fallback에서도 유지한다.

```json
{
  "duration": 30,
  "mood": "pulse",
  "bpm": 120,
  "key": "A",
  "minor": true,
  "global_styles": ["instrumental electronic pulse, no vocals"],
  "sections": [
    {"name": "Intro", "start": 0, "energy": 0.3},
    {"name": "Main", "start": 8, "energy": 0.8},
    {"name": "Resolve", "start": 24, "energy": 0.35}
  ],
  "events": [{"t": 8, "type": "hit"}]
}
```

합성 mood는 `cinematic`, `pulse`, `soft`, `playful` 중 하나다. `global_styles`는 ElevenLabs용이며 내장 합성은 네 mood의 제한된 악기·질감을 사용한다.

## 내장 합성

프로젝트 폴더에서 실행한다. `$S`는 adapter가 확인한 절대 경로다. ffmpeg와 numpy가 필요하다. 이미 만든 음악이 있으면 새 음악 폴더에서 생성하고 검수가 끝난 뒤 `music.file`을 바꾼다. 기존 유료 원본과 납품본을 덮어쓰지 않는다.

```bash
python3 "$S/synth_music.py" music audio/music/spec.json audio/music/music.wav
python3 "$S/music_tools.py" analyze audio/music/music.wav
```

합성 WAV는 48 kHz stereo 16-bit다. op55의 24-bit와 혼동하지 않는다. 추가 skill·음악 API 키는 필요 없다. 합성 자체가 실패하면 실패한 명령과 원인을 반환한다. 무음이나 이전 파일을 새 BGM으로 처리하지 않는다.

## 공통 수락과 타이밍

- `script.json`의 `music.provider`에 `op55`, `elevenlabs`, `synth` 중 실제 사용한 값을 적는다. `music.file`은 이번에 검수한 파일을 가리킨다. 이전 프로젝트에 provider가 없으면 제작노트·악보·파일을 읽어 판단하고 op55로 가정하지 않는다.
- 파일 존재, 실제 길이와 영상 길이의 일치, 디코딩 가능 여부를 확인한다. `analysis.json`이 유효한 JSON이며 `duration`·`bpm`은 유한한 양수, `beats`·`downbeats`·`hits`는 초 단위의 유한한 수 배열인지 본다. 시각이 음악 길이를 벗어나거나 경로가 다른 음악을 가리키면 타임라인을 만들지 않는다.
- API·내장 합성의 분석은 추정값이다. 현재 분석기는 일정한 템포와 4박 다운비트를 가정하며 첫 다운비트와 마디 번호가 원래 spec과 다를 수 있다. 내장 합성의 장면 기준점은 spec의 섹션·강세 시각을 초 단위 큐로 쓴다. API는 실제 음원에서 확인한 기준점을 쓴다. 추정 `barN`과 spec 마디 번호가 같다고 가정하지 않는다.
- op55 이외에는 `score.mjs`·`music.meta.json`을 요구하지 않는다. 이전 op55 meta가 남아 있어도 새 음악의 격자·크레딧으로 쓰지 않는다. API 제공사·모델·설정·사용량·출처는 제작노트에 기록한다.
- 공통 믹스는 `mix.py`의 줄별 나레이션 대 배경 표로 검수한다. ✗와 미측정 항목을 남긴 채 완료로 쓰지 않는다. 파형·수치 검사는 사람의 전체 청취를 대신하지 않는다.
