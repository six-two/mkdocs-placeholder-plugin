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
    min-width: min(30vw, 200px);
    max-width: initial;
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

.input-for-variable.value-modified {
    font-weight: bold;
}
"""


DEBUG_STYLE = """
.placeholder-value {
    background-color: #aaa;
    padding: 3px;
    border-radius: 3px;
}
"""

def generate_generic_style_sheet(debug: bool) -> str:
    if debug:
        return BASIC_STYLE + DEBUG_STYLE
    else:
        return BASIC_STYLE
