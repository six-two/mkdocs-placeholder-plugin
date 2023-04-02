import { debug_disable_reload } from "./debug"
import { PluginConfig } from "./parse_settings"


export const export_api_functions = (config: PluginConfig) => {
    (window as any).PlaceholderPlugin = {
        "settings": config.settings,
        "placeholders": config.placeholders,
        "debug_disable_reload": debug_disable_reload,
        "debug_print_dependency_graph": () => config.dependency_graph.debug_print_representation(),
    }
}
