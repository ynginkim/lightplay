# Third-party provenance and licensing scope

The repository's original contributions are MIT. This does not relicense third-party code, externally installed packages, service outputs, fonts, images, or audio.

## showreel-derived code and resources

This project started from [revfactory/showreel](https://github.com/revfactory/showreel) and its [ynginkim/showreel fork at commit 307b3fd8407feca15c7bd74a089276e8002b204c](https://github.com/ynginkim/showreel/tree/307b3fd8407feca15c7bd74a089276e8002b204c). The [baseline license](https://github.com/ynginkim/showreel/blob/307b3fd8407feca15c7bd74a089276e8002b204c/LICENSE) is MIT, Copyright (c) 2026 Minho Hwang (revfactory).

That copyright and full MIT permission notice are retained in `LICENSE` and `skills/resolve-showreel-tools/LICENSE`. Keep both when distributing the repository or the standalone adapter. The repository does not automatically track upstream changes.

## Playwright

`skills/resolve-showreel-tools/scripts/package.json` declares `playwright-core` (`^1.60.0`). Playwright is an external installed dependency under [Apache-2.0](https://github.com/microsoft/playwright/blob/main/LICENSE), not original MIT code from this repository. Preserve the license and notices shipped with the actual installed version when redistributing it. A browser installation has its own terms; an automation wrapper does not relicense the browser.

## Lottie asset dependencies

`skills/resolve-showreel-tools/scripts/package.json` pins six packages for asset-mode, each under MIT: [`@lottiefiles/dotlottie-web`](https://github.com/LottieFiles/dotlottie-web) 0.82.1, [`lottie-web`](https://github.com/airbnb/lottie-web) 5.13.0, [`opentype.js`](https://github.com/opentypejs/opentype.js) 2.0.0, [`svgpath`](https://github.com/fontello/svgpath) 2.6.0, [`@lottie-animation-community/lottie-specs`](https://github.com/Lottie-Animation-Community/lottie-specs) 0.3.2, and [`@dotlottie/dotlottie-js`](https://github.com/LottieFiles/dotlottie-js) 1.9.0. The player page in `skills/resolve-showreel-tools/assets/player/` is original MIT code.

MIT covers these six packages only. Their dependency tree, recorded in `package-lock.json`, includes other licenses. `@dotlottie/dotlottie-js` depends on `sharp` (Apache-2.0), whose optional platform binaries `@img/sharp-libvips-*` are LGPL-3.0-or-later, and on `wasm-imagemagick` (Apache-2.0). Other transitive packages are BSD-3-Clause, ISC, or 0BSD. Check the installed tree before redistributing `node_modules`, and keep the notices that ship with each package.

## ElevenLabs service

`skills/resolve-showreel-tools/scripts/eleven.py` calls the [ElevenLabs API](https://elevenlabs.io/docs/api-reference/introduction) through HTTP. This is a remote service integration, not an included ElevenLabs SDK or a license grant to voices, music, or generated outputs. Service access, usage permissions, output rights, attribution requirements, and commercial-use eligibility depend on the applicable provider terms and account plan. This repository's MIT license does not replace those terms. Verify them for each intended use rather than relying on a code license or a cached plan description.

## op55

The default music path uses the separate [op55 skillset](https://github.com/ynginkim/op55). The installed skillset and its output contract are checked at runtime. Commit `828990b` identifies the original migration validation, not a required runtime version. Its own code license and [third-party notices](https://github.com/ynginkim/op55/blob/main/THIRD_PARTY.md) apply separately, including sound-bank, font, and vendored-code terms. Retain the attribution emitted for assets that require it. This document does not assert clearance of every sample or resulting output.

## Project-specific assets and fonts

No font files are bundled in the reviewed repository tree. Fonts, images, video, audio, and other assets added to individual video projects need their own source and license records. Do not assume every imported font uses SIL OFL or that every generated asset is covered by MIT. Include the actual applicable license and attribution with redistributed assets where required.

## Community document

The Contributor Covenant text in `CODE_OF_CONDUCT.md` retains its stated Creative Commons Attribution 4.0 license and attribution; it is not relicensed MIT.

## Lichtspiel Opus I film excerpt

- **Local assets:** `assets/lichtspiel-opus-i-1921.gif`; the earlier still `assets/lichtspiel-opus-i-1921.png` is retained.
- **Work:** Walter Ruttmann, *Lichtspiel Opus I* (1921).
- **Source:** [Wikimedia Commons: Lichtspiel Opus I (1921).webm](https://commons.wikimedia.org/wiki/File:Lichtspiel_Opus_I_(1921).webm).
- **Excerpt:** 05:30~05:36 in that silent, video-only source, converted to a looping 480 × 360 GIF at 8 fps (48 frames, approximately 1.34 MB). Frames are sampled in their original order and timing; no interpolation, retouching, upscaling, or color grading is applied. GIF conversion uses a 64-color palette. No soundtrack is included. The retained PNG is the 05:30 frame.
- **Rights record:** The Commons file page marks the source `PD-old-70-expired` and [Public Domain Mark 1.0](https://creativecommons.org/publicdomain/mark/1.0/). The mark identifies public-domain status; it is not this repository's MIT license.
- **Purpose:** Historical reference for the project's name, not a Lightplay-generated demo or an endorsement of this project.
