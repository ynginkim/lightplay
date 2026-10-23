---
name: deliver-video
description: "최종·조각 렌더, 믹스, 마감, 자동 검수, 납품 보고, 납품 뒤 정리를 하는 기술. 오디오만 다시 마감할 때도 쓴다."
disable-model-invocation: true
---

# 최종 렌더·믹스·마감·납품

Read ../resolve-showreel-tools/SKILL.md

입력은 검수를 통과한 `reel/`, `timeline.json`, 오디오, `S`이다. 결과는 `out/` 납품 파일, `qa/qa_report.md`, 최종 시트, 납품 보고, `제작노트.md`, 정리 목록다. 다음 단계와 반복 여부는 이 skill을 부른 playbook이 정한다.

## 직접 불러도 지킬 것

- 최종 렌더 뒤 움직임 검사를 반드시 다시 한다.
- 사운드를 직접 들어 봐 달라고 요청한다. Claude는 소리를 들을 수 없고 수치로만 확인했다.
- 지우는 일은 사용자가 끝났다고 확인한 뒤에만 한다. 크레딧을 쓴 소리, 납품본, 재현 코드는 남긴다.

## 이식 대상

골격 단계다. 원본 `SKILL.md:211-264`, references/qa.md의 자동 검수·납품·정리의 절차를 이 파일과 이 폴더의 references로 옮긴다.
