import { logger } from "./debug";
import { ComputedPlaceholder, InputType, Placeholder } from "./parse_settings";
import { safe_replace_multiple_placeholders_in_string } from "./replacer";
import { clear_state } from "./state_manager";


// Should be a directed acyclical graph
export class DependencyGraph {
    private nodes: Map<string, GraphNode>;
    private placeholders: Map<string, Placeholder>;

    constructor(placeholders: Map<string, Placeholder>) {
        this.placeholders = placeholders;
        this.nodes = new Map<string, GraphNode>();
        this.reset();
    }

    reset() {
        this.nodes.clear();
        for (const placeholder of this.placeholders.values()) {
            this.nodes.set(placeholder.name, new GraphNode(placeholder));
        }
        // Needs to be in different loops to ensure that all nodes have been created first
        for (const placeholder of this.placeholders.values()) {
            try {
                this.on_placeholder_value_change(placeholder);
            } catch (e) {
                console.error("Error while building dependency graph", e);
                console.warn("Placeholder values may be inconsistent. Clearing your localStorage should fix this problem.");
                if (confirm("We detected a problem with your placeholder values. Resetting them to the defaults should fix this. Should we reset your placeholders?")) {
                    clear_state();
                }
            }
        }

        // Make sure that all expanded values are calculated
        // We take every node with no downlinks (bottom of the graph) and do a recursive recalculation (upwards).
        // Not super efficient, but simple to implement
        for (const node of this.nodes.values()) {
            if (node.downlinks.length == 0) {
                node.recalculate_expanded_value(true);
            }
        }
    }

    debug_print_representation() {
        let text = "Dependency graph nodes (DEBUG view):";
        for (const node of this.nodes.values()) {
            const dependencies = node.downlinks.map(n => n.placeholder.name).join(", ");
            if (dependencies.length == 0) {
                text +=`\n${node.placeholder.name} (${node.placeholder.expanded_value}) has no dependencies`;
            } else {
                text +=`\n${node.placeholder.name} (${node.placeholder.expanded_value}) depends on ${dependencies}`;
            }
        }
        logger.debug(text);
    }

    unmark_everything(): void {
        for (const node of this.nodes.values()) {
            node.marked = false;
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
        const node = this.get_node(placeholder);
        this.update_placeholder_downlinks(placeholder);
        
        if (this.has_loop()) {
            // Emergency measure: ignore any placeholders in this value. This should fix the loop
            placeholder.expanded_value = placeholder.current_value;
            node.downlinks = [];
            
            // Also raise an exception to inform the user
            throw new Error(`Placeholder ${placeholder.name} was part of a loop and has temporarily been made non-recursive`);
        } else {
            node.recalculate_expanded_value(true);
        }
    }

    get_all_marked(): Placeholder[] {
        const marked: Placeholder[] = [];
        for (const node of this.nodes.values()) {
            if (node.marked) {
                marked.push(node.placeholder);
            }
        }
        return marked;
    }

    get_all_upstream(placeholder: Placeholder): Placeholder[] {
        this.unmark_everything()

        const node = this.get_node(placeholder);
        node.recursive_mark_upstream();

        return this.get_all_marked();
    }

    update_placeholder_downlinks(placeholder: Placeholder) {
        // Step 1: remove all old downlinks
        const node = this.get_node(placeholder);
        for (const old_downlink of node.downlinks) {
            old_downlink.remove_uplink(node);
        }
        node.downlinks = [];

        // Step 2: set new downlinks based on placeholder type
        if (placeholder.type === InputType.Computed) {
            // Computed placeholders have explicit dependencies declared in computed_depends_on
            const comp = placeholder as ComputedPlaceholder;
            for (const dep_name of comp.computed_depends_on) {
                const dep_node = this.nodes.get(dep_name);
                if (dep_node) {
                    node.downlinks.push(dep_node);
                    dep_node.uplinks.push(node);
                } else {
                    console.error(`Computed placeholder '${comp.name}': dependency '${dep_name}' not found in graph`);
                }
            }
        } else if (placeholder.allow_nested) {
            // Nested placeholders: scan the value string for references to other placeholders
            for (const other_node of this.nodes.values()) {
                // No placeholder should directly be able to contain itself -> ignoring this case.
                // This should lead to the placeholder's name appearing in it's text, which was probably intended
                if (other_node != node) {
                    if (string_contains_placeholder(placeholder.current_value, other_node.placeholder)) {
                        // This placeholder's value contains a reference to the other node's placeholder
                        //  -> This node depends on the other node
                        node.downlinks.push(other_node);
                        other_node.uplinks.push(node);
                    }
                }
            }
        } else {
            logger.debug(`${placeholder.name} has no dependencies (not nested, not computed)`);
        }
    }

    get_all_used_placeholders(): Placeholder[] {
        // Also includes all placeholders used by the placeholders that were included
        this.unmark_everything()

        // Mark all used placeholders and their downstream nodes
        for (const node of this.nodes.values()) {
            if (node.placeholder.count_on_page > 0) {
                node.recursive_mark_downstream()
            }
        }
        return this.get_all_marked();
    }

    has_loop() {
        // General algorithm: https://www.geeksforgeeks.org/detect-cycle-in-a-graph/
        this.unmark_everything();
        for (const node of this.nodes.values()) {
            // Make sure that we check every single node (we likely have multiple graphs that are not connected)
            if (!node.marked) {
                if (this._has_loop([], node)) {
                    return true;
                }
            }
        }
        return false;
    }

    private _has_loop(back_stack: GraphNode[], current_node: GraphNode): boolean {
        const new_back_stack = [...back_stack, current_node];
        const index = back_stack.indexOf(current_node);
        if (index != -1) {
            let message = "Dependency cycle in placeholders detected:";
            for (let i = index; i < new_back_stack.length; i++) {
                const placeholder = new_back_stack[i].placeholder;
                message += `\n$ -> ${placeholder.name}: ${placeholder.current_value}`;
            }
            console.warn(message);
            return true;
        } else if (!current_node.marked) {
            // No cycle found yet, scan all children that are not yet marked
            current_node.marked = true;
            for (const child of current_node.downlinks) {
                if (this._has_loop(new_back_stack, child)) {
                    return true;
                }
            }
            return false;
        } else {
            // Already checked, so no need to start recursive scans
            return false;
        }

    }
}

const string_contains_placeholder = (string_to_test: string, placeholder_to_find: Placeholder): boolean => {
    return placeholder_to_find.regex_dynamic.test(string_to_test) ||
            placeholder_to_find.regex_editable.test(string_to_test) ||
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
    // State used during operations to see if this node was already visited/processed
    marked: boolean = false;

    constructor(placeholder: Placeholder) {
        this.placeholder = placeholder;
    }

    remove_uplink(node: GraphNode): void {
        this.uplinks = this.uplinks.filter(x => x != node);
    }

    recalculate_expanded_value(recursive: boolean) {
        if (this.placeholder.type === InputType.Computed) {
            // Computed placeholders: re-evaluate the function using dependency values from downlinks
            const comp = this.placeholder as ComputedPlaceholder;
            const args: Record<string, string> = {};
            for (const downlink of this.downlinks) {
                args[downlink.placeholder.name] = downlink.placeholder.current_value;
            }
            try {
                const result = comp.computed_function(args);
                comp.current_value = result;
                comp.expanded_value = result;
                logger.debug(`Computed placeholder '${comp.name}' evaluated to: '${result}'`);
            } catch (error) {
                console.error(`Error evaluating computed placeholder '${comp.name}':`, error);
                comp.current_value = "COMPUTED_ERROR";
                comp.expanded_value = "COMPUTED_ERROR";
            }
        } else {
            // Regular placeholders: expand nested placeholder references via string substitution
            let expanded_value = this.placeholder.current_value;
            if (this.placeholder.allow_nested) {
                expanded_value = safe_replace_multiple_placeholders_in_string(expanded_value, this.downlinks.map(n => n.placeholder));
            }
            this.placeholder.expanded_value = expanded_value;
        }

        if (recursive) {
            // Recalculate all uplink nodes in recursive too
            for (const uplink_node of this.uplinks) {
                uplink_node.recalculate_expanded_value(recursive);
            }
        }
    }

    recursive_mark_upstream() {
        this.marked = true;
        for (const node of this.uplinks) {
            node.recursive_mark_upstream();
        }
    }

    recursive_mark_downstream() {
        this.marked = true;
        for (const node of this.downlinks) {
            node.recursive_mark_downstream();
        }
    }
}

