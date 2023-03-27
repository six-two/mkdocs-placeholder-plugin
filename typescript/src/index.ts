import { parse_config } from "./parse_settings";
import { init_logging, logger } from "./debug";
import { replace_placeholders_in_subtree } from "./replacer";

const main = () => {
    const config = parse_config((window as any).PlaceholderPluginConfigJson);
    
    init_logging(config.settings.debug);
    
    logger.info("PluginConfig", config);
    
    replace_placeholders_in_subtree(document.body, config);
}

// If the data is loaded via another script, make it work in any order
if ((window as any).PlaceholderPluginConfigJson) {
    main();
} else {
    document.addEventListener("PlaceholderPluginConfigJson", main);
}
