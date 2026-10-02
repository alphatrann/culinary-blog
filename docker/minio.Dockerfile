# MinIO no longer publishes community images (quay.io/minio/minio and minio/minio are gone),
# so build the server from a pinned release tag.
ARG MINIO_RELEASE=RELEASE.2025-10-15T17-29-55Z

FROM golang:1.24-alpine AS build
ARG MINIO_RELEASE
RUN apk add --no-cache git
RUN git clone --depth 1 --branch "${MINIO_RELEASE}" https://github.com/minio/minio.git /src
WORKDIR /src
RUN CGO_ENABLED=0 go build -trimpath -ldflags "$(go run buildscripts/gen-ldflags.go)" -o /out/minio

FROM alpine:3.22
# curl is used by the compose healthcheck.
RUN apk add --no-cache ca-certificates curl
COPY --from=build /out/minio /usr/bin/minio
EXPOSE 9000 9001
ENTRYPOINT ["/usr/bin/minio"]
