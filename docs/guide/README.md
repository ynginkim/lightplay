# 사용 가이드

## 지금 할 일

### 설치

영상을 만들 작업 폴더(Git 저장소)에서 이 skillset을 설치한다. op55는 기본 음악 경로를 사용할 때 같은 프로젝트 범위에 설치한다.

```bash
npx skills@1.7.4 add ynginkim/motion-graphic-skills -a claude-code -a codex
npx skills@1.7.4 add ynginkim/op55 -a claude-code -a codex
```

op55를 찾지 못하면 설치 경로를 제공하거나 설치를 선택한다. ElevenLabs Music을 선택하면 [BYOK 안내](../../skills/prepare-video-audio/references/elevenlabs-music.md)에 따라 사용자가 환경변수나 Git에서 제외한 프로젝트 `.env`에 키를 설정한다. 키는 대화에 붙이지 않는다. op55와 API가 모두 사용 불가하면 내장 합성으로 이어간다.

같은 작업 폴더에 예전 `showreel` skill이 설치돼 있으면 두 skill이 같은 영상 요청을 두고 경쟁한다. 한 작업 폴더에는 하나만 둔다.

### 새 영상

자연어로 요청한다. `showreel-mode`가 진입해 사용자만 아는 사실(대상, 꼭 넣을 정보, 자료 위치)만 묻고 나머지는 스스로 정한다. 끝나면 납품 보고의 절대 경로 표에서 마스터 파일을 열어 처음부터 끝까지 보고, 스피커나 이어폰으로 소리를 확인한다. Claude는 소리를 듣지 못하고 수치와 받아쓰기로만 확인했다.

### 만든 영상 고치기

"나레이션 울림만 줄여 줘", "음악을 바꿔 줘", "세로 영상으로도 만들어 줘"처럼 요청한다. `revise-video`가 바뀌는 값과 다시 만들 범위를 먼저 정한다. 오디오만 바뀌면 영상을 다시 렌더하지 않는다. 음악을 바꾸면 화면이 쓰는 큐·히트·음악 에너지가 그대로인지 비교한 뒤 정한다.

### 정리

납품 보고에 지울 목록과 합계가 붙어 있다. 영상을 확인하고 "끝났다"고 말하면 그때 지운다. 휴지통으로 옮기기를 원하면 그렇게 말한다. 나레이션·효과음처럼 비용이 든 파일, 납품본, 장면 코드, 최종 검수 기록은 남는다.

### 옛 프로젝트 다시 렌더

폰트가 없는 옛 프로젝트는 adapter의 "옛 프로젝트 복원" 순서로 폰트를 받고 엔진 파일과 `project.json`을 원래 바이트로 되돌린 뒤 렌더한다.

## 유지보수

```bash
python3 scripts/check.py .            # 구조·참조·정책·사본·명령 스냅샷·문서 드리프트
python3 scripts/check.py . --write-docs   # README·DESIGN 생성 블록 갱신
python3 scripts/selftest.py           # 검사기 오류 주입
python3 scripts/test_music.py         # 발견·BYOK·합성 경로 검증
python3 scripts/install_smoke.py . --dest <새 빈 폴더>   # 임시 Git 폴더에 실제 설치
```

- 저장소 루트에 `SKILL.md`를 두지 않는다. 설치기가 저장소 전체를 skill 하나로 설치한다(이식 중 골격 커밋의 CI 실패로 확인).
- 스크립트·엔진은 `skills/resolve-showreel-tools/` 한 곳에만 둔다. 다른 skill에 복사하지 않는다.
- 같은 문제를 두 번 겪으면 그 일을 맡은 skill의 references에 적는다.
- op55는 실행 시 설치본 문서와 도구 경로를 확인한다. 기준 커밋은 과거 검증 기록으로만 남긴다. 음악 생성 정책은 prepare-video-audio의 reference가 소유한다.

## 설계 이유

- **mode 하나, playbook 둘.** 새 영상과 수정은 출발 상태와 다시 만들 범위가 다르다. 장르(쇼릴·브랜드·교육)는 절차가 같고 기준만 다르므로 playbook을 나누지 않았다.
- **adapter 하나가 도구를 소유.** 스크립트와 엔진을 한 벌만 두고, 다른 skill은 adapter가 확인한 실제 경로로 실행한다. 예전 설치 위치를 추측하는 탐색에 기대지 않도록 op55 경로와 `mix.py` 경로를 자식 명령에 명시한다.
- **hard constraint는 leaf마다.** leaf를 직접 불러도 비용·라이선스·삭제 제약이 빠지지 않는다.
- **op55는 독립.** op55의 내부 작곡·렌더 절차는 현재 설치본 문서를 따른다. 공통 음악 파일·분석 계약으로 연결하고 op55 진입을 중첩하지 않는다.

자세한 기준과 결정은 [DESIGN.md](../../DESIGN.md)에 있다.
