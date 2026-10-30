# Desenvolvimento local

O servidor `pdm dev` atende em HTTP: `http://127.0.0.1:8000/admin/`.

Configure `DEBUG=true` e `SECURE_SSL_REDIRECT=false` apenas no `.env` local, reinicie o Django e use o prefixo `http://` no navegador. O erro `ERR_SSL_PROTOCOL_ERROR` indica tentativa de HTTPS em um servidor HTTP. Se o Chrome insistir em HTTPS, desative temporariamente o modo de conexões sempre seguras para localhost ou limpe a política HSTS local.

O cadastro padrão exige ativação por e-mail. Com `DEBUG=true`, o link de confirmação aparece no terminal do Django; abra o link antes do login.
