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
