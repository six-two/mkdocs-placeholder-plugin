BASIC_STYLE = """
/* For the licensing of inline icons (data URLs) see https://pictogrammers.com/docs/general/license/,
   They should be under the Apache License 2.0 */

:root {
    --inline-editor-color-default: green;
    --inline-editor-color-warning: orange;
    --inline-editor-color-error: red;
}

.placeholder-value-any {
    --inline-editor-color: var(--inline-editor-color-default);
}

.placeholder-value-editable.validation-error {
    --inline-editor-color: var(--inline-editor-color-error);
}

.placeholder-value-editable.validation-warn {
    --inline-editor-color: var(--inline-editor-color-warning);
}

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

/* prevent visual glitch for slow loading pages or with high replace_delay_millis */
.auto-input-table {
    display: none;
}

.placeholder-plugin-init-done .auto-input-table {
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
    color: var(--inline-editor-color);
    border-color: var(--inline-editor-color);
    font-style: italic;
    outline: none;
    word-wrap: break-word;
}

.placeholder-value-any .inline-editor-icon-span {
    display: none;
    width: 1em;
    height: 1em;
    margin: 0px 3px;
    vertical-align: text-top;
    fill: var(--inline-editor-color);
}

.placeholder-value-editable:focus {
    cursor: initial;
}

.inline-editor-icons .placeholder-value-editable:focus .inline-editor-icon-span,
.inline-editor-simple .placeholder-value-editable:focus .inline-editor-icon-span {
    display: none !important;
}

.placeholder-value-editable:focus::after {
    /* Source: https://pictogrammers.com/library/mdi/icon/pencil/ */
    content: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iZ3JlZW4iPjxwYXRoIGQ9Ik0yMC43MSw3LjA0QzIxLjEsNi42NSAyMS4xLDYgMjAuNzEsNS42M0wxOC4zNywzLjI5QzE4LDIuOSAxNy4zNSwyLjkgMTYuOTYsMy4yOUwxNS4xMiw1LjEyTDE4Ljg3LDguODdNMywxNy4yNVYyMUg2Ljc1TDE3LjgxLDkuOTNMMTQuMDYsNi4xOEwzLDE3LjI1WiIgLz48L3N2Zz4=");
    width: 0em;
    height: 1em;
    display: inline-block;
}

.placeholder-value-any:hover,
.inline-editor-icons .placeholder-value-any:hover {
    border-bottom: 2px solid;
}

.inline-editor-simple .placeholder-value-any.value-empty::before {
    content: "  ";
    background-color: pink;
}

.inline-editor-icons .placeholder-value-any {
    border-bottom: 2px dotted;
    margin: 0px 3px;
    padding: 0px 3px;
}

.inline-editor-simple .placeholder-value-any:focus,
.inline-editor-icons  .placeholder-value-any:focus {
    border: 2px solid;
}

.inline-editor-simple .placeholder-value-any:focus .inline-editor-icon-span,
.inline-editor-simple .placeholder-value-any:hover .inline-editor-icon-span,
.inline-editor-icons  .placeholder-value-any .inline-editor-icon-span {
    display: inline-block;
}

.placeholder-value-editable.value-modified {
    font-weight: bold;
}

.placeholder-value-checkbox.unchecked .checkbox-checked {
    display: none;
}

.placeholder-value-checkbox.checked .checkbox-unchecked {
    display: none;
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
