# showreel 공유 계약

여러 leaf가 함께 쓰는 기준과 파일 계약이다. 이 파일이 정본이다. 문장은 원본 showreel `SKILL.md`(기준 커밋 `307b3fd`)에서 옮겼고 출처 줄을 절마다 적었다.

## 결과물 기준

원본 `SKILL.md:8-25`.

이 작업은 아래 요청에서 출발했다.

> 당신이 얼마나 놀라운 모션 그래픽 디자이너인지 보여주는 역동적인 한글버전 1분 모션그래픽 비디오를 만들어 보세요. 이력서용 쇼릴 처럼요. 전력을 다해요.

요청의 각 부분이 결과물에 요구하는 것은 다음과 같다.

| 요청 | 뜻 | 결과물에서 확인할 것 |
| --- | --- | --- |
| 당신이 얼마나 놀라운 모션 그래픽 디자이너인지 | 영상 자체가 만든 사람의 실력을 증명한다. 무엇을 말하는지보다 화면을 어떻게 만들었는지가 먼저 보인다 | 화면마다 템플릿으로는 나오지 않는 판단(구도, 움직임 설계, 재질)이 있다 |
| 놀라운 | 보는 사람이 다음 화면을 예상하지 못한다 | 앞 구간과 다른 방식의 화면이 이어서 나온다. 구간마다 "어떻게 만들었지" 싶은 순간이 있다 |
| 역동적인 | 빠르기만 한 영상이 아니다. 빠름과 멈춤, 큼과 작음의 대비가 음악의 박·섹션과 같은 시각에 바뀐다 | 몰아치는 구간과 비운 구간이 모두 있다. 실수로 멈춘 구간이 없고, 멈춤은 의도한 자리에만 있다 |
| 한글버전 | 한글을 번역 자막이 아니라 디자인 재료로 쓴다 | 자모 구조, 획, 네모꼴, 가변 굵기 같은 한글의 형태가 움직임에 쓰인다 |
| 이력서용 쇼릴 | 서로 다른 작업의 가장 좋은 구간을 음악에 맞춰 이어 붙이고 이름(과 연락처)으로 끝나는 형식 | 표현 범위가 넓다(2D·3D·타이포·데이터·사진·생성 그래픽 등). 구간마다 다른 프로젝트처럼 보인다 |
| 전력을 다해요 | 첫 아이디어에서 멈추지 않고 시간과 반복을 아끼지 않는다 | 콘셉트 후보를 여러 개 비교한 기록과 약한 구간을 다시 만든 기록이 있다 |

다른 주제(제품 소개, 행사 홍보, 인물 프로필)에 이 문장이 붙어 오면 주제는 요청대로 따르고, 만드는 기준은 위 표를 따른다. 이 문장이 없는 요청에도 "놀라운·역동적인·한글버전·전력을 다해요" 기준은 그대로 적용한다. "구간마다 다른 프로젝트처럼 보인다"는 기준은 작업 모음 형식(쇼릴)일 때 적용한다. 브랜드·교육 영상처럼 한 작품으로 보여야 하는 영상은 한 영상 안의 일관성을 먼저 지키고, 매체와 움직임으로 장면을 나눈다.

## 기술 기본값

원본 `SKILL.md:33-44`. 요청에 없는 항목은 아래 값으로 진행한다. 사용자가 정한 값과 작업 폴더의 프로젝트 정책이 먼저다.

| 항목 | 기본값 |
| --- | --- |
| 길이·규격 | 60초, 16:9 1920×1080, 30fps. 릴스·쇼츠 용도면 9:16 1080×1920 |
| 나레이션 | 요청에 있거나 내용을 말로 전해야 할 때만 넣는다. 쇼릴은 음악과 화면으로 전한다. 넣을 때는 콘셉트에 맞는 보이스를 prepare-video-audio의 audio.md 보이스 표와 `eleven.py voices --lang ko`에서 고른다. Marcus `ibCGc01503OQd2R6i1n1`은 한국어 낭독 설정(`eleven_multilingual_v2`, stability 0.45 · similarity 0.8 · style 0.4)을 검증해 둔 보이스다 |
| 음악 | [op55](https://github.com/ynginkim/op55)로 Claude가 작곡한다(합성 악기 + 실제 악기 샘플, 결정적 렌더, 숫자 검증). ElevenLabs Music은 쓰지 않는다(크레딧을 가장 많이 쓰는 항목이다). ElevenLabs는 나레이션·효과음에만 쓴다 |
| 이미지 | 콘셉트에 필요할 때만 codex-image로 생성한다. 실존 인물의 얼굴은 생성하지 않고 실제 사진만 쓴다 |
| 산출물 | 마스터 MP4, 공유용 MP4, 포스터 JPG, 자막 SRT(나레이션이 있을 때), 제작노트 |
| 음량 | -14 LUFS. `mix.py`가 true peak -2.0 dBTP로 마스터링하고, 검수 기준은 -1.0 dBTP 이하다 |

## 작업 위치

원본 `SKILL.md:46-50`.

모든 작업 파일은 프로젝트 폴더 아래에 만든다. 시스템 임시 폴더(/tmp, /private/tmp)와 세션 scratchpad에는 아무것도 저장하지 않는다. 세션이 끝나면 임시 폴더가 지워져 재생성 명령·검수 시트·생성 이미지·나레이션 테이크를 다시 쓸 수 없게 된다. 검수용 스틸과 시트는 `<프로젝트>/qa/`, 중간 렌더는 `<프로젝트>/out/`에 둔다.

프로젝트 폴더는 사용자가 지정하지 않으면 현재 작업 폴더 아래에 영문 소문자 이름(예: `<주제-slug>/`)으로 만든다.

## 프로젝트 파일

`new_project.py`가 만드는 폴더는 `research/`, `assets/`(img, photos, gen, cutout, logo), `audio/`(vo, music, sfx), `reel/`, `qa/`, `out/`와 `project.json`(ratio, width, height, fps, duration)이다.

| 파일 | 만드는 쪽 | 쓰는 쪽 |
| --- | --- | --- |
| `concept.md`, `storyboard.md`, `research/` | plan-video | 모든 leaf, 제작노트 |
| `script.json` | plan-video(원고), prepare-video-audio(음악·효과음) | `narrate.py`, `timeline.py`, `qa_check.py --script` |
| `audio/vo/*.mp3`와 정렬 정보 | `narrate.py` | `timeline.py`, `mix.py` |
| `audio/music/score.mjs`, `music.wav`, `analysis.json`, `music.meta.json` | op55 | `timeline.py`, `mix.py`, 크레딧 |
| `timeline.json` | `timeline.py` | `mix.py`, `finish.py`, `motion_check.py`, `qa_check.py`, op55 `verify.py --mix` |
| `reel/timeline.js` | `timeline.py`(사람이 고치지 않는다) | 장면 코드(`window.TL`) |
| `reel/` 장면 코드·`assets/` | build-video-scenes | `render.mjs`, `render_pieces.py` |
| `out/video.mp4`, `audio/mix.wav` | `render.mjs`, `mix.py` | `finish.py` |
| `out/<제목>_<길이>s*` | `finish.py` | `qa_check.py`, 납품 |
| `qa/critique_NN.md`, `qa/qa_report.md`, `qa/final_sheet*.png` | critique-video, `qa_check.py` | 납품 판정 |

## op55 경계

op55 기준 커밋 `828990bb00ed1b887bb29d79710006c3c4bec526`의 계약이다. 그 뒤의 op55 변경은 따라가지 않는다.

| 파일·필드 | 계약 |
| --- | --- |
| `audio/music/score.mjs` | op55가 해석하는 악보. showreel은 `concept.md`의 구간·에너지·강세와 나레이션 빈틈을 넘긴다 |
| `script.json`의 `music.file` | 프로젝트 기준 `audio/music/music.wav`. `gain_db`, 덕킹, 시작, 자동화 같은 믹스 설정은 showreel 쪽 소유 |
| `analysis.json` | `file`, `duration`, `bpm`, `beats`·`downbeats`·`hits`(초 단위 수 배열), `energy`. `timeline.py`가 `music.start`를 더해 `bar1…`(다운비트)와 `music.hit1…` 큐를 만든다. `--music-analysis`의 상대 경로는 `script.json`이 있는 폴더 기준 |
| `music.meta.json` | 격자(beat, t0, beatsPerBar, firstDownbeat), 섹션·강세·빈틈, `credits`. 크레딧 문구가 있으면 영상 크레딧에 넣는다 |
| 화면의 음악 에너지 | `timeline.py`가 `music.file`의 WAV에서 소리 크기 곡선을 다시 계산해 `reel/timeline.js`에 넣는다. `analysis.json`의 `energy`를 그대로 쓰지 않는다 |
| 믹스 | `mix.py`가 음악을 -16 LUFS로 맞춘 뒤 gain·덕킹을 적용한다. op55 마스터 음량과 영상 목표 음량은 별개다 |

`timeline.py`는 빠진 필드에 기본값을 쓰는 부분이 있다. 그래서 음악을 받을 때 파일 존재, 유효한 JSON, `bpm` 수와 `beats`·`downbeats`·`hits` 배열, 길이와 프로젝트 경로가 맞는지를 직접 확인한다. 하나라도 어긋나면 중단하고 원인을 돌려준다.
