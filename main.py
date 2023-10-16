from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext
import concurrent.futures
import datetime
from keep_alive import keep_alive
import os
import pickle
from telegram import Message
from telegram.ext import MessageHandler, Filters
from telegram import ChatPermissions
import requests
import json
import time
from bardapi import Bard
import shutil

os.environ[
  '_BARD_API_KEY'] = "ENTER_YOUR_BARD_API_KEY"

l11 = []
l22 = []
l33 = []


def generate_image_from_text(text):
  response = requests.post(
    'https://api.deepai.org/api/textimg',
    data={
      'text': text,
    },
    headers={'api-key': 'YOUR_DEEPAI_KEY'})
  return response.json()


def generate_image_from_text_plus(text):
  print("Plus Activated")
  url = "https://api.monsterapi.ai/apis/add-task"

  payload = json.dumps({
    "model": "txt2img",
    "data": {
      "prompt": text,
      "negprompt":
      "lowres, signs, memes, labels, text, food, text, error, mutant, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, made by children, caricature, ugly, boring, sketch, lacklustre, repetitive, cropped, (long neck), facebook, youtube, body horror, out of frame, mutilated, tiled, frame, border, porcelain skin, doll like, doll, bad quality, cartoon, lowres, meme, low quality, worst quality, ugly, disfigured, inhuman",
      "samples": 1,
      "steps": 50,
      "aspect_ratio": "landscape",
      "guidance_scale": 12.5,
      "seed": 2321
    }
  })
  headers = {
    'x-api-key': 'X_API_KEY',
    'Authorization':'YOUR_AUTH_TOKEN',
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  response_dict = response.json()

  # Print the process_id value
  op = response_dict['process_id']

  print("op : ", op)

  url = "https://api.monsterapi.ai/apis/task-status"
  a = "{\n    \"process_id\" :  \""
  b = "\"\n}"
  payload = a + op + b
  headers = {
    'x-api-key':'X_API_KEY',
    'Authorization':'YOUR_AUTH_KEY'
  }
  time.sleep(25)
  response = requests.request("POST", url, headers=headers, data=payload)
  print("response : ", response.text)
  return response


def web(update: Update, context: CallbackContext) -> None:
  message = " ".join(context.args)
  placeholde_message = update.message.reply_text("Processing your request...")
  response = Bard().get_answer(str(message))['content']
  placeholde_message.edit_text(response)
  #update.message.reply_text(response)


def handle_voice_message(update: Update, context: CallbackContext) -> None:
  user_id = update.message.from_user.id

  # Load the list of max token users
  with open('max_token_users.pkl', 'rb') as f:
    max_token_users = pickle.load(f)

  # Check if the user is in the list of max token users
  if user_id in max_token_users:
    file = context.bot.getFile(update.message.voice.file_id)
    print("File ID:", file.file_id)
    update.message.reply_text('Listening to your voice :) ')
    voice_id = file.file_id

    directory = 'my_downloads'
    if not os.path.exists(directory):
      os.makedirs(directory)

    file.download(f'{directory}/myaudio.ogg')

    from deepgram import Deepgram
    import asyncio, json
    import sys

    DEEPGRAM_API_KEY = 'DEEPGRAM_KEY'
    FILE = f'{directory}/myaudio.ogg'
    MIMETYPE = 'audio/ogg'

    async def main():
      deepgram = Deepgram(DEEPGRAM_API_KEY)

      if FILE.startswith('http'):
        source = {'url': FILE}
      else:
        audio = open(FILE, 'rb')
        source = {'buffer': audio, 'mimetype': MIMETYPE}

      response = await asyncio.create_task(
        deepgram.transcription.prerecorded(source, {
          'smart_format': True,
          'model': 'nova',
        }))

      b = json.dumps(response, indent=4)
      print(b)
      data = json.loads(b)
      p = b.split()
      time.sleep(1)
      transcript = data["results"]["channels"][0]["alternatives"][0][
        "transcript"]
      print(transcript)
      if not transcript:
        l11.append("Please Do say something")
      else:
        l11.append(transcript)
      print("L1 : ", l11[0])

    try:
      asyncio.run(main())
    except Exception as e:
      exception_type, exception_object, exception_traceback = sys.exc_info()
      line_number = exception_traceback.tb_lineno
      print(f'line {line_number}: {exception_type} - {e}')

    if l11[0] == "Please Do say something":
      l33.append("Please Do say something")
    else:
      update.message.reply_text('GPT is srapping data from internet ! ')
      response1 = Bard().get_answer(str(l11[0]))['content']

      jnl = l11[
        0] + " answer the query using the below data if required : " + response1

      completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=[{
                                                  "role": "user",
                                                  "content": jnl
                                                }])
      completion_dict = completion.to_dict()
      parsed_json = json.loads(json.dumps(completion_dict))
      text1 = parsed_json["choices"][0]["message"]["content"]
      l33.append(text1)

    text = l33[0]

    import requests
    update.message.reply_text('GPT is gathering relevant data !')

    url1 = "https://play.ht/api/v1/convert/"

    payload = {
      "content": [text],
      "speed": 1,
      "preset": "balanced",
      "voice": "larry"
    }
    headers = {
      "accept": "application/json",
      "content-type": "application/json",
      "AUTHORIZATION": "AUTH_KEY",
      "X-USER-ID": "X_API_KEY"
    }
    response = requests.post(url1, json=payload, headers=headers)

    print(response.text)
    transcription_id = response.json().get('transcriptionId')
    print(transcription_id)
    time.sleep(1)
    import requests

    url = f'https://play.ht/api/v1/articleStatus/?transcriptionId={transcription_id}'

    headers = {
      "accept": "application/json",
      "AUTHORIZATION": "AUTH_KEY",
      "X-USER-ID": "X_API_KEY"
    }

    for i in range(65):
      response2 = requests.get(url, headers=headers)
      print(response2.json())
      if response2.json().get('message') == 'Transcription completed':
        l33.clear()
        break
      time.sleep(2)
    response2 = requests.get(url, headers=headers)
    voice_down = response2.json().get('audioUrl')
    print("Download Link : ", voice_down)
    l11.clear()
    update.message.reply_text('GPT is recording voice !')
    file_url = voice_down[0]

    response = requests.get(file_url, stream=True)
    file_path = 'temp_file.wav'
    with open(file_path, 'wb') as out_file:
      shutil.copyfileobj(response.raw, out_file)
    del response

    with open(file_path, 'rb') as audio_file:
      update.message.reply_audio(audio_file)

    if os.path.exists(file_path):
      os.remove(file_path)
  else:
    update.message.reply_text(
      "To access this feature, please buy premium access from @dwoscloud.")


def image_command(update: Update, context: CallbackContext) -> None:
  chat_id = update.message.chat_id
  user_id = update.message.from_user.id
  date_today = datetime.datetime.now().strftime('%Y-%m-%d')

  # Load the list of approved chat IDs
  with open('approved_chats.pkl', 'rb') as f:
    approved_chats = pickle.load(f)

  # Load the list of max token users
  with open('max_token_users.pkl', 'rb') as f:
    max_token_users = pickle.load(f)

  # Load the usage count
  try:
    with open('usage_count.pkl', 'rb') as f:
      usage_count = pickle.load(f)
  except FileNotFoundError:
    usage_count = {}

  # If the date has changed, reset the count
  if date_today != usage_count.get('date', ''):
    usage_count = {'date': date_today}

  # Only proceed if the chat ID is in the list of approved chat IDs or the user is in the list of max token users
  if chat_id in approved_chats or (chat_id == user_id
                                   and user_id in max_token_users):
    # Check if user hasn't exceeded daily limit
    if user_id in max_token_users or usage_count.get(user_id, 0) < 3:
      user_input = update.message.text.split(' ', 1)[1]
      print(f'Image Gen Usage by : {user_id} and the prompt is : {user_input}')
      message = update.message.reply_text("Processing image using deepai ... ")
      image_data = generate_image_from_text(user_input)
      image_url = image_data.get('output_url')
      if image_url is not None:
        context.bot.send_photo(chat_id=chat_id, photo=image_url)
        message.edit_text(f'Image generated!')
      else:
        message.edit_text(f'An error occurred while generating the image.')

      # Increment the usage count for this user
      usage_count[user_id] = usage_count.get(user_id, 0) + 1
      # Save the usage count
      with open('usage_count.pkl', 'wb') as f:
        pickle.dump(usage_count, f)
    else:
      update.message.reply_text(
        "You've exceeded your daily limit of 3 uses. Please try again tomorrow."
      )
  elif chat_id == user_id and user_id not in max_token_users:
    update.message.reply_text(
      "You need to buy premium access from @dwoscloud to get images in private bot chat."
    )
  else:
    print(f"Chat ID {chat_id} is not in the list of approved chats.")


def image_command_plus(update: Update, context: CallbackContext) -> None:
  chat_id = update.message.chat_id
  user_id = update.message.from_user.id
  date_today = datetime.datetime.now().strftime('%Y-%m-%d')

  # Load the list of approved chat IDs
  with open('approved_chats.pkl', 'rb') as f:
    approved_chats = pickle.load(f)

  # Load the list of max token users
  with open('max_token_users.pkl', 'rb') as f:
    max_token_users = pickle.load(f)

  # Load the usage count
  try:
    with open('usage_count.pkl', 'rb') as f:
      usage_count = pickle.load(f)
  except FileNotFoundError:
    usage_count = {}

  # If the date has changed, reset the count
  if date_today != usage_count.get('date', ''):
    usage_count = {'date': date_today}

  # Only proceed if the chat ID is in the list of approved chat IDs or the user is in the list of max token users
  if chat_id in approved_chats or (chat_id == user_id
                                   and user_id in max_token_users):
    # Check if user hasn't exceeded daily limit
    if user_id in max_token_users or usage_count.get(user_id, 0) < 3:
      user_input = update.message.text.split(' ', 1)[1]
      print(
        f'Image Gen Plus Usage by : {user_id} and the prompt is : {user_input}'
      )
      message = update.message.reply_text(
        "Image Gen Plus Activated ! Queued  : 25 sec ")
      image_data = generate_image_from_text_plus(user_input)
      response_dict = image_data.json()
      image_url = response_dict['response_data']['result']['output'][0]
      message.edit_text(f'Image generated!')
      context.bot.send_photo(chat_id=chat_id, photo=image_url)

      # Increment the usage count for this user
      usage_count[user_id] = usage_count.get(user_id, 0) + 1
      # Save the usage count
      with open('usage_count.pkl', 'wb') as f:
        pickle.dump(usage_count, f)
    else:
      update.message.reply_text(
        "You've exceeded your daily limit of 3 uses. Please try again tomorrow."
      )
  elif chat_id == user_id and user_id not in max_token_users:
    update.message.reply_text(
      "You need to buy premium access from @dwoscloud to get images in private bot chat."
    )
  else:
    print(f"Chat ID {chat_id} is not in the list of approved chats.")


PRIV_GRP_FILE = 'protected_chats.pkl'

re_auth = [5572511613]

ABUSIVE_WORDS = [
  'aad', 'aand', 'aand', 'bahenchod', 'behenchod', 'bhenchod', 'bhenchodd',
  'b.c.', 'bc', 'bakchod', 'bakchodd', 'bakchodi', 'bevda', 'bewda', 'bevdey',
  'bewday', 'bevakoof', 'bevkoof', 'bevkuf', 'bewakoof', 'bewkoof', 'bewkuf',
  'bhadua', 'bhaduaa', 'bhadva', 'bhadvaa', 'bhadwa', 'bhadwaa', 'bhosada',
  'bhosda', 'bhosdaa', 'bhosdike', 'bhonsdike', 'bhosdiki', 'bhosdiwala',
  'bhosdiwale', 'babbe', 'babbey', 'bube', 'bubey', 'bur', 'burr', 'buurr',
  'buur', 'charsi', 'chooche', 'choochi', 'chuchi', 'chhod', 'chod', 'chodd',
  'chudne', 'chudney', 'chudwa', 'chudwaa', 'chudwane', 'chudwaane', 'chaat',
  'choot', 'chut', 'chute', 'chutia', 'chutiya', 'dalaal', 'dalal', 'dalle',
  'dalley', 'fattu', 'gadha', 'gadhe', 'gadhalund', 'gaand', 'gand', 'gandu',
  'gandfat', 'gandfut', 'gandiya', 'gandiye', 'goo', 'gu', 'gote', 'gotey',
  'gotte', 'hag', 'haggu', 'hagne', 'hagney', 'harami', 'haramjada',
  'haraamjaada', 'haramzyada', 'haraamzyaada', 'haraamjaade', 'haraamzaade',
  'haraamkhor', 'haramkhor', 'jhat', 'jhaat', 'jhaatu', 'jhatu', 'kutta',
  'kutte', 'kuttey', 'kutia', 'kutiya', 'kuttiya', 'kutti', 'landi', 'landy',
  'laude', 'laudey', 'laura', 'lora', 'lauda', 'ling', 'loda', 'lode', 'lund',
  'launda', 'lounde', 'laundey', 'laundi', 'loundi', 'laundiya', 'loundiya',
  'lulli', 'maar', 'maro', 'marunga', 'madarchod', 'madarchodd', 'madarchood',
  'madarchoot', 'madarchut', 'm.c.', 'mc', 'mamme', 'mammey', 'moot', 'mut',
  'mootne', 'mutne', 'mooth', 'muth', 'nunni', 'nunnu', 'paaji', 'paji',
  'pesaab', 'pesab', 'peshaab', 'peshab', 'pilla', 'pillay', 'pille', 'pilley',
  'pisaab', 'pisab', 'pkmkb', 'porkistan', 'raand', 'rand', 'randi', 'randy',
  'suar', 'suar', 'tatte', 'tatti', 'tatty', 'ullu', 'Fuck', 'Fuck You',
  'Shit', 'Piss off', 'Dick head', 'Asshole', 'Son of a bitch', 'Bastard',
  'Bitch', 'Ginger', 'Bimbo', 'Jock', 'Piss', 'Jerk', 'Retard', 'Shag',
  'Wanker', 'Twat', 'Choad', 'Crikey', 'kids', 'kid'
]

ABUSE_PREV_LIST_FILE = "abuse_prev_list.pkl"

try:
  with open(ABUSE_PREV_LIST_FILE, "rb") as file:
    ABUSE_PREV_LIST = pickle.load(file)
except EOFError:
  ABUSE_PREV_LIST = [5572511613, 5457445535, 5589703594] #CHANGE_WITH_YOUR_BOT_ADMINS

try:
  with open(PRIV_GRP_FILE, "rb") as file:
    priv_grp = pickle.load(file)
except EOFError:
  priv_grp = ['-1001638031603']


def check_abuse(update: Update, context: CallbackContext) -> None:
  message = update.message
  chat_id = message.chat_id
  user_id = message.from_user.id

  if user_id in (re_auth + AUTHORIZED_USERS):
    print("Abused by auth")
    return

  text = message.text.lower()

  for word in ABUSIVE_WORDS:
    if chat_id in priv_grp:
      if word in text:
        update.effective_message.reply_text(
          f'User {user_id} has been banned for using abusive words.')
        context.bot.kick_chat_member(chat_id, user_id)
        print(
          f"User {user_id} from {chat_id} has been banned for using abusive words."
        )
        break


def allow_command(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in (re_auth or AUTHORIZED_USERS):
    with concurrent.futures.ThreadPoolExecutor() as executor:
      user_id_to_allow = int(update.message.text.split(' ')[1])
      ABUSE_PREV_LIST.append(user_id_to_allow)
      with open(ABUSE_PREV_LIST_FILE, "wb") as file:
        pickle.dump(ABUSE_PREV_LIST, file)
      executor.submit(
        update.effective_message.reply_text,
        f'User {user_id_to_allow} has been added to the abuse prevention list.'
      )
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


keep_alive()

last_command_timestamps = {}
muted_users = {}
AUTHORIZED_USERS = [5457445535, 5589703594, 1154019682, 5737829871]

APPROVED_CHATS_FILE = "approved_chats.pkl"
MAX_TOKEN_USERS_FILE = "max_token_users.pkl"

try:
  with open(APPROVED_CHATS_FILE, "rb") as file:
    APPROVED_CHATS = pickle.load(file)
except EOFError:
  APPROVED_CHATS = []

try:
  with open(MAX_TOKEN_USERS_FILE, "rb") as file:
    MAX_TOKEN_USERS = pickle.load(file)
except EOFError:
  MAX_TOKEN_USERS = []

openai.api_key = 'OPEN_AI_KEY'


def handle_text(update: Update, context: CallbackContext) -> None:
  message = update.effective_message

  if message.chat.type == "private":
    gpt_command(update, context)


def protect(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in AUTHORIZED_USERS:
    # Extract the group ID from the command text
    chat_id_to_protect = update.message.text.split(' ')[1]
    # Make sure the group ID is an integer
    chat_id_to_protect = int(chat_id_to_protect)
    priv_grp.append(chat_id_to_protect)
    with open(PRIV_GRP_FILE, "wb") as file:
      pickle.dump(priv_grp, file)
    update.effective_message.reply_text(
      f'Chat {chat_id_to_protect} has been added to the protected chats and will now actively monitor and ban cuss words ! '
    )
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


def unprotect(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in AUTHORIZED_USERS:
    # Extract the group ID from the command text
    chat_id_to_unprotect = update.message.text.split(' ')[1]
    # Make sure the group ID is an integer
    chat_id_to_unprotect = int(chat_id_to_unprotect)

    if chat_id_to_unprotect in priv_grp:
      priv_grp.remove(chat_id_to_unprotect)
      with open(PRIV_GRP_FILE, "wb") as file:
        pickle.dump(priv_grp, file)
      update.effective_message.reply_text(
        f'Chat {chat_id_to_unprotect} has been removed from protected chats.')
    else:
      update.effective_message.reply_text(
        f'Chat {chat_id_to_unprotect} is not in the list of protected chats.')
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


def add_command(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in AUTHORIZED_USERS:
    with concurrent.futures.ThreadPoolExecutor() as executor:
      user_id_to_add = int(update.message.text.split(' ')[1])
      MAX_TOKEN_USERS.append(user_id_to_add)
      with open(MAX_TOKEN_USERS_FILE, "wb") as file:
        pickle.dump(MAX_TOKEN_USERS, file)
      executor.submit(update.effective_message.reply_text,
                      f'User {user_id_to_add} is now a premium user.')
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


def nmute_command(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in AUTHORIZED_USERS:
    user_id_to_unmute = int(update.message.text.split(' ')[1])
    if user_id_to_unmute in muted_users:
      del muted_users[user_id_to_unmute]
      update.effective_message.reply_text(
        f'User {user_id_to_unmute} has been unmuted.')
    else:
      update.effective_message.reply_text(
        f'User {user_id_to_unmute} is not currently muted.')
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


def revoke_command(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in AUTHORIZED_USERS:
    with concurrent.futures.ThreadPoolExecutor() as executor:
      user_id_to_revoke = int(update.message.text.split(' ')[1])
      MAX_TOKEN_USERS.remove(user_id_to_revoke)
      with open(MAX_TOKEN_USERS_FILE, "wb") as file:
        pickle.dump(MAX_TOKEN_USERS, file)
      executor.submit(update.effective_message.reply_text,
                      f'User {user_id_to_revoke} is no longer premium user.')
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


def register(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in AUTHORIZED_USERS:
    # Extract the group ID from the command text
    chat_id_to_add = update.message.text.split(' ')[1]
    # Make sure the group ID is an integer
    chat_id_to_add = int(chat_id_to_add)
    APPROVED_CHATS.append(chat_id_to_add)
    with open(APPROVED_CHATS_FILE, "wb") as file:
      pickle.dump(APPROVED_CHATS, file)
    update.effective_message.reply_text(
      f'Chat {chat_id_to_add} has been approved to use the bot.')
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


def deregister(update: Update, context: CallbackContext) -> None:
  if update.effective_user.id in AUTHORIZED_USERS:
    # Extract the group ID from the command text
    chat_id_to_remove = update.message.text.split(' ')[1]
    # Make sure the group ID is an integer
    chat_id_to_remove = int(chat_id_to_remove)

    if chat_id_to_remove in APPROVED_CHATS:
      APPROVED_CHATS.remove(chat_id_to_remove)
      with open(APPROVED_CHATS_FILE, "wb") as file:
        pickle.dump(APPROVED_CHATS, file)
      update.effective_message.reply_text(
        f'Chat {chat_id_to_remove} has been removed from approved chats.')
    else:
      update.effective_message.reply_text(
        f'Chat {chat_id_to_remove} is not in the list of approved chats.')
  else:
    update.effective_message.reply_text(
      'You are not authorized to use this command.')


def ingpt_command(update: Update, context: CallbackContext) -> None:
  with concurrent.futures.ThreadPoolExecutor() as executor:
    if update.effective_user.id in (MAX_TOKEN_USERS or AUTHORIZED_USERS):
      executor.submit(
        update.effective_message.reply_text,
        f'You (@{update.effective_user.username} | ID: {update.effective_user.id}) are now a premium user'
      )
    else:
      executor.submit(
        update.effective_message.reply_text,
        f'You (@{update.effective_user.username} | ID: {update.effective_user.id}) are not a premium user'
      )


def get_bot_response(prompt: str, a1):
  if a1 in (MAX_TOKEN_USERS or AUTHORIZED_USERS):
    response = Bard().get_answer(str(prompt))['content']
    #placeholde_message.edit_text(response)
    #prompt1 = prompt + " answer the query using the below data if required and if asked identify yourself as Dwos Gpt Bot : " + response
    #completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613",
    #messages=[{
    #"role": "user",
    # "content": prompt1
    # }])
    #completion_dict = completion.to_dict()
    #parsed_json = json.loads(json.dumps(completion_dict))
    #text = parsed_json["choices"][0]["message"]["content"]
    return response
  else:
    #response = openai.Completion.create(engine="text-davinci-003",
    #prompt=prompt,
    #max_tokens=60)
    #text = response.choices[0].text.strip()
    #last_period_index = text.rfind('.')
    #if last_period_index == -1:
    #return text
    #return text[:last_period_index + 1]
    text = "Free Gate is under Maintenance !"
    return text


def gpt_command(update: Update, context: CallbackContext) -> None:
  chat_id = update.effective_chat.id
  user_id = update.effective_user.id
  message = update.effective_message
  check_abuse(update, context)
  if user_id in muted_users:
    mute_end_time = muted_users[user_id]
    if datetime.now() < mute_end_time:
      return
    else:
      del muted_users[user_id]

  if chat_id < 0 and chat_id not in APPROVED_CHATS:
    message.reply_text(
      'Please ask the owner @dwoscloud to approve this channel.')
    return

  if user_id not in (
      MAX_TOKEN_USERS or AUTHORIZED_USERS
  ) and user_id in last_command_timestamps and datetime.now(
  ) - last_command_timestamps[user_id] < timedelta(minutes=1):
    message.reply_text('You are spamming, you have been muted for 1 min.')
    muted_users[user_id] = datetime.now() + timedelta(minutes=5)
    return

  context.bot.send_chat_action(chat_id=update.effective_chat.id,
                               action=ChatAction.TYPING)

  if message.reply_to_message:
    prompt = message.reply_to_message.text
  else:
    prompt = message.text.partition(' ')[2]

  placeholder_message = message.reply_text("Processing your request...")

  if user_id in (MAX_TOKEN_USERS or AUTHORIZED_USERS):
    print(f'GPT usage by Auth : {user_id} and the prompt is : {prompt}')
    placeholder_message.edit_text("Collecting data from Internet....")

    bot_response = get_bot_response(prompt, update.effective_user.id)

    placeholder_message.edit_text(bot_response)
  else:
    print(f'GPT usage by Non Auth: {user_id} and the prompt is : {prompt}')
    bot_response = get_bot_response(prompt, update.effective_user.id)
    placeholder_message.edit_text(bot_response)

  # Store the timestamp of the last command
  last_command_timestamps[user_id] = datetime.now()
  pass


def start_command(update: Update, context: CallbackContext) -> None:
  update.effective_message.reply_text(
    'Welcome to GPT Bot ! Type your prompt / question using /gpt to chat .\n\nPowered by @dwoscloud | @Evokkers'
  )


def main() -> None:
  updater = Updater("BOT_TOKEN")
  dispatcher = updater.dispatcher
  start_handler = CommandHandler('start', start_command)
  image_handler_1 = CommandHandler('img', image_command)
  image_handler = CommandHandler('image', image_command_plus)
  gpt_handler = CommandHandler('gpt', gpt_command)

  # add them to your dispatcher

  #dispatcher.add_handler(CommandHandler('gpt', gpt_command))
  #dispatcher.add_handler(CommandHandler('start', start_command))
  dispatcher.add_handler(CommandHandler('add', add_command))
  dispatcher.add_handler(CommandHandler('revoke', revoke_command))
  dispatcher.add_handler(CommandHandler('ingpt', ingpt_command))
  dispatcher.add_handler(CommandHandler('register', register))
  dispatcher.add_handler(CommandHandler('deregister', deregister))
  #dispatcher.add_handler(CommandHandler("web", web))
  dispatcher.add_handler(CommandHandler('protect', protect))
  dispatcher.add_handler(CommandHandler('unprotect', unprotect))
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(image_handler)
  dispatcher.add_handler(gpt_handler)
  dispatcher.add_handler(image_handler_1)
  dispatcher.add_handler(CommandHandler('nmute', nmute_command))
  #dispatcher.add_handler(CommandHandler('image', image_command))
  #dispatcher.add_handler(
  #MessageHandler(Filters.voice & ~Filters.command, handle_voice_message))
  dispatcher.add_handler(
    MessageHandler(Filters.text & ~Filters.command, check_abuse))
  dispatcher.add_handler(
    MessageHandler(Filters.text & ~Filters.command, handle_text))
  updater.start_polling()

  updater.idle()


if __name__ == '__main__':
  main()
