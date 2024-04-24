import { parse_config, PluginConfig } from "./parse_settings";
import { init_logging, logger } from "./debug";
import { replace_dynamic_placeholder_values, replace_placeholders_in_subtree } from "./replacer";
import { initialize_all_input_fields } from "./inputs";
import { export_api_functions } from "./api";
import { initialize_auto_tables, initialize_placeholder_settings_divs } from "./auto_tables";
import { register_inline_value_editors } from "./inline-inputs";


export const main = () => {
    // This is the easiest way to read the attribute from the window. It should be set by "placeholder-data.js"
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const config = parse_config((window as any).PlaceholderPluginConfigJson);
    
    init_logging(config.settings.debug);

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
    config.dependency_graph.debug_print_representation();
    
    initialize_all_input_fields(config);
    initialize_auto_tables(config);
    initialize_placeholder_settings_divs(config);

    if (config.settings.inline_editors) {
        register_inline_value_editors(config);
    }

    // Normally it should not be necessary, but without it the initial values for checkbox placeholdersdo not have the checked/unchecked class assigned
    // @TODO later: investigate and fix
    replace_dynamic_placeholder_values([...config.placeholders.values()]);
}

