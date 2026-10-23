---
name: critique-video
description: "초안을 렌더해 스틸 시트·프레임 띠·경계 프레임·움직임 검사를 보고 구간마다 유지·고침·다시 만듦을 판정하는 기술. 맥락 없는 독립 비평도 받는다."
disable-model-invocation: true
---

# 초안 렌더와 비평

Read ../resolve-showreel-tools/SKILL.md

입력은 프로젝트의 `reel/`, `timeline.json`, `concept.md`, adapter가 확인한 `S`다. 결과는 `qa/`의 스틸·시트, `qa/critique_NN.md`의 구간별 유지·고침·다시 만듦 판정과 이유, 움직임 검사의 ✗·△ 목록과 처리 여부다. 고치는 일은 build-video-scenes가 하고, 반복을 멈출지는 이 skill을 부른 playbook이 정한다.

## 직접 불러도 지킬 것

- 만든 시트는 반드시 Read로 열어 직접 본다. 렌더한 프레임을 보지 않고 완료라고 하지 않는다.
- 섬광 ✗는 의도와 관계없이 고칠 것으로 돌려준다(광과민성).
- 검수 스틸·시트·클립은 `<프로젝트>/qa/`, 중간 렌더는 `<프로젝트>/out/`에 둔다.

## 스틸과 초안

원래 9단계다. **principle-judge-rendered-evidence**를 적용한다.

```bash
node $S/render.mjs --dir <프로젝트>/reel --stills <시작+0.5>,<큐+0.4>,<끝-0.6> --outdir <프로젝트>/qa/stills_<장면>   # 장면 하나를 만들 때마다
node $S/render.mjs --dir <프로젝트>/reel --every 0.5 --outdir <프로젝트>/qa/stills     # 전체 스틸(모든 장면이 생긴 뒤)
python3 $S/contact_sheet.py --dir <프로젝트>/qa/stills --out <프로젝트>/qa/sheet_stills.png --timeline <프로젝트>/timeline.json
node $S/render.mjs --dir <프로젝트>/reel --out <프로젝트>/out/draft.mp4 --scale 0.5          # 초안(60초에 약 30초)
python3 $S/contact_sheet.py --video <프로젝트>/out/draft.mp4 --every 1 --out <프로젝트>/qa/sheet_draft.png
python3 $S/motion_check.py <프로젝트>/out/draft.mp4 --timeline <프로젝트>/timeline.json   # 실수로 멈춘 구간·큰 움직임 부족·섬광 과다를 시각과 장면 이름으로 알려 준다
python3 $S/contact_sheet.py --video <프로젝트>/out/draft.mp4 --around <구간 경계 초들> --frames 3 --out <프로젝트>/qa/sheet_cuts.png
```

만든 시트는 **반드시 Read로 열어 직접 본다.** 렌더한 프레임을 보지 않고 완료라고 하지 않는다. 간격 기준과 시트를 볼 때 확인할 것은 `references/qa.md`의 "검수 단계"와 "시트를 볼 때 확인할 것"에 있다.

## 비평

초안마다 `references/qa.md`의 "비평"을 따라 구간별로 유지·고침·다시 만듦을 판정하고 `qa/critique_NN.md`에 남긴다. 가장 약한 구간은 수치를 조정하기보다 방향을 바꿔 다시 만들라고 판정한다. 한 번 고치고 끝내지 않는다. 모든 구간이 "유지"가 되고 `qa.md`의 기술 점검표를 통과할 때까지 반복한다.

최종 렌더 전에 한 번은 만든 맥락이 없는 하위 agent에게 시트·프레임 띠·비평 질문만 주고 판정을 받아 `qa/critique_NN.md`에 남긴다. 만든 쪽이 놓친 문제를 찾기 위해서다. 그 agent에게 이 영상을 만든 의도나 이전 판정을 주지 않는다.

## 움직임 검사 읽기

`motion_check.py`는 문제를 출력하고도 정상 종료할 수 있다. 종료 코드가 아니라 출력의 ✗·△를 읽는다.

`motion_check.py`가 △를 내면 그 시각이 의도한 정지인지 확인하고, 아니면 사건을 더하라고 돌려준다. 섬광 ✗는 의도와 관계없이 초안 단계에서 고친다(광과민성). 최종 렌더 뒤에 고치면 렌더를 다시 해야 한다. 초안(모션 블러 없음)에서 통과해도 최종 렌더(`--sub 4`)에서는 컷이 두 프레임에 섞여 섬광이 늘 수 있다. 밝은 바탕에서 컷이 잦은 구간은 최종 렌더 전에 그 구간만 `render.mjs --from <초> --to <초> --sub 4 --scale 0.5 --out <프로젝트>/out/chk_<구간>.mp4`로 뽑아 `motion_check.py`로 확인한다. 렌더러가 종료 코드 2로 끝나면 페이지 오류가 난 것이니 로그의 오류부터 고친다.

구간만 뽑은 클립을 검사할 때는 보려는 구간 뒤로 3초 이상 더 뽑는다. `motion_check.py`는 클립의 마지막 3초를 재지 않는다(0~8초 클립으로 확인했다가 7.3~9.4초 정지를 놓친 사례). 섬광이 어느 프레임에서 생기는지는 `python3 $S/flash_list.py <클립> <클립 시작 초>`로 본다.

## references

references 문서가 다른 문서 이름(`design.md` 등)을 말하면 adapter의 "자료 위치" 표에서 경로를 찾는다.

| 파일 | 언제 읽나 |
| --- | --- |
| `references/qa.md` | 검수 단계, 비평, 기술 점검표, 시트 읽는 법. 뒤쪽의 자동 검수·납품·정리는 deliver-video가 읽는다 |
