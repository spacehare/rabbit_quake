import unittest
import shutil
import src.autosave as autosave
import src.jamgen as jamgen
import src.app.paths as paths
import src.submit as submit
import src.app.parse as parse
from src.app.settings import Settings
from pathlib import Path

# https://docs.python.org/3/library/unittest.html
# python -m unittest
# python -m unittest -h
# python -m unittest src.test.TestSubmit

TEST_MAP_PATH: Path = Path('./assets/tests/test.map')
TEST_SUBMIT_PATH: Path = Path('./assets/tests/maps')


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


class TestParser(unittest.TestCase):
    def test_parser(self):
        map_text = TEST_MAP_PATH.read_text()

        entity = parse.Entity.loads(map_text)
        entity_dumped = entity.dumps()
        entity_loaded_from_dumped = parse.Entity.loads(entity_dumped)
        redump = entity_loaded_from_dumped.dumps()

        self.assertEqual(entity_dumped, redump)


if __name__ == '__main__':
    unittest.main()
