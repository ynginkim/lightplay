# 검사 키트 출처

2026-10-23 meta-harness 설치본(이 저장소 `.agents/skills/`, 출처 `/Users/fluentt/Documents/meta-harness` HEAD `dab5f3f08be34fc0a844ac932b21f0f4ecda6b8b`)에서 그대로 복사했다. 독자 수정 없음.

| 사본 | 원본 | sha256 |
| --- | --- | --- |
| `scripts/check.py` | `check-skillset/scripts/check.py` | `24cb1401310b10f29612f55c2cf5d3286e5e708bed7f6cb8659291b7125be280` |
| `scripts/selftest.py` | `check-skillset/scripts/selftest.py` | `d8a9af469ae173ffaa0cac91e55b51562e8a421b92b19dbc64474538a50b7c0f` |
| `scripts/install_smoke.py` | `check-skillset/scripts/install_smoke.py` | `2c91646abd23bd881cebf5d1c0d90ffae7527b5fcf10411a6b54baaf68c9ea0b` |
| `.github/workflows/check.yml` | `scaffold-skillset/assets/check.yml` | `e9a9279aa1ee08c24d9f1a414d59400ee9aa88aa4aeb56435dcd20e63df8d7e9` |

갱신할 때는 정본과 diff를 검토하고 `python3 scripts/selftest.py`로 오류 주입 검사를 다시 실행한다.
