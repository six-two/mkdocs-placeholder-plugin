import { parse_config } from "./parse_settings";
import { init_logging, logger } from "./debug";
import { replace_placeholders_in_subtree } from "./replacer";

const config = parse_config((window as any).PlaceholderConfig);

init_logging(config.settings.debug);

logger.info("PluginConfig", config);

replace_placeholders_in_subtree(document.body, config);
