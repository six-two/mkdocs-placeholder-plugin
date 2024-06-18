import base64

# Used for the :after work around, since it can not contain CSS variables defined on the main page
def pen_icon_inline_svg_url(color: str) -> str:
    # Source: https://pictogrammers.com/library/mdi/icon/pencil/
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z" /></svg>'
    svg_base64_str = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{svg_base64_str}"


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

.placeholder-value-any {
    cursor: pointer;
}

.inline-editor-icons  .placeholder-value-any,
.inline-editor-simple .placeholder-value-any {
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
}

.inline-editor-icons  .placeholder-value-any .inline-editor-icon-span,
.inline-editor-simple .placeholder-value-any .inline-editor-icon-span {
    margin: 0px 3px;
    vertical-align: text-top;
    fill: var(--inline-editor-color);
}

.placeholder-value-editable:focus {
    cursor: initial;
}

.inline-editor-icons .placeholder-value-editable:focus .inline-editor-icon-span,
.inline-editor-simple .placeholder-value-editable:focus .inline-editor-icon-span {
    display: none;
}

.inline-editor-icons .placeholder-value-editable:focus::after {
    /* Source: https://pictogrammers.com/library/mdi/icon/pencil/ */
    content: url("PEN_OK_URL");
    width: 1em;
    height: 1em;
    display: inline-block;
    vertical-align: text-top;
    margin-right: 2px;

}

.inline-editor-icons .placeholder-value-editable.validation-warn:focus::after {
    content: url("PEN_WARN_URL");
}

.inline-editor-icons .placeholder-value-editable.validation-error:focus::after {
    content: url("PEN_ERROR_URL");
}


/* https://itnext.io/finally-a-css-only-solution-to-hover-on-touchscreens-c498af39c31c */
@media(hover: hover) and (pointer: fine) {
    .inline-editor-simple .placeholder-value-any:hover,
    .inline-editor-icons .placeholder-value-any:hover {
        border-bottom: 2px solid;
    }

    .inline-editor-simple .placeholder-value-any:hover:not(:focus) .inline-editor-icon-span {
        display: inline-block;
    }
}

.inline-editor-simple .placeholder-value-any.value-empty::before {
    content: "  ";
    background-color: pink;
}

.inline-editor-icons .placeholder-value-any {
    border-bottom: 2px dotted;
    margin: 0px 3px;
    padding-left: 3px;
}

.inline-editor-simple .placeholder-value-any:focus,
.inline-editor-icons  .placeholder-value-any:focus {
    border: 2px solid;
}

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
""" \
    .replace("PEN_OK_URL", pen_icon_inline_svg_url("green")) \
    .replace("PEN_WARN_URL", pen_icon_inline_svg_url("orange")) \
    .replace("PEN_ERROR_URL", pen_icon_inline_svg_url("red")) \


DEBUG_STYLE = """
.placeholder-value {
    background-color: #aaa;
    padding: 3px;
    border-radius: 3px;
}
"""

def generate_generic_style_sheet(debug: bool) -> str:
    style = BASIC_STYLE
    if debug:
        style += DEBUG_STYLE
    
    return style
