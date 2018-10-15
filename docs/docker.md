# Docker

## Быстрый старт

1. Сгенерировать ssl сертификат `server/ssl/gencert.sh`, если используем ssl, и скопировать его клиенту.

2. Сгенерировать `server/auth.digest` через `htpasswd` или онлайн генератором.

3. Скопировать в `server/nginx.conf` `nginx.conf.nossl`, если не пользуемся ssl.

4. Запустить ферму `docker-compose up`

5. Запустить клиент с флагом `--ssl`

---

Также можно подправить `server/nginx.conf` для вашего случая, а если не пользоваться ssl, то можно убрать `nginx` из `server/docker-compose.yml`
