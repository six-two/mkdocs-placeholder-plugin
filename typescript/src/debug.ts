const timestamp = () => `${new Date().toISOString().slice(11,23)} (TS)`;
let is_reload_enabled = true;

function internal_log(...args: any[]) {
    console.log.apply(console, [`${timestamp()} |`, ...arguments]);
}

function internal_info(...args: any[]) {
    console.info.apply(console, [`${timestamp()} |`, ...arguments]);
}

function internal_debug(...args: any[]) {
    console.debug.apply(console, [`${timestamp()} |`, ...arguments]);
}

function noop(...args: any[]) {
}

export const reload_page = () => {
    if (is_reload_enabled) {
        window.location.reload();
    } else {
        internal_info("Page reload was triggered and blocked due to PlaceholderPlugin.debug_disable_reload");
    }
}

export const create_logging = (enable_debug: boolean) => {
    if (enable_debug) {
        // Write debugging messages to console
        return {
            "log": internal_log,
            "info": internal_info,
            "debug": internal_debug,
        }
    } else {
        // If debugging is disabled, make the functions do nothing
        return {
            "log": noop,
            "info": noop,
            "debug": noop,
        }
    }
}


// You can call this manually from the browser's console to temporarily disable reloads and debug the application
export const debug_disable_reload = () => {
    internal_info("Page reload was disabled for debugging purposes");
    is_reload_enabled = false;
}
