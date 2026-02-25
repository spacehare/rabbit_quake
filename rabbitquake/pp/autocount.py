from enum import Enum

from rabbitquake.app.parse import Brush, Entity

SYMBOL_COUNT = "#"


class EntitySkillflags(Enum):
    NOT_ON_EASY = 256  # '0b00100000000'
    NOT_ON_NORMAL = 512  # '0b01000000000'
    NOT_ON_HARD = 1024  # '0b10000000000'


def autocount(trigger_counter: Entity, entities: list[Entity]) -> list[Entity] | None:
    if not ((count_value := trigger_counter.kv.get("count")) and count_value.startswith(SYMBOL_COUNT)):
        return

    totals: list[int] = [0] * 3

    # check who is targeting the trigger_counter
    for entity in [e for e in entities if e is not trigger_counter]:
        monster_count: int = 1

        # respawning monsters, like in copper
        if entity.classname.startswith("monster"):
            if respawn_count := entity.kv.get("count"):
                monster_count = int(respawn_count)

        # skill flags
        if possible_spawnflags := entity.kv.get("spawnflags"):
            spawnflags: int = int(possible_spawnflags)

            is_easy = not (EntitySkillflags.NOT_ON_EASY.value & spawnflags)
            is_normal = not (EntitySkillflags.NOT_ON_NORMAL.value & spawnflags)
            is_hard = not (EntitySkillflags.NOT_ON_HARD.value & spawnflags)

            monster_skill_bools = (is_easy, is_normal, is_hard)
        else:
            monster_skill_bools = (True, True, True)

        # handle target1, target2, target4, target4, etc
        for key in [k for k in entity.kv if k.startswith("target")]:
            if entity.kv[key] == trigger_counter.kv["targetname"]:
                for idx, skill_bool in enumerate(monster_skill_bools):
                    if skill_bool:
                        totals[idx] += monster_count
