FROM grafana/tempo:latest
COPY observability/tempo.yaml /etc/tempo.yaml
CMD ["-config.file=/etc/tempo.yaml"]
