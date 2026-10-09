"""Read-only Steam parsing tests using temporary, synthetic Steam libraries."""

from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.helper_loader import load_helper


class SteamFixtureTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper("gaming")
        self.temporary = tempfile.TemporaryDirectory(prefix="rog-steam-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.steam = self.base / "Steam"
        self.steam.mkdir()
        self.helper.STEAM = [self.steam]

    def write(self, path, text=""):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def manifest(self, root, appid, name):
        return self.write(root / "steamapps" / ("appmanifest_" + appid + ".acf"),
                          '"AppState"\n{\n"appid" "' + appid + '"\n"name" "' + name + '"\n}\n')

    def localconfig(self, root, account, entries):
        blocks = ['"' + appid + '"\n{\n"LastPlayed" "' + str(timestamp) + '"\n}' for appid, timestamp in entries]
        return self.write(root / "userdata" / account / "config/localconfig.vdf", "\n".join(blocks))

    def test_roots_skip_missing_installations_and_resolve_symlinks(self):
        alias = self.base / "steam-alias"
        alias.symlink_to(self.steam, target_is_directory=True)
        self.helper.STEAM = [self.base / "missing", alias]
        self.assertEqual(list(self.helper.roots()), [self.steam.resolve()])

    def test_missing_steam_returns_empty_library_and_recent(self):
        self.helper.STEAM = [self.base / "missing"]
        self.assertEqual(self.helper.library(), {})
        self.assertEqual(self.helper.recent({}), [])

    def test_library_reads_local_and_config_external_library_manifests(self):
        external = self.base / "Extra Games"
        self.manifest(self.steam, "10", "Local Game")
        self.manifest(external, "20", "External Game")
        self.write(self.steam / "config/libraryfolders.vdf", '"libraryfolders"\n{\n"1"\n{\n"path" "' + str(external) + '"\n}\n}\n')
        self.assertEqual(self.helper.library(), {"10": "Local Game", "20": "External Game"})

    def test_library_uses_steamapps_libraryfolders_fallback(self):
        external = self.base / "secondary"
        self.manifest(external, "20", "Fallback Library Game")
        self.write(self.steam / "steamapps/libraryfolders.vdf", '"path" "' + str(external) + '"')
        self.assertEqual(self.helper.library(), {"20": "Fallback Library Game"})

    def test_library_handles_flatpak_root_and_deduplicates_app_ids(self):
        flatpak = self.base / ".var/app/com.valvesoftware.Steam/.local/share/Steam"
        self.manifest(self.steam, "10", "Shared Game")
        self.manifest(flatpak, "10", "Shared Game")
        self.manifest(flatpak, "30", "Flatpak Game")
        self.helper.STEAM = [self.steam, flatpak]
        self.assertEqual(self.helper.library(), {"10": "Shared Game", "30": "Flatpak Game"})

    def test_library_excludes_steam_compatibility_tools(self):
        self.manifest(self.steam, "10", "Hollow Knight: Silksong")
        self.manifest(self.steam, "20", "Constance")
        self.manifest(self.steam, "30", "Proton Experimental")
        self.manifest(self.steam, "40", "Proton 9.0")
        self.manifest(self.steam, "50", "Steam Linux Runtime 3.0 (sniper)")
        self.manifest(self.steam, "60", "Steamworks Common Redistributables")
        self.manifest(self.steam, "70", "Proton Wars")  # A game, not a compatibility tool
        self.assertEqual(self.helper.library(), {
            "10": "Hollow Knight: Silksong", "20": "Constance",
            "70": "Proton Wars",
        })

    def test_recent_nested_steam_config_and_missing_art(self):
        raw='''"UserLocalConfigStore" { "Software" { "Valve" { "Steam" {
            "apps" {
                "10" { "LastPlayed" "100" "Playtime" "30" }
                "20" { "LastPlayed" "200" }
                "30" { "Playtime" "15" }
            }
        } } } }'''
        self.write(self.steam / "userdata/111/config/localconfig.vdf", raw)
        result=self.helper.recent({"10":"Silksong","20":"Constance","30":"Not played"})
        self.assertEqual([x["name"] for x in result], ["Constance","Silksong"])

    def test_library_ignores_missing_or_nonnumeric_app_ids_and_missing_names(self):
        folder = self.steam / "steamapps"
        self.write(folder / "appmanifest_no_id.acf", '"name" "No ID"')
        self.write(folder / "appmanifest_text_id.acf", '"appid" "abc"\n"name" "Bad ID"')
        self.write(folder / "appmanifest_no_name.acf", '"appid" "30"')
        self.write(folder / "unrelated.acf", '"appid" "40"\n"name" "Wrong file pattern"')
        self.manifest(self.steam, "50", "Valid Game")
        self.assertEqual(self.helper.library(), {"50": "Valid Game"})

    def test_library_replaces_undecodable_bytes_without_crashing(self):
        path = self.steam / "steamapps/appmanifest_10.acf"
        path.parent.mkdir(parents=True)
        path.write_bytes(b'"appid" "10"\n"name" "Game \xff"')
        self.assertEqual(self.helper.library(), {"10": "Game \ufffd"})

    def test_recent_uses_latest_account_timestamp_sorts_and_limits_five(self):
        games = {str(i): "Game " + str(i) for i in range(1, 8)}
        self.localconfig(self.steam, "111", [(str(i), i * 10) for i in range(1, 8)])
        self.localconfig(self.steam, "222", [("1", 999), ("2", 5)])
        result = self.helper.recent(games)
        self.assertEqual([item["id"] for item in result], ["1", "7", "6", "5", "4"])
        self.assertEqual([item["lastPlayed"] for item in result], [999, 70, 60, 50, 40])
        self.assertEqual(result[0]["name"], "Game 1")
        self.assertTrue(all(item["art"] == "" for item in result))

    def test_recent_only_includes_installed_games_with_last_played(self):
        self.localconfig(self.steam, "111", [("10", 123), ("999", 9999)])
        self.assertEqual(self.helper.recent({"10": "Installed", "20": "Never played"}), [
            {"id": "10", "name": "Installed", "lastPlayed": 123, "art": ""}
        ])

    def test_recent_timestamp_key_is_case_insensitive(self):
        self.write(self.steam / "userdata/111/config/localconfig.vdf", '"10"\n{\n"lastplayed" "123"\n}')
        self.assertEqual(self.helper.recent({"10": "Game"})[0]["lastPlayed"], 123)

    def test_recent_supports_each_cover_art_layout(self):
        self.localconfig(self.steam, "111", [("10", 123)])
        cache = self.steam / "appcache/librarycache"
        candidates = (cache / "10_library_600x900.jpg", cache / "10_library_600x900.png", cache / "10/library_600x900.jpg", cache / "10/library_600x900.png")
        for candidate in candidates:
            with self.subTest(candidate=str(candidate.relative_to(cache))):
                self.write(candidate, "fixture image path only")
                self.assertEqual(self.helper.recent({"10": "Game"})[0]["art"], candidate.resolve().as_uri())
                candidate.unlink()

    def test_recent_art_can_come_from_another_existing_steam_root(self):
        secondary = self.base / "secondary"
        art = self.write(secondary / "appcache/librarycache/10_library_600x900.jpg")
        self.localconfig(self.steam, "111", [("10", 123)])
        self.helper.STEAM = [self.steam, secondary]
        self.assertEqual(self.helper.recent({"10": "Game"})[0]["art"], art.resolve().as_uri())

    def test_last_played_must_stay_inside_its_game_block(self):
        # A neighboring app timestamp must not leak into this app.
        self.write(self.steam / "userdata/111/config/localconfig.vdf", '''"10"
{
    "Playtime" "42"
}
"20"
{
    "LastPlayed" "999"
}
''')
        result = self.helper.recent({"10": "Never played", "20": "Actually played"})
        self.assertEqual([item["id"] for item in result], ["20"])


class GamingInfoTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper("gaming")

    def test_info_combines_library_profiles_and_controller_results(self):
        controllers = [{"name": "Gamepad", "mac": "AA:BB:CC:DD:EE:FF", "battery": None}]
        with patch.object(self.helper, "library", return_value={"10": "Game"}), patch.object(self.helper, "recent", return_value=[{"id": "10"}]), patch.object(self.helper, "roots", return_value=iter([Path("/fixture/Steam")])), patch.object(self.helper, "controllers", return_value=controllers), patch.object(self.helper, "profiles", return_value=["quiet"]), patch.object(self.helper, "profile_details", return_value={"quiet": "Quiet"}), patch.object(self.helper.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "quiet\n", "")):
            result = self.helper.info()
        self.assertEqual(result, {
            "ok": True, "installed": 1, "recent": [{"id": "10"}], "steamFound": True,
            "controllers": controllers, "profiles": ["quiet"], "details": {"quiet": "Quiet"}, "active": "quiet"
        })

    def test_info_keeps_steam_data_when_z13ctl_is_missing(self):
        with patch.object(self.helper, "library", return_value={"10": "Game"}), patch.object(self.helper, "recent", return_value=[]), patch.object(self.helper, "roots", return_value=iter([])), patch.object(self.helper, "controllers", return_value=[]), patch.object(self.helper, "profiles", side_effect=FileNotFoundError("z13ctl")):
            result = self.helper.info()
        self.assertTrue(result["ok"])
        self.assertEqual(result["installed"], 1)
        self.assertFalse(result["steamFound"])
        self.assertEqual(result["profiles"], [])
        self.assertEqual(result["active"], "")


if __name__ == "__main__":
    unittest.main()
