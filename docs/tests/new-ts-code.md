# Tests: TypeScript code

Tests for features introduced in v0.3.0

- [xLINKx](iLINKi)
- Password: xPASSWORDx
- xALIAS_DROPDOWNx
- xAx

<button class="md-button md-button--primary" onclick="PlaceholderPlugin.debug_print_dependency_graph()">Debug: Print dependency graph to console</button>

## For 0.4.1

Placeholder with a validator, that uses the new `import_rules_from` feature: xTEST_IMPORT_RULES_FROMx

See console (`F12`).

<script>setTimeout(() => console.log(`TEST_IMPORT_RULES_FROM's rules:\n`, ...PlaceholderPlugin.placeholders.get("TEST_IMPORT_RULES_FROM").validators[0].rules), 1000)</script>
