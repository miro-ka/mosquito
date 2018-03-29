import configargparse
import logging
import telegram


def run(token, chat_id):
    """
    Telegram bot connection
    """

    bot = telegram.Bot(token=token)
    logger = logging.getLogger(__name__)
    bot.send_message(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")
    logger.info(bot.get_me())
    """
    
        file = open('mosquito_stats.html', 'w')
        file.write(body)
        file.close()

        token = '572035357:AAEZ0na7xvdIUk53o9OTfLzwZkX52_nTAY4'
        chat_id = '406903247'
        bot = telegram.Bot(token=token)
        bot.send_document(chat_id=chat_id, document=open('mosquito_stats.html', 'rb'))
    """


if __name__ == '__main__':
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--telegram_token', help='Telegram token', required=True)
    arg_parser.add('--chat_id', help='Telegram Chat id', required=True)

    args = arg_parser.parse_known_args()[0]
    run(token=args.telegram_token, chat_id=args.chat_id)
