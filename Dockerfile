FROM alpine:3.14

RUN apk update \
    && apk upgrade \
    && apk add --no-cache \
        python3 \
        py3-pip \
    && rm -r /var/cache/apk/*

RUN adduser -D \
    account-admin

RUN mkdir -p \
    /var/opt/unix-accounts/certs \
    /var/opt/unix-accounts \
    && chown -R account-admin:account-admin /var/opt/unix-accounts

VOLUME /var/opt/unix-accounts

ADD dist/unix_accounts-1.0.0-py3-none-any.whl /tmp

RUN apk update \
    && apk add --virtual build-deps --no-cache \
      gcc \
      g++ \
      musl-dev \
      python3-dev \
    && rm -r /var/cache/apk/* \
    && pip3 install /tmp/unix_accounts-1.0.0-py3-none-any.whl \
    && apk del build-deps


USER account-admin
ENTRYPOINT ["unix-accounts-server"]
