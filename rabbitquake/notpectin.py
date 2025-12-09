from app.parse import Brush, Entity


def check_entities(ent_list: list[Entity]):
    starts = [ent for ent in ent_list if ent.classname in ["info_player_start", "info_player_coop"]]
    for ent in ent_list:
        if ent.classname == "info_player_start":
            pass
