# Python Import Conventions

## Rules

- Import pydantic as `pdt`: `import pydantic as pdt`
- Import typing as `tp`: `import typing as tp`
- Refer to subclasses with the alias: `class MyModel(pdt.BaseModel): ...`
- Use alias for all references: `tp.Union[...]`, `tp.List[...]`, `tp.Optional[...]`, `pdt.Field(...)`, `pdt.validator(...)`, ...
- Prefer single quotes over double quotes for strings
- Use black to format Python code
