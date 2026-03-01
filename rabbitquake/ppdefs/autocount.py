import copy
from enum import Enum

from rabbitquake.app.parse import Entity

SYMBOL_COUNT = "#"


class Skillsflags(Enum):
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

            is_easy = not (Skillsflags.NOT_ON_EASY.value & spawnflags)
            is_normal = not (Skillsflags.NOT_ON_NORMAL.value & spawnflags)
            is_hard = not (Skillsflags.NOT_ON_HARD.value & spawnflags)

            monster_skill_bools = (is_easy, is_normal, is_hard)
        else:
            monster_skill_bools = (True, True, True)

        # handle target1, target2, target4, target4, etc
        for key in [k for k in entity.kv if k.startswith("target")]:
            if entity.kv[key] == trigger_counter.kv["targetname"]:
                for idx, skill_bool in enumerate(monster_skill_bools):
                    if skill_bool:
                        totals[idx] += monster_count

    # create new trigger_counter copies, per-skill
    clones = []
    for idx, skill_flag in enumerate(Skillsflags):
        if totals[idx] == 0:
            continue

        # set count
        clone: Entity = copy.deepcopy(trigger_counter)
        clone.kv["count"] = str(totals[idx])

        # unset "NOT ON <SKILL>" for the one we want
        clone_spawnflags = int(clone.kv.get("spawnflags", 0)) & ~skill_flag.value
        # set "NOT ON <SKILL>" for the ones we don't
        for skill in [flag for flag in Skillsflags if flag is not skill_flag]:
            clone_spawnflags |= skill.value

        clone.kv["spawnflags"] = str(clone_spawnflags)

        clones.append(clone)

    return clones
