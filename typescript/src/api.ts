import { debug_disable_reload } from "./debug"
import { PluginConfig } from "./parse_settings"


export const export_api_functions = (config: PluginConfig) => {
    // This is the simplest way to assign something to the window object without TypeScript complaining, so I keep it
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (window as any).PlaceholderPlugin = {
        "settings": config.settings,
        "placeholders": config.placeholders,
        "debug_disable_reload": debug_disable_reload,
        "debug_print_dependency_graph": () => config.dependency_graph.debug_print_representation(),
    }
}
