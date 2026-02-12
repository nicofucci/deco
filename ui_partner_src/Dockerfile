FROM node:20-alpine

WORKDIR /app

# Inyectamos la URL pública del orquestador en build para que el bundle
# del navegador llame a HTTPS y no a 127.0.0.1.
ARG NEXT_PUBLIC_ORCHESTRATOR_URL="https://api.deco-security.com"
ENV NEXT_PUBLIC_ORCHESTRATOR_URL=${NEXT_PUBLIC_ORCHESTRATOR_URL}
ARG ORCHESTRATOR_URL="https://api.deco-security.com"
ENV ORCHESTRATOR_URL=${ORCHESTRATOR_URL}
ARG NEXT_PUBLIC_SHOW_BUILD_STAMP="false"
ENV NEXT_PUBLIC_SHOW_BUILD_STAMP=${NEXT_PUBLIC_SHOW_BUILD_STAMP}

COPY package*.json ./
RUN npm install

COPY . .

# Build de Next con las variables ya presentes
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
