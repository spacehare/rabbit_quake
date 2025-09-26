import unittest
from pathlib import Path

import rabbitquake.app.parse as parse
from rabbitquake.app.parse import Entity

TEST_MAP_PATH: Path = Path("./assets/tests/pack/ex_rabbit/mapsrc/packtest.map")


class TestParser(unittest.TestCase):
    def test_parser(self):
        self.maxDiff = None

        self.assertEqual(parse.to_number_string(-6.123233995736766e-17), "-6.123233995736766e-17")

        map_text = TEST_MAP_PATH.read_text()
        map_lines: list[str] = [line for line in map_text.splitlines() if not line.startswith('//')]

        entities_1: list[Entity] = parse.parse_whole_map(map_text)
        dumps_1: list[str] = [e.dumps() for e in entities_1]

        entities_2: list[Entity] = [Entity.loads(s) for s in dumps_1]
        dumps_2: list[str] = [e.dumps() for e in entities_2]

        for i in [dumps_1, dumps_2]:
            # ensure parser output doesn't alter data just by parsing
            l: list[str] = [line for text in i for line in text.splitlines()]
            self.assertListEqual(l, map_lines)


if __name__ == "__main__":
    unittest.main()
