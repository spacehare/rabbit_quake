from dataclasses import dataclass

from src.app.parse import Entity


@dataclass(kw_only=True)
class DependencyData:
    name: str
    destination: str
    str_eval: str = ""
    str_exec: str = ""

    @staticmethod
    def from_dict(d: dict) -> "DependencyData":
        return DependencyData(
            name=d.get("name", "unnamed pattern"),
            destination=d["destination"],
            str_eval=d.get("eval", ""),
            str_exec=d.get("exec", ""),
        )

    def get_dependencies(self, entity: Entity) -> list[str] | None:
        assert not (self.str_eval and self.str_exec)

        context = {"entity": entity}
        output = None

        if self.str_eval:
            output = eval(self.str_eval, context)
        elif self.str_exec:
            namespace = {}
            exec(self.str_exec, context, namespace)
            output = namespace.get("output")

        if isinstance(output, str):
            output = [output]

        return output
