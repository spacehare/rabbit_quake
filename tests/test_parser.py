import unittest
import src.app.parse as parse
from pathlib import Path


TEST_MAP_PATH: Path = Path("./assets/tests/pack/mapsrc/packtest.map")


class TestParser(unittest.TestCase):
    def test_parser(self):
        MAP_TEXT = TEST_MAP_PATH.read_text()

        entities1 = parse.parse_whole_map(MAP_TEXT)
        dumps1 = [e.dumps() for e in entities1]

        entities2 = [parse.Entity.loads(s) for s in dumps1]
        dumps2 = [e.dumps() for e in entities2]

        self.assertEqual(dumps1, dumps2)


if __name__ == "__main__":
    unittest.main()
