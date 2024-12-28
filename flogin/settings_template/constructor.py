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
        """
        Initialize a new SettingsTemplate instance with an empty list of fields.
        
        This method creates a new SettingsTemplate object and prepares it to store various field types
        such as TextBlockField, TextareaField, DropdownField, CheckboxField, and InputField.
        
        Attributes:
            fields (list[FieldType]): An empty list that will store field instances for the settings template.
        """
        self.fields: list[FieldType] = []

    def add_field(self, field: FieldType) -> None:
        """
        Add a single field to the settings template.
        
        Parameters:
            field (FieldType): A field object to be added to the template. 
                               Can be one of TextBlockField, TextareaField, 
                               DropdownField, CheckboxField, or InputField.
        
        Raises:
            TypeError: If the provided field is not a valid FieldType.
        """
        self.fields.append(field)

    def add_fields(self, *fields: FieldType) -> None:
        """
        Add multiple fields to the settings template.
        
        Parameters:
            fields (FieldType): Variable number of field objects to be added to the template.
        
        Description:
            Extends the internal `fields` list with the provided field objects. 
            Allows adding multiple fields in a single method call.
        
        Example:
            template = SettingsTemplate()
            text_field = InputField(...)
            checkbox_field = CheckboxField(...)
            template.add_fields(text_field, checkbox_field)
        """
        self.fields.extend(fields)

    def remove_field(self, field: FieldType) -> None:
        """
        Remove a specific field from the settings template.
        
        Parameters:
            field (FieldType): The field to be removed from the template's list of fields.
        
        Raises:
            ValueError: If the specified field is not found in the list of fields.
        """
        self.fields.remove(field)

    def remove_fields(self, *fields: FieldType) -> None:
        """
        Remove multiple fields from the settings template.
        
        Parameters:
            *fields (FieldType): Variable number of fields to be removed from the template.
        
        Raises:
            ValueError: If any of the specified fields are not present in the template.
        """
        for field in fields:
            self.remove_field(field)

    def clear(self) -> None:
        """
        Clear all fields from the settings template.
        
        This method removes all fields from the internal `fields` list, effectively resetting the settings template to an empty state.
        
        Returns:
            None
        """
        self.fields.clear()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the settings template fields to a dictionary representation.
        
        Returns:
            dict[str, Any]: A dictionary with a 'body' key containing a list of dictionaries, 
            where each dictionary represents a field's configuration.
        
        Example:
            template = SettingsTemplate()
            template.add_field(InputField('username'))
            result = template.to_dict()
            # result will be: {"body": [{'type': 'input', 'name': 'username', ...}]}
        """
        return {"body": [field.to_dict() for field in self.fields]}

    def save_as(self, fp: str | BytesIO | TextIOWrapper) -> None:
        """
        Save the settings template to a specified file or file-like object.
        
        This method supports saving to a file path (string) or directly to a file-like object (BytesIO or TextIOWrapper).
        If a file path is provided, it opens the file in write mode. The settings are serialized to YAML format.
        
        Parameters:
            fp (str | BytesIO | TextIOWrapper): The file path or file-like object to save the settings template.
                - If a string, it represents the file path where the settings will be saved.
                - If a file-like object, the settings will be directly dumped to it.
        
        Raises:
            RuntimeError: If PyYAML library is not installed. Provides instructions for installation.
            IOError: If there are issues opening or writing to the specified file path.
        
        Examples:
            # Save to a file path
            settings.save_as('my_settings.yaml')
        
            # Save to a file-like object
            with open('settings.yaml', 'w') as f:
                settings.save_as(f)
        """
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
        """
        Save the settings template to a default file named "SettingsTemplate.yaml".
        
        This method is a convenience wrapper around the `save_as` method, which saves the current
        settings template to a predefined file with a standard filename.
        
        Raises:
            RuntimeError: If the PyYAML library is not installed.
            IOError: If there are issues writing to the default file.
        """
        return self.save_as("SettingsTemplate.yaml")
