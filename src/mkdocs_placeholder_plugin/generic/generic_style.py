import base64

def svg_to_data_url(svg_html_code: str) -> str:
    svg_as_base64 = base64.b64encode(svg_html_code.encode()).decode()
    return f"data:image/svg+xml;base64,{svg_as_base64}"

def show_icon_for_placeholder_class(placeholder_css_selector: str, icon_svg_url: str) -> str:
    # should work but does not:
    # content: url("{SVG_URL}");

    return """
{CSS_SELECTOR}::after {
    content: url("{SVG_URL}");
    width: 1em;
}
""".replace("{SVG_URL}", icon_svg_url).replace("{CSS_SELECTOR}", placeholder_css_selector)

# Source: https://pictogrammers.com/library/mdi/icon/pencil/
PEN_SVG_URL = svg_to_data_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>pencil</title><path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z" /></svg>')

# Source: https://pictogrammers.com/library/mdi/icon/checkbox-outline/
CHECKED_SVG_URL = svg_to_data_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>checkbox-outline</title><path d="M19,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M19,5V19H5V5H19M10,17L6,13L7.41,11.58L10,14.17L16.59,7.58L18,9" /></svg>')

# Source: https://pictogrammers.com/library/mdi/icon/checkbox-blank-outline/
UNCHECKED_SVG_URL = svg_to_data_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>checkbox-blank-outline</title><path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19Z" /></svg>')

# Source: https://pictogrammers.com/library/mdi/icon/swap-horizontal/
SWAP_SVG_URL = svg_to_data_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>swap-horizontal</title><path d="M21,9L17,5V8H10V10H17V13M7,11L3,15L7,19V16H14V14H7V11Z" /></svg>')


BASIC_STYLE = """
/* For the licensing of inline icons (data URLs) see https://pictogrammers.com/docs/general/license/,
   They should be under the Apache License 2.0 */

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
    color: blue;
    font-style: italic;
}

.placeholder-value-editable:focus {
    cursor: initial;
}

.placeholder-value-any:hover {
    border-bottom: 2px solid blue;
}

.placeholder-value-any::after {
    display: none;
    margin: 0px 3px;
    font-style: normal;
}

.inline-editor-simple .placeholder-value-any:empty::before {
    content: "  ";
    background-color: pink;
}

.inline-editor-icons .placeholder-value-any {
    border-bottom: 2px dotted blue;
    margin: 0px 3px;
    padding: 0px 3px;
}

.inline-editor-icons .placeholder-value-any:hover {
    border-bottom: 2px solid blue;
}

.inline-editor-simple .placeholder-value-any:focus,
.inline-editor-icons  .placeholder-value-any:focus {
    border: 2px solid blue;
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
""" \
    + show_icon_for_placeholder_class(".placeholder-value-editable", PEN_SVG_URL) \
    + show_icon_for_placeholder_class(".placeholder-value-checkbox.checked", CHECKED_SVG_URL) \
    + show_icon_for_placeholder_class(".placeholder-value-checkbox.unchecked", UNCHECKED_SVG_URL) \
    + show_icon_for_placeholder_class(".placeholder-value-dropdown", SWAP_SVG_URL)

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
