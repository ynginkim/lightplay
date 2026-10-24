# motion-graphic-skills

코드로 렌더하는 한국어 모션그래픽 영상을 콘셉트부터 납품까지 만들고, 만든 영상을 피드백대로 고치는 skillset이다.

한 줄 철학: 주제에서 콘셉트를 세우고, 화면은 렌더한 증거로 판정하며, 오디오와 화면은 이름 붙은 큐로 묶어 늦은 수정을 싸게 만든다.

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
| skill | `plan-video`, `prepare-video-audio`, `build-video-scenes`, `critique-video`, `deliver-video` | 기획·원고, 음악(op55)·나레이션·효과음·타임라인, 이미지·장면, 초안 비평, 최종 렌더·믹스·마감·납품 |
| principle | `principle-concept-before-template`, `principle-judge-rendered-evidence`, `principle-stable-cues-late-surfaces` | 콘셉트가 먼저, 렌더한 증거로 판정, 큐는 고정하고 표면은 늦게 |

음악은 별도 skillset인 [op55](https://github.com/ynginkim/op55)가 만든다. 이 skillset은 op55의 파일 계약과 문서로만 연결한다(기준 커밋 `828990b`).

## 설치

한 프로젝트에 모든 skill을 함께 설치한다. leaf가 형제 폴더의 adapter와 references를 읽기 때문이다.

```bash
npx skills@1.7.4 add ynginkim/motion-graphic-skills -a claude-code -a codex
npx skills@1.7.4 add ynginkim/op55 -a claude-code
```

설치본은 복사본이다. 이 저장소가 바뀌면 다시 설치한다. 렌더러 의존성(playwright-core)은 첫 `new_project.py` 실행 때 설치본의 scripts 폴더 안에 받는다. 비공개 저장소이므로 설치하는 계정에 읽기 권한이 있어야 한다. 로컬 경로 설치는 설치 smoke로 확인하지만, GitHub 형식(`ynginkim/motion-graphic-skills`) 설치는 아직 확인하지 않았다.

## 시작 프롬프트

- "당신이 얼마나 놀라운 모션 그래픽 디자이너인지 보여주는 역동적인 한글버전 1분 모션그래픽 비디오를 만들어 보세요. 이력서용 쇼릴 처럼요. 전력을 다해요."
- "다음 달 판교에서 하는 밋업 홍보용 15초 세로 영상 만들어 줘. 일시와 장소는 …"
- "지난번 만든 영상에서 나레이션에 울림이 많아. 그것만 고쳐 줘."

## 검증 수준

기존 검증 기록에서는 구조 검사(`scripts/check.py`), 검사기 오류 주입(`scripts/selftest.py`), 원본 명령 스냅샷 대조, 임시 Git 폴더 설치 smoke, GitHub Actions를 통과했다. 이번 미병합 변경의 원격 CI 결과는 해당 PR에서 별도로 확인한다. 원본 showreel과의 정적 호출 흐름 대조(dry-run, 시나리오 8개)는 별도 판정자 2라운드에서 회귀 0건이다. 기록은 [docs/validation.md](docs/validation.md)에 있다. 실제 영상·음악 품질은 만들어 보고 사람이 보고 듣기 전까지 확인되지 않은 상태다.

사용법은 [docs/guide/README.md](docs/guide/README.md), 설계는 [DESIGN.md](DESIGN.md), 이식 기록은 [docs/migration.md](docs/migration.md)에 있다.

## 출처와 라이선스

[revfactory/showreel](https://github.com/revfactory/showreel)과 그 포크 [ynginkim/showreel](https://github.com/ynginkim/showreel)의 커밋 `307b3fd8407feca15c7bd74a089276e8002b204c`에서 시작했다. 이후 upstream은 추적하지 않는다. MIT 라이선스이며 원 저작권 고지는 [LICENSE](LICENSE)에 그대로 있다. 스크립트·엔진 자원을 담은 `skills/resolve-showreel-tools/`에도 같은 LICENSE가 있다.

외부 패키지, API 서비스, 음악, 프로젝트별 폰트·자산의 조건은 [THIRD_PARTY.md](THIRD_PARTY.md)에서 구분한다.

## 기여와 버전

[기여 안내](CONTRIBUTING.md) · [행동강령](CODE_OF_CONDUCT.md) · [보안 제보](SECURITY.md) · [도움받기](SUPPORT.md) · [변경 기록](CHANGELOG.md) · [버전·릴리스](RELEASING.md)

소스 버전은 [VERSION](VERSION)에서, 발행된 태그·릴리스는 [GitHub Releases](https://github.com/ynginkim/motion-graphic-skills/releases)에서 확인한다. 재현 가능한 설치에는 실제 존재하는 태그 또는 전체 40자리 커밋 SHA를 `#REF`로 지정한다. `@name`은 버전이 아니라 skill 선택이다. 비공개 저장소에는 기존 읽기 권한이 필요하다. 설치·구조 검사는 실제 모델 실행이나 산출물 품질 검증과 별개다.

[하네스 패밀리](https://github.com/ynginkim/harness-family) 공통 철학과 목록. 비공개 저장소는 접근 권한이 있는 계정에서만 열린다.
