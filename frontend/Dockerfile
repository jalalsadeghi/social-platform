FROM node:20-alpine

WORKDIR /app

RUN apk update && apk add --no-cache git

COPY package.json package-lock.json ./

RUN npm install jwt-decode @types/jwt-decode && npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
