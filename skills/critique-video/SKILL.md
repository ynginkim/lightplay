---
name: critique-video
description: "초안을 렌더해 스틸 시트·프레임 띠·경계 프레임·움직임 검사를 보고 구간마다 유지·고침·다시 만듦을 판정하는 기술. 맥락 없는 독립 비평도 받는다."
disable-model-invocation: true
---

# 초안 렌더와 비평

Read ../resolve-showreel-tools/SKILL.md

입력은 프로젝트의 `reel/`, `timeline.json`, `concept.md`, `S`이다. 결과는 `qa/` 시트, `qa/critique_NN.md`의 구간별 판정과 이유, 움직임 검사의 ✗·△ 목록다. 다음 단계와 반복 여부는 이 skill을 부른 playbook이 정한다.

## 직접 불러도 지킬 것

- 시트는 반드시 Read로 열어 본다. 렌더한 프레임을 보지 않고 완료라고 하지 않는다.
- 섬광 ✗는 의도와 관계없이 고칠 것으로 돌려준다.
- 검수 파일은 프로젝트의 `qa/`에 둔다.

## 이식 대상

골격 단계다. 원본 `SKILL.md:191-209`, references/qa.md의 절차를 이 파일과 이 폴더의 references로 옮긴다.
