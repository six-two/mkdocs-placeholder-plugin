import { logger } from "./debug";
import { update_tooltip, validate_placeholder_value } from "./validator";
import { InputType, Placeholder, PluginConfig, TextboxPlaceholder } from "./parse_settings";


type Replacer = (root_element: Element, search_regex: RegExp, replacement_value: string) => number;

// Replace a specific placeholder and return the estimated number of occurences (underestimated, may actually be higher)
const static_replace: Replacer = (root_element, search_regex, replacement_value) => {
    const walker = document.createTreeWalker(root_element, NodeFilter.SHOW_TEXT);
    let node;
    let count = 0;
    if (!search_regex.global) {
        console.warn(`You should set the global flag for the regex. Context: replacing '${search_regex.source}' with '${replacement_value}'`);
    }
    while (node = walker.nextNode()) {
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

const inner_html_replace: Replacer = (root_element, search_regex, replacement_value) => {
    // User supplied input, HTML escape it before we inject it in the page
    replacement_value = escapeHTML(replacement_value);

    if (!search_regex.global) {
        console.warn(`You should set the global flag for the regex. Context: replacing '${search_regex.source}' with '${replacement_value}'`);
    }
    const new_value = root_element.innerHTML.replace(search_regex, replacement_value);
    if (new_value != root_element.innerHTML) {
        root_element.innerHTML = new_value;
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
    const walker = document.createTreeWalker(root_element, NodeFilter.SHOW_TEXT);
    let node;
    if (!search_regex.global) {
        console.warn(`You should set the global flag for the regex. Context: replacing '${search_regex.source}' with '${placeholder.current_value}'`);
    }

    let existing_count = 0;
    if (search_for_pre_replaced){
        const already_existing_wrappers = document.querySelectorAll(".placeholder-value[data-placeholder]");
        for (const wrapper of already_existing_wrappers) {
            if (wrapper.getAttribute("data-placeholder") === placeholder.name) {
                existing_count++;
            }
        }
        if (existing_count > 0) {
            logger.debug(`${existing_count} dynamic placeholder elements already exist for placeholder ${placeholder.name}`);
        }
    }

    const nodes_to_modify = [];
    while (node = walker.nextNode()) {
        if (node.nodeValue) {
            if (node.nodeValue.match(search_regex)) {
                // Do not modify in-place while iterating over the DOM
                nodes_to_modify.push(node);
            }
        }
    }
    
    // Do not put in the value yet, otherwise it may be replaced by other placeholders
    const replacement_value = `<span class="placeholder-value" data-placeholder="${escapeHTML(placeholder.name)}">TEMPORARY PLACEHOLDER</span>`;
    for (const node of nodes_to_modify) {
        if (node.nodeValue) {
            const replaced_str = escapeHTML(node.nodeValue).replace(search_regex, replacement_value);
            const new_node = document.createElement("span");
            new_node.innerHTML = replaced_str;
            node.parentElement?.replaceChild(new_node, node);
        }
    }
    return nodes_to_modify.length + existing_count;
}

const do_dynamic_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const count = dynamic_replace(root_element, placeholder.regex_dynamic, placeholder, true);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via dynamic method at least ${count} time(s)`);
        placeholder.count_on_page += count;
    }
}

const do_normal_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const count = dynamic_replace(root_element, placeholder.regex_normal, placeholder, false);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via normal (dynamic) method at least ${count} time(s)`);
        placeholder.count_on_page += count;
    }
}

const do_static_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const count = static_replace(root_element, placeholder.regex_static, placeholder.expanded_value);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via static method at least ${count} time(s)`);
        placeholder.count_on_page += count;
        placeholder.reload_page_on_change = true;
    }
}

const do_html_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
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
        do_dynamic_replace(root_element, placeholder, config);
        do_normal_replace(root_element, placeholder, config);
        do_static_replace(root_element, placeholder, config);

        if (placeholder.allow_inner_html) {
            do_html_replace(root_element, placeholder, config);
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
        .replace(placeholder.regex_html, value)
        .replace(placeholder.regex_normal, value)
        .replace(placeholder.regex_static, value);
}

export const replace_dynamic_placeholder_values = (placeholder_list: Placeholder[]) => {
    for (const placeholder of placeholder_list) {
        if (placeholder.output_elements.length > 0) {
            for (const element of placeholder.output_elements) {
                element.textContent = placeholder.expanded_value;
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
            }
        }
    }
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


