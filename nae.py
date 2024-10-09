from pyrogram import Client, filters
from pytz import timezone
from datetime import datetime
import asyncio
import threading


api_id = "20319418"
api_hash = "bbd5da4fc6764ff98081b134fa8a6c7a"
session_string = "BACIVfMAMQcBgw0CAdh21VCf1NXBWRqUdQmQk1b8sRrZQ8mSRdSa1FLt52cVX4sPc1d-R5Id9U8FFKzLOBWfWAwR7dL3UQh_kR1z18br1CIaTrMwVeDCmXlzWaf67PFHGu6pdaq3E4tl84eBgNa-porJCgfPxViQvzjMiKD5PkKlIHinOBViMjTPl2BuHM0KfHMgsTl4qufIJyp-HHs6r9wI_5INXpidNyWM3U-MnhPInbDUkKH4GgyEtZx8UO9opR9Uclptv5TYflLs3jbIDVyjGZnvU5jfuHvEC8rwOuFBfyW1NXn6rm80EI9iCt6jL71WX5NHC1FxYd1Z3TEb0b4rJWmMVAAAAAGlAwwgAA"

app = Client("my_account", api_id=api_id, api_hash=api_hash, session_string=session_string)

target_timezone = timezone('Asia/Baghdad')

update_time_in_name = True
update_time_in_bio = True

decorations_list = [
    {'0': '𝟶', '1': '𝟷', '2': '𝟸', '3': '𝟹', '4': '𝟺', '5': '𝟻', '6': '𝟼', '7': '𝟽', '8': '𝟾', '9': '𝟿', ':': ':'}, # 0
    {'0': '𝟢', '1': '𝟣', '2': '𝟤', '3': '𝟥', '4': '𝟦', '5': '𝟧', '6': '𝟨', '7': '𝟩', '8': '𝟪', '9': '𝟫', ':': ':'}, # 1
    {'0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５', '6': '６', '7': '７', '8': '８', '9': '９', ':': ':'} # 2
]


decoration_choice = 1 # اختر هنا رقم الزغرفة من 0 الى 2
fixed_decorations = decorations_list[decoration_choice]

def get_decorated_time_string():
    now = datetime.now(target_timezone)
    time_str = now.strftime("%I:%M")
    
   
    if time_str.startswith('0'):
        time_str = time_str[1:]
    
    decorated_time = "".join(fixed_decorations.get(char, char) for char in time_str)
    return decorated_time
    
async def change_profile_name_and_bio():
    if update_time_in_name or update_time_in_bio:
        decorated_time = get_decorated_time_string()
        user_info = await app.get_me()
        existing_bio = user_info.bio if hasattr(user_info, 'bio') and user_info.bio else ""
        bio = f". {decorated_time} -" if update_time_in_bio else existing_bio
        profile_name = decorated_time if update_time_in_name else user_info.last_name

        await app.update_profile(
            last_name=profile_name,
            bio=bio
        )

@app.on_message(filters.command("ايقاف بايو وقتي") & filters.private)
def stop_bio(client, message):
    global update_time_in_bio
    update_time_in_bio = False
    message.reply("تحديث الوقت في بايو البروفايل غير مفعل.")

@app.on_message(filters.command("ايقاف اسم وقتي") & filters.private)
def stop_time(client, message):
    global update_time_in_name
    update_time_in_name = False
    message.reply("تحديث الوقت في اسم البروفايل غير مفعل.")
    
@app.on_message(filters.command("تشغيل بايو وقتي") & filters.private)
def start_bio(client, message):
    global update_time_in_bio
    update_time_in_bio = True
    message.reply("تحديث الوقت في بايو البروفايل مفعل.")

@app.on_message(filters.command("تشغيل اسم وقتي") & filters.private)
def start_time(client, message):
    global update_time_in_name
    update_time_in_name = True
    message.reply("تحديث الوقت في اسم البروفايل مفعل.")

@app.on_message(filters.photo | filters.video & filters.private)
async def handle_media(client, message):
    if message.photo:
        file = await message.download()
        caption = f"- تم حفظ الصـورة بنجاح .\n- من : @{message.from_user.username}" if message.from_user.username else "من: مستخدم مجهول"
        await client.send_photo("me", file, caption=caption)
    elif message.video:
        file = await message.download()
        caption = f"- تم حفظ الفيـديو بنجاح .\n- من : @{message.from_user.username}" if message.from_user.username else "من: مستخدم مجهول"
        await client.send_video("me", file, caption=caption)
    await client.send_message("me", "ـــــــــــــــــــــــــــــــــــــــــــــــــــ")

async def main():
    await app.start()

    while True:
        await change_profile_name_and_bio()
        await asyncio.sleep(60)

posting_threads = {}

def start_posting(group_id, message_text, interval):
    while group_id in posting_threads and posting_threads[group_id]['is_posting']:
        try:
            app.send_message(group_id, message_text)
        except Exception as e:
            print(f"Error while sending message: {e}")
        time.sleep(interval)

@app.on_message(filters.text & ~filters.private)
def handle_messages(client, message):
    global posting_threads

    text = message.text.strip()
    group_id = message.chat.id

    if text.startswith("ن"):
        try:
            message.delete()
        except Exception as e:
            print(f"Error while deleting message: {e}")

        try:
            content = text[1:].strip()
            *message_lines, interval_str = content.rsplit(" ", 1)
            message_text = " ".join(message_lines)
            interval = int(interval_str)
        except ValueError as ve:
            print(f"Error parsing message: {ve}")
            return

        if group_id in posting_threads and posting_threads[group_id]['is_posting']:
            return

        posting_threads[group_id] = {
            'is_posting': True,
            'message_text': message_text,
            'interval': interval,
            'thread': threading.Thread(target=start_posting, args=(group_id, message_text, interval))
        }
        posting_threads[group_id]['thread'].start()

    elif text == "ايقاف":
        try:
            message.delete()
        except Exception as e:
            print(f"Error while deleting message: {e}")

        if group_id not in posting_threads or not posting_threads[group_id]['is_posting']:
            return

        posting_threads[group_id]['is_posting'] = False
        if posting_threads[group_id]['thread']:
            posting_threads[group_id]['thread'].join()
            del posting_threads[group_id]

app.run(main())