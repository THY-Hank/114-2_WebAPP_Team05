FROM node:20-alpine AS build
WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

ARG VITE_AES_KEY
ARG VITE_AES_IV
ENV VITE_AES_KEY=$VITE_AES_KEY
ENV VITE_AES_IV=$VITE_AES_IV

COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
