import pandas as pd
import re

def preprocess(data):
    pattern = re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[ap]m\s-\s)')
    split_data = re.split(pattern, data)

    # Messages are at even indexes starting from 2
    messages = [split_data[i] for i in range(2, len(split_data), 2)]
    # Dates are the matched patterns
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    cleaned_messages = []

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name exists
            users.append(entry[1])
            cleaned_messages.append(" ".join(entry[2:]))
        else:  # system/group notification
            users.append('group_notification')
            cleaned_messages.append(entry[0])

    df['user'] = users
    df['message'] = cleaned_messages
    df.drop(columns=['user_message'], inplace=True)

    # Extra datetime features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # ✅ Add period column for heatmap
    def get_period(hour):
        if hour == 23:
            return f"{hour}-00"
        elif hour == 0:
            return "00-1"
        else:
            return f"{hour}-{hour+1}"

    df['period'] = df['hour'].apply(get_period)

    return df
