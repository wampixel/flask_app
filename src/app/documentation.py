from typing import Any

from spectree import SpecTree


def has_validated_input(operation: dict[str, Any]) -> bool:
    queried = any(parameter["in"] != "path" for parameter in operation.get("parameters", []))
    return queried or "requestBody" in operation


class ApiSpec(SpecTree):
    def _generate_spec(self) -> dict[str, Any]:
        spec = super()._generate_spec()
        for operations in spec["paths"].values():
            for operation in operations.values():
                if not has_validated_input(operation):
                    operation["responses"].pop(str(self.validation_error_status), None)
        return spec
