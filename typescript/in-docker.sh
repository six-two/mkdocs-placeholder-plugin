#!/bin/bash
# copy everything except the node_modules to the build directory
cd /mnt/
cp -r *.json *.js src /app/

# Build the code with webpack
cd /app/
# npm install
npm run build
cp -r build /mnt/
