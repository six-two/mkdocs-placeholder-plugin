import { parse_config, PluginConfig } from "./parse_settings";
import { init_logging, logger } from "./debug";
import { replace_placeholders_in_subtree } from "./replacer";
import { initialize_all_input_fields } from "./inputs";
import { export_api_functions } from "./api";
import { initialize_auto_tables, initialize_placeholder_settings_divs } from "./auto_tables";
import { register_inline_value_editors } from "./inline-editors/register";


export const main = () => {
    // This is the easiest way to read the attribute from the window. It should be set by "placeholder-data.js"
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const config = parse_config((window as any).PlaceholderPluginConfigJson);
    
    init_logging(config.settings.debug);

    logger.info("PluginConfig", config);

    export_api_functions(config);

    const delay_millis = config.settings.delay_millis;
    
    // Then do the placeholder replacing at the user-specified time
    const document_listener = (window as any).document$;
    if (document_listener) {
        // This means we are using MkDocs, so we hook into it's init system
        // SEE https://github.com/squidfunk/mkdocs-material/discussions/5925
        document_listener.subscribe(() => {
            if (delay_millis > 0) {
                setTimeout(() => do_plugin_stuff(config), delay_millis);
            } else {
                do_plugin_stuff(config);
            }
        })
    } else {
        // Use the normal HTML5 way of waiting for the execution (window.onload)
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
}

const do_plugin_stuff = (config: PluginConfig) => {
    logger.info("Called do_plugin_stuff (function for parsing and modifying the page)")
    // @TODO: clear current state in case we are called multiple times (instant loading)
    config.dependency_graph.reset();
    config.placeholders.forEach((placeholder, _key, _map) => {
        placeholder.count_on_page = 0;
        placeholder.input_elements = [];
    });

    replace_placeholders_in_subtree(document.body, config);
    config.dependency_graph.debug_print_representation();
    
    initialize_all_input_fields(config);
    initialize_auto_tables(config);
    initialize_placeholder_settings_divs(config);

    if (config.settings.inline_editors) {
        register_inline_value_editors(config);
    }
}

