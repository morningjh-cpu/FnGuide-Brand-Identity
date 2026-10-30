# syntax=docker/dockerfile:1
# Registry-verified multi-platform digest; includes linux/amd64 and linux/arm64.
FROM nginx/nginx-unprivileged:stable-alpine@sha256:2daef144b574804198caccc4041819fa1801ecd5df2252a39646bfa2b1ff3bea

USER root
RUN rm -rf /usr/share/nginx/html \
    && mkdir -p /usr/share/nginx/html \
    && chown nginx:nginx /usr/share/nginx/html

COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --chown=nginx:nginx index.html index_old.html /usr/share/nginx/html/
COPY --chown=nginx:nginx ["Apply skills Ver/", "/usr/share/nginx/html/Apply skills Ver/"]
COPY --chown=nginx:nginx out/brand-site/ /usr/share/nginx/html/out/brand-site/
COPY --chown=nginx:nginx out/FnGuideLogotype-v*.zip /usr/share/nginx/html/out/
COPY --chown=nginx:nginx out/font-critique/img/ /usr/share/nginx/html/out/font-critique/img/
COPY --chown=nginx:nginx out/font-critique/FnGuide-Logotype-v1.200-critique.html out/font-critique/FnGuide-Logotype-v1.200-proposal.html /usr/share/nginx/html/out/font-critique/
COPY --chown=nginx:nginx out/font-update/v1.200/fonts/FnGuideLogotype-Regular.woff /usr/share/nginx/html/out/font-update/v1.200/fonts/

USER nginx
ENV TZ=Asia/Seoul
ARG BUILD_VERSION=unknown
ARG DEPLOY_ENV=unknown
ARG GIT_COMMIT=unknown
RUN printf 'version : %s\nenv     : %s\ncommit  : %s\n' "$BUILD_VERSION" "$DEPLOY_ENV" "$GIT_COMMIT" \
    > /usr/share/nginx/html/VERSION

EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -T 4 -O /dev/null http://127.0.0.1:3000/health || exit 1
CMD ["nginx", "-g", "daemon off;"]
