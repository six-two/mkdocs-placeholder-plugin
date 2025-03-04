import { logger } from "./debug";
import { update_tooltip, validate_placeholder_value } from "./validator";
import { CheckboxPlaceholder, InputType, Placeholder, PluginConfig, TextboxPlaceholder } from "./parse_settings";
import { update_inline_checkbox_editor_classes } from "./inline-editors/checkbox";


// Replace a specific placeholder and return the estimated number of occurences (underestimated, may actually be higher)
const static_replace = (root_element: Element, search_regex: RegExp, replacement_value: string) => {
    const walker = document.createTreeWalker(root_element, NodeFilter.SHOW_TEXT);
    let node;
    let count = 0;
    if (!search_regex.global) {
        console.warn(`You should set the global flag for the regex. Context: replacing '${search_regex.source}' with '${replacement_value}'`);
    }
    while ((node = walker.nextNode())) {
        if (node.nodeValue) {
            const replaced_str = node.nodeValue.replace(search_regex, replacement_value);
            if (node.nodeValue != replaced_str) {
                node.nodeValue = replaced_str;
                count++; // Of course, it might have been replaced multiple times by replaceAll. But this is just for debugging
                // and performing an accurate count would impact the performace.
            }
        }
    }
    return count;
};

const escapeHTML = (text: string): string => {
    const element = document.createElement("div");
    element.appendChild(document.createTextNode(text));
    return element.innerHTML;
}

const inner_html_replace = (root_element: Element, search_regex: RegExp, replacement_value: string) => {
    if (!search_regex.global) {
        console.warn(`You should set the global flag for the regex. Context: replacing '${search_regex.source}' with '${replacement_value}'`);
    }
    const new_value = root_element.innerHTML.replace(search_regex, replacement_value);
    // Only process this node if it or its children contain the placeholder
    if (new_value != root_element.innerHTML) {
        // First update/check all children (recursively)
        for (const child of root_element.childNodes) {
            if (child.nodeType == Node.ELEMENT_NODE) {
                let element = child as Element;
                inner_html_replace(element, search_regex, replacement_value)
            } else {
                if (child.nodeValue) {
                    child.nodeValue = child.nodeValue.replace(search_regex, replacement_value);
                }
            }
        }

        // If the element still contains the placeholder, then we need to replace it entirely
        const new_value_after_updating_children = root_element.innerHTML.replace(search_regex, replacement_value);
        if (new_value_after_updating_children != root_element.innerHTML) {
            root_element.innerHTML = new_value;
        }

        return 1;
    } else {
        return 0;
    }
};

export const create_dynamic_placeholder_element = (placeholder: Placeholder): HTMLSpanElement => {
    const span = document.createElement("span");
    span.classList.add("placeholder-value");
    span.dataset.placeholder = placeholder.name;
    span.textContent = placeholder.expanded_value;
    return span;
}

const dynamic_replace = (root_element: Element, search_regex: RegExp, placeholder: Placeholder, search_for_pre_replaced: boolean) => {
    return inner_dynamic_or_editable_replace(root_element, search_regex, placeholder, search_for_pre_replaced, "placeholder-value-static");
}

const editable_replace = (root_element: Element, search_regex: RegExp, placeholder: Placeholder, search_for_pre_replaced: boolean) => {
    return inner_dynamic_or_editable_replace(root_element, search_regex, placeholder, search_for_pre_replaced, "inline-editor-requested");
}

const inner_dynamic_or_editable_replace = (root_element: Element, search_regex: RegExp, placeholder: Placeholder, search_for_pre_replaced: boolean, extra_class: string | null) => {
    const walker = document.createTreeWalker(root_element, NodeFilter.SHOW_TEXT);
    let node;
    if (!search_regex.global) {
        console.warn(`You should set the global flag for the regex. Context: replacing '${search_regex.source}' with '${placeholder.current_value}'`);
    }

    let existing_count = 0;
    if (search_for_pre_replaced){
        const extra_class_query = extra_class ? `.${extra_class}` : "";
        const already_existing_wrappers = document.querySelectorAll(`${extra_class_query}.placeholder-value[data-placeholder]`);
        for (const wrapper of already_existing_wrappers) {
            if (wrapper.getAttribute("data-placeholder") === placeholder.name) {
                existing_count++;
            }

        }
        if (existing_count > 0) {
            const query_type = extra_class ? "editable" : "dynamic";
            logger.debug(`${existing_count} ${query_type} placeholder elements already exist for placeholder ${placeholder.name}`);
        }
    }

    const nodes_to_modify = [];
    while ((node = walker.nextNode())) {
        if (node.nodeValue) {
            if (node.nodeValue.match(search_regex)) {
                // Do not modify in-place while iterating over the DOM
                nodes_to_modify.push(node);
            }
        }
    }
    
    if (nodes_to_modify) {
        // Do not put in the value yet, otherwise it may be replaced by other placeholders
        const extra_class_insert = extra_class ? ` ${extra_class}` : "";
        const replacement_value = `<span class="placeholder-value${extra_class_insert}" data-placeholder="${escapeHTML(placeholder.name)}">TEMPORARY PLACEHOLDER</span>`;
        for (const node of nodes_to_modify) {
            if (node.nodeValue) {
                const replaced_str = escapeHTML(node.nodeValue).replace(search_regex, replacement_value);
                const new_node = document.createElement("span");
                new_node.innerHTML = replaced_str;
                node.parentElement?.replaceChild(new_node, node);
            }
        }
    }
    return nodes_to_modify.length + existing_count;
}

const do_dynamic_replace = (root_element: Element, placeholder: Placeholder): void => {
    const count = dynamic_replace(root_element, placeholder.regex_dynamic, placeholder, true);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via dynamic method at least ${count} time(s)`);
        placeholder.count_on_page += count;
    }
}

const do_editable_replace = (root_element: Element, placeholder: Placeholder): void => {
    const count = editable_replace(root_element, placeholder.regex_editable, placeholder, true);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via editable method at least ${count} time(s)`);
        placeholder.count_on_page += count;
    }
}


const do_normal_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const count = inner_do_normal_replace(root_element, placeholder, config);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via normal (${config.settings.normal_is_alias_for}) method at least ${count} time(s)`);
        placeholder.count_on_page += count;
    }
}

const inner_do_normal_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): number => {
    // Replace with the actual method that normal maps to and return the count
    switch (config.settings.normal_is_alias_for) {
        case "dynamic":
            return dynamic_replace(root_element, placeholder.regex_normal, placeholder, false);
        case "editable":
            return editable_replace(root_element, placeholder.regex_normal, placeholder, false);
        case "html":
            // User supplied input, HTML escape it before we inject it in the page
            const replacement_value = escapeHTML(placeholder.expanded_value)
            return inner_html_replace(root_element, placeholder.regex_html, replacement_value);
        case "static":
            return static_replace(root_element, placeholder.regex_static, placeholder.expanded_value);
        default:
            console.warn(`Unknown replace type mapped in 'settings.normal_is_alias_for': ${config.settings.normal_is_alias_for}. Skipping replacing normal placeholders`);
            return 0;
    }
}


const do_static_replace = (root_element: Element, placeholder: Placeholder): void => {
    const count = static_replace(root_element, placeholder.regex_static, placeholder.expanded_value);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via static method at least ${count} time(s)`);
        placeholder.count_on_page += count;
        placeholder.reload_page_on_change = true;
    }
}

const do_html_replace = (root_element: Element, placeholder: Placeholder): void => {
    const count = inner_html_replace(root_element, placeholder.regex_html, placeholder.expanded_value);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via innerHTML method at least ${count} time(s)`);
        placeholder.count_on_page += count;
        placeholder.reload_page_on_change = true;
    }
}


// Replace all placeholders in the given order and return which placeholders actually were actually found in the page
export const replace_placeholders_in_subtree = (root_element: Element, config: PluginConfig): void => {
    for (const placeholder of config.placeholders.values()) {
        do_dynamic_replace(root_element, placeholder);
        do_editable_replace(root_element, placeholder);
        do_normal_replace(root_element, placeholder, config);
        do_static_replace(root_element, placeholder);

        if (placeholder.allow_inner_html) {
            do_html_replace(root_element, placeholder);
        }
    }

    find_dynamic_placeholder_wrappers(config);
    replace_dynamic_placeholder_values([...config.placeholders.values()]);
}

export const safe_replace_multiple_placeholders_in_string = (text: string, placeholder_list: Placeholder[]): string => {
    // Optimize for trivial cases
    if (placeholder_list.length == 0) {
        return text;
    } else if (placeholder_list.length == 1) {
        // We can directly replace it without any problems
        const placeholder = placeholder_list[0];
        return replace_placeholder_in_string_with(text, placeholder, placeholder.expanded_value);
    } else {
        // If we just replace the values directly in a for loop, we get bugs, when the value of one placeholder contains another placeholder that is also replaced, but later
        // To circumvent this, we replace placeholders with randomized other placeholders and then replace these with the actual values
        const unique = `${Date.now()}_${Math.random()}`;
        for (const placeholder of placeholder_list) {
            text = replace_placeholder_in_string_with(text, placeholder, `x${placeholder.name}#${unique}x`);
        }
        for (const placeholder of placeholder_list) {
            const regex = new RegExp(`x${placeholder.name}#${unique}x`, "g");
            text = text.replace(regex, placeholder.expanded_value);
        }
        return text;
    }
}

const replace_placeholder_in_string_with = (text: string, placeholder: Placeholder, value: string): string => {
    // This funtion will perform replacements, but will ignore the replacement type (all will be simple/direct replace)
    return text.replace(placeholder.regex_dynamic, value)
        .replace(placeholder.regex_editable, value)
        .replace(placeholder.regex_html, value)
        .replace(placeholder.regex_normal, value)
        .replace(placeholder.regex_static, value);
}

export const replace_dynamic_placeholder_values = (placeholder_list: Placeholder[]) => {
    for (const placeholder of placeholder_list) {
        if (placeholder.output_elements.length > 0) {
            for (const element of placeholder.output_elements) {
                change_text_keep_other_children(element, placeholder.expanded_value);
            }
            if (placeholder.type == InputType.Textbox) {
                // could have inline editor, and we need to correctly set their validation states.
                // Perform validation only once and reuse it for all elements
                //@TODO: Check current_value or expanded_value?
                const result = validate_placeholder_value(placeholder as TextboxPlaceholder, placeholder.expanded_value);

                for (const element of placeholder.output_elements) {
                    if (element.classList.contains("placeholder-value-editable")) {
                        // This element is an inline editor
                        update_tooltip(element, result);
                    }
                }
            } else if (placeholder.type == InputType.Checkbox) {
                for (const element of placeholder.output_elements) {
                    if (element.classList.contains("placeholder-value-checkbox")) {
                        // This element is an inline editor
                        update_inline_checkbox_editor_classes(element, placeholder as CheckboxPlaceholder);
                    }
                }
            }
        }
    }
}

export const change_text_keep_other_children = (element: HTMLElement, new_text: string) => {
    if (new_text) {
        element.classList.remove("value-empty");
    } else {
        element.classList.add("value-empty");
    }

    // If it exists, replace the first text node
    for (const child of element.childNodes) {
        if (child.nodeType === Node.TEXT_NODE) {
            child.textContent = new_text;
            return
        }
    }

    // If no text node exists, add a text node to the beginning
    element.insertAdjacentText("afterbegin", new_text);
}

const find_dynamic_placeholder_wrappers = (config: PluginConfig) => {
    const output_list: NodeListOf<HTMLElement> = document.querySelectorAll(".placeholder-value[data-placeholder]");
    for (const element of output_list) {
        const placeholder_name = element.getAttribute("data-placeholder");
        if (placeholder_name) {
            const placeholder = config.placeholders.get(placeholder_name);
            if (placeholder) {
                placeholder.output_elements.push(element);
            } else {
                console.warn(`No placeholder named '${placeholder_name}', that is referenced by element:`, element);
            }
        } else {
            console.warn(`Element has empty/no attribute 'data-placeholder':`, element);
        }
    }
}


