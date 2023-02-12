PlaceholderPlugin.timestamp = () => new Date().toISOString().slice(11,23);
PlaceholderPlugin.reload_page = () => window.location.reload();
PlaceholderPlugin.DEBUG_COUNTER = 0;
PlaceholderPlugin.increment_debug_counter = () => PlaceholderPlugin.DEBUG_COUNTER++;

// Set up or disable logging as early as possible
let log, info, debug;
if (PlaceholderData.debug) {
    // Write debugging messages to console
    debug = function() {
        console.debug.apply(console, [`${PlaceholderPlugin.timestamp()} |`, ...arguments]);
    };
    info = function() {
        console.info.apply(console, [`${PlaceholderPlugin.timestamp()} |`, ...arguments]);
    };
    log = function() {
        console.log.apply(console, [`${PlaceholderPlugin.timestamp()} |`, ...arguments]);
    };
} else {
    // If debugging is disabled, make the functions do nothing
    debug = () => {};
    info = () => {};
    log = () => {};
}

// You can call this manually from the browser's console to temporarily disable reloads and debug the application
PlaceholderPlugin.debug_disable_reload = () => {
    console.info(`${PlaceholderPlugin.timestamp()} | Page reload was disabled for debugging purposes`);
    PlaceholderPlugin.reload_page = () => {
        console.info(`${PlaceholderPlugin.timestamp()} | Page reload was triggered and blocked due to PlaceholderPlugin.debug_disable_reload`);
    }
}
