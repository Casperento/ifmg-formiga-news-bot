# Bot que envia mensagens com newsletter do IFMG Campus Formiga formatado.
import io
import os
import logging
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

CHAT_ID = os.getenv("CHAT_ID")
TOKEN = os.getenv("TOKEN")


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
    url = "https://formiga.ifmg.edu.br/?format=feed&type=rss"
    logging.info(f"Adquirindo XML de \"{url}\"...")
    req = requestUrl(url)
    if req is not None:
        logging.info("Analisando XML adquirido...")

        tree = ET.parse(io.BytesIO(req.content))
        root = tree.getroot()
        items = list(reversed([i for i in root.iter('item')]))
        items_links = [x.find('link').text for x in items]
        new_links = items_links
        cached_file_name = 'news_cached.tmp'
        if os.path.exists(cached_file_name):
            fp = open(cached_file_name, 'r')
            cached = eval(fp.read())
            new_links = [x for x in items_links if x not in cached]
            fp.close()
        else:
            fp = open(cached_file_name, 'w')
            fp.write(str(new_links))
            fp.close()

        f_items = list(filter(lambda x: x.find('link').text in new_links, items))
        for node in f_items:
            title = str()
            description = str()
            link = str()
            for elem in node.iter():
                if not elem.tag == node.tag:
                    if elem.tag == 'title':
                        title = elem.text
                    elif elem.tag == 'description':
                        description = elem.text.replace('\n', '')
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.find_all('p')[1].text
                    elif elem.tag == 'link':
                        link = elem.text

            await context.bot.send_message(CHAT_ID, f"[{title}]({link})\n\nResumo:\n\n{description}",
                                           parse_mode='Markdown')

        logging.info("Noticias mais recentes enviadas para o canal com sucesso!")
    else:
        logging.error(f"Algo deu errado ao requisitar a url \"{url}\"")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interval = 12*3600  # em segundos
    logging.info(f"Configurando job_queue para enviar mensagens a cada {interval} segundos...")
    context.job_queue.run_repeating(coroutine, interval, chat_id=CHAT_ID, name=str(CHAT_ID))
    await update.message.reply_text("Bot inicializado!")


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
