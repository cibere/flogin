from __future__ import annotations

from typing import Any, Generic, TypeVar

from ..enums import SettingTemplateInputType

DefaultValueT = TypeVar("DefaultValueT")

__all__ = (
    "TextBlockField",
    "InputField",
    "TextareaField",
    "CheckboxField",
    "DropdownField",
)


class BaseField:
    type: SettingTemplateInputType

    def __init__(self, **attrs: Any) -> None:
        self.attrs = attrs

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "attributes": self.attrs,
        }


class _BaseFieldWithAttrs(BaseField, Generic[DefaultValueT]):
    def __init__(
        self,
        name: str,
        *,
        label: str,
        description: str | None = None,
        default_value: DefaultValueT | None = None,
    ) -> None:
        super().__init__(
            name=name, label=label, description=description, defaultValue=default_value
        )

    @property
    def description(self) -> str:
        return self.attrs["description"]

    @description.setter
    def description(self, value: str) -> None:
        self.attrs["description"] = value

    @property
    def label(self) -> str:
        return self.attrs["label"]

    @label.setter
    def label(self, value: str) -> None:
        self.attrs["label"] = value

    @property
    def name(self) -> str:
        return self.attrs["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.attrs["name"] = value

    @property
    def default_value(self) -> DefaultValueT:
        return self.attrs["defaultValue"]

    @default_value.setter
    def default_value(self, value: DefaultValueT) -> None:
        self.attrs["defaultValue"] = value


class TextBlockField(BaseField):
    type = SettingTemplateInputType.text_block

    def __init__(self, description: str) -> None:
        super().__init__(description=description)

    @property
    def description(self) -> str:
        return self.attrs["description"]

    @description.setter
    def description(self, value: str) -> None:
        self.attrs["description"] = value


class InputField(_BaseFieldWithAttrs[str]):
    type = SettingTemplateInputType.input


class TextareaField(_BaseFieldWithAttrs[str]):
    type = SettingTemplateInputType.textarea


class CheckboxField(_BaseFieldWithAttrs[bool]):
    type = SettingTemplateInputType.checkbox


class DropdownField(_BaseFieldWithAttrs[str]):
    type = SettingTemplateInputType.dropdown

    def __init__(
        self,
        name: str,
        *,
        label: str,
        options: list[str],
        description: str | None = None,
        default_value: str | None = None,
    ) -> None:
        BaseField.__init__(
            self,
            name=name,
            label=label,
            description=description,
            defaultValue=default_value,
            options=options,
        )

    @property
    def options(self) -> list[str]:
        return self.attrs["options"]

    @options.setter
    def options(self, value: list[str]) -> None:
        self.attrs["options"] = value
