server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'kingDoba'
token = 'oauth:wwmnp95ew8qge8q3edmq5mbkarwkky'
#Select channel to monitor
channel = '#sodapoppin'

#To establish a connection to Twitch IRC we'll be using Python's socket library. First we need to instantiate a socket:
import socket


sock = socket.socket()
#Next we'll connect this socket to Twitch by calling `connect()` with the `server` and `port` we defined above:
sock.connect((server, port))

#With sockets, we need to `send()` these parameters as encoded strings:
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))


#Receiving channel messages
resp = sock.recv(2048).decode('utf-8')


### Writing messages to a file

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('chat.log', encoding='utf-8')])


logging.info(resp)


## Continuous message writing

from emoji import demojize

while True:
    resp = sock.recv(2048).decode('utf-8')

    if resp.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))
    
    elif len(resp) > 0:
        logging.info(demojize(resp))
        
        
        
#Parsing Logs
import pandas as pd
import datetime
import re
import TextBlob


def get_chat_dataframe(file):
    data = []

    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n\n')

        for line in lines:
            try:
                time_logged = line.split('—')[0].strip()
                print(time_logged)
                time_logged = datetime.strptime(time_logged, '%Y-%m-%d_%H:%M:%S')

                username_message = line.split('—')[1:]
                username_message = '—'.join(username_message).strip()
                print(username_message)


                username, channel, message = re.search(
                        ':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', username_message
                ).groups()

                d = {
                    'dt': time_logged,
                    'channel': channel,
                    'username': username,
                    'message': message
                }

                data.append(d)

            except Exception:
                pass

    return pd.DataFrame().from_records(data)

df = get_chat_dataframe('chat.log')


df.set_index('dt', inplace=True)

print(df.shape)

df.head()



df['polarity'] = df['message'].apply(lambda tweet: TextBlob(tweet).polarity)
df.head()

#Remove stop words
content = ' '.join(df["message"])
content = re.sub(r"http\S+", "", content)
content = content.replace('RT ', ' ').replace('&amp;', 'and')
content = re.sub('[^A-Za-z0-9]+', ' ', content)
content = content.lower()

import nltk
nltk.download('punkt')
nltk.download('stopwords')


from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
tokenized_word = word_tokenize(content)
stop_words=set(stopwords.words("english"))
filtered_sent=[]
for w in tokenized_word:
    if w not in stop_words:
        filtered_sent.append(w)
fdist = FreqDist(filtered_sent)
fd = pd.DataFrame(fdist.most_common(10),                    \
    columns = ["Word","Frequency"]).drop([0]).reindex()