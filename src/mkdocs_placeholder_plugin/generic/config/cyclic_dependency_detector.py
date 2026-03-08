import re
# local
from .parser_utils import PlaceholderConfigErrorWithData
from .configuration import PlaceholderConfig
from .placeholder import InputType, Placeholder


def build_regexes(config: PlaceholderConfig) -> dict[str, re.Pattern]:
    """
    Returns a map of all placeholder names to regexes that match the placeholder using any replace mode (matches xNAMEx, sNAMEs, etc)
    """
    s = config.settings
    prefix_options = [s.dynamic_prefix, s.editable_prefix, s.html_prefix, s.normal_prefix, s.static_prefix]
    suffix_options = [s.dynamic_suffix, s.editable_suffix, s.html_suffix, s.normal_suffix, s.static_suffix]
    prefix_string = "[" + "|".join([re.escape(x) for x in prefix_options]) + "]"
    suffix_string = "[" + "|".join([re.escape(x) for x in suffix_options]) + "]"

    return {name: re.compile(prefix_string + re.escape(name) + suffix_string)
            for name in config.placeholders.keys()}


def get_direct_dependencies(placeholder: Placeholder, placeholder_regexes: dict[str, re.Pattern]) -> set[str]:
    # Computed placeholders: add explicit depends_on
    if placeholder.input_type == InputType.Computed:
        return set(placeholder.computed_depends_on)

    # allow_nested: treat placeholders referenced in default_value as dependencies
    if placeholder.allow_nested and placeholder.default_value:
        # Find all placeholder names referenced in default_value (e.g., xNAMEx)
        referenced = set()
        for match_name, match_regex in placeholder_regexes.items():
            if match_regex.search(placeholder.default_value):
                referenced.add(match_name)
        return referenced

    # Normal placeholders have no dependencies
    return set()


class DependencyGraph:
    def __init__(self, config: PlaceholderConfig, location: str):
        self.placeholders = config.placeholders
        placeholder_regexes: dict[str, re.Pattern] = build_regexes(config)
        self.dep_graph: dict[str, set[str]] = {name: get_direct_dependencies(placeholder, placeholder_regexes) for name, placeholder in self.placeholders.items()}
        self.location = location

    def ensure_no_cycles_exist(self):
        visited: set[str] = set()
        for name in self.placeholders:
            if name not in visited:
                self._dfs(name, [name], visited, set())

    # Vibe coded with Copilot
    def _dfs(self, node: str, stack: list[str], visited: set[str], rec_stack: set[str]):
        """
        Do a depth first search and return a cycle if it was found
        """
        visited.add(node)
        rec_stack.add(node)
        for neighbor in self.dep_graph[node]:
            if neighbor not in self.placeholders:
                continue  # skip unknowns, already validated elsewhere
            if neighbor not in visited:
                if self._dfs(neighbor, stack + [neighbor], visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                # Cycle detected
                cycle_path = stack + [neighbor]

                raise PlaceholderConfigErrorWithData(
                    f"Dependency cycle detected among placeholders: {' -> '.join(cycle_path)}",
                    self.location,
                    # Return a list of all involved placeholders and what they depend on
                    {x: list(self.dep_graph[x]) for x in cycle_path}
                )
        rec_stack.remove(node)
        return False
