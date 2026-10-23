---
name: build-video-scenes
description: "콘셉트에 필요한 이미지와 스타일 프레임을 만들고 시간의 순수 함수인 장면 코드를 쓰는 기술. 장면 수정과 규격 변경 레이아웃에도 쓴다."
disable-model-invocation: true
---

# 이미지·스타일 프레임·장면

Read ../resolve-showreel-tools/SKILL.md

입력은 `concept.md`, `storyboard.md`, `reel/timeline.js`, 프로젝트 폴더, `S`이다. 결과는 `assets/`의 이미지와 출처, 스타일 프레임 시트, `reel/` 장면 코드와 장면별 스틸다. 다음 단계와 반복 여부는 이 skill을 부른 playbook이 정한다.

## 직접 불러도 지킬 것

- 실존 인물의 얼굴·몸은 생성하지 않는다. 실존 회사의 로고·브랜드를 흉내 내지 않는다.
- 화면은 시간 t의 순수 함수다. 시각은 타임라인 큐로 건다.
- 섬광은 어두운 배경에서 opacity 0.15 이하, 1초에 3번 이하로 쓴다.

## 이식 대상

골격 단계다. 원본 `SKILL.md:162-189`, references/images.md, `design.md`, `engine.md`, `techniques.md`의 절차를 이 파일과 이 폴더의 references로 옮긴다.
