import unittest
import shutil

import autosave
import bcolors
import jamgen
import paths
import submit
from settings import Settings
import shared
import symlink_cfg
import tb
import templates


class Tests(unittest.TestCase):
    def test_autosave_get(self):
        self.assertIsNotNone(autosave.get_all_autosaves())

    def test_submit(self):
        ex_map = Settings.maps[0]
        ex_zip = submit.zip(ex_map, paths.TEMP)
        self.assertTrue(ex_zip.exists())
        ex_zip.unlink()

    def test_jamgen(self):
        ex_jam = jamgen.gen(paths.TEMP, 'test')
        self.assertTrue(ex_jam.exists())
        shutil.rmtree(ex_jam)


if __name__ == '__main__':
    unittest.main()
