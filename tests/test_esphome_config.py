import os
import shutil
import subprocess
import sysconfig
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / "esphome" / "devices" / "kitchen.yaml"


class KitchenConfigTests(unittest.TestCase):
    def test_voice_assistant_is_top_level(self):
        lines = CONFIG.read_text(encoding="utf-8").splitlines()
        component_line = lines.index("voice_assistant:")
        self.assertEqual(lines[component_line + 1], "  id: va")

    def run_esphome(self, command):
        esphome = shutil.which("esphome")
        if esphome is None:
            executable = "esphome.exe" if os.name == "nt" else "esphome"
            candidate = Path(sysconfig.get_path("scripts")) / executable
            if not candidate.is_file():
                self.skipTest("ESPHome CLI is not installed or is not on PATH.")
            esphome = str(candidate)
        with tempfile.TemporaryDirectory() as temp_dir:
            test_config = Path(temp_dir) / CONFIG.name
            shutil.copyfile(CONFIG, test_config)
            test_config.with_name("secrets.yaml").write_text(
                "\n".join(
                    (
                        'wifi_ssid: "test-network"',
                        'wifi_password: "test-wifi-password"',
                        'kitchen_api_encryption_key: '
                        '"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="',
                        'kitchen_fallback_password: "test-fallback-password"',
                        "",
                    )
                ),
                encoding="utf-8",
            )
            if os.name == "nt":
                powershell = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
                if powershell is None:
                    self.skipTest("PowerShell is required to run ESPHome on Windows.")
                executable_arg = esphome.replace("'", "''")
                config_arg = str(test_config).replace("'", "''")
                powershell_command = (
                    "$env:MSYSTEM = $null; "
                    f"& '{executable_arg}' {command} '{config_arg}'; "
                    "exit $LASTEXITCODE"
                )
                process = [powershell, "-NoProfile", "-Command", powershell_command]
            else:
                process = [esphome, command, str(test_config)]
            result = subprocess.run(
                process,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            if command == "compile" and result.returncode == 0:
                firmware = (
                    Path(temp_dir)
                    / ".esphome"
                    / "build"
                    / CONFIG.stem
                    / "build"
                    / f"{CONFIG.stem}.bin"
                )
                self.assertTrue(
                    firmware.is_file(),
                    f"ESPHome reported success without creating {firmware}.\n"
                    f"{result.stdout}\n{result.stderr}",
                )
        return result

    def test_esphome_schema_validation(self):
        result = self.run_esphome("config")
        self.assertEqual(
            result.returncode,
            0,
            f"ESPHome config validation failed:\n{result.stdout}\n{result.stderr}",
        )

    @unittest.skipUnless(
        os.environ.get("ESPHOME_TEST_COMPILE") == "1",
        "Set ESPHOME_TEST_COMPILE=1 to run the firmware compile.",
    )
    def test_esphome_firmware_compile(self):
        result = self.run_esphome("compile")
        self.assertEqual(
            result.returncode,
            0,
            f"ESPHome firmware compile failed:\n{result.stdout}\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()