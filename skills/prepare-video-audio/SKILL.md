---
name: prepare-video-audio
description: "op55로 음악을 만들고 나레이션·효과음을 준비해 timeline.json과 reel/timeline.js를 만드는 기술. 오디오 교체와 나레이션 수정에도 쓴다."
disable-model-invocation: true
---

# 음악·나레이션·효과음과 타임라인

Read ../resolve-showreel-tools/SKILL.md

입력은 `concept.md`, `script.json`, 프로젝트 폴더, `S`·`O`이다. 결과는 `audio/music/`의 op55 산출물, `audio/vo/`, `audio/sfx/`, `timeline.json`, `reel/timeline.js`와 검사 결과다. 다음 단계와 반복 여부는 이 skill을 부른 playbook이 정한다.

## 직접 불러도 지킬 것

- BGM은 코드로만 만든다. 외부 음원·루프나 음악 생성 서비스(ElevenLabs Music 포함)를 쓰지 않는다.
- ElevenLabs 크레딧을 아낀다. 바뀐 줄만 다시 만들고 공용 효과음 라이브러리를 먼저 찾는다.
- op55 렌더가 쓴 analysis.json을 그대로 타임라인에 준다.

## 이식 대상

골격 단계다. 원본 `SKILL.md:126-160`, references/audio.md의 절차를 이 파일과 이 폴더의 references로 옮긴다.
