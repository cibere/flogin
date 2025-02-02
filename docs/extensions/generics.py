# pyright: basic
# temp fix for
# https://github.com/sphinx-doc/sphinx/issues/10568

generics: dict[str, tuple[str]] = {"flogin.plugin.Plugin": ("SettingsT",)}


def process_signature(app, what, name, obj, options, signature, return_annotation):
    if what == "class":
        params = generics.get(name)
        if params:
            signature = ", ".join([f"[{param}]" for param in params]) + (
                signature or ""
            )
        print(f"{name=}")
    return signature, return_annotation


def setup(app):
    app.connect("autodoc-process-signature", process_signature)
