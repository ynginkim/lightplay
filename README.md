# Lightplay

**Lightplay**는 코드로 렌더하는 한국어 모션그래픽 영상을 콘셉트부터 납품까지 만들고, 만든 영상을 피드백대로 고치는 skillset이다.

한 줄 철학: 주제에서 콘셉트를 세우고, 화면은 렌더한 증거로 판정하며, 오디오와 화면은 이름 붙은 큐로 묶어 늦은 수정을 싸게 만든다.

## 왜 Lightplay인가

**빛과 도형의 움직임에도 악보가 있다.**

Lightplay(라이트플레이)는 발터 루트만(Walter Ruttmann)의 1921년 추상 영화 *Lichtspiel Opus I*에서 이름을 가져왔다. 독일어 *Lichtspiel*을 영어로 옮긴 이름이 *Lightplay*, 빛의 유희다. 색과 도형의 움직임을 시간 위에 펼친 이 작품은 초기 추상 영화의 한 사례다. [작품 정보 — 퐁피두 센터](https://www.centrepompidou.fr/fr/ressources/oeuvre/cdLrro)

그 움직임에는 음악을 함께 설계한 사람이 있었다. 작곡가 막스 부팅(Max Butting)이다. [구겐하임의 상영 프로그램](https://www.guggenheim.org/wp-content/uploads/2017/08/guggenheim-film-visionaries-program.pdf)은 루트만이 부팅에게 현악 사중주 악보를 의뢰하고, 화면과 음악의 타이밍을 맞추기 위한 표기를 악보에 더했다고 설명한다.

Lightplay가 이 작품에서 가져오는 것은 그 협업 방식이다. 도형 하나가 나타나는 순간, 글자가 멈추는 순간, 음악의 강세가 닿는 순간을 함께 설계한다. **모션그래픽으로 영상을 만들되, 화면과 소리를 같은 시간 위에 놓는다.**

## OP55와 함께

[OP55](https://github.com/ynginkim/op55)가 음악을 작곡하고 렌더하면, Lightplay는 그 음악을 장면·타이포그래피·나레이션과 연결한다. 기본 음악 경로로 OP55를 쓰며, 실제 역할은 다음처럼 나뉜다.

- **OP55는 소리의 악보를 만든다.** 영상 길이, 구간별 에너지와 강세, 나레이션 사이의 빈틈을 받아 음악을 만들고 검수한다.
- **Lightplay는 움직임의 타이밍을 잡는다.** 음악과 오디오의 타이밍을 정한 뒤, 장면을 이름 붙은 큐와 박 격자에 연결한다. 글자와 도형이 언제 들어오고 멈추고 사라질지를 그 위에서 구성한다.
- **완성은 렌더한 결과로 확인한다.** 화면이 쓰는 큐나 값이 바뀌면 해당 장면을 다시 렌더하고, 화면에 영향을 주지 않는 음색·볼륨 같은 수정은 믹스와 마감에서 처리한다.

루트만과 부팅의 화면·음악 협업은 이름의 영감이고, 오늘의 연결 방식은 코드와 타임라인이다. 구현의 기준은 [음악 경로](skills/prepare-video-audio/references/music.md)와 [큐는 고정, 표면은 늦게](skills/principle-stable-cues-late-surfaces/SKILL.md)에 있다.

## 구성

<!-- skillset:summary:start -->
mode 1개, playbook 2개, skill 6개, principle 3개 (설치 단위 10개).

검사: `python3 scripts/check.py .`
<!-- skillset:summary:end -->

| 종류 | 이름 | 하는 일 |
| --- | --- | --- |
| mode | `showreel-mode` | 자연어로 진입한다. 요청과 프로젝트 상태를 보고 playbook을 고르고 결과물·완료·사람 판정을 맡는다 |
| playbook | `create-video`, `revise-video` | 새 영상 만들기(원래 0~11단계), 만든 영상 고치기(무효화 범위와 재사용 판단) |
| adapter | `resolve-showreel-tools` | 스크립트·엔진 자원을 한 벌 소유하고 `S`·`O` 경로, 환경 점검, 새 프로젝트, 옛 프로젝트 복원을 맡는다 |
| skill | `plan-video`, `prepare-video-audio`, `build-video-scenes`, `critique-video`, `deliver-video` | 기획·원고, 음악·나레이션·효과음·타임라인, 이미지·장면, 초안 비평, 최종 렌더·믹스·마감·납품 |
| principle | `principle-concept-before-template`, `principle-judge-rendered-evidence`, `principle-stable-cues-late-surfaces` | 콘셉트가 먼저, 렌더한 증거로 판정, 큐는 고정하고 표면은 늦게 |

음악은 [op55](https://github.com/ynginkim/op55)가 기본이다. 선택한 ElevenLabs Music은 사용자 API 키로 쓰고, 두 경로가 실패하거나 사용 불가하면 내장 합성을 쓴다. op55의 현재 설치본 문서와 영상에 필요한 파일 계약을 실행 시 확인한다. [음악 경로와 BYOK 안내](skills/prepare-video-audio/references/music.md)에 선택 기준이 있다.

## 설치

고정된 [`skills@1.7.4` 설치 도구](https://github.com/vercel-labs/skills/blob/v1.7.4/package.json)는 Node.js ≥ 22.20.0을 요구한다. 이는 설치 도구의 요구 사항이며, 영상·음악 제작에 필요한 개별 도구와 자산은 별도로 확인한다.

한 프로젝트에 모든 skill을 함께 설치한다. leaf가 형제 폴더의 adapter와 references를 읽기 때문이다.

```bash
npx skills@1.7.4 add ynginkim/motion-graphic-skills -a claude-code -a codex
```

기본 음악 경로인 op55를 쓸 때는 같은 프로젝트에 `npx skills@1.7.4 add ynginkim/op55 -a claude-code -a codex`로 설치한다. op55 경로를 직접 제공할 수도 있다. 지원 기준은 op55 0.2.0 이상과 resolve-op55-tools 구조다. 0.2.0은 아직 릴리스 전이며 곧 태그가 붙을 예정이다. 버전 정보가 없는 기존 resolve-op55-tools 설치본은 실제 경로와 "버전 미확인"을 기록하고 산출물로 호환성을 확인한다. 옛 op55/scripts 배치는 새 설치 후 `npx skills@1.7.4 remove op55`로 정리한다. 전역 사본이면 `-g`를 붙인다. ElevenLabs Music은 TTS용 키가 있어도 Music 권한·크레딧을 별도로 확인한다. API를 쓰지 않으면 내장 합성으로 진행할 수 있다.

설치본은 복사본이다. 이 저장소가 바뀌면 다시 설치한다. 렌더러 의존성(playwright-core)은 첫 `new_project.py` 실행 때 설치본의 scripts 폴더 안에 받는다. 비공개 저장소이므로 설치하는 계정에 읽기 권한이 있어야 한다. 로컬 경로 설치는 설치 smoke로 확인하지만, GitHub 형식(`ynginkim/motion-graphic-skills`) 설치는 아직 확인하지 않았다.

## 시작 프롬프트

- "당신이 얼마나 놀라운 모션 그래픽 디자이너인지 보여주는 역동적인 한글버전 1분 모션그래픽 비디오를 만들어 보세요. 이력서용 쇼릴 처럼요. 전력을 다해요."
- "다음 달 판교에서 하는 밋업 홍보용 15초 세로 영상 만들어 줘. 일시와 장소는 …"
- "지난번 만든 영상에서 나레이션에 울림이 많아. 그것만 고쳐 줘."

## 검증 수준

기존 검증 기록에서는 구조 검사(`scripts/check.py`), 검사기 오류 주입(`scripts/selftest.py`), 원본 명령 스냅샷 대조, 임시 Git 폴더 설치 smoke, GitHub Actions를 통과했다. 이번 미병합 변경의 원격 CI 결과는 해당 PR에서 별도로 확인한다. 원본 showreel과의 정적 호출 흐름 대조는 시나리오 8개와 시나리오 7의 후속 재판정을 포함해 별도 판정자 4라운드를 기록했다. 최신 시나리오 7 판정의 확정 회귀는 0건이며, 전체 분류는 보존·질문 분기의 수용 범위 때문에 판정 불가로 남았다. 기록과 작성 세션 의견은 [docs/validation.md](docs/validation.md)에 있다. 실제 영상·음악 품질은 만들어 보고 사람이 보고 듣기 전까지 확인되지 않은 상태다.

사용법은 [docs/guide/README.md](docs/guide/README.md), 설계는 [DESIGN.md](DESIGN.md), 이식 기록은 [docs/migration.md](docs/migration.md)에 있다.

## 출처와 라이선스

[revfactory/showreel](https://github.com/revfactory/showreel)과 그 포크 [ynginkim/showreel](https://github.com/ynginkim/showreel)의 커밋 `307b3fd8407feca15c7bd74a089276e8002b204c`에서 시작했다. 이후 upstream은 추적하지 않는다. MIT 라이선스이며 원 저작권 고지는 [LICENSE](LICENSE)에 그대로 있다. 스크립트·엔진 자원을 담은 `skills/resolve-showreel-tools/`에도 같은 LICENSE가 있다.

외부 패키지, API 서비스, 음악, 프로젝트별 폰트·자산의 조건은 [THIRD_PARTY.md](THIRD_PARTY.md)에서 구분한다.

## 기여와 버전

[기여 안내](CONTRIBUTING.md) · [행동강령](CODE_OF_CONDUCT.md) · [보안 제보](SECURITY.md) · [도움받기](SUPPORT.md) · [변경 기록](CHANGELOG.md) · [버전·릴리스](RELEASING.md)

소스 버전은 [VERSION](VERSION)에서, 발행된 태그·릴리스는 [GitHub Releases](https://github.com/ynginkim/motion-graphic-skills/releases)에서 확인한다. 재현 가능한 설치에는 실제 존재하는 태그 또는 전체 40자리 커밋 SHA를 `#REF`로 지정한다. `@name`은 버전이 아니라 skill 선택이다. 비공개 저장소에는 기존 읽기 권한이 필요하다. 설치·구조 검사는 실제 모델 실행이나 산출물 품질 검증과 별개다.

[하네스 패밀리](https://github.com/ynginkim/harness-family) 공통 철학과 목록. 비공개 저장소는 접근 권한이 있는 계정에서만 열린다.
