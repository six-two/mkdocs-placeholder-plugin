// if this script is loaded first, placeholder.min.js will find window.PlaceholderPluginConfigJson
window.PlaceholderPluginConfigJson = __MKDOCS_PLACEHOLDER_PLUGIN_NEW_JSON__;

// this will initialize the plugin if it was loaded before this file
document.dispatchEvent(new Event("PlaceholderPluginConfigJson"));
