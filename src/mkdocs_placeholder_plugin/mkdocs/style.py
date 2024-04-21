from ..generic import warning
from ..generic.generic_style import generate_generic_style_sheet


# MkDocs Material specific code
MATERIAL_STYLE = """
.input-for-variable {
    border: 2px solid gray;
    border-radius: 3px;
    background-color: var(--md-default-bg-color);
    padding: 5px;
}

.input-for-variable:focus {
    border: 4px solid var(--md-primary-fg-color);
    padding: 3px;
}

.auto-input-table {
    width: fit-content;
}
"""
# If someone can figure out, why the material theme makes table rows not expand, even if I set the table width to 100%, please tell me.
# I cannot figure it out. As a workaround, to not make it look insanely bad, I have to shrink the table's parent.


def generate_mkdocs_style_sheet(theme_name: str, debug: bool, inline_editor_icons: bool):
    generic_style = generate_generic_style_sheet(debug, inline_editor_icons)
    
    if theme_name == "material":
        # MkDocs for Material screws up the look of imput elements (makes them look really bad)
        # So I implemented some rough fixes that should fit in with the users color choices
        return generic_style + MATERIAL_STYLE
    elif theme_name in ["mkdocs", "readthedocs"]:
        # These themes have been tested (at some point in the past) and should work ok.
        # No specific tweaks were needed
        return generic_style
    else:
        warning(f"Unknown theme: '{theme_name}'. Your may need to add custom CSS to make the placeholder inputs/tables look good.")
        return generic_style
