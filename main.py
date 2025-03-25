import asyncio

from telethon import TelegramClient, events
from telethon.tl.types import PeerUser

# ====== Replace with your values ======
api_id =  12345               # Your API ID
api_hash = 'hashhere'     # Your API Hash
bot_token = '2309239023:tokenhere'  # Your Telegram bot token
notify_chat_id = 1234567     # Your user/chat ID to get notifications
# ======================================

# Store messages in-memory (chat_id -> message_id -> text)
message_store = {}

# Create client for your account
client = TelegramClient('PAssisstant_account', api_id, api_hash)

# Create client for bot (to send notifications)
bot = TelegramClient('PAssisstant_bot', api_id, api_hash).start(bot_token=bot_token)

async def notify(text):
    await bot.send_message(notify_chat_id, text)

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    if isinstance(event.message.peer_id, PeerUser):
        chat_id = event.message.chat_id
        msg_id = event.message.id
        text = event.message.message or ''
        
        if chat_id not in message_store:
            message_store[chat_id] = {}
        
        message_store[chat_id][msg_id] = text

@client.on(events.MessageEdited(incoming=True))
async def handle_edit(event):
    if isinstance(event.message.peer_id, PeerUser):
        chat_id = event.message.chat_id
        msg_id = event.message.id
        new_text = event.message.message or ''

        original_text = message_store.get(chat_id, {}).get(msg_id, '<original message not stored>')

        message_store[chat_id][msg_id] = new_text

        user = await event.get_sender()
        chat_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or str(chat_id)
        user_link = f"[{chat_name}](tg://user?id={user.id})"

        notify_text = (f"✏️ **Message Edited** in chat with {user_link}:\n\n"
                       f"**Original:**\n{original_text}\n"
                       f"**Edited:**\n{new_text}")

        await notify(notify_text)

@client.on(events.MessageDeleted())
async def handle_delete(event):
    for msg_id in event.deleted_ids:
        for chat_id, messages in message_store.items():
            if msg_id in messages:
                deleted_text = messages.pop(msg_id, '<message text unknown>')
                user = await client.get_entity(chat_id)
                chat_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or str(chat_id)
                user_link = f"[{chat_name}](tg://user?id={user.id})"

                notify_text = (f"🗑 **Message Deleted** in chat with {user_link}:\n\n"
                               f"**Deleted message:**\n{deleted_text}")

                await notify(notify_text)
                break


async def main():
    print("Client and bot started. Listening to private messages...")
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client.start()
    bot.start()
    loop.run_until_complete(main())
