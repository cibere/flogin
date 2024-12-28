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
        """
        Initialize a field with arbitrary attributes.
        
        Parameters:
            **attrs (Any): Keyword arguments representing the field's attributes. 
                           These attributes can be of any type and will be stored 
                           in the `attrs` dictionary for later use.
        """
        self.attrs = attrs

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the field instance to a dictionary representation.
        
        Returns:
            dict[str, Any]: A dictionary containing the field's type and attributes.
            - 'type': The string value of the field's type enum
            - 'attributes': A dictionary of the field's attributes
        """
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
        """
        Initialize a field with specific attributes for a settings template.
        
        Parameters:
            name (str): The unique identifier for the field.
            label (str): A human-readable label describing the field.
            description (str, optional): A detailed explanation of the field's purpose. Defaults to None.
            default_value (DefaultValueT, optional): The initial or default value for the field. Defaults to None.
        
        Raises:
            TypeError: If invalid types are provided for parameters.
        
        Notes:
            - Uses keyword-only arguments for label to enforce explicit naming
            - Calls parent class initializer with standardized attribute names
        """
        super().__init__(
            name=name, label=label, description=description, defaultValue=default_value
        )

    @property
    def description(self) -> str:
        """
        Get the description of the field.
        
        Returns:
            str: The description text stored in the field's attributes.
        
        Raises:
            KeyError: If no description is set in the field's attributes.
        """
        return self.attrs["description"]

    @description.setter
    def description(self, value: str) -> None:
        """
        Set the description for the field.
        
        Parameters:
            value (str): The description text to be associated with the field.
        
        Raises:
            TypeError: If the provided value is not a string.
        """
        self.attrs["description"] = value

    @property
    def label(self) -> str:
        """
        Get the label for the field.
        
        Returns:
            str: The label associated with the field, retrieved from the 'label' attribute in the attrs dictionary.
        """
        return self.attrs["label"]

    @label.setter
    def label(self, value: str) -> None:
        """
        Set the label for the field.
        
        Parameters:
            value (str): The label text to assign to the field.
        
        This method updates the 'label' attribute in the field's attributes dictionary.
        """
        self.attrs["label"] = value

    @property
    def name(self) -> str:
        """
        Get the name of the field.
        
        Returns:
            str: The name of the field as stored in the 'name' attribute of the attrs dictionary.
        """
        return self.attrs["name"]

    @name.setter
    def name(self, value: str) -> None:
        """
        Set the name attribute of the field.
        
        Parameters:
            value (str): The name to assign to the field.
        
        This method updates the 'name' key in the internal attributes dictionary.
        """
        self.attrs["name"] = value

    @property
    def default_value(self) -> DefaultValueT:
        """
        Get the default value for the field.
        
        Returns:
            DefaultValueT: The default value stored in the field's attributes dictionary under the key "defaultValue".
        
        Raises:
            KeyError: If no default value has been set in the attributes dictionary.
        """
        return self.attrs["defaultValue"]

    @default_value.setter
    def default_value(self, value: DefaultValueT) -> None:
        """
        Set the default value for the field.
        
        Parameters:
            value (DefaultValueT): The default value to be assigned to the field. 
                                    The type matches the generic type of the field.
        
        Side Effects:
            Updates the 'defaultValue' key in the field's attributes dictionary.
        """
        self.attrs["defaultValue"] = value


class TextBlockField(BaseField):
    type = SettingTemplateInputType.text_block

    def __init__(self, description: str) -> None:
        """
        Initialize a TextBlockField with a description.
        
        Parameters:
            description (str): A descriptive text for the text block field.
        """
        super().__init__(description=description)

    @property
    def description(self) -> str:
        """
        Get the description of the field.
        
        Returns:
            str: The description text stored in the field's attributes.
        
        Raises:
            KeyError: If no description is set in the field's attributes.
        """
        return self.attrs["description"]

    @description.setter
    def description(self, value: str) -> None:
        """
        Set the description for the field.
        
        Parameters:
            value (str): The description text to be associated with the field.
        
        Raises:
            TypeError: If the provided value is not a string.
        """
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
        """
        Initialize a DropdownField with specific configuration options.
        
        Parameters:
            name (str): Unique identifier for the dropdown field
            label (str): Human-readable label displayed for the field
            options (list[str]): List of selectable options for the dropdown
            description (str, optional): Additional explanatory text for the field. Defaults to None.
            default_value (str, optional): Pre-selected value from the options list. Defaults to None.
        
        Raises:
            ValueError: If default_value is provided but not in the options list
        """
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
        """
        Get the list of options for the dropdown field.
        
        Returns:
            list[str]: A list of available options for the dropdown field.
        """
        return self.attrs["options"]

    @options.setter
    def options(self, value: list[str]) -> None:
        """
        Set the list of options for the dropdown field.
        
        Parameters:
            value (list[str]): A list of string options to be displayed in the dropdown.
        
        Raises:
            TypeError: If the provided value is not a list of strings.
        """
        self.attrs["options"] = value
