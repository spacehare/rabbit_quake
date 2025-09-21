import unittest
from pathlib import Path

import src.app.paths as paths
import src.submit as submit

TEST_SUBMIT_PATH: Path = Path("./assets/tests/maps")


class TestSubmit(unittest.TestCase):
    def setUp(self):
        self.ex_map = TEST_SUBMIT_PATH
        self.zip = submit.compress(self.ex_map, paths.TEMP, mode=submit.Mode.ZIP)
        self.seven_zip = submit.compress(
            self.ex_map, paths.TEMP, mode=submit.Mode.SEVEN
        )

    def tearDown(self) -> None:
        self.zip.unlink()
        self.seven_zip.unlink()

    def test_submit(self):
        self.assertTrue(self.zip.exists())
        self.assertTrue(self.seven_zip.exists())


if __name__ == "__main__":
    unittest.main()
