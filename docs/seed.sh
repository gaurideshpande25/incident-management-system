#!/bin/bash
echo "Seeding failure scenario..."
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/api/signals \
    -H "Content-Type: application/json" \
    -d '{"component_id":"POSTGRES_PRIMARY","error_code":"DB_CONN_TIMEOUT","message":"DB down","severity":"P0","metadata":{}}' &
done
for i in {1..3}; do
  curl -s -X POST http://localhost:8000/api/signals \
    -H "Content-Type: application/json" \
    -d '{"component_id":"CACHE_CLUSTER_01","error_code":"CACHE_MISS","message":"Cache degraded","severity":"P2","metadata":{}}' &
done
wait
echo "Done! Check dashboard."
