FROM	nginx:stable-alpine

RUN		apk add --no-cache openssl

COPY	nginx.conf /etc/nginx/nginx.conf
COPY	docker-entrypoint.sh /usr/local/bin/start-nginx.sh

RUN 	chmod +x /usr/local/bin/start-nginx.sh \
		&& mkdir -p /etc/nginx/certs

EXPOSE	443

ENTRYPOINT [ "/bin/sh", "usr/local/bin/start-nginx.sh" ]