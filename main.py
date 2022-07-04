# Bot que envia mensagens com newsletter do IFMG Campus Formiga formatado.
import io
import os
import json
import logging
import requests
import xml.etree.ElementTree as ET
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

CHAT_ID = "---"
TOKEN = "---"


def requestUrl(url):
    try:
        req = requests.get(url)
        if req.status_code != 200:
            raise requests.ConnectionError(f'ERROR: a url \"{url}\" retornou o codigo {req.status_code}...')
    except requests.ConnectionError as ce:
        logging.error(ce)
        return None
    else:
        return req
    finally:
        req.close()


async def coroutine(context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Adquirindo XML de \"https://formiga.ifmg.edu.br/?format=feed&type=rss\"...")
    url = "https://formiga.ifmg.edu.br/?format=feed&type=rss"
    req = requestUrl(url)
    if req is not None:
        logging.info("Analisando XML adquirido...")

        tree = ET.parse(io.BytesIO(req.content))
        root = tree.getroot()

        items = list()
        # cached_file_name = 'news_cached.json'
        # if os.path.exists(cached_file_name):
        #     fp = open(cached_file_name, 'r')
        #     items = json.load(fp)
        #     items = [x for x in items.values()]
        #     fp.close()
        #
        # fp = open(cached_file_name, 'w+')

        rev = [i for i in root.iter('item') if not (i in items)]
        items = reversed(rev)

        # rev_vals = dict()
        # for v in range(len(rev)):
        #     rev_vals[v] = rev[v]
        #
        # for k, v in rev_vals.items():
        #     items[k] = v
        #
        # json.dump(items, fp)
        # fp.close()
        # items = rev_vals.values()

        for item in items:
            title = f"{item.find('title').text}"
            link = f"{item.find('link').text}"
            description = item.find('description').text.replace('\n','')
            print('dd:', description)

            #await context.bot.send_message(CHAT_ID, f"[{title}]({link})", parse_mode='Markdown')
        logging.info("Noticias mais recentes enviadas para o canal com sucesso!")
    else:
        logging.error(f"Algo deu errado ao requisitar a url \"{url}\"")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interval = 30  # em segundos
    logging.info(f"Configurando job_queue para enviar mensagens a cada {interval} segundos...")
    context.job_queue.run_repeating(coroutine, interval, chat_id=CHAT_ID, name=str(CHAT_ID))


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_jobs = context.job_queue.get_jobs_by_name(CHAT_ID)
    for job in current_jobs:
        job.schedule_removal()
    logging.info("job do envio de mensagens encerrado...")


def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stop', stop))
    app.run_polling()


if __name__ == '__main__':
    main()
