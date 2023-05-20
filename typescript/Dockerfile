FROM node:latest
WORKDIR /app
COPY package.json package-lock.json in-docker.sh /app/
RUN npm install
RUN npm install --only=dev
VOLUME /mnt
CMD bash ./in-docker.sh
