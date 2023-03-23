import { parse_settings } from "./parse_settings";

const settings = parse_settings((window as any).PlaceholderPlugin.raw_data);
console.info("Settings", settings);
