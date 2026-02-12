FROM node:20-alpine


WORKDIR /app

RUN apk add --no-cache libc6-compat

# URL pública del orquestador embebida en el build del cliente.
ARG NEXT_PUBLIC_ORCHESTRATOR_URL="https://api.deco-security.com"
ENV NEXT_PUBLIC_ORCHESTRATOR_URL=${NEXT_PUBLIC_ORCHESTRATOR_URL}

COPY package*.json ./
RUN npm install

COPY . .

# Build de Next con env definida
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
