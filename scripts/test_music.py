#!/usr/bin/env python3
import importlib.util
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "skills/resolve-showreel-tools/scripts"
sys.path.insert(0, str(SCRIPTS))
import eleven
import preflight


class MusicDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.project = self.root / "project"
        self.home = self.root / "home"
        for target, value in (("cwd", self.project), ("home", self.home)):
            p = patch.object(Path, target, return_value=value)
            p.start()
            self.addCleanup(p.stop)
        for p in (patch.dict(os.environ, {}, clear=True),
                  patch.object(preflight, "HERE", self.project / ".agents/skills/resolve-showreel-tools/scripts"),
                  patch.object(preflight, "SKILLS", self.home / ".claude/skills")):
            p.start()
            self.addCleanup(p.stop)

    def install(self, base, name="resolve-op55-tools"):
        scripts = base / name / "scripts"
        scripts.mkdir(parents=True)
        for name in ("render.mjs", "verify.py", "setup.mjs"):
            (scripts / name).touch()
        return scripts

    def test_current_project_install(self):
        scripts = self.install(self.project / ".agents/skills")
        self.assertEqual(preflight.find_op55(), scripts)

    def test_legacy_project_install(self):
        scripts = self.install(self.project / ".claude/skills", "op55")
        self.assertEqual(preflight.find_op55(), scripts)

    def test_home_codex_install(self):
        scripts = self.install(self.home / ".agents/skills")
        self.assertEqual(preflight.find_op55(), scripts)

    def test_project_precedes_old_home_copy(self):
        self.install(self.home / ".claude/skills", "op55")
        scripts = self.install(self.project / ".agents/skills")
        self.assertEqual(preflight.find_op55(), scripts)

    def test_explicit_path_with_spaces(self):
        scripts = self.install(self.root / "custom location")
        os.environ["OP55_SCRIPTS"] = str(scripts)
        self.assertEqual(preflight.find_op55(), scripts)

    def test_invalid_explicit_path_does_not_select_another_engine(self):
        self.install(self.project / ".agents/skills")
        os.environ["OP55_SCRIPTS"] = str(self.root / "missing")
        self.assertIsNone(preflight.find_op55())

    def test_incomplete_install_is_not_usable(self):
        scripts = self.install(self.project / ".agents/skills")
        (scripts / "verify.py").unlink()
        self.assertIsNone(preflight.find_op55())


class MusicKeyTests(unittest.TestCase):
    def test_project_key_and_environment_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text('ELEVENLABS_API_KEY="project-test-key"\n')
            with patch.dict(os.environ, {}, clear=True), patch.object(Path, "cwd", return_value=root):
                self.assertEqual(eleven.api_key(), "project-test-key")
                with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "environment-test-key"}):
                    self.assertEqual(eleven.api_key(), "environment-test-key")

    def test_missing_key_does_not_send_request(self):
        with patch.object(eleven, "api_key", return_value=None), patch.object(eleven.subprocess, "run") as run:
            with self.assertRaises(eleven.ElevenError) as raised:
                eleven.request("POST", "/v1/music")
            self.assertEqual(raised.exception.code, 2)
            run.assert_not_called()

    def test_key_stays_out_of_command_arguments(self):
        response = subprocess.CompletedProcess([], 0, stdout=b"audio\n200", stderr=b"")
        with patch.object(eleven, "api_key", return_value="request-test-key"), \
                patch.object(eleven.subprocess, "run", return_value=response) as run:
            self.assertEqual(eleven.request("GET", "/v1/models"), b"audio")
            self.assertNotIn("request-test-key", " ".join(run.call_args.args[0]))
            self.assertIn(b"xi-api-key: request-test-key", run.call_args.kwargs["input"])


class MusicPreflightTests(unittest.TestCase):
    def inspect(self, key, tier=None, models_error=False):
        def request(method, path, **kwargs):
            self.assertEqual(method, "GET")
            if path == "/v1/models" and models_error:
                raise eleven.ElevenError("models permission missing", 3, 401)
            return json.dumps({"tier": tier})

        output = StringIO()
        with patch.object(eleven, "api_key", return_value=key), \
                patch.object(eleven, "request", side_effect=request), \
                patch.object(preflight, "find_op55", return_value=None), \
                patch.object(preflight, "run", return_value=(0, "fixture tool")), \
                patch.dict(sys.modules, {"numpy": object(), "PIL": object()}), \
                patch.object(sys, "argv", ["preflight.py", "--json"]), redirect_stdout(output):
            preflight.main()
        self.assertNotIn("preflight-test-key", output.getvalue())
        return json.loads(output.getvalue())["caps"]

    def test_missing_key_is_unavailable(self):
        self.assertIs(self.inspect(None)["music_api"], False)

    def test_free_plan_is_unavailable(self):
        self.assertIs(self.inspect("preflight-test-key", "free")["music_api"], False)

    def test_paid_tts_key_does_not_prove_music_permission(self):
        self.assertIsNone(self.inspect("preflight-test-key", "creator")["music_api"])

    def test_models_scope_failure_does_not_reject_music_only_key(self):
        self.assertIsNone(self.inspect("preflight-test-key", models_error=True)["music_api"])


class MusicRequestTests(unittest.TestCase):
    def test_prompt_and_plan_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "music.mp3"
            with patch.object(eleven, "request", return_value=b"audio") as request:
                eleven.music(output, prompt="instrumental", length_s=8)
                self.assertTrue(request.call_args.kwargs["body"]["force_instrumental"])
                self.assertEqual(request.call_args.kwargs["body"]["music_length_ms"], 8000)
                self.assertEqual(output.read_bytes(), b"audio")
                plan = {"sections": [{"duration_ms": 8000}]}
                eleven.music(output, plan=plan)
                self.assertEqual(request.call_args.kwargs["body"]["composition_plan"], plan)
                self.assertNotIn("prompt", request.call_args.kwargs["body"])

    def test_timeout_does_not_retry_chargeable_generation(self):
        response = subprocess.CompletedProcess([], 28, stdout=b"", stderr=b"timeout")
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(eleven, "api_key", return_value="timeout-test-key"), \
                patch.object(eleven.subprocess, "run", return_value=response) as run, \
                patch.object(eleven.time, "sleep"):
            output = Path(tmp) / "music.mp3"
            with self.assertRaises(eleven.ElevenError):
                eleven.music(output, prompt="instrumental", length_s=8)
            self.assertEqual(run.call_count, 1)
            self.assertFalse(output.exists())

    def test_api_rejection_preserves_existing_music(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "music.mp3"
            output.write_bytes(b"previous paid music")
            with patch.object(eleven, "request", side_effect=eleven.ElevenError("payment required", 4, 402)):
                with self.assertRaises(eleven.ElevenError):
                    eleven.music(output, prompt="instrumental", length_s=8)
            self.assertEqual(output.read_bytes(), b"previous paid music")


@unittest.skipUnless(shutil.which("ffmpeg") and importlib.util.find_spec("numpy"), "ffmpeg and numpy required")
class MusicPipelineTests(unittest.TestCase):
    def test_synth_analysis_timeline_and_mix(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            music = project / "audio/music"
            music.mkdir(parents=True)
            (music / "spec.json").write_text(json.dumps({"duration": 8, "mood": "pulse", "bpm": 120,
                "sections": [{"start": 0, "energy": 0.3}, {"start": 4, "energy": 0.7}]}))
            (project / "script.json").write_text(json.dumps({"duration": 8, "lines": [],
                "music": {"file": "audio/music/music.wav"},
                "scenes": [{"id": "intro", "start": 0, "end": 8}]}))
            commands = [
                ["synth_music.py", "music", "audio/music/spec.json", "audio/music/music.wav"],
                ["music_tools.py", "analyze", "audio/music/music.wav"],
                ["timeline.py", "script.json", "--music-analysis", "audio/music/analysis.json"],
                ["mix.py", "timeline.json"],
            ]
            for script, *args in commands:
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *args],
                    cwd=project, capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with wave.open(str(music / "music.wav")) as wav:
                self.assertEqual(wav.getframerate(), 48000)
                self.assertEqual(wav.getnchannels(), 2)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertAlmostEqual(wav.getnframes() / wav.getframerate(), 8, delta=0.1)
            analysis = json.loads((music / "analysis.json").read_text())
            self.assertEqual(analysis["file"], "audio/music/music.wav")
            self.assertTrue(analysis["beats"])
            self.assertTrue(analysis["downbeats"])
            timeline = json.loads((project / "timeline.json").read_text())
            self.assertTrue(timeline["music_tl"]["beats"])
            self.assertTrue((project / "audio/mix.wav").stat().st_size > 1000)
            self.assertTrue((project / "reel/timeline.js").is_file())


if __name__ == "__main__":
    unittest.main()
