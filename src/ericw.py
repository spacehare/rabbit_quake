import subprocess
from pathlib import Path
from bcolors import Ind
from settings import Ericw, EricwProfile


class Compiler:
    def __init__(self, path: Path):
        self.path = path
        self.qbsp = path / 'bin/qbsp.exe'
        self.vis = path / 'bin/vis.exe'
        self.light = path / 'bin/light.exe'

    def compile_qbsp(self, params: list[str], map_path: Path, bsp_path: Path):
        return subprocess.run([self.qbsp, *params, map_path, bsp_path])

    def compile_vis(self, params: list[str], bsp_path: Path):
        return subprocess.run([self.vis, *params, bsp_path])

    def compile_light(self, params: list[str], bsp_path: Path):
        return subprocess.run([self.light, *params, bsp_path])


def compile(profile: EricwProfile, compiler: Compiler, map_path: Path, bsp_path: Path | None = None, *, qbsp=True, vis=True, light=True):
    print(f'running profile {profile.name}')
    out_bsp: Path = bsp_path or (map_path.parent / Ericw.bsp_dir / map_path.with_suffix('.bsp').name)
    out_mapsrc: Path = Ericw.src_dir / map_path

    for idx, tool_bool in enumerate([qbsp, vis, light]):
        proc_code = 0
        if tool_bool:
            match idx:
                case 0: proc_code = get_output(compiler.compile_qbsp(profile.qbsp_params, map_path, out_bsp))
                case 1: proc_code = get_output(compiler.compile_vis(profile.vis_params, out_bsp))
                case 2: proc_code = get_output(compiler.compile_light(profile.light_params, out_bsp))
        if proc_code != 0:
            print(Ind.mark(False), 'compiling failed')
            return

    print(Ind.mark(), 'done compiling')
    return out_bsp


def get_output(process: subprocess.CompletedProcess[bytes]):
    out = process.stdout and process.stdout.decode('utf-8')
    err = process.stderr and process.stderr.decode('utf-8')
    code = process.returncode
    print(out or '')
    print(err or '')
    print(Ind.mark(code == 0), code)
    return code
