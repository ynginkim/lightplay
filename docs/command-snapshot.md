# 원본 명령 스냅샷

showreel `SKILL.md`(기준 커밋 `307b3fd`, 이 저장소 `374df70`)의 명령 문자열을 줄 번호와 함께 옮긴 것이다. `skillset.json`의 `command_snapshots`가 이 파일과 각 leaf에 같은 문자열이 있는지 검사한다. 명령의 실행 가능성이나 현재 help 출력은 확인하지 않았다(이번 작업은 도메인 스크립트 실행 금지).

이식 뒤 바뀐 명령은 둘이다. 환경 점검은 앞에 `OP55_SCRIPTS=$O`를 붙이고, op55 test mix는 앞에 `SHOWREEL_SCRIPTS=$S`, 뒤에 `--mix-py $S/mix.py`를 붙였다. 아래 원래 문자열은 새 명령 안에 그대로 들어 있다.

| 원본 줄 | 담당 skill | 명령 |
| --- | --- | --- |
| 69 | resolve-showreel-tools | `python3 $S/preflight.py` |
| 76 | resolve-showreel-tools | `python3 $S/eleven.py voices --lang ko` |
| 101 | resolve-showreel-tools | `python3 $S/new_project.py <프로젝트> --ratio 16:9 --duration 60 [--fonts "Hahmlet:wght@300;900"]` |
| 124 | plan-video | `python3 -c "import datetime;print(datetime.date(2026,11,20).strftime('%A'))"` |
| 128 | resolve-showreel-tools | `npx skills add ynginkim/op55 -a claude-code` |
| 128 | resolve-showreel-tools | `node $O/setup.mjs` |
| 138 | prepare-video-audio | `python3 $S/narrate.py <프로젝트>/script.json --stt` |
| 140 | prepare-video-audio | `node $O/render.mjs --score <프로젝트>/audio/music/score.mjs --out <프로젝트>/audio/music/music.wav --analysis <프로젝트>/audio/music/analysis.json` |
| 141 | prepare-video-audio | `python3 $O/verify.py <프로젝트>/audio/music/music.wav --analysis <프로젝트>/audio/music/analysis.json --waveform-png` |
| 142 | prepare-video-audio | `python3 $S/eleven.py sfx-kit <프로젝트>/audio/sfx --names impact,riser` |
| 143 | prepare-video-audio | `python3 $S/timeline.py <프로젝트>/script.json --music-analysis audio/music/analysis.json` |
| 144 | prepare-video-audio | `python3 $O/verify.py <프로젝트>/audio/music/music.wav --analysis <프로젝트>/audio/music/analysis.json --mix <프로젝트>/timeline.json` |
| 156 | prepare-video-audio | `python3 $S/sfx_library.py find 종이` |
| 156 | prepare-video-audio | `python3 $S/sfx_library.py use <이름…> --to <프로젝트>` |
| 166 | build-video-scenes | `~/.claude/skills/codex-image/scripts/codex_imagegen_batch.sh <프로젝트>/assets/gen "프롬프트::이름.png" …` |
| 169 | build-video-scenes | `python3 $S/prep_images.py <프로젝트>/assets/gen --out <프로젝트>/assets/img [--cutout]` |
| 170 | build-video-scenes | `python3 $S/prep_images.py --sheet <프로젝트>/assets/img --out <프로젝트>/qa/sheet_images.png` |
| 194 | critique-video | `node $S/render.mjs --dir <프로젝트>/reel --stills <시작+0.5>,<큐+0.4>,<끝-0.6> --outdir <프로젝트>/qa/stills_<장면>` |
| 195 | critique-video | `node $S/render.mjs --dir <프로젝트>/reel --every 0.5 --outdir <프로젝트>/qa/stills` |
| 196 | critique-video | `python3 $S/contact_sheet.py --dir <프로젝트>/qa/stills --out <프로젝트>/qa/sheet_stills.png --timeline <프로젝트>/timeline.json` |
| 197 | critique-video | `node $S/render.mjs --dir <프로젝트>/reel --out <프로젝트>/out/draft.mp4 --scale 0.5` |
| 198 | critique-video | `python3 $S/contact_sheet.py --video <프로젝트>/out/draft.mp4 --every 1 --out <프로젝트>/qa/sheet_draft.png` |
| 199 | critique-video | `python3 $S/motion_check.py <프로젝트>/out/draft.mp4 --timeline <프로젝트>/timeline.json` |
| 200 | critique-video | `python3 $S/contact_sheet.py --video <프로젝트>/out/draft.mp4 --around <구간 경계 초들> --frames 3 --out <프로젝트>/qa/sheet_cuts.png` |
| 209 | critique-video | `python3 $S/flash_list.py <클립> <클립 시작 초>` |
| 214 | deliver-video | `node $S/render.mjs --dir <프로젝트>/reel --out <프로젝트>/out/video.mp4 --sub 4 --format png` |
| 215 | deliver-video | `python3 $S/mix.py <프로젝트>/timeline.json` |
| 216 | deliver-video | `python3 $S/finish.py --video <프로젝트>/out/video.mp4 --audio <프로젝트>/audio/mix.wav \` |
| 217 | deliver-video | `  --name "<제목>_<길이>s" --outdir <프로젝트>/out --timeline <프로젝트>/timeline.json` |
| 223 | deliver-video | `python3 $S/render_pieces.py --dir <프로젝트>/reel --out <프로젝트>/out/video.mp4 --cuts 0,51.6,103.2,<길이>` |
| 224 | deliver-video | `python3 $S/render_pieces.py --dir <프로젝트>/reel --out <프로젝트>/out/video.mp4 --cuts 0,51.6,103.2,<길이> --only 2` |
| 240 | deliver-video | `python3 $S/qa_check.py <프로젝트>/out/<이름>.mp4 --timeline <프로젝트>/timeline.json --script <프로젝트>/script.json --stt` |
| 261 | deliver-video | `python3 $S/sfx_library.py add <프로젝트>` |
| 262 | deliver-video | `python3 $S/cleanup.py <프로젝트>` |
| 263 | deliver-video | `python3 $S/cleanup.py <프로젝트> --apply` |
