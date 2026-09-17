FROM grafana/loki:latest
COPY observability/loki-config.yaml /etc/loki/loki-config.yaml
CMD ["-config.file=/etc/loki/loki-config.yaml"]
