from pathlib import Path
from tomllib import load
import appsettings

settings: dict
with open('settings.toml', 'rb') as f:
    settings = load(f)

path_configs = Path(settings['folders']['configs'])
cfg_files = [f for f in path_configs.glob('*')]
allowlist: dict = settings['limit']


def create_autoexec_and_copy_cfgs(where: Path):
    with open(where / 'autoexec.cfg', 'w') as autoexec:
        filtered_cfg_files = []
        for cfg_file in cfg_files:
            for key, val in allowlist.items():
                # cfg is allowed to be in this mod folder
                if key not in cfg_file.name or where.name in val:
                    filtered_cfg_files.append(cfg_file)
                    new_file = where / cfg_file.name
                    new_file.symlink_to(cfg_file.resolve())

        lines = [f'exec {cfg_file.name}\n' for cfg_file in filtered_cfg_files]
        autoexec.writelines(lines)


def main():
    for mod_location in appsettings.Settings.engines:
        for mod_dir in mod_location.mods:
            print('MOD_DIR', mod_dir)
            for existing_cfg in [child for child in mod_dir.rglob('*') if (child.is_file() or child.is_symlink()) and child.suffix == '.cfg']:
                if existing_cfg.stem != 'config':
                    print('\t', existing_cfg)
                    existing_cfg.unlink()
            create_autoexec_and_copy_cfgs(mod_dir)


if __name__ == '__main__':
    main()
