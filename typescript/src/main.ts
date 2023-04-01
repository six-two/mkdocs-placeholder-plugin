import { parse_config, PluginConfig } from "./parse_settings";
import { init_logging, logger } from "./debug";
import { replace_placeholders_in_subtree } from "./replacer";
import { initialize_all_input_fields } from "./inputs";
import { export_api_functions } from "./api";
import { initialize_auto_tables } from "./auto_tables";

export const main = () => {
    const config = parse_config((window as any).PlaceholderPluginConfigJson);
    
    init_logging(config.settings.debug);

    console.warn("@TODO: set the expanded_value for all placeholders to the correct value")
    for (const placeholder of config.placeholders.values()) {
        if (placeholder.allow_recursive) {
            placeholder.expanded_value = placeholder.current_value; // this is wrong, but I will fix it later
        } else {
            placeholder.expanded_value = placeholder.current_value;
        }
    }

    logger.info("PluginConfig", config);

    export_api_functions(config);

    const delay_millis = config.settings.delay_millis;
    
    // Then do the placeholder replacing at the user-specified time
    if (delay_millis < 0) {
        // For values smaller than 0, immediately do the replacements
        do_plugin_stuff(config);
    } else if (delay_millis == 0) {
        // Replace placeholders as soon as the page finished loading
        window.addEventListener("load", () => do_plugin_stuff(config));
    } else {
        // Wait the amount of millis specified by the user
        window.addEventListener("load", () => {
            setTimeout(() => do_plugin_stuff(config), delay_millis);
        });
    }
}

const do_plugin_stuff = (config: PluginConfig) => {
    replace_placeholders_in_subtree(document.body, config);

    // @TODO: set input_elements and output_elements for all placeholders
    // @TODO: update_all_dynamic_output_elements

    initialize_all_input_fields(config);

    initialize_auto_tables(config);
}

