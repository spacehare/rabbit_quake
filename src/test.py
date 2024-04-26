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
import parse

# https://docs.python.org/3/library/unittest.html


class TestZip(unittest.TestCase):
    def setUp(self):
        self.ex_map = Settings.maps[0]
        self.ex_zip = submit.zip(self.ex_map, paths.TEMP)

    def tearDown(self) -> None:
        self.ex_zip.unlink()

    def test_submit(self):
        self.assertTrue(self.ex_zip.exists())


class testGen(unittest.TestCase):
    def setUp(self) -> None:
        self.ex_jam = jamgen.gen(paths.TEMP, 'test')

    def tearDown(self) -> None:
        shutil.rmtree(self.ex_jam)

    def test_jamgen(self):
        self.assertTrue(self.ex_jam.exists())


class Tests(unittest.TestCase):
    def test_autosave_get(self):
        self.assertIsNotNone(autosave.get_all_autosaves())

    def test_parser(self):
        ex_ent_str = '''
// entity 275
{
"classname" "func_detail_wall"
"_tb_group" "261152"
// brush 0
{
( -896 1408 96 ) ( -896 1409 96 ) ( -896 1408 97 ) tech_st2_grey2 [ 0 -1 0 0 ] [ 0 0 -1 160 ] 0 1 1
( -896 1424 96 ) ( -896 1424 97 ) ( -895 1424 96 ) tech_st2_grey2 [ 1 0 0 -64 ] [ 0 0 -1 160 ] 0 1 1
( -768 1536 120 ) ( -767 1536 120 ) ( -768 1537 120 ) tech_st2_grey2 [ 0 1.0000000000000002 0 0 ] [ 1.0000000000000002 0 0 -144 ] 0 1 1
( -768 1536 128 ) ( -768 1537 128 ) ( -767 1536 128 ) tech_st2_grey2 [ 0 1.0000000000000002 0 0 ] [ 1.0000000000000002 0 0 -96 ] 0 1 1
( -768 1520 128 ) ( -767 1520 128 ) ( -768 1520 129 ) tech_st2_grey2 [ -1 0 0 64 ] [ 0 0 -1 160 ] 0 1 1
( -880 1536 128 ) ( -880 1536 129 ) ( -880 1537 128 ) tech_st2_grey2 [ 0 1.0000000000000002 0 0 ] [ 0 0 -1.0000000000000002 -336 ] 0 1 1
}
// brush 1
{
( -896 1408 96 ) ( -896 1409 96 ) ( -896 1408 97 ) tech_st2_grey2 [ 0 -1 0 0 ] [ 0 0 -1 160 ] 0 1 1
( -896 1424 96 ) ( -896 1424 97 ) ( -895 1424 96 ) tech_st2_grey2 [ 1 0 0 -64 ] [ 0 0 -1 160 ] 0 1 1
( -768 1536 112 ) ( -767 1536 112 ) ( -768 1537 112 ) tech_st2_grey2 [ 0 1.0000000000000002 0 0 ] [ 1.0000000000000002 0 0 -144 ] 0 1 1
( -768 1536 120 ) ( -768 1537 120 ) ( -767 1536 120 ) tech_st2_grey2 [ 0 1.0000000000000002 0 0 ] [ 1.0000000000000002 0 0 -88 ] 0 1 1
( -768 1520 128 ) ( -767 1520 128 ) ( -768 1520 129 ) tech_st2_grey2 [ -1 0 0 64 ] [ 0 0 -1 160 ] 0 1 1
( -864 1536 128 ) ( -864 1536 129 ) ( -864 1537 128 ) tech_st2_grey2 [ 0 1.0000000000000002 0 0 ] [ 0 0 -1.0000000000000002 -320 ] 0 1 1
}
}
'''
        ex_ent = parse.Entity.loads(ex_ent_str)
        ex_ent_dumped = ex_ent.dumps()
        ex_ent_loaded = parse.Entity.loads(ex_ent_dumped)
        self.assertEqual(ex_ent.dumps(), ex_ent_loaded.dumps())


if __name__ == '__main__':
    unittest.main()
