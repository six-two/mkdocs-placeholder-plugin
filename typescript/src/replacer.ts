import { logger } from "./debug";
import { Placeholder, PluginConfig } from "./parse_settings";


type Replacer = (root_element: Element, search_regex: RegExp, replacement_value: string) => number;

// Replace a specific placeholder and return the estimated number of occurences (underestimated, may actually be higher)
const direct_replace: Replacer = (root_element, search_regex, replacement_value) => {
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

const dynamic_replace: Replacer = (root_element, search_regex, replacement_value) => {
    console.warn("@TODO Dynamic replacement not implemented yet");
    return 0;
}

const do_normal_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const prefix = config.settings.normal_prefix;
    const suffix = config.settings.normal_suffix;
    const regex = RegExp(prefix + placeholder.name + suffix, "g");
    const count = direct_replace(root_element, regex, placeholder.current_value);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via direct method at least ${count} time(s)`);
        placeholder.count_on_page += count;
        placeholder.reload_page_on_change = true;
    }
}

const do_html_replace = (root_element: Element, placeholder: Placeholder, config: PluginConfig): void => {
    const prefix = config.settings.html_prefix;
    const suffix = config.settings.html_suffix;
    const regex = RegExp(prefix + placeholder.name + suffix, "g");
    const count = inner_html_replace(root_element, regex, placeholder.current_value);
    if (count > 0) {
        logger.debug(`Replaced ${placeholder.name} via innerHTML method at least ${count} time(s)`);
        placeholder.count_on_page += count;
        placeholder.reload_page_on_change = true;
    }
}


// Replace all placeholders in the given order and return which placeholders actually were actually found in the page
export const replace_placeholders_in_subtree = (root_element: Element, config: PluginConfig): void => {
    for (const placeholder of config.placeholders.values()) {
        do_normal_replace(root_element, placeholder, config);
        if (placeholder.allow_inner_html) {
            do_html_replace(root_element, placeholder, config);
        }
    }
}


