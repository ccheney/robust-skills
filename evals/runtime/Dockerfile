FROM node:24.11.1-bookworm-slim@sha256:48abc13a19400ca3985071e287bd405a1d99306770eb81d61202fb6b65cf0b57
WORKDIR /opt/eval
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/browsers
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund \
    && npx playwright install --with-deps chromium \
    && apt-get install -y --no-install-recommends python3 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
ARG TARGETARCH
RUN curl -fsSL "https://github.com/bazel-contrib/buildtools/releases/download/v8.5.1/buildifier-linux-${TARGETARCH}" -o /usr/local/bin/buildifier \
    && case "$TARGETARCH" in amd64) expected=887377fc64d23a850f4d18a077b5db05b19913f4b99b270d193f3c7334b5a9a7 ;; arm64) expected=947bf6700d708026b2057b09bea09abbc3cafc15d9ecea35bb3885c4b09ccd04 ;; *) exit 1 ;; esac \
    && echo "$expected  /usr/local/bin/buildifier" | sha256sum -c - \
    && chmod +x /usr/local/bin/buildifier
COPY . .
USER node
CMD ["node", "run.mjs"]
