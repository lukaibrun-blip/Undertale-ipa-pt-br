import plistlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.validate_inputs import validate_inputs


class ValidateInputsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.ipa = self.root / "test.ipa"
        self.resource = self.root / "game.ios"
        self.write_ipa()
        self.write_resource()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_ipa(
        self,
        bundle_id: str = "com.jockeholm.undertale",
        version: str = "2.0.0",
        include_game_resource: bool = True,
    ) -> None:
        info = plistlib.dumps({
            "CFBundleIdentifier": bundle_id,
            "CFBundleShortVersionString": version,
        })
        with zipfile.ZipFile(self.ipa, "w") as archive:
            archive.writestr("Payload/UNDERTALE.app/Info.plist", info)
            if include_game_resource:
                archive.writestr("Payload/UNDERTALE.app/games/game.ios", b"placeholder")

    def write_resource(self, header: bytes = b"FORM0000GEN8") -> None:
        self.resource.write_bytes(header + b"test-data")

    def test_accepts_matching_metadata_and_basic_header(self) -> None:
        errors, warnings = validate_inputs(self.ipa, self.resource)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_rejects_wrong_bundle_id(self) -> None:
        self.write_ipa(bundle_id="example.other")
        errors, _ = validate_inputs(self.ipa, self.resource)
        self.assertTrue(any("Bundle ID diferente" in error for error in errors))

    def test_rejects_wrong_version(self) -> None:
        self.write_ipa(version="1.0.0")
        errors, _ = validate_inputs(self.ipa, self.resource)
        self.assertTrue(any("Versão diferente" in error for error in errors))

    def test_rejects_missing_embedded_game_resource(self) -> None:
        self.write_ipa(include_game_resource=False)
        errors, _ = validate_inputs(self.ipa, self.resource)
        self.assertTrue(any("games/game.ios" in error for error in errors))

    def test_rejects_unrecognized_candidate_header(self) -> None:
        self.write_resource(header=b"NOT-A-GAME!")
        errors, _ = validate_inputs(self.ipa, self.resource)
        self.assertTrue(any("FORM/GEN8" in error for error in errors))

    def test_rejects_invalid_archive(self) -> None:
        self.ipa.write_bytes(b"not a ZIP")
        errors, _ = validate_inputs(self.ipa, self.resource)
        self.assertTrue(any("arquivo ZIP" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
