from . import warning

# Prevent long descriptions from messing up the table too badly
# Make the input elements take up the whole row
BASIC_STYLE = """
select.placeholder-dropdown {
    max-width: min(30vw, 200px);
}

input.input-for-variable.validation-error {
    background-color: #fc4462;
    color: black;
}

input.input-for-variable.validation-warn {
    background-color: #f7dd67;
    color: black;
}

table tr td button.placeholder-input-apply-button,
table tr td input.input-for-variable,
table tr td select.placeholder-dropdown {
    min-width: max(200px, 100%);
}

table tr td input.input-for-variable[type="checkbox"] {
    min-width: initial;
}

.auto-input-table .info-message {
    background-color: lightgray;
    color: black;
    border: 1px solid gray;
    border-radius: 4px;
    padding: 4px;
}
"""

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
"""

def generate_style_sheet(theme_name: str):
    if theme_name == "material":
        # MkDocs for Material screws up the look of imput elements (makes them look really bad)
        # So I implemented some rough fixes that should fit in with the users color choices
        return BASIC_STYLE + MATERIAL_STYLE
    elif theme_name in ["mkdocs", "readthedocs"]:
        # These themes have been tested (at some point in the past) and should work ok.
        # No specific tweaks were needed
        return BASIC_STYLE
    else:
        warning(f"Unknown theme: '{theme_name}'. Your may need to add custom CSS to make the placeholder inputs/tables look good.")
        return BASIC_STYLE

