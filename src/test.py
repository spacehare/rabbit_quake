import unittest
import shutil
import src.autosave as autosave
import src.jamgen as jamgen
import src.app.paths as paths
import src.submit as submit
import src.app.parse as parse
import src.jampack as jampack
from src.app.settings import Settings
from pathlib import Path

# https://docs.python.org/3/library/unittest.html
# python -m unittest
# python -m unittest -h
# python -m unittest src.test.TestSubmit

TEST_MAP_PATH: Path = Path('./assets/tests/pack/mapsrc/packtest.map')
TEST_SUBMIT_PATH: Path = Path('./assets/tests/maps')
TEST_PACK_PATH: Path = Path('./assets/tests/pack')


class TestSubmit(unittest.TestCase):
    def setUp(self):
        self.ex_map = TEST_SUBMIT_PATH
        self.zip = submit.compress(self.ex_map, paths.TEMP, mode=submit.Mode.ZIP)
        self.seven_zip = submit.compress(self.ex_map, paths.TEMP, mode=submit.Mode.SEVEN)

    def tearDown(self) -> None:
        self.zip.unlink()
        self.seven_zip.unlink()

    def test_submit(self):
        self.assertTrue(self.zip.exists())
        self.assertTrue(self.seven_zip.exists())


class TestGenerate(unittest.TestCase):
    def setUp(self) -> None:
        self.ex_jam = jamgen.gen(paths.TEMP, 'test')

    def tearDown(self) -> None:
        shutil.rmtree(self.ex_jam)

    def test_jamgen(self):
        self.assertTrue(self.ex_jam.exists())


class TestAutosave(unittest.TestCase):
    def test_autosave_get(self):
        self.assertIsNotNone(autosave.get_all_autosaves())


# class TestPack(unittest.TestCase):
#     def test_pack(self):
#         jampack.package_submissions


class TestParser(unittest.TestCase):
    def test_parser(self):
        MAP_TEXT = TEST_MAP_PATH.read_text()

        entities1 = parse.parse_whole_map(MAP_TEXT)
        dumps1 = [e.dumps() for e in entities1]

        entities2 = [parse.Entity.loads(s) for s in dumps1]
        dumps2 = [e.dumps() for e in entities2]

        self.assertEqual(dumps1, dumps2)


if __name__ == '__main__':
    unittest.main()
