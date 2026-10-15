from dataclasses import dataclass
import re


def identifier(value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]{0,99}", value):
        raise ValueError(f"Invalid SQL identifier: {value!r}")
    return f"`{value}`"


def token(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise ValueError("Run/batch identifiers must be 1–100 ASCII letters, numbers, _ or -")
    return value


@dataclass(frozen=True)
class Config:
    catalog: str
    prefix: str = "retailflow"
    max_reject_fraction: float = 1.0

    def __post_init__(self):
        identifier(self.catalog)
        if not re.fullmatch(r"retailflow(?:_[a-z0-9]+)?", self.prefix):
            raise ValueError("Schema prefix must be retailflow or retailflow_<alphanumeric>")
        if not 0 <= self.max_reject_fraction <= 1:
            raise ValueError("Reject threshold must be between zero and one")

    def schema(self, layer):
        if layer not in ("bronze", "silver", "gold", "ops"):
            raise ValueError("Unknown layer")
        return f"{identifier(self.catalog)}.{identifier(self.prefix + '_' + layer)}"

    def table(self, layer, name):
        return f"{self.schema(layer)}.{identifier(name)}"

    @property
    def volume(self):
        return f"/Volumes/{self.catalog}/{self.prefix}_bronze/fixtures"
