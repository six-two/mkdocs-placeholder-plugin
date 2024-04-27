# Prevent long descriptions from messing up the table too badly
# Make the input elements take up the whole row
BASIC_STYLE = """
.placeholder-value.placeholder-value-highlighted {
    background-color: lightcyan;
}

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

.auto-input-table {
    display: flex;
    flex-direction: column;
    border: 3px solid gray;
    border-radius: 4px;
}

.auto-input-table .auto-table-title {
    display: flex;
    text-align: center;
    color: white;
    background-color: gray;
}

.auto-input-table .expandable_contents,
.auto-input-table .settings_contents, .placeholder-settings-panel {
    display: flex;
    flex-direction: column;
}

.auto-input-table .settings_contents {
    border-bottom: 3px solid gray;
    padding: 5px;
    margin-bottom: 5px;
}

.auto-input-table .settings_contents b {
    text-align: center;
}

.auto-input-table .settings_button, .placeholder-settings-panel .settings_button {
    display: flex;
    align-items: center;
}

.auto-input-table .settings_button svg, .placeholder-settings-panel .settings_button svg {
    width: 1.1em;
    height: 1.1em;
    cursor: pointer;
    margin: 0 auto;
    display: block;
}

/* Hide empty auto input tables' borders & co if JS is disabled (not working in Firefox) */
.auto-input-table:has(noscript:empty) {
    display: none;
}

.auto-input-table .button-bar, .placeholder-settings-panel .button-bar {
    margin-top: 10px;
    display: flex;
}

.auto-input-table button, .placeholder-settings-panel button {
    padding: 4px;
    border-radius: 5px;
    background-color: gray;
    color: white;
    max-width: 250px;
    margin: auto;
}

.auto-input-table .table-div {
    display: flex;
	flex-direction: column;
}

.auto-input-table .table-div b {
    margin: 3px auto 10px auto;
    padding: 0px 5px;
}

.auto-input-table .auto-table-title .text {
    flex: 1;
    margin-right: 20px;
    cursor: pointer;
}

.auto-input-table .md-typeset__scrollwrap,
.auto-input-table .md-typeset__table {
    margin-top: 0px;
    margin-bottom: 0px;
}

.auto-input-table table {
    width: 100%;
}

.input-for-variable.value-modified {
    font-weight: bold;
}

/* Highlight inline editable entries in the page */
.placeholder-value-any {
    cursor: pointer;
    color: blue;
    font-style: italic;
}

.placeholder-value-editable:focus {
    cursor: initial;
}

.placeholder-value-any:hover,
.placeholder-value-any:focus {
    border: 2px solid blue;
    padding: 0px 2px;
}

.placeholder-value-any::after {
    display: none;
    margin: 0px 3px;
    font-style: normal;
}

.placeholder-value-editable::after {
    content: "🖊";
}

.placeholder-value-checkbox.checked::after {
    content: "☑";
}

.placeholder-value-checkbox.unchecked::after {
    content: "☐";
}

.placeholder-value-dropdown::after {
    content: "↓";
}

.inline-editor-simple .placeholder-value-any:empty::before {
    content: "  ";
    background-color: pink;
}

.inline-editor-icons .placeholder-value-any {
    background-color: lightblue;
    border-radius: 3px;
    margin: 0px 3px;
    padding: 0px 3px;
}

.inline-editor-icons .placeholder-value-any:focus,
.inline-editor-icons .placeholder-value-any:hover {
    background-color: transparent;
}

.inline-editor-simple .placeholder-value-any:focus::after,
.inline-editor-simple .placeholder-value-any:hover::after,
.inline-editor-icons  .placeholder-value-any::after {
    display: inline-block;
}

.placeholder-value-editable.validation-error {
    color: red;
}

.placeholder-value-editable.validation-warn {
    color: orange;
}

.placeholder-value-editable.value-modified {
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

def generate_generic_style_sheet(debug: bool, inline_editor_icons: bool) -> str:
    style = BASIC_STYLE
    if debug:
        style += DEBUG_STYLE
    
    return style
