# Bot que envia mensagens com newsletter do IFMG Campus Formiga formatado.
import io
import os
import logging
import traceback
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

CHAT_ID = os.getenv("CHAT_ID")
TOKEN = os.getenv("TOKEN")
DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")


def requestUrl(url) -> requests.Response:
    try:
        req = requests.get(url)
        if req.status_code != 200:
            raise requests.ConnectionError(f'ERROR: a url \"{url}\" retornou o codigo {req.status_code}...')
    except requests.ConnectionError as ce:
        logging.error(ce)
        return None
    else:
        return req


async def error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    logging.error(tb_string)


async def send_debug_message(context: ContextTypes.DEFAULT_TYPE, message) -> None:
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def coroutine(context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://formiga.ifmg.edu.br/?format=feed&type=rss"
    logging.info(f"Adquirindo XML de \"{url}\"...")
    req = requestUrl(url)
    if req is not None:
        logging.info("Analisando XML adquirido...")
        tree = ET.parse(io.BytesIO(req.content))
        root = tree.getroot()
        
        fp = open('last_message_pubDate.txt', 'r')
        dt = fp.read().replace('\n', '')
        fp.close()
        logging.info(f'datetime da mensagem mais recente: {dt}')
        last_msg_date = datetime.strptime(dt, '%a, %d %b %Y %H:%M:%S %z')
        
        items = list(reversed([i for i in root.iter('item')]))  # último elem é o mais recente
        #items_dates = [x.find('pubDate').text for x in items]
        new_links = [x.find('link').text for x in items if datetime.strptime(x.find('pubDate').text, '%a, %d %b %Y %H:%M:%S %z') > last_msg_date]

        if DEVELOPER_CHAT_ID != '-1':
            await send_debug_message(context, f"items:{len(items)}\nnews_links:{len(new_links)}")

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

            if DEVELOPER_CHAT_ID != '-1':
                await context.bot.send_message(DEVELOPER_CHAT_ID, f"[{title}]({link})\n\nResumo:\n\n{description}",
                                               parse_mode=ParseMode.MARKDOWN)
            else:
                await context.bot.send_message(CHAT_ID, f"[{title}]({link})\n\nResumo:\n\n{description}",
                                               parse_mode=ParseMode.MARKDOWN)

        logging.info("Noticias mais recentes enviadas para o canal com sucesso!")
        if len(new_links) > 0:
            fp = open('last_message_pubDate.txt', 'w')
            fp.write(items[-1].find('pubDate').text)
            fp.close()
    else:
        logging.error(f"Algo deu errado ao requisitar a url \"{url}\"")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interval = 1200  # em segundos
    if DEVELOPER_CHAT_ID != '-1':
        interval = 20

    context.job_queue.run_repeating(coroutine, interval, chat_id=CHAT_ID,
                                    name=f'<JOB> Chat ID: {CHAT_ID} | '
                                         f'Developer Chat ID: {DEVELOPER_CHAT_ID} | '
                                         f'Interval (secs): {interval}'
                                    )
    await update.message.reply_text("Bot inicializado!")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_jobs = context.job_queue.get_jobs_by_name(CHAT_ID)

    if DEVELOPER_CHAT_ID != '-1':
        current_jobs = context.job_queue.get_jobs_by_name(DEVELOPER_CHAT_ID)

    for job in current_jobs:
        job.schedule_removal()

    logging.info("job do envio de mensagens encerrado...")

    await update.message.reply_text("Bot encerrado.")


def main() -> None:
    logging.info(f'Getting environment vars...')
    logging.info(f'CHAT_ID: {CHAT_ID}')
    logging.info(f'DEVELOPER_CHAT_ID: {DEVELOPER_CHAT_ID}')
    logging.info(f'TOKEN: {TOKEN}')

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stop', stop))
    app.add_error_handler(error)
    app.run_polling()


if __name__ == '__main__':
    main()
