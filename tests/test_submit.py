import unittest
import zipfile
from pathlib import Path

import rabbitquake.app.paths as paths
import rabbitquake.submit as submit

TEST_SUBMIT_PATH: Path = Path("./assets/tests/pack/ex_rabbit")


class TestSubmit(unittest.TestCase):
    def setUp(self):
        self.ex_map_path = TEST_SUBMIT_PATH
        self.zip_path = submit.compress(
            self.ex_map_path, paths.TEMP, mode=submit.Mode.ZIP, convert_markdown=True
        )
        self.seven_zip_path = submit.compress(
            self.ex_map_path, paths.TEMP, mode=submit.Mode.SEVEN
        )

    def tearDown(self) -> None:
        self.zip_path.unlink()
        self.seven_zip_path.unlink()

    def test_submit(self):
        self.assertTrue(self.zip_path.exists())
        self.assertTrue(self.seven_zip_path.exists())

        has_html = None
        with zipfile.ZipFile(self.zip_path, "r") as file:
            for name in file.namelist():
                print("name:", name)
                if name.endswith(".html"):
                    has_html = True

        self.assertTrue(has_html)


if __name__ == "__main__":
    unittest.main()
