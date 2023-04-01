import { Placeholder, PluginConfig } from "./parse_settings";

const calculate_expanded_values_for_all_placeholders = (config: PluginConfig): void => {
    const to_process = [...config.placeholders.values()];
    const processed = new Map<string, string>();

    // First pass: all placeholders that can not conatin other placeholders 
    for (const placeholder of config.placeholders.values()) {
        if (placeholder.allow_recursive == false) {
            processed.set(placeholder.name, placeholder.current_value);
        }
    }
}


// Should be a directed acyclical graph
class DependencyGraph {
    private nodes: Map<string, GraphNode>;

    constructor(config: PluginConfig) {
        this.nodes = new Map<string, GraphNode>();
        for (const placeholder of config.placeholders.values()) {
            this.nodes.set(placeholder.name, new GraphNode(placeholder));
        }
        // Needs to be in different loops to ensure that all nodes have been created first
        for (const placeholder of config.placeholders.values()) {
            this.on_placeholder_value_change(placeholder);
        }
    }

    get_node(placeholder: Placeholder): GraphNode {
        const node = this.nodes.get(placeholder.name);
        if (node == undefined) {
            throw new Error(`Placeholder ${placeholder.name} is not part of the dependency graph`);
        } else {
            return node;
        }
    }

    on_placeholder_value_change(placeholder: Placeholder) {
        this.update_placeholder_downlinks(placeholder);
        
        if (this.has_loop()) {
            // Emergency measure: ignore any placeholders in this value. This should fix the loop
            placeholder.expanded_value = placeholder.current_value;
            const node = this.get_node(placeholder);
            node.downlinks = [];
            
            // Also raise an exception to inform the user
            throw new Error(`Placeholder ${placeholder.name} was part of a loop and has temporarily been made non-recursive`);
        } else {

            // @TODO: update all uplinks expanded values
            // Update this elements expanded value
        }
    }

    update_placeholder_downlinks(placeholder: Placeholder) {
        if (placeholder.allow_recursive == false) {
            // By definition, non-recursive placeholders can not rely on other placeholders
            return;
        }

        const node = this.get_node(placeholder);

        // Step 1: remove all old downlinks
        for (const old_downlink of node.downlinks) {
            old_downlink.remove_uplink(node)
        }
        node.downlinks = [];
        
        // Step 2: parse placeholder's value (again)
        for (const other_node of this.nodes.values()) {
            // No placeholder should directly be able to contain itself -> ignoring this case.
            // This should lead to the placeholder's name appearing in it's text, which was probably intended
            if (other_node != node) {
                if (string_contains_placeholder(placeholder.current_value, other_node.placeholder)) {
                    // This placeholders value contains a reference to the other node's placeholder
                    //  -> This node depends on the other node
                    node.downlinks.push(other_node);
                }
            }
        }
    }

    has_loop() {
        console.warn("@TODO check for loops");
        return false;
    }
}

const string_contains_placeholder = (string_to_test: string, placeholder_to_find: Placeholder): boolean => {
    return placeholder_to_find.regex_dynamic.test(string_to_test) ||
            placeholder_to_find.regex_html.test(string_to_test) ||
            placeholder_to_find.regex_normal.test(string_to_test) ||
            placeholder_to_find.regex_static.test(string_to_test);
}

class GraphNode {
    // This is the placeholder associated with this node
    placeholder: Placeholder;
    // These other nodes depend on this node
    uplinks: GraphNode[] = [];
    // This are the nodes this node depends on
    downlinks: GraphNode[] = [];

    constructor(placeholder: Placeholder) {
        this.placeholder = placeholder;
    }

    remove_uplink(node: GraphNode): void {
        this.uplinks = this.uplinks.filter(x => x != node);
    }
}

