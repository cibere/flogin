from .fields import (
    CheckboxField,
    DropdownField,
    InputField,
    TextareaField,
    TextBlockField,
)

FieldType = TextBlockField | TextareaField | DropdownField | CheckboxField | InputField
from io import BytesIO, TextIOWrapper
from typing import Any

__all__ = ("SettingsTemplate",)


class SettingsTemplate:
    def __init__(self) -> None:
        self.fields: list[FieldType] = []

    def add_field(self, field: FieldType) -> None:
        self.fields.append(field)

    def add_fields(self, *fields: FieldType) -> None:
        self.fields.extend(fields)

    def remove_field(self, field: FieldType) -> None:
        self.fields.remove(field)

    def remove_fields(self, *fields: FieldType) -> None:
        for field in fields:
            self.remove_field(field)

    def clear(self) -> None:
        self.fields.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"body": [field.to_dict() for field in self.fields]}

    def save_as(self, fp: str | BytesIO | TextIOWrapper) -> None:
        if isinstance(fp, str):
            with open(fp, "w") as f:
                return self.save_as(f)

        try:
            import yaml
        except ImportError:
            raise RuntimeError(
                "PyYAML is not installed. Run `pip install PyYAML` to install it, or install flogin[dev]"
            )

        yaml.dump(self.to_dict(), fp)

    def save(self) -> None:
        return self.save_as("SettingsTemplate.yaml")
