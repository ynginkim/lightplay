# 이식 장부

이 장부는 최초 이식의 기록이다. 현재 op55 경계는 [음악 검증 기록](music-validation.md)의 후속 정리를 따른다. 과거 test mix 인자는 현재 실행 지침이 아니다.

showreel 단일 skill(`307b3fd`, 이 저장소 `374df70`)을 showreel-mode skillset으로 옮긴 기록이다. 상태는 모두 "완료"이며 `skillset.json`의 `migration.pending`은 0건이다. 다시 만들려면 `git show 374df70:<원본 경로>`와 새 파일을 비교한다.

## 원본 SKILL.md 대응

| ID | 원본 `SKILL.md` 줄 | 내용 | 새 위치 | 상태 |
| --- | --- | --- | --- | --- |
| A01 | 1-4 | 이름·설명(범위, 발동 문구, 제외 범위) | `showreel-mode` frontmatter. 수정 요청 문구를 더함 | 완료 |
| A02 | 8-25 | 이 스킬이 맞추는 기준 | `resolve-showreel-tools/references/contract.md` "결과물 기준" | 완료 |
| A03 | 27-31 | 정해 두지 않은 것 | `principle-concept-before-template`, plan-video "콘셉트" | 완료 |
| A04 | 33-44 | 기술 기본값 | contract.md "기술 기본값", mode "브리프" | 완료 |
| A05 | 46-50 | 작업 위치 | contract.md "작업 위치", 각 leaf "직접 불러도 지킬 것" | 완료 |
| A06 | 52-58 | 0~11 진행 순서 | `playbooks/create-video.md` 7단계(단계마다 원래 번호 표기) | 완료 |
| A07 | 60 | 질문 정책 | mode "브리프", plan-video "요청 읽기" | 완료 |
| A08 | 62 | 백그라운드·서브에이전트 | mode "진행 장부와 운영"(하네스 중립 문장) | 완료 |
| A09 | 64 | 스크립트 경로 `S` | `resolve-showreel-tools` "S와 O" | 완료 |
| A10 | 66-76 | 0 환경 점검 | adapter "환경 점검". 명령에 `OP55_SCRIPTS=$O` 추가 | 완료 |
| A11 | 78-84 | 1 요청 읽기 | plan-video "요청 읽기" | 완료 |
| A12 | 86-94 | 2 콘셉트 | plan-video "콘셉트" | 완료 |
| A13 | 96-106 | 3 프로젝트 만들기 | adapter "새 프로젝트" | 완료 |
| A14 | 108-113 | 3 조사와 자료 | plan-video "조사와 자료" | 완료 |
| A15 | 115-124 | 4 구성과 원고 | plan-video "구성과 원고" | 완료 |
| A16 | 126-160 | 5 오디오 | prepare-video-audio "순서"·"효과음"·"타임라인". op55 test mix에 `SHOWREEL_SCRIPTS=$S`, `--mix-py $S/mix.py` 추가 | 완료 |
| A17 | 128 | "op55 스킬을 불러" | prepare-video-audio가 op55 문서(`$O/../SKILL.md`)를 읽음. transition 등록 | 완료(transition) |
| A18 | 149 | 격자가 같으면 화면 재렌더 불필요 | prepare-video-audio "음악 교체"의 소비값 비교로 보강(plan §3, artifact-graph) | 완료 |
| A19 | 162-170 | 6 이미지 | build-video-scenes "이미지" | 완료 |
| A20 | 172-177 | 7 스타일 프레임 | build-video-scenes "스타일 프레임" | 완료 |
| A21 | 179-189 | 8 장면 제작 | build-video-scenes "장면 제작" | 완료 |
| A22 | 191-209 | 9 초안 렌더와 비평 반복 | critique-video. 반복은 create-video 5단계 | 완료 |
| A23 | 211-235 | 10 최종 렌더·믹스·마감 | deliver-video "최종 렌더·믹스·마감"·"믹스 판단" | 완료 |
| A24 | 237-252 | 11 자동 검수·납품 보고 | deliver-video "자동 검수"·"납품 보고" | 완료 |
| A25 | 254-264 | 납품 뒤 정리 | deliver-video "납품 뒤 정리". 삭제는 사용자 확인 뒤(DESIGN "이번 결정으로 대체") | 완료 |
| A26 | 266-273 | 지킬 것 | 수행하는 leaf마다 "직접 불러도 지킬 것"(268·269·270 → plan-video·build-video-scenes, 271·272 → prepare-video-audio, 273 → build-video-scenes·critique-video) | 완료 |
| A27 | 275-294 | 자주 생기는 문제 | 증상을 맡은 leaf의 표(279·280·287·288·289·293 → build-video-scenes, 281 → plan-video, 282·285·286·290 → prepare-video-audio, 283·284·291·292·294 → deliver-video) | 완료 |
| A28 | 296-308 | 참조 표 | 각 leaf의 references 표, adapter "자료 위치" | 완료 |

## 포크 관리 파일

| 파일 | 처리 | 근거 |
| --- | --- | --- |
| `CUSTOM.md` | 삭제 | 로컬 수정의 의도는 DESIGN과 leaf로 옮김: 음악 기본값·op55(prepare-video-audio, contract), 스크립트 경로(adapter), 9·10단계 보강(critique-video, deliver-video), 납품 뒤 정리(deliver-video), `finish.py` 공유용 음량 수정(deliver-video 자주 생기는 문제), 효과음 라이브러리(prepare-video-audio). 업스트림 PR·동기화 절차는 추적 종료(Q3)로 필요 없음 |
| `tools/sync.sh` | 삭제 | upstream 동기화 전용. 설치는 `npx skills add`로 대체 |
| `README.md` | 다시 씀 | 새 skillset 설명. 출처와 MIT 고지 포함 |
| `README.ko.md` | 삭제 | 한국어 README.md로 통합 |
| `CHANGELOG.md` | 삭제 | 업스트림 변경 기록. `git show 374df70:CHANGELOG.md`로 볼 수 있음 |
| `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md` | 삭제 후 다시 씀 | 업스트림 공개 저장소용 안내(설치 경로·연락처가 업스트림 기준)라 지웠고, 이 저장소 기준으로 #1(2026-10-24)에서 새로 썼다 |
| `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` | 삭제 후 이슈 템플릿만 다시 둠 | 이식 때는 PR 없이 main에서 작업했다. 이후 PR로 작업하며 이슈 템플릿을 이 저장소 기준으로 새로 뒀다. CI는 `.github/workflows/check.yml` |
| `docs/media/` | 삭제 | 업스트림 데모 결과물. 이 skillset으로 만든 영상이 아니므로 README에 쓰지 않음 |
| `evals/evals.json` | 유지(바이트 그대로) | 역사적 prompt 집합. 활성·보관 assertion 구분은 `evals/README.md` |
| `LICENSE` | 유지 + 본인 줄 추가 | 사본 `skills/resolve-showreel-tools/LICENSE`, `copies`로 바이트 대조 |
| `.gitignore` | 유지 | |

## 옮긴 파일의 바이트 대조

아래는 최초 이식 시점의 기록이다. 이후 음악 경로 변경으로 preflight.py·eleven.py·audio.md가 바뀌었으며 현재 검증은 [음악 검증 기록](music-validation.md)을 따른다.

scripts·assets는 모두 원본과 같다. references는 아래 줄만 바꿨다. 바꾼 이유는 둘이다. (가) 경로 문장: 스크립트가 다른 skill 폴더로 옮겨져 skill 기준 상대 경로 `scripts/…`가 맞지 않게 되어 adapter의 `$S`로 바꾸거나, 프로젝트 기준 경로에 `<프로젝트>/`를 붙이거나, 옛 단일 `SKILL.md`를 가리키던 문장을 새 위치로 바꿨다. (나) 검사기 표기: 구조 검사기가 runtime 문서의 긴 대시와 인라인 코드 안의 절대 경로를 실패로 보므로 문장부호와 표기만 바꿨다(뜻은 같음).

| 원본(374df70) | 새 경로 | sha256 원본 | 결과 |
| --- | --- | --- | --- |
| `assets/engine/engine.js` | `skills/resolve-showreel-tools/assets/engine/engine.js` | `b595f361e0e1f661` | 같음 |
| `assets/engine/fx.js` | `skills/resolve-showreel-tools/assets/engine/fx.js` | `cf028c72328aacc6` | 같음 |
| `assets/engine/index.html` | `skills/resolve-showreel-tools/assets/engine/index.html` | `4140bc2a6be1bdc0` | 같음 |
| `assets/engine/scenes.js` | `skills/resolve-showreel-tools/assets/engine/scenes.js` | `70ba3bcb53f4d061` | 같음 |
| `assets/sfx_presets.json` | `skills/resolve-showreel-tools/assets/sfx_presets.json` | `4d6459d9728bfb52` | 같음 |
| `references/audio.md` | `skills/prepare-video-audio/references/audio.md` | `9f3c3b9c5c167e9f` | 줄 15,32,79,82,123,128,129,139,144,154,163,165,171,172,175,188만 다름 |
| `references/brief.md` | `skills/plan-video/references/brief.md` | `8838231f3c5c117b` | 줄 90,101만 다름 |
| `references/design.md` | `skills/build-video-scenes/references/design.md` | `d4e8ff5a84db3658` | 같음 |
| `references/engine.md` | `skills/build-video-scenes/references/engine.md` | `2639e9fdb49a846b` | 줄 21,24,30,32,73,401,403만 다름 |
| `references/images.md` | `skills/build-video-scenes/references/images.md` | `1987916569bc68c6` | 줄 34,98,99만 다름 |
| `references/qa.md` | `skills/critique-video/references/qa.md` | `281f0744ce98d674` | 줄 170,173,177만 다름 |
| `references/story.md` | `skills/plan-video/references/story.md` | `83aa6ce6d962ae73` | 줄 159,165,174만 다름 |
| `references/techniques.md` | `skills/build-video-scenes/references/techniques.md` | `bb6f32abb1f557b5` | 줄 228,347만 다름 |
| `scripts/cleanup.py` | `skills/resolve-showreel-tools/scripts/cleanup.py` | `3f9a817c8738c1d0` | 같음 |
| `scripts/codex_ref_image.sh` | `skills/resolve-showreel-tools/scripts/codex_ref_image.sh` | `84d9c732e11f38ab` | 같음 |
| `scripts/contact_sheet.py` | `skills/resolve-showreel-tools/scripts/contact_sheet.py` | `212c64f25800ed3d` | 같음 |
| `scripts/eleven.py` | `skills/resolve-showreel-tools/scripts/eleven.py` | `ad61f1a5431a18d0` | 같음 |
| `scripts/finish.py` | `skills/resolve-showreel-tools/scripts/finish.py` | `86740cb88b94bffa` | 같음 |
| `scripts/flash_list.py` | `skills/resolve-showreel-tools/scripts/flash_list.py` | `513c87a914924ec4` | 같음 |
| `scripts/mix.py` | `skills/resolve-showreel-tools/scripts/mix.py` | `569f5b2e285dd723` | 같음 |
| `scripts/motion_check.py` | `skills/resolve-showreel-tools/scripts/motion_check.py` | `d2feb0d8dba77a1b` | 같음 |
| `scripts/music_tools.py` | `skills/resolve-showreel-tools/scripts/music_tools.py` | `d7bf2725e502b7b3` | 같음 |
| `scripts/narrate.py` | `skills/resolve-showreel-tools/scripts/narrate.py` | `7148e331b3cc66c5` | 같음 |
| `scripts/new_project.py` | `skills/resolve-showreel-tools/scripts/new_project.py` | `b43f42fca4ba4ccd` | 같음 |
| `scripts/package-lock.json` | `skills/resolve-showreel-tools/scripts/package-lock.json` | `245cd864f287d0f5` | 같음 |
| `scripts/package.json` | `skills/resolve-showreel-tools/scripts/package.json` | `101a6d230ff2661e` | 같음 |
| `scripts/preflight.py` | `skills/resolve-showreel-tools/scripts/preflight.py` | `b1802e13d5fa9895` | 같음 |
| `scripts/prep_images.py` | `skills/resolve-showreel-tools/scripts/prep_images.py` | `7fa0534b90cbb801` | 같음 |
| `scripts/qa_check.py` | `skills/resolve-showreel-tools/scripts/qa_check.py` | `0765be750b043e0d` | 같음 |
| `scripts/render.mjs` | `skills/resolve-showreel-tools/scripts/render.mjs` | `52ac114394256491` | 같음 |
| `scripts/render_pieces.py` | `skills/resolve-showreel-tools/scripts/render_pieces.py` | `a2c716a048ef3980` | 같음 |
| `scripts/sfx_library.py` | `skills/resolve-showreel-tools/scripts/sfx_library.py` | `8b23c1f12ecd585c` | 같음 |
| `scripts/synth_music.py` | `skills/resolve-showreel-tools/scripts/synth_music.py` | `bd035ddeee3790e0` | 같음 |
| `scripts/timeline.py` | `skills/resolve-showreel-tools/scripts/timeline.py` | `95e872e1fb23f150` | 같음 |
| `scripts/tools/cutout.swift` | `skills/resolve-showreel-tools/scripts/tools/cutout.swift` | `292e252c05bd2775` | 같음 |

같음 28개, 줄 수정 7개, 합계 35개

### references 줄 변경 목록

| 파일 | 줄 | 종류 | 변경 |
| --- | --- | --- | --- |
| audio.md | 15, 79, 128, 129, 139, 144, 154, 163, 165, 171, 172, 188 | 가 | `scripts/…` → `$S/…` |
| audio.md | 175 | 가 | `assets/sfx_presets.json` → `$S/../assets/sfx_presets.json` |
| audio.md | 32 | 나 | `/v1/user/subscription` → `GET /v1/user/subscription` |
| audio.md | 82 | 나 | `/with-timestamps` → `…/with-timestamps` |
| audio.md | 123 | 나 | 긴 대시 → 쌍점 |
| brief.md | 90 | 나 | 긴 대시 → 쌍점 |
| brief.md | 101 | 나 | `0–6` → `0~6` |
| engine.md | 21, 24, 32 | 나 | 긴 대시 → 쌍점 |
| engine.md | 30 | 나 | `../assets/img/x.jpg` → `'../assets/img/x.jpg'`(프로젝트 `reel/` 기준 경로라 skill 기준으로 해석되지 않게) |
| engine.md | 73 | 가 | "SKILL.md 7단계" → build-video-scenes의 SKILL.md "스타일 프레임" |
| engine.md | 401 | 가 | "SKILL.md 맨 앞 기준 표" → `../resolve-showreel-tools/references/contract.md`의 "결과물 기준" |
| engine.md | 403 | 나 | 인라인 코드 `/tmp` → 일반 글자 /tmp |
| images.md | 34 | 가 | `assets/gen/` → `<프로젝트>/assets/gen/` |
| images.md | 98, 99 | 가 | `scripts/prep_images.py` → `$S/prep_images.py` |
| qa.md | 170, 173 | 가 | `assets/gen/` → `<프로젝트>/assets/gen/` |
| qa.md | 177 | 가 | `scripts/cleanup.py` → `$S/cleanup.py` |
| story.md | 159 | 나 | 긴 대시 → 쌍점 |
| story.md | 165 | 나 | `0–8.3` → `0~8.3` |
| story.md | 174 | 가 | `scripts/narrate.py` → `$S/narrate.py` |
| techniques.md | 228 | 나 | `45–920` → `45~920` |
| techniques.md | 347 | 나 | `0–9–0` → `0-9-0` |

references 안에서 다른 문서를 파일 이름만으로 부르는 곳(`design.md`의 … 등)은 그대로 두고, adapter의 "자료 위치" 표가 실제 경로를 알려 준다.
