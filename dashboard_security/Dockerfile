FROM node:20-alpine

WORKDIR /app

# Permite inyectar la URL del orquestador en tiempo de build para que
# el bundle del cliente use directamente HTTPS público y no 127.0.0.1.
ARG NEXT_PUBLIC_ORCHESTRATOR_URL="https://api.deco-security.com"
ENV NEXT_PUBLIC_ORCHESTRATOR_URL=${NEXT_PUBLIC_ORCHESTRATOR_URL}

COPY package*.json ./
RUN npm install

COPY . .

# Build de Next con la URL ya expuesta en env
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
