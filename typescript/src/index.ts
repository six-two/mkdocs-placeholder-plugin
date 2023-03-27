import { main } from "./main";

// If the data is loaded via another script, make it work in any order
if ((window as any).PlaceholderPluginConfigJson) {
    main();
} else {
    document.addEventListener("PlaceholderPluginConfigJson", main);
}
