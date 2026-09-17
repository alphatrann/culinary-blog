FROM prom/prometheus:latest
COPY observability/prometheus.yml /etc/prometheus/prometheus.yml
