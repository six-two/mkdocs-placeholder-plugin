FROM node:latest
WORKDIR /app
COPY package.json package-lock.json in-docker.sh /app/
RUN npm install
VOLUME /mnt
CMD bash ./in-docker.sh
