FROM node:latest
WORKDIR /app
COPY package.json package-lock.json in-docker.sh eslint.config.js /app/
RUN npm install
ENV PATH="$PATH:/app/node_modules/.bin/"
VOLUME /mnt
CMD ["bash", "./in-docker.sh"]
