# Tests: Mermaid diagrams

These diagrams require the Material theme to work correctly.

!!! fail "Known issue"
    Placeholders in mermaid diagrams do not get replaced (yet). I will try to fix it in the furure

Flowchart:
```mermaid
graph LR
  A[Alice] --> B{xCOMB_FIRST_NAMEx};
  B -->|xCOMB_DOMAINx| C[Does it work?];
```

Sequence diagram:
``` mermaid
sequenceDiagram
  Alice->>xCOMB_FIRST_NAMEx: xTESTx
  loop xTESTx
      xCOMB_FIRST_NAMEx->>xCOMB_FIRST_NAMEx: xLINKx
  end
  Note right of xCOMB_FIRST_NAMEx: xTESTx
```

@TODO: As soon as the two above work, create simple diagrams for all officially supported types
