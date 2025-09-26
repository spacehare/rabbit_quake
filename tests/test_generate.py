import shutil
import unittest

import rabbitquake.app.paths as paths
import rabbitquake.jamgen as jamgen


class TestGenerate(unittest.TestCase):
    def setUp(self) -> None:
        stem = "abc_username"
        self.ex_jam = paths.TEMP / stem
        jamgen.gen(self.ex_jam, stem)

    def tearDown(self) -> None:
        shutil.rmtree(self.ex_jam)

    def test_jamgen(self):
        self.assertTrue(self.ex_jam.exists())


if __name__ == "__main__":
    unittest.main()
