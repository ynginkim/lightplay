# Changelog

Changes are grouped using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versioned using [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- deliver-video audio-only refinish no longer reruns `finish.py` under the master's name. It always writes a new name (`_r2`), so the existing master is kept until the new QA passes.
- deliver-video audio-only refinish now compares the per-line narration-over-bed table from `mix.py` with the previous mix. `qa_check.py` does not check that table, so a louder bed could pass QA.
- The shared SFX library location now matches `sfx_library.py`: `--lib`, then `SHOWREEL_SFX_LIBRARY`, then `$CLAUDE_PROJECT_DIR/sfx-library`. Without any of these the script stops, and the docs say to pass `--lib` before the subcommand.

## [0.1.0] - 2026-10-24

### Added
- Contribution, conduct, security, support, and release-readiness documentation.
- A development version source and explicit release verification checklist.

### Changed
- README installation and third-party license guidance reviewed for reproducibility and scope.

This is the first versioned code release. Earlier development history remains available in Git. Cross-repository integration and model/media quality are not guaranteed by structural or installation checks.
