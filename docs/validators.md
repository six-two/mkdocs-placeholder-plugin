# Validators

Using validators you can restrict what values can be stored in a (normal textbox) placeholder.
You can also warn users, that values may break stuff (for example if a value contains whitespace, quotes, backslashes, etc and is injected into a command) but accept the values anyway.

## Predefined validators

There exists a (hopefully growing) number of predefined validators.
You can simply specify the name of the validator that you want to use.
You can see (and try out) the full list of predefined validators [on this page](./tests/validators.md).

### Example

For example if you wanted a value to only match an IPv4 address, you could define a placeholder like this:

```yaml
VALIDATOR_IPV4_ADDRESS:
  default: 127.0.0.1
  validators: ipv4_address
```

When you then define an input element for the placeholder, it will change it's background to yellow if the validator generates a warning.
It changes to red if the validator detects an error.
When warnings or errors exist, you can list them by hovering over the input filed.
Try it out:

<input data-input-for="VALIDATOR_IPV4_ADDRESS">


## Custom validators

You can alss define your own validators.
Each validator is a collection of rules.
Each rule is checked and the list of the error messages is shown to the user.

### Rules

Each rule consists of the following fields:

1. To decide if the rule matches, there are multiple ways:

    - `regex` specifies a [regular expression](https://en.wikipedia.org/wiki/Regular_expression) that the input should / should not match.
    - `match_function` defines a JavaScript expression that will be evaluated.
        The value to be tested will be available as the `value` variable.
        Similar to a placeholder's `default-function` attribute you can use the `placeholder_extra_js` configuration value to ensure that any function you want to call is loaded beforehand.

2. `should_match` specifies if the input is expected to match the input:

    - `true` means that the validator will complain if the input **does not** match.
    - `false` means that the validator will complain if the input **does** match.

3. `severity` specifies how serious the rule is:

    - `warn` will cause the background to turn yellow, but the value will be accepted anyways.
    - `error` (the default value) will cause the background to trun red and the value will be rejected.

4. `error_message` specifies the message shown.
    This should be informative, so that use user can understand what is wrong and fix the input.

### Example

Placeholder specification:

```yaml
CUSTOM_VALIDATORS:
  default: A12
  validators:
  - name: Excel cell name
    rules:
    - regex: "^[A-Za-z]+"
      should_match: true
      error_message: "Needs to start with at least one letter"
    - regex: "[0-9]+$"
      should_match: true
      error_message: "Needs to end with at least one digit"
    - regex: "^[A-Za-z0-9]+$"
      should_match: true
      error_message: "Can only contain letters and numbers"
    - severity: warn
      regex: "^[A-Za-z]+[0-9]+$"
      should_match: true
      error_message: "Should look like AB123"
```

Coresponding input element:

<input data-input-for="CUSTOM_VALIDATORS">


## Multiple validators

You can specify multiple validators for a value.
Of course you can use both predefined and custom validators.
Only the best matching validators will be used, so it is like a logical or (meaning only one of them needs to match).
If one validator accepts the input, but others do not, then the input will be accepted and no errors will be shown.
If at least one validator only has warnings, only messages for the validators that match best (they do not have errors) will be shown.

### Example

Placeholder specification:

```yaml
MULTI_VALIDATORS:
  default: "127.0.0.1"
  description: "Multiple validators: mest be an IPv4 address, domain name, or hostname"
  validators:
  - ipv4_address
  - domain
  - hostname
  - name: IPv6 loopback
    rules:
    - regex: "^::1$"
      should_match: true
      error_message: "Only the value '::1' is accepted"
```

Coresponding input element:

<input data-input-for="MULTI_VALIDATORS">

