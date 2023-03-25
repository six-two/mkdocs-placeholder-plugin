import { parse_config } from "./parse_settings";

const settings = parse_config((window as any).PlaceholderConfig);
console.info("Settings", settings);
