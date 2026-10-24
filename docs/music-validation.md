# 음악 경로 변경 검증

2026-10-25. 음악 경로는 op55 기본, ElevenLabs Music BYOK 선택, 내장 합성 fallback이다. Suno는 범위에서 제외했다. op55는 설치본의 현재 문서와 영상 소비 계약으로 연결하며 특정 커밋을 실행 조건으로 쓰지 않는다.

## 설계 결정

기존 helper와 skill 지시문으로 선택을 수행한다. 새 음악 dispatcher는 만들지 않았다. op55의 작곡과 런타임 문서 확인은 에이전트가 맡아야 하므로 dispatcher를 더하면 별도 입력·승인·상태 관리가 생긴다.

공통 데이터는 음악 파일, analysis, 실제 `music.provider`, 출처·크레딧이다. 악보와 op55 meta는 op55에만 요구한다. API·합성의 추정 격자와 op55의 정확한 격자를 구분한다. 기존 파일과 유료 원본은 새 검수가 끝날 때까지 보존한다.

## 재실행할 검사

```bash
python3 -B scripts/check.py .
python3 -B scripts/selftest.py
python3 -B scripts/test_music.py
python3 -B scripts/install_smoke.py . --dest <새 빈 폴더>
```

`test_music.py`는 실제 키나 음악 API를 사용하지 않는다. 발견 테스트는 임시 설치본을 만들고, BYOK 테스트는 요청 경계에서 가짜 응답을 쓴다. ffmpeg와 numpy가 있으면 임시 프로젝트에서 실제 내장 합성·음원 분석·타임라인·믹스를 실행한다. 두 도구가 없으면 이 통합 사례만 skip하며 단위 테스트는 실행한다.

검사 범위는 현재·예전 op55 배치, 두 하네스의 설치 위치, 명시한 경로 실패, 불완전 설치본, 환경변수 우선순위, 키 없는 요청 차단, 키의 argv 비노출, Music 요청 본문, 생성 타임아웃의 중복 호출 방지, 실패 시 기존 음악 보존, TTS 권한과 Music 가용성의 구분이다.

CI는 구조 검사, 검사기 오류 주입, 음악 단위 테스트, 실제 skill 설치 smoke를 실행한다. CI에는 ffmpeg·numpy를 추가 설치하지 않으므로 합성 통합 사례의 실행 여부는 테스트 출력으로 확인한다.

## 이번 실행 결과

프로젝트 구조 검사에서 오류·경고가 없었다. 검사기 오류 주입 49개와 음악 테스트 18개가 통과했다. 음악 테스트에는 실제 8초 합성 WAV의 분석·타임라인·믹스가 포함된다. 임시 Git 프로젝트에 10개 skill을 설치했고 두 하네스 경로에서 playbook 4건과 참조 158건이 열렸다.

skill-creator의 공용 quick_validate는 기존 `disable-model-invocation` frontmatter를 지원하지 않아 거부했다. 이 저장소의 checker는 그 필드를 진입 정책으로 검증하며 통과했다. 공용 validator에 맞추려고 기존 하네스 정책을 제거하지 않았다.

## 확인하지 못한 것

| 항목 | 상태 | 닫을 조건 |
| --- | --- | --- |
| 실제 ElevenLabs Music 호출 | unverified | 사용자가 준비한 BYOK와 생성 범위로 실행하고 출력·사용량 확인 |
| 실제 op55 작곡·렌더 연결 | unverified | 설치본의 문서를 읽고 새 음악과 기존 음악 교체를 실행해 계약 확인 |
| 영상 전체 제작·음악 품질 | unverified | 각 경로의 영상 제작과 사용자의 전체 시청·청취 |

테스트와 설치 smoke는 음악의 청취 품질이나 외부 API의 현재 사용 권한을 증명하지 않는다. 독립 검수의 대상 커밋·판정·CI 결과는 해당 PR에 기록한다.
