import unittest
from pathlib import Path

import rabbitquake.autosave as autosave
from rabbitquake.app import deps
from rabbitquake.app.settings import jampack

# import tempfile


TEST_PACK_PATH: Path = Path("./assets/tests/pack")


# class TestPack(unittest.TestCase):
#     def test_pack(self):
#         jampack.package_submission()

if __name__ == "__main__":
    unittest.main()
