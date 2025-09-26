import unittest

import rabbitquake.autosave as autosave


class TestAutosave(unittest.TestCase):
    def test_autosave_get(self):
        self.assertIsNotNone(autosave.get_all_autosaves())


if __name__ == "__main__":
    unittest.main()
