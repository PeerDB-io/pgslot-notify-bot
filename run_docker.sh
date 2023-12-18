python ./main.py \
  --db-host="${DB_HOST}" \
  --db-port="${DB_PORT}" \
  --db-user="${DB_USER}" \
  --db-password="${DB_PASSWORD}" \
  --db-name="${DB_NAME}" \
  --slack-channel="${SLACK_CHANNEL}" \
  --interval-seconds=${INTERVAL_SECONDS} \
  --size-threshold-mb=${SIZE_THRESHOLD_MB}
