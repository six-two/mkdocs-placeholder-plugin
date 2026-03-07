# Tests: Computed Placeholders

## Placeholders with dependencies

Computed placeholders automatically derive their value from other placeholders.
Change the **Environment** dropdown below and watch the other fields update instantly without a page reload.

Environment | <input data-input-for="ENV">

Variable | Computed value
---|---
Server IP | xSERVER_IPx
Connection string | xCONNECTION_STRINGx

## Placeholders without dependencies

```bash
curl https://ifconfig.me >> ip_xTIMESTAMP_FOR_FILENAMEx.txt
curl -X POST --data '{"id": "xRANDOM_UUIDx", "event":"Login failed"}' https://127.0.0.1/logs
```

UUID repeated three times: xMULTIPLE_RANDOM_UUIDSx

## Cyclic dependencies

Probably show nothing, since they (should) cause errors during the python build process:

Indirect cyclic dependency (A -> B -> A -> B -> ...): xCYCLE_Ax

Direct self reference (C -> C -> C -> ...): xCYCLE_Cx

## Placeholders with errors

Error A: xERROR_Ax
Error B: xERROR_Bx
