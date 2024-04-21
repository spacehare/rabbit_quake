use inputbot::KeybdKey as key;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug, serde::Deserialize)]
struct Settings {
    trenchbroom: PathBuf,
    trenchbroom_preferences: PathBuf,
    ericw: PathBuf,
    engine_exes: Vec<PathBuf>,
    configs: PathBuf,
}

#[derive(Debug, serde::Deserialize)]
struct Keybinds {
    map: KeybindsMap,
    path_corner: KeybindsPathCorner,
}

#[derive(Debug, serde::Deserialize)]
struct KeybindsMap {
    compile: String,
    launch: String,
}

#[derive(Debug, serde::Deserialize)]
struct KeybindsPathCorner {
    iterate: String,
    close_loop: String,
}

fn main() {
    let config_path = Path::new("cfg/settings.toml");
    let config_file = std::fs::read_to_string(config_path).unwrap();
    let config: Settings = toml::from_str(&config_file).unwrap();

    let binds_path = Path::new("cfg/keybinds.toml");
    let binds_file = std::fs::read_to_string(binds_path).unwrap();
    let keybinds: Keybinds = toml::from_str(&binds_file).unwrap();

    let trenchbroom_exe = config
        .trenchbroom
        .join("trenchbroom.exe")
        .as_path()
        .to_owned();
    println!("{}", trenchbroom_exe.display());

    key::DKey.bind(move || open::that(&trenchbroom_exe).unwrap());
    // inputbot::from_keybd_key(k)

    inputbot::handle_input_events();

    // https://github.com/obv-mikhail/InputBot/blob/develop/src/public.rs#L704
    let mut ahk = HashMap::new();
    ahk.insert("!", key::LAltKey);
    ahk.insert("^", key::LControlKey);
    ahk.insert("#", key::LSuper);
    ahk.insert("+", key::LShiftKey);
}
