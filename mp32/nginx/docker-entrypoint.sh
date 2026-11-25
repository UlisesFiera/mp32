#!/bin/sh

set -eu

CERT_DIR="/etc/nginx/certs"
CERT_FILE="$CERT_DIR/localhost.crt"
KEY_FILE="$CERT_DIR/localhost.key"

mkdir -p "$CERT_DIR"

if [ ! -s "$CERT_FILE" ] || [ ! -s "$KEY_FILE" ]; then
	echo	"Generating self-signed TLS certificate..."

	umask	077

	openssl	req \
			-x509 \
			-nodes \
			-days 365 \
			-newkey rsa:2048 \
			-keyout "$KEY_FILE" \
			-out "$CERT_FILE" \
			-subj "/CN=localhost" \
			-addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

	chmod	600 "$KEY_FILE"
	chmod	644 "$CERT_FILE"

	echo	"TLS certificated generated succesfully."
else
	echo	"TLS certificated found."
fi

echo	"Validating Nginx configuration..."
nginx -t

echo	"Starting Nginx.."
exec nginx -g "daemon off;"