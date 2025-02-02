# pyright: basic
# temp fix for
# https://github.com/sphinx-doc/sphinx/issues/10568

from typing import TypeVar


def get_generic_params(obj: type):
    typevars: list[TypeVar] = getattr(obj, "__parameters__", [])
    return [var.__name__ for var in typevars]


def process_signature(app, what, name, obj, options, signature, return_annotation):
    if what == "class":
        params = get_generic_params(obj)
        if params:
            print(f"Adding generics for {name!r}: {params!r}")
            signature = ", ".join([f"[{param}]" for param in params]) + (
                signature or ""
            )
    return signature, return_annotation


def setup(app):
    app.connect("autodoc-process-signature", process_signature)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
