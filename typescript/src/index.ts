import { main } from "./main";

// If the data is loaded via another script, make it work in any order
// eslint-disable-next-line @typescript-eslint/no-explicit-any
if ((window as any).PlaceholderPluginConfigJson) {
    main();
} else {
    document.addEventListener("PlaceholderPluginConfigJson", main);
}
