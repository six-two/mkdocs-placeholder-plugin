import { parse_config } from "./parse_settings";
import { create_logging } from "./debug";

const config = parse_config((window as any).PlaceholderConfig);

const logger = create_logging(config.settings.debug);

logger.info("PluginConfig", config);
