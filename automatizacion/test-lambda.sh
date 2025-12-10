#!/bin/bash

LAMBDA_NAME="get-proyectos-portafolio-lambda"
EVENT_FILE="event.json"
OUTPUT_FILE="response.json"

echo "🔄 Ejecutando Lambda: $LAMBDA_NAME"
echo "📤 Payload: $EVENT_FILE"

aws lambda invoke \
  --function-name "$LAMBDA_NAME" \
  --payload file://$EVENT_FILE \
  $OUTPUT_FILE \
  --log-type Tail \
  --query 'LogResult' \
  --output text | base64 --decode

echo ""
echo "📥 Respuesta guardada en: $OUTPUT_FILE"
echo ""
cat $OUTPUT_FILE
