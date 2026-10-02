#!/usr/bin/env bash
# Throwaway Redis for the cache concurrency tests (tests/cache/test_redis_cache_integration.py). Used locally and by CI.
#
#   scripts/test-redis.sh start   # starts redis:7-alpine and prints the TEST_REDIS_URL to export
#   scripts/test-redis.sh stop
#   export TEST_REDIS_URL=$(scripts/test-redis.sh start) && uv run pytest
#
# PORT (default 6391) is the host port. The tests FLUSHDB database 15, so never point them at a Redis you care about.
set -euo pipefail
NAME=culinary-test-redis
PORT="${PORT:-6391}"

case "${1:-}" in
  start)
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    docker run -d --rm --name "$NAME" -p "$PORT:6379" redis:7-alpine >/dev/null
    for _ in $(seq 1 30); do
      docker exec "$NAME" redis-cli ping >/dev/null 2>&1 && { echo "redis://localhost:$PORT/15"; exit 0; }
      sleep 0.5
    done
    echo "test Redis did not become ready" >&2
    exit 1
    ;;
  stop)
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    ;;
  *)
    echo "usage: $0 start|stop" >&2
    exit 2
    ;;
esac
