# Use the official Node.js image as the base image
FROM node:22-slim

# Set the working directory
WORKDIR /app

COPY . .

RUN npm install

EXPOSE 3000

CMD [ "tail", "-f" , "/dev/null" ]