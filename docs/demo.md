# Demo page

Enter the values for your variables here:

Variable | Value
---|---
Server IP | <input data-input-for="DEMO_SERVER_IP">
Server port | <input data-input-for="DEMO_SERVER_PORT">
Binding to port requires sudo | <input data-input-for="DEMO_SUDO">
File name to transfer | <input data-input-for="DEMO_FILENAME">
Netcat binary | <input data-input-for="DEMO_NETCAT">


These are your variables.
They are also set for all other page (like the [test page](tests/basic.md)).
However after changing them, you need to may need to reload the page to show the new values (depends on the configuration, here it should not be required).

Below you can see the placeholders in action.

## Transfer files

You can transfer various files on linux systems using common command line tools.
This assumes, that you want to transfer the file "xDEMO_FILENAMEx" to/from the server with the IP address xDEMO_SERVER_IPx.
To sucessfully transfer the files, you need shell access (for example via SSH) to both systems (the server and the client).

### netcat

#### upload (client -> server)

On the server run:
```bash
xDEMO_SUDOxxDEMO_NETCATx -lnp xDEMO_SERVER_PORTx | tee xDEMO_FILENAMEx
```

Then run the following on the client:
```
cat xDEMO_FILENAMEx | xDEMO_NETCATx xDEMO_SERVER_IPx xDEMO_SERVER_PORTx
```

#### download (server -> client)

On the server run:
```bash
cat xDEMO_FILENAMEx | xDEMO_SUDOxxDEMO_NETCATx -lnp xDEMO_SERVER_PORTx
```

Then run the following on the client:
```
xDEMO_NETCATx xDEMO_SERVER_IPx xDEMO_SERVER_PORTx | tee xDEMO_FILENAMEx
```

### download with curl & python (server -> client)

This can be used to transfer files from the server to the client.
Start a HTTP server on the server.
Do **not** start it in your home directory, since all files in the directory will be made available:
```
mkdir public
cd public
cp ../xDEMO_FILENAMEx .
xDEMO_SUDOxpython -m http.server xDEMO_SERVER_PORTx
```

On the client run:
```
curl http://xDEMO_SERVER_IPx:xDEMO_SERVER_PORTx/xDEMO_FILENAMEx -o xDEMO_FILENAMEx
```

