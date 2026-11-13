# 실제 화면 캡처

## 목차

- 언제 캡처하나
- 캡처 설정 파일
- 로그인이 필요한 화면
- 실명 가리기
- 긴 페이지와 스크롤
- 장면에서 쓰기: 가상 카메라

## 언제 캡처하나

- 제품, 서비스, 저장소가 주제인 정보 영상은 실제 화면을 먼저 쓴다. 기능은 실제 화면 위에서 짚는다. 추상 비유와 코드로 그린 가짜 화면으로 만든 제품 영상은 거절됐고, 실제 화면을 캡처한 영상은 통과했다.
- 비유는 이름이나 도입 구간에만 쓴다. 기능 설명을 비유로 대신하지 않는다.
- 캡처할 수 없을 때만(아직 없는 기능, 접근 권한 없음, 가릴 수 없는 개인정보) 코드로 목업을 그린다. 화면 안에 목업임을 밝히고(예: "재현 화면") 제작노트에도 적는다.
- 어떤 화면과 계정을 쓸지, 비공개 저장소를 화면에 보여도 되는지는 plan-video의 내용 맞추기 표("쓸 실제 자료")에서 사용자 동의를 받는다.

## 캡처 설정 파일

캡처는 `$S/capture.mjs`가 한다. 무엇을 어떻게 찍었는지 다시 찍을 수 있게 설정을 `<프로젝트>/capture/shots.json`으로 남긴다.

```json
{
  "viewport": {"width": 1920, "height": 1080},
  "scale": 2,
  "colorScheme": "dark",
  "locale": "en-US",
  "wait": 3000,
  "redact": ["실명", "별칭"],
  "shots": [
    {"name": "repo", "url": "https://github.com/<owner>/<repo>", "full": true},
    {"name": "issues", "url": "https://github.com/<owner>/<repo>/issues"},
    {"name": "readme", "url": "https://github.com/<owner>/<repo>", "scroll": {"to": "article.markdown-body", "offset": -80, "frames": 90}}
  ]
}
```

```bash
node $S/capture.mjs shots <프로젝트>/capture/shots.json --out <프로젝트>/capture/<화면 묶음>
```

- 2배율(`scale: 2`)로 찍는다. 장면에서 확대해도 글자가 선명하다.
- 결과는 `<이름>_view_2x.png`(화면 크기), `full`이면 `<이름>_full_2x.png`(전체 페이지), `scroll`이면 `<이름>_scroll/` 프레임이다. `manifest.json`에 파일마다 원본 픽셀 크기 `[너비, 높이]`가 남고(스크롤 폴더는 `[너비, 높이, 프레임 수]`), 장면 코드가 이 크기를 쓴다.
- `scroll.to`는 선택자나 px다. 선택자는 그 페이지에 실제로 있는지 먼저 본다. GitHub 저장소 첫 화면의 README 본문은 `article.markdown-body`다.
- 한 장이 실패해도(HTTP 오류, 없는 선택자) 나머지는 찍고 종료 코드 1로 끝난다. 출력의 `실패` 줄을 읽는다.
- 찍은 PNG는 Read로 열어 로그인 상태, 가림, 잘림을 확인한다.

## 로그인이 필요한 화면

비공개 저장소나 로그인한 화면은 로그인 전용 브라우저 프로필로 찍는다. 프로필에는 로그인 쿠키가 남으므로 프로젝트 폴더 밖 임시 폴더에 만들고 촬영이 끝나면 지운다.

```bash
PROFILE=$(mktemp -d)
node $S/capture.mjs login --profile "$PROFILE" --url https://github.com/login --check 'meta[name="user-login"][content]'
node $S/capture.mjs shots <프로젝트>/capture/shots.json --out <프로젝트>/capture/<화면 묶음> --profile "$PROFILE"
node $S/capture.mjs forget --profile "$PROFILE"
```

1. `login`이 창을 띄우면 사용자에게 그 창에서 직접 로그인해 달라고 한다. 비밀번호나 인증 코드를 대신 입력하지 않는다. 로그인이 확인되면 창이 닫힌다.
2. 설정 파일에 `"check"`(위 `--check`와 같은 선택자)를 넣으면 첫 화면이 로그인 상태가 아닐 때 아무것도 찍지 않고 종료 코드 2로 멈춘다. GitHub는 로그아웃 상태에서도 `content`가 빈 `user-login` meta를 내므로, 도구는 `content`가 빈 meta를 일치로 치지 않는다.
3. 찍은 뒤 바로 `forget`으로 프로필을 지운다. 제작노트에 "로그인 전용 창에서 사용자가 로그인, 촬영 뒤 프로필 삭제"라고 적는다.

## 실명 가리기

- `redact`에 실명, 별칭, 이메일을 넣으면 찍기 전에 화면 글자에서 같은 길이의 `█`로 가린다(대소문자 무시). 출력의 가린 개수를 보고, 그 화면에 있어야 할 이름이 0개면 표기가 다른지 확인한다. 찍은 PNG를 Read로 열어 남은 이름이 없는지 본다.
- `█`는 영문자보다 넓어 가린 줄이 길어지거나 줄바꿈이 바뀔 수 있다. 짧은 이름에는 문제없지만 빽빽한 화면이면 가리지 않고 찍은 뒤 장면의 `redact`로 덮는다.
- 이미지 속 글자(아바타, 그림)는 가리지 못한다. 장면에서 아래 `redact`로 덮는다.
- 영상에 쓸 화면을 만들려고 실제 보드나 저장소에 글을 올리는 일은 사용자가 요청했을 때만 하고, 누가 무엇을 올렸는지 제작노트에 밝힌다. 올리는 글의 @멘션은 백틱으로 감싸 실제 사용자에게 알림이 가지 않게 한다.

## 긴 페이지와 스크롤

- 긴 페이지는 전체 페이지 스틸(`full`)을 찍고 장면의 가상 카메라로 내려가는 방법이 먼저다. 글자가 선명하고 스크롤 시각을 장면이 정한다.
- 고정 헤더, 지연 로딩, 스크롤에 반응하는 화면처럼 전체 페이지 스틸이 실제와 다르게 나오면 `scroll`로 프레임마다 찍은 시퀀스를 쓴다.

## 장면에서 쓰기: 가상 카메라

2배 캡처를 패널에 넣고 원본 좌표로 카메라를 움직인다. 좌표는 모두 원본 픽셀(1920 폭 2배 캡처면 3840 폭) 기준이다.

```js
const { css, h } = REEL;
// natW, natH 는 capture/<묶음>/manifest.json 의 크기
function shot(parent, src, natW, natH, o = {}) {
  const w = o.w || 1920, hh = o.h || 1080;
  const box = h('div', '', parent);
  css(box, { position: 'absolute', overflow: 'hidden', width: w + 'px', height: hh + 'px', borderRadius: (o.radius ?? 18) + 'px' });
  const layer = h('div', '', box);
  css(layer, { position: 'absolute', left: '0', top: '0', width: natW + 'px', height: natH + 'px', transformOrigin: '0 0' });
  const im = REEL.img('../' + src); layer.appendChild(im);
  css(im, { display: 'block', width: natW + 'px', height: natH + 'px' });
  return { box, layer, w, h: hh };
}
// 원본 (cx, cy)를 패널 가운데에 두고 k배로 본다(k = 화면 px / 원본 px). 3840 폭 캡처는 k = 0.5 면 전체가 보이고 k = 1 이 선명하게 볼 수 있는 최대다
function look(sh, cx, cy, k) {
  css(sh.layer, { transform: `translate(${(sh.w / 2 - cx * k).toFixed(2)}px,${(sh.h / 2 - cy * k).toFixed(2)}px) scale(${k.toFixed(5)})` });
}
// 원본 좌표의 사각형을 흐리게 덮는다. 카메라와 함께 움직인다
function redact(sh, x, y, w, hh) {
  const m = h('div', '', sh.layer);
  css(m, { position: 'absolute', left: x + 'px', top: y + 'px', width: w + 'px', height: hh + 'px', borderRadius: '8px', background: 'rgba(13,17,23,.55)', backdropFilter: 'blur(16px)' });
  return m;
}
```

`render`에서 `kf`로 카메라를 옮긴다. 예: `look(this.sh, kf(lt, [[0, 1920], [1.2, 2600, ease.swift]]), kf(lt, [[0, 1080], [1.2, 900, ease.swift]]), kf(lt, [[0, 0.5], [1.2, 0.9, ease.swift]]))`. 짚을 곳에는 원본 좌표로 테두리나 밝은 띠를 더하고, 확대 뒤 1초 이상 머물러 읽을 시간을 준다.
