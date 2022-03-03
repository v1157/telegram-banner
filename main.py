import asyncio
import configparser
import datetime
import os
import random
from random import choice

import pandas as pd
from telethon import TelegramClient, errors, functions, types

IN_FOLDER = 'in'
TELEGRAM_SESSION_NAME = 'session_new'


class TextGenerator:
    @staticmethod
    def generate():
        first_part = [
            "Propaganda of the war in Ukraine. ",
            "Propaganda of the murder of Ukrainians and Ukrainian soldiers. ",
            "Dissemination of military personal data. ",
            "The channel undermines the integrity of the Ukrainian state. ",
            "Spreading fake news, misleading people. ",
            "Propaganda of violence and russian agression. ",
            "Dangerous fake news from russian propagandist against Ukraine. ",
        ]
        second_part = [
            "Block the channel! ",
            "Block it as soon as possible! ",
            "Ban this channel please ",
            "It would be helpful if you ban this channel ",
            "This channel is violating Telegram rules and must be stopped ",
        ]
        return choice(first_part) + choice(second_part)


async def run(tg_client):
    for file in os.listdir(IN_FOLDER):
        channels = []
        if file.endswith('.csv'):
            data = pd.read_csv(os.path.join(IN_FOLDER, file))
            data.sort_values(by=['priority'])
            df_grouped = data.groupby(['priority'], as_index=False)['channel'].agg(lambda x: list(x))['channel']
            for group in df_grouped:
                channels.extend(group)
        elif file.endswith('.txt'):
            with open(os.path.join(IN_FOLDER, file)) as infile:
                channels = infile.readlines()
        else:
            print(f'unsupported format for target file {file}')
            continue
        for channel in channels:
            channel = channel.replace('https://', '').replace('@', '').strip()
            try:
                result = await tg_client(functions.account.ReportPeerRequest(
                    peer=channel,
                    reason=types.InputReportReasonSpam(),
                    message=TextGenerator.generate())
                )
                print(channel, result)
            except ValueError:
                print("Channel not found")
            except errors.UsernameInvalidError:
                print("Nobody is using this username, or the username is unacceptable")
            except errors.FloodWaitError as e:
                print("Flood wait error. Waiting for ", str(datetime.timedelta(seconds=e.seconds)))
            await asyncio.sleep(10 + 2 * random.random())


if __name__ == '__main__':
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
        api_id = config['TelegramApi']['api_id']
        api_hash = config['TelegramApi']['api_hash']
    else:
        api_id = int(input("api id: "))
        api_hash = input("api hash: ")
        config['TelegramApi'] = {'api_id': api_id, 'api_hash': api_hash}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    client = TelegramClient(TELEGRAM_SESSION_NAME, api_id, api_hash)
    client.start()
    print('Bot started')
    with client:
        client.loop.run_until_complete(run(tg_client=client))
    asyncio.run(run(tg_client=client))
