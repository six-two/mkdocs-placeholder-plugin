# Tests: Validators

Input type | Validator name | Input element
---|---|---
Domain | `domain` | <input data-input-for="VALIDATOR_DOMAIN">
File name (Linux) | `file_name_linux` | <input data-input-for="VALIDATOR_FILE_LINUX">
File name (Windows) | `file_name_windows` | <input data-input-for="VALIDATOR_FILE_WINDOWS">
Hostname | `hostname` | <input data-input-for="VALIDATOR_HOSTNAME">
IPv4 address | `ipv4_address` | <input data-input-for="VALIDATOR_IPV4_ADDRESS">
IPv4 address range (CIDR) | `ipv4_range_cidr` | <input data-input-for="VALIDATOR_IPV4_CIDR">
IPv4 address range (dashes) | `ipv4_range_dashes` | <input data-input-for="VALIDATOR_IPV4_DASHES">
IPv6 address | `ipv6_address` | <input data-input-for="VALIDATOR_IPV6_ADDRESS">
File path (Linux) | `path_linux` | <input data-input-for="VALIDATOR_PATH_LINUX">
File path (Windows) | `path_windows` | <input data-input-for="VALIDATOR_PATH_WINDOWS">
Port number | `port_number` | <input data-input-for="VALIDATOR_PORT">
URL (any protocol) | `url_any` | <input data-input-for="VALIDATOR_URL_ANY">
URL (HTTP or HTTPS) | `url_http` | <input data-input-for="VALIDATOR_URL_HTTP">

## Test buttons

### Invalid values on page load

When you click this button and reload the page, you should see the value reset to the default and a warning message in the console:

<button class="md-button md-button--primary" onclick="localStorage.setItem('VALIDATOR_DOMAIN', 'not-a-valid/domain.')">Assign invalid value to domain input field</button>

### Disable page reload

<button class="md-button md-button--primary" onclick="PlaceholderPlugin.debug_disable_reload()">Debug: Disable page reload</button>

