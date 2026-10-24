# ElevenLabs Music을 BYOK로 사용하기

음악 경로 선택은 `references/music.md`를 따른다. 이 경로는 사용자의 ElevenLabs 계정과 API 키를 사용하며 음악 생성 크레딧이 든다. Suno나 다른 제공사로 요청을 전달하지 않는다.

## 키와 사용 범위 준비

1. 기존 TTS용 `ELEVENLABS_API_KEY`가 있으면 같은 키를 재사용할 수 있다. 사용자 대시보드에서 Music 권한·크레딧과 키별 한도를 확인한다. 현재 helper의 TTS·구독 조회만으로 Music 사용 가능 여부를 증명할 수는 없다. 사용자가 Music 사용을 선택했으면 승인한 길이·곡 수 안에서 첫 생성 POST를 한 번 보내고 그 결과로 실제 사용 가능 여부를 판정한다. 기존 승인 범위 안에서는 매 호출마다 다시 묻지 않는다.
2. 키가 없으면 [공식 키 발급 안내](https://elevenlabs.io/docs/eleven-api/guides/cookbooks/music)에서 사용자가 키를 발급한다. 이번 작업에 필요한 Music 권한을 켠다. TTS·STT·효과음을 함께 쓸 때만 해당 권한을 더한다. 크레딧 조회용 User Read는 선택이다.
3. 사용자가 실행 환경의 `ELEVENLABS_API_KEY` 또는 Git에서 제외한 프로젝트 `.env`에 `ELEVENLABS_API_KEY=<발급한 키>`를 직접 설정한다. 파일을 쓰기 전에 `git check-ignore .env`로 제외 여부를 확인하고, 제외되지 않았으면 작업 프로젝트의 `.gitignore`에 추가한다. 대화에는 설정 완료만 알린다. 키 원문을 요청하거나 출력·커밋하지 않는다. 전역 셸 설정은 자동으로 바꾸지 않는다.
4. 기존 helper는 환경변수, 현재 폴더의 `.env`, 부모 폴더의 `.env`, 홈의 `.config/showreel/.env` 순서로 읽는다. 프로젝트 폴더에서 실행한다. 부모·홈의 공유 키를 쓰게 되면 그 계정이 이번 작업용인지 사용자에게 확인한다. 키 존재·조회 성공만으로 Music 사용 가능이나 생성 성공을 선언하지 않는다.

Music API는 유료 사용자용이다. 최신 권한·모델·제약·이용 조건은 [공식 quickstart](https://elevenlabs.io/docs/eleven-api/guides/cookbooks/music), [인증 안내](https://elevenlabs.io/docs/api-reference/authentication), [Compose API](https://elevenlabs.io/docs/api-reference/music/compose)에서 실제 사용 직전에 확인한다. 여기에 고정 요금이나 플랜별 권한 표를 복제하지 않는다.

## 생성과 후처리

프로젝트 폴더에서 실행한다. `$S`는 adapter가 확인한 scripts 절대 경로다. `references/music.md`의 spec을 먼저 쓴다. `global_styles`에는 콘셉트의 장르·악기·질감과 instrumental을 적는다. API에 아티스트·작곡가·곡 이름을 넣지 않는다.

```bash
python3 "$S/music_tools.py" plan audio/music/spec.json
python3 "$S/eleven.py" music audio/music/generated.mp3 --plan audio/music/plan.json
python3 "$S/music_tools.py" fit audio/music/generated.mp3 audio/music/music.wav --dur 30
python3 "$S/music_tools.py" analyze audio/music/music.wav
```

`--dur`는 spec과 프로젝트의 실제 길이로 바꾼다. 이미 음악이 있으면 새 폴더를 쓰고 모든 명령의 경로를 함께 바꾼다. 생성된 원본 MP3는 보존한다. 보정·편집한 최종 파일에서 분석을 다시 만든다. 분석의 `file`이 `music.file`과 같은 파일을 뜻하는지 확인한다.

짧은 요청은 plan 대신 prompt를 쓸 수 있다. 길이와 모델은 현재 API가 지원하는 범위에서 정한다. 아래 모델은 기존 helper의 기본값이며 최신 권장 모델이라는 뜻은 아니다.

```bash
python3 "$S/eleven.py" music audio/music/generated.mp3 --prompt "Instrumental electronic pulse, no vocals" --length 30 --model music_v1
```

prompt와 plan은 함께 보내지 않는다. prompt 모드는 helper가 `force_instrumental`을 보낸다. plan 모드는 instrumental 지침을 plan에 포함한다. seed는 완전한 재현성을 보장하지 않는다. 생성 파일의 실제 길이·무음·가창 유무·구간별 에너지를 확인한다. 요청한 구간과 실제 구간이 다를 수 있으므로 결과를 분석한 뒤 장면 기준점을 정한다.

## 실패와 fallback

- 키 없음·인증 실패·권한 부족·유료 플랜 또는 크레딧 부족은 원인을 안내한다. 사용자가 준비하지 않으면 `references/music.md`의 경로 선택으로 돌아간다. 한도를 늘리거나 결제·키 교체를 자동으로 하지 않는다.
- 요청 오류는 현재 API 문서와 인자를 확인한다. 유료 생성 POST는 자동 재시도하지 않는다. helper는 403의 출력 포맷 제한에만 낮은 비트레이트로 다시 요청한다.
- 타임아웃·연결 끊김·서버 오류는 생성·과금 여부가 불명확할 수 있다. 요청 기록을 확인하고 중복 생성하지 않는다. `references/music.md`의 경로 선택으로 돌아가며 미확인 사용량을 보고한다.
- 생성·보정·분석이 실패하면 이전 파일을 성공 결과로 사용하지 않는다. `references/music.md`의 같은 경로 선택을 따른다. 실패 원인, 실제 사용한 경로, 추가 생성 횟수를 남긴다.

검수는 `references/music.md`의 공통 수락 기준, `references/audio.md`의 믹스 기준과 최종 QA를 따른다. op55의 악보 전용 검증기를 이 경로에 요구하지 않는다.
