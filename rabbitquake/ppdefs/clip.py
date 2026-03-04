import copy

from rabbitquake.app.parse import Brush, Entity


def clip(ent: Entity) -> list[Brush]:
    output_brushes: list[Brush] = []
    for brush in ent.brushes:
        clone = copy.deepcopy(brush)
        for plane in clone.planes:
            plane.texture_name = "clip"
        output_brushes.append(clone)
    return output_brushes
