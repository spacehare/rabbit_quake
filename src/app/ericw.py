import subprocess
from pathlib import Path
from app.bcolors import Ind
from app.settings import _contents, make_listpath, Settings
import shutil

# https://ericwa.github.io/ericw-tools/doc/qbsp.html
# https://ericwa.github.io/ericw-tools/doc/vis.html
# https://ericwa.github.io/ericw-tools/doc/light.html

# https://ericw-tools.readthedocs.io/en/latest/


class Profile:
    def __init__(
        self,
        name: str,
        qbsp_params: list[str] | None,
        vis_params: list[str] | None,
        light_params: list[str] | None,
    ):
        self.name = name
        self.qbsp_params = qbsp_params or []
        self.vis_params = vis_params or []
        self.light_params = light_params or []
        print(f"({__name__}) creating profile {self.name}")

    @staticmethod
    def from_dict(d: dict):
        return Profile(d["name"], d.get("qbsp"), d.get("vis"), d.get("light"))


class Compiler:
    def __init__(self, path: Path):
        self.path = path
        self.qbsp = path / "bin/qbsp.exe"
        self.vis = path / "bin/vis.exe"
        self.light = path / "bin/light.exe"

    def compile_qbsp(self, params: list[str], map_path: Path, bsp_path: Path):
        return subprocess.run([self.qbsp, *params, map_path, bsp_path])

    def compile_vis(self, params: list[str], bsp_path: Path):
        return subprocess.run([self.vis, *params, bsp_path])

    def compile_light(self, params: list[str], bsp_path: Path):
        return subprocess.run([self.light, *params, bsp_path])


def compile(
    profile: Profile,
    compiler: Compiler,
    map_path: Path,
    bsp_path: Path | None = None,
    *,
    qbsp=True,
    vis=True,
    light=True,
):
    print(f"running profile {profile.name}")
    print("with map", map_path)
    out_bsp: Path = bsp_path or (
        map_path.parent / bsp_dir / map_path.with_suffix(".bsp").name
    )
    print("to bsp", out_bsp)
    out_mapsrc: Path = src_dir / map_path

    for idx, tool_bool in enumerate([qbsp, vis, light]):
        proc_code = 0
        if tool_bool:
            match idx:
                case 0:
                    proc_code = get_output(
                        compiler.compile_qbsp(profile.qbsp_params, map_path, out_bsp)
                    )
                case 1:
                    proc_code = get_output(
                        compiler.compile_vis(profile.vis_params, out_bsp)
                    )
                case 2:
                    proc_code = get_output(
                        compiler.compile_light(profile.light_params, out_bsp)
                    )
        if proc_code != 0:
            print(Ind.mark(False), "compiling failed")
            return

    print(Ind.mark(), "done compiling")
    return out_bsp


def get_output(process: subprocess.CompletedProcess[bytes]):
    out = process.stdout and process.stdout.decode("utf-8")
    err = process.stderr and process.stderr.decode("utf-8")
    code = process.returncode
    print(out or "")
    print(err or "")
    print(Ind.mark(code == 0), code)
    return code


bsp_dir: Path = Path(_contents["ericw"]["bsp"])
src_dir: Path = Path(_contents["ericw"]["src"])
compilers: list[Compiler] = [
    Compiler(path=comp_path) for comp_path in make_listpath(Settings._ericw)
]
profiles: list[Profile] = [
    Profile.from_dict(prof) for prof in _contents["ericw"]["profiles"]
]


def transfer_or_link(file: Path, location_folder: Path, copy=True):
    out = location_folder / file.name
    if copy:
        shutil.copyfile(file, out)
    else:
        out.symlink_to(file)
    return out
