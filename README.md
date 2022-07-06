# Bot de Newsletter para Telegram

Este projeto implementa um bot simples para assinar o feed RSS do site [IFMG - Campus Formiga](https://formiga.ifmg.edu.br/). Em seguida, ele envia a notícia mais recente para o canal [Newsletter - IFMG Campus Formiga](https://t.me/ifmg_formiga_news), no Telegram.

# Execução

Para instanciar o bot, deve-se configurar as seguintes variáveis de ambiente:

- Linux

Configurando as variáveis de ambiente com _bash_:
```bash
$ export TOKEN="TOKEN-BOT-FATHER"
$ export CHAT_ID="ID-CANAL-DESEJADO"
$ export DEVELOPER_CHAT_ID="ID-CHAT-DO-PERFIL-DEV"
$ export MODE="MODO-DE-EXECUCAO"
```

- Windows

Configurando as variáveis de ambiente com _Powershell_:
```
PS C:\Windows\system32> $env:TOKEN="TOKEN-BOT-FATHER"
PS C:\Windows\system32> $env:CHAT_ID="ID-CANAL-DESEJADO"
PS C:\Windows\system32> $env:DEVELOPER_CHAT_ID="ID-CHAT-DO-PERFIL-DEV"
PS C:\Windows\system32> $env:MODE="MODO-DE-EXECUCAO"
```

`MODE` pode ser *"dev"* ou *"deploy"*. O primeiro envia as mensagens para o chat com o desenvolvedor, e o segundo para o chat desejado.

- Executando o bot:

Executando o bot:
```
python main.py
```