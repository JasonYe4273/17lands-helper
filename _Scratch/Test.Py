from discord.ext import tasks

from messaging.message_sender import *
from messaging import message_sender
from data_handling.data_fetch import *
from global_vals.settings import load_set_config, load_defaults_config
from LocalToken import TOKEN


@tasks.loop(minutes=5)
async def refresh_data():
    load_set_config()
    load_defaults_config()
    updated = update_all_card_level_data()

    update_list = []
    for s in updated:
        for f in updated[s]:
            if updated[s][f]:
                update_list.append(f'{s} {f}')
    
    if len(update_list) != 0:
        message = "**Sets Updated:**\r\n\t" + '\r\n\t'.join(update_list)
        #await log(message)
        print(message)
        #sleep(60)


@CLIENT.event
async def on_ready():
    message_sender.init()
    await log("VIXI starting up!")
    cache_manamojis(CLIENT)
    print('Logged in as {0.user}'.format(CLIENT))
    load_all_data()
    refresh_data.start()
    

@CLIENT.event
async def on_message(message):
    # Don't parse own messages
    if message.author == CLIENT.user:
        return

    await send_response(message)
        
    # Be cordial.
    dm = str(message.channel.type) == 'private'
    if dm and 'thank' in message.content.lower():
        await send_message(message.channel, f"You're welcome, {str(message.author)[:-5]}")
            

if __name__ == "__main__":
    CLIENT.run(TOKEN)
    pass
