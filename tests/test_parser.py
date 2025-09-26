import unittest
from pathlib import Path

import src.app.parse as parse
from src.app.parse import Entity

TEST_MAP_PATH: Path = Path("./assets/tests/pack/ex_rabbit/mapsrc/packtest.map")


class TestParser(unittest.TestCase):
    def test_parser(self):
        MAP_TEXT = TEST_MAP_PATH.read_text()

        entities1: list[Entity] = parse.parse_whole_map(MAP_TEXT)
        dumps1 = [e.dumps() for e in entities1]

        entities2: list[Entity] = [Entity.loads(s) for s in dumps1]
        dumps2 = [e.dumps() for e in entities2]

        self.assertEqual(dumps1, dumps2)


if __name__ == "__main__":
    unittest.main()
