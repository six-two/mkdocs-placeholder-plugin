import { logger } from "./debug";
import { Placeholder, PluginConfig } from "./parse_settings";


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

const dynamic_replace = (root_element: Element, search_regex: RegExp, placeholder: Placeholder) => {
    const walker = document.createTreeWalker(root_element, NodeFilter.SHOW_TEXT);
    let node;
    if (!search_regex.global) {
        console.warn(`You should set the global flag for the regex. Context: replacing '${search_regex.source}' with '${placeholder.current_value}'`);
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
    return nodes_to_modify.length;
}

const do_dynamic_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const count = dynamic_replace(root_element, placeholder.regex_dynamic, placeholder);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via dynamic method at least ${count} time(s)`);
        placeholder.count_on_page += count;
    }
}

const do_normal_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const count = dynamic_replace(root_element, placeholder.regex_normal, placeholder);
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
}


