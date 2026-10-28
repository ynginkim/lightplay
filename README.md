<p align="center"><img src="assets/banner.png" alt="빛의 궤적과 도형이 하나의 악보 위에서 만나는 Lightplay 창작 이미지" width="100%"></p>

<h1 align="center">Lightplay</h1>

<p align="center">
<b>글자와 도형을 움직이고, 음악과 같은 시간 위에 놓는다.</b><br>
코드로 만드는 한국어 모션그래픽. 콘셉트부터 렌더, 비평, 수정, 납품까지.<br>
Claude Code와 Codex에서 쓰는 모션그래픽 제작 하네스.
</p>

<p align="center">
<img alt="Claude Code and Codex" src="https://img.shields.io/badge/runs%20in-Claude%20Code%20%C2%B7%20Codex-efe6d6?style=for-the-badge&labelColor=111111">
<img alt="music by op55" src="https://img.shields.io/badge/music-op55-e85c3a?style=for-the-badge&labelColor=111111">
<img alt="license MIT" src="https://img.shields.io/badge/license-MIT-a99d8a?style=for-the-badge&labelColor=111111">
</p>

<p align="center"><a href="#왜-lightplay인가">이름의 이야기</a> · <a href="#설치">설치</a> · <a href="#만들고-고치는-법">사용법</a> · <a href="#op55와-함께">OP55와 함께</a> · <a href="#thanks-to-showreel">Thanks to Showreel</a> · <a href="docs/guide/README.md">가이드</a></p>

---

## 왜 Lightplay인가

**빛과 도형의 움직임에도 악보가 있다.**

1921년, 발터 루트만(Walter Ruttmann)은 색과 도형이 움직이는 추상 영화 *Lichtspiel Opus I*를 선보였다. *Lichtspiel*은 빛의 유희, 영어로는 *Lightplay*. 이 이름은 그 작품에서 가져왔다. [퐁피두 센터의 작품 기록](https://www.centrepompidou.fr/fr/ressources/oeuvre/cdLrro)

화면만의 작품은 아니었다. 작곡가 막스 부팅(Max Butting)이 음악을 맡았다. [구겐하임의 상영 프로그램](https://www.guggenheim.org/wp-content/uploads/2017/08/guggenheim-film-visionaries-program.pdf)은 루트만이 부팅에게 현악 사중주 악보를 의뢰하고, 화면과 음악의 타이밍을 맞추기 위한 표기를 악보에 더했다고 설명한다.

Lightplay는 그 협업에서 출발한다. 글자가 들어오는 순간, 도형이 멈추는 순간, 음악의 강세가 닿는 순간을 따로 만들지 않는다. 같은 시간 위에서 함께 설계한다.

오늘의 악보는 코드와 타임라인이다. 장면은 DOM·Canvas·WebGL·3D로 만들고, 소리와 화면은 이름 붙은 큐로 잇는다. 완성 여부는 코드를 다 썼는지가 아니라 **렌더한 장면이 의도대로 움직이는지**로 확인한다.

## 무엇을 만드는가

- **모션그래픽.** 한글 타이포그래피, 도형, 데이터, 이미지가 움직이는 쇼릴·제품 소개·행사 홍보·교육 영상.
- **하나의 콘셉트.** 정해진 템플릿에 내용을 끼우지 않고, 주제에서 표현 방식을 고른다. 구간별 움직임과 화면의 밀도도 그 콘셉트에서 정한다.
- **다시 고칠 수 있는 프로젝트.** MP4와 함께 원고, 타임라인, 장면 코드, 오디오 원본, 검수 기록을 남긴다.

실사 촬영본의 컷 편집이나 Sora·Veo 같은 생성형 비디오 모델 호출은 이 하네스의 범위가 아니다. 이미지 생성은 장면에 필요한 재료를 만드는 데 쓴다.

## 설치

고정된 [`skills@1.7.4` 설치 도구](https://github.com/vercel-labs/skills/blob/v1.7.4/package.json)는 Node.js ≥ 22.20.0을 요구한다. 이는 설치 도구의 요구 사항이며, 영상·음악 제작에 필요한 개별 도구와 자산은 별도로 확인한다.

한 프로젝트에 모든 skill을 함께 설치한다. leaf가 형제 폴더의 adapter와 references를 읽기 때문이다.

```bash
npx skills@1.7.4 add ynginkim/lightplay -a claude-code -a codex
```

<details>
<summary>음악 경로·기존 설치본·환경 확인</summary>

기본 음악 경로인 op55를 쓸 때는 같은 프로젝트에 `npx skills@1.7.4 add ynginkim/op55 -a claude-code -a codex`로 설치한다. op55 경로를 직접 제공할 수도 있다. 지원 기준은 op55 0.2.0 이상과 resolve-op55-tools 구조다. [v0.2.0 릴리스](https://github.com/ynginkim/op55/releases/tag/v0.2.0)가 발행되어 있다. 버전 정보가 없는 기존 resolve-op55-tools 설치본은 실제 경로와 "버전 미확인"을 기록하고 산출물로 호환성을 확인한다. 옛 op55/scripts 배치는 새 설치 후 `npx skills@1.7.4 remove op55`로 정리한다. 전역 사본이면 `-g`를 붙인다. ElevenLabs Music은 TTS용 키가 있어도 Music 권한·크레딧을 별도로 확인한다. API를 쓰지 않으면 내장 합성으로 진행할 수 있다.

설치본은 복사본이다. 이 저장소가 바뀌면 다시 설치한다. 렌더러 의존성(playwright-core)은 첫 `new_project.py` 실행 때 설치본의 scripts 폴더 안에 받는다. 비공개 저장소이므로 설치하는 계정에 읽기 권한이 있어야 한다. 로컬 경로 설치는 설치 smoke로 확인하지만, GitHub 형식(`ynginkim/lightplay`) 설치는 아직 확인하지 않았다.

</details>

## 만들고 고치는 법

영상 작업 폴더에서 자연어로 요청한다. 현재 진입 스킬 이름은 `showreel-mode`다. 제품명은 Lightplay지만 설치된 스킬·도구의 내부 이름은 유지한다.

### 처음 만들 때

> 다음 달 밋업을 소개하는 15초 세로 모션그래픽을 만들어 줘. 한글 타이포그래피가 중심이고, 마지막 음악 강세에 행사명이 나타나면 좋겠어. 일시·장소·신청 링크는 이 자료를 써 줘.

대상과 꼭 넣을 정보, 자료 위치를 확인한 뒤 콘셉트·원고·오디오·장면을 만든다. 초안을 렌더하고 약한 구간을 비평해 다시 만든 후 최종 믹스와 검수를 거친다.

```text
요청 → 콘셉트·원고 → 음악·나레이션·큐 → 장면 코드 → 초안 렌더
                                                    ↓
                    납품 ← 최종 렌더·믹스 ← 비평·재작업
```

### 만든 것을 고칠 때

> 마지막 문구만 바꾸고, 나레이션 울림을 줄여 줘. 음악과 전체 길이는 그대로 유지해 줘.

수정 요청은 별도 playbook으로 처리한다. 무엇이 바뀌는지 먼저 찾고, 그 값에 의존하는 결과만 다시 만든다. 화면이 읽는 큐·음악 에너지·규격이 달라지면 해당 장면을 다시 렌더한다. 음색이나 볼륨처럼 화면에 영향을 주지 않는 수정은 믹스와 마감에서 처리한다.

### 남는 것

| 결과 | 용도 |
| --- | --- |
| 마스터 MP4 · 공유용 MP4 · 포스터 JPG | 완성 영상과 배포용 파일 |
| 자막 SRT | 나레이션이 있는 영상의 자막 |
| 원고 · 타임라인 · 장면 코드 · 오디오 원본 | 수정하고 다시 렌더할 근거 |
| 비평 기록 · 검수 시트 · 수치 보고 | 무엇을 확인했고 무엇을 고쳤는지 |
| 제작노트 | 출처·크레딧·재생성 명령·남은 사람 확인 |

## 세 가지 제작 원칙

| 원칙 | 실제로 하는 일 |
| --- | --- |
| **콘셉트가 먼저** | 주제에서 표현 방식을 찾는다. 도구 목록이나 익숙한 템플릿부터 고르지 않는다. |
| **렌더한 증거로 판정** | 프레임·검수 시트·수치를 보고 약한 구간을 고친다. 실행 성공을 영상 품질로 대신하지 않는다. |
| **큐는 고정, 표면은 늦게** | 화면과 소리를 이름 붙은 큐에 연결한다. 수정할 때는 화면이 소비하는 값이 바뀌었는지부터 확인한다. |

원칙은 각각 [콘셉트](skills/principle-concept-before-template/SKILL.md), [렌더 증거](skills/principle-judge-rendered-evidence/SKILL.md), [큐와 수정 범위](skills/principle-stable-cues-late-surfaces/SKILL.md)에 적혀 있다.

## OP55와 함께

**OP55는 음악을 작곡하고, Lightplay는 그 음악 위에 움직임을 설계한다.**

[OP55](https://github.com/ynginkim/op55)의 이름은 *Opus 5.5 → Op. 55*, 베토벤의 교향곡 3번으로 이어진다. Lightplay의 이름은 루트만과 부팅의 *Lichtspiel Opus I*에서 왔다. 두 이름의 연결은 소개 문구에서 끝나지 않는다.

- **음악을 부탁한다.** Lightplay가 영상 길이, 구간별 에너지와 강세, 나레이션 사이의 빈틈을 정하면 OP55가 악보를 코드로 쓰고 음악을 렌더·검수한다.
- **같은 시간을 쓴다.** 음악 파일과 박·다운비트·히트 정보를 받아 타임라인을 만들고, 글자와 도형이 등장하고 멈추는 순간을 큐에 연결한다.
- **고칠 곳을 나눈다.** OP55는 작곡과 음악 렌더를, Lightplay는 장면·나레이션·효과음·최종 믹스를 맡는다. 바뀐 값이 화면에 영향을 주는지 확인한 뒤 재렌더 범위를 정한다.

루트만과 부팅의 협업은 이름의 영감이다. 지금 두 하네스를 잇는 것은 [음악 파일 계약](skills/prepare-video-audio/references/music.md)과 [공유 타임라인](skills/resolve-showreel-tools/references/contract.md)이다. 특정 버전 조합의 실제 영상·음악 품질을 보장한다는 뜻은 아니다.

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

## 확인한 것과 남은 것

납품 파일이 있다고 감상까지 끝난 것은 아니다. 에이전트는 프레임·수치·STT로 확인하고, 사람은 영상 전체의 리듬·가독성·의도 전달과 실제 소리를 보고 듣는다.

- 실제 영상·음악 품질은 만들어 보고 사람이 확인하기 전까지 미검증이다.
- ElevenLabs를 선택하면 계정 권한·크레딧·사용 조건을 별도로 확인한다. API를 쓰지 않는 음악 경로도 있다.
- 한글 타이포그래피와 한국어 나레이션을 중심으로 설계했다. 다른 언어에 같은 결과를 보장하지 않는다.
- 배너는 프로젝트의 시각적 정체성을 위한 그림이며, Lightplay로 만든 영상 데모가 아니다.

<details>
<summary>구조·설치·회귀 검증 기록</summary>

기존 검증 기록에서는 구조 검사(`scripts/check.py`), 검사기 오류 주입(`scripts/selftest.py`), 원본 명령 스냅샷 대조, 임시 Git 폴더 설치 smoke, GitHub Actions를 통과했다. 변경별 원격 CI 결과는 해당 커밋이나 PR에서 별도로 확인한다. 원본 showreel과의 정적 호출 흐름 대조는 시나리오 8개와 시나리오 7의 후속 재판정을 포함해 별도 판정자 4라운드를 기록했다. 최신 시나리오 7 판정의 확정 회귀는 0건이며, 전체 분류는 보존·질문 분기의 수용 범위 때문에 판정 불가로 남았다. 기록과 작성 세션 의견은 [docs/validation.md](docs/validation.md)에 있다. 실제 영상·음악 품질은 만들어 보고 사람이 보고 듣기 전까지 확인되지 않은 상태다.

사용법은 [docs/guide/README.md](docs/guide/README.md), 설계는 [DESIGN.md](DESIGN.md), 이식 기록은 [docs/migration.md](docs/migration.md)에 있다.

</details>

## Thanks to Showreel

**Lightplay의 출발점은 [Minho Hwang(revfactory)의 Showreel](https://github.com/revfactory/showreel)이다.**

코드로 모션그래픽을 만든다는 아이디어만 가져온 것이 아니다. 콘셉트를 세우고, 원고와 오디오를 먼저 맞추고, 장면을 렌더한 뒤 약한 구간을 다시 만드는 제작 흐름부터 엔진·스크립트·레퍼런스까지, Showreel이 열어 둔 작업 위에서 시작했다.

특히 고마운 것은 **도구와 함께 만드는 기준까지 공개했다는 점**이다. 결과물이 움직이는 데서 멈추지 않고, 왜 이 콘셉트인지, 어느 장면이 약한지, 무엇을 다시 만들어야 하는지 묻게 했다. 덕분에 출발선부터 다시 만들지 않고 그 위에서 다음 질문을 이어 갈 수 있었다.

Lightplay는 이 기반을 mode·playbook·skill·principle로 나누고, OP55와의 음악 연결과 수정 범위 판단을 더해 발전시키고 있다. 이름이 바뀌어도 어디서 시작했는지는 남긴다. 좋은 작업 방식을 다른 사람이 이어받을 수 있도록 MIT로 공개해 준 Minho Hwang과 Showreel에 감사한다.

[Showreel 살펴보기](https://github.com/revfactory/showreel) · [이식 과정](docs/migration.md) · [원 저작권 고지](LICENSE)

## 출처와 라이선스

- **코드와 제작 지침.** [revfactory/showreel](https://github.com/revfactory/showreel)과 [ynginkim/showreel의 기준 커밋](https://github.com/ynginkim/showreel/tree/307b3fd8407feca15c7bd74a089276e8002b204c)에서 시작했다. 이후 upstream을 자동 추적하지 않는다. 원 저작권과 MIT 허가문은 [LICENSE](LICENSE)와 [adapter의 LICENSE](skills/resolve-showreel-tools/LICENSE)에 보존한다.
- **이름의 영감.** Walter Ruttmann, *Lichtspiel Opus I* (1921), 음악 Max Butting. 위 작품·상영 기록은 이름과 제작 철학의 출처이며, 이 프로젝트와의 제휴나 보증을 뜻하지 않는다.
- **대표 그림.** README 배너는 이미지 생성 도구로 만든 창작 이미지다. 영화의 실제 프레임이나 역사적 자료가 아니다.
- **외부 자산.** 패키지, API 서비스, 음악, 프로젝트별 폰트·이미지의 조건은 [THIRD_PARTY.md](THIRD_PARTY.md)에서 구분한다. 이 저장소의 MIT 라이선스가 외부 자산까지 다시 허가하지는 않는다.

## 기여와 버전

[기여 안내](CONTRIBUTING.md) · [행동강령](CODE_OF_CONDUCT.md) · [보안 제보](SECURITY.md) · [도움받기](SUPPORT.md) · [변경 기록](CHANGELOG.md) · [버전·릴리스](RELEASING.md)

소스 버전은 [VERSION](VERSION)에서, 발행된 태그·릴리스는 [GitHub Releases](https://github.com/ynginkim/lightplay/releases)에서 확인한다. 재현 가능한 설치에는 실제 존재하는 태그 또는 전체 40자리 커밋 SHA를 `#REF`로 지정한다. `@name`은 버전이 아니라 skill 선택이다. 비공개 저장소에는 기존 읽기 권한이 필요하다. 설치·구조 검사는 실제 모델 실행이나 산출물 품질 검증과 별개다.

[하네스 패밀리](https://github.com/ynginkim/harness-family) 공통 철학과 목록. 비공개 저장소는 접근 권한이 있는 계정에서만 열린다.
