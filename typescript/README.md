# README

This is the subdirectory for the rewrite of the javascript code.

## build code

The result will be written to `./build/bundle.min.js`.

### With podman

If you are on a Mac:
```bash
podman machine start
```

Build docker container:
```bash
podman build --tag placeholder-npm .
```

Build code using docker container:
```bash
podman run -it --rm -v "$(pwd):/mnt" localhost/placeholder-npm:latest
```

### With native npm

Install dependencies:
```bash
npm install
```

Build code:
```bash
npm run build
```

## Common tasks

### Update package.json

I do not like native npm, so instead I start a shell in a nodejs container:
```bash
podman run --rm -it --entrypoint=sh -v $(pwd):/share docker.io/library/node:latest
```

Inside the container:

1. Install `ncu`:
    ```bash
    npm install -g npm-check-updates
    ```
2. Switch into the mounted `typescript` directory with the `package.json`:
    ```bash
    cd /share
    ```
3. Update the `package.json`:
    ```bash
    ncu -u
    ```
4. I think this is needed to update `package-lock.json`:
    ```bash
    npm install
    ```

Then exit the container, rebuild the `placeholder-npm` container and try to compile/transpile the code as described above.
