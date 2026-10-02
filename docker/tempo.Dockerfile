FROM grafana/tempo:2.4.0
COPY observability/tempo.yaml /etc/tempo.yaml
CMD ["-config.file=/etc/tempo.yaml"]
