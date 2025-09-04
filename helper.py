from urlextract import URLExtract
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

# ------------------- FETCH STATS -------------------
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # total messages
    num_messages = df.shape[0]

    # total words
    words = []
    for message in df['message']:
        words.extend(message.split())
    total_words = len(words)

    # media messages
    num_media_messages = df[df['message'] == "<Media omitted>\n"].shape[0]

    # links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    total_links = len(links)

    return num_messages, total_words, num_media_messages, total_links

# ------------------- MOST BUSY USERS -------------------
def most_busy_users(df):
    # top 5 users by messages
    x = df['user'].value_counts().head()

    # percentage contribution
    new_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    new_df.columns = ['name', 'percent']

    return x, new_df

# ------------------- WORDCLOUD -------------------
def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # filter out notifications and media
    temps = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

    if temps.empty:
        return None  # no messages for this user

    # remove stopwords from messages
    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    temps['message'] = temps['message'].apply(remove_stop_words)

    # generate wordcloud
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temps['message'].str.cat(sep=" "))

    return df_wc

# ------------------- MOST COMMON WORDS -------------------
def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # ignore media messages
    temp = df[df['message'] != '<Media omitted>\n']

    if temp.empty:
        return pd.DataFrame(columns=['word', 'count'])

    # load stopwords
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    # top 20 words
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])

    return most_common_df

import pandas as pd
from collections import Counter
import emoji

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # ignore media messages
    temp = df[df['message'] != '<Media omitted>\n']

    emojis = []
    for message in temp['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    # if no emojis, return empty DataFrame
    if not emojis:
        return pd.DataFrame(columns=['emoji', 'count'])

    # create DataFrame with named columns
    emoji_df = pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])

    return emoji_df


def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap

