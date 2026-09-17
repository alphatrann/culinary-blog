FROM redis:7-alpine
COPY config/redis.cache.conf /usr/local/etc/redis/redis.conf
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
