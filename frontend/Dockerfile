FROM node:20-alpine AS build

WORKDIR /app

ARG REACT_APP_API_URL=https://demo.eminencetechsolutions.com:13066/api
ARG REACT_APP_WS_URL=wss://demo.eminencetechsolutions.com:13066/ws
ARG REACT_APP_GATEWAY_URL=https://demo.eminencetechsolutions.com:13066/gw

ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL
ENV REACT_APP_GATEWAY_URL=$REACT_APP_GATEWAY_URL

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# Final stage: serve built files via a tiny container
# Docker compose volume mount will make /app/build accessible to nginx
FROM busybox:1.36
COPY --from=build /app/build /app/build
VOLUME /app/build
# Keep container running to maintain volume
CMD ["sh", "-c", "cp -r /app/build/. /output/ 2>/dev/null; echo 'Frontend build ready'; tail -f /dev/null"]
