import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import emoji

st.set_page_config(layout="wide")
st.sidebar.title("WhatsApp Chat Analyzer")

# -------------------- Upload File --------------------
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    st.dataframe(df.head())

    # -------------------- Select User --------------------
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    # -------------------- Show Analysis --------------------
    if st.sidebar.button("Show Analysis"):

        # --- Fetch statistics ---
        num_messages, total_words, num_media, total_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(total_words)
        with col3:
            st.header("Media Shared")
            st.title(num_media)
        with col4:
            st.header("Links Shared")
            st.title(total_links)


        # --- Monthly Timeline ---
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation=45)
        plt.xlabel("Time")
        plt.ylabel("Number of Messages")
        st.pyplot(fig)


         # --- Daily Timeline ---
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='orange')
        plt.xticks(rotation=45)
        plt.xlabel("Date")
        plt.ylabel("Number of Messages")
        st.pyplot(fig)


        # --- Activity Map ---
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='green')
            plt.xlabel("Day")
            plt.ylabel("Number of Messages")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='purple')
            plt.xlabel("Month")
            plt.ylabel("Number of Messages")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # --- Most busy users (Overall only) ---
        if selected_user == 'Overall':
            st.title("Most Busy Users")
            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='red')
                ax.set_xticklabels(x.index, rotation=45)
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # --- WordCloud ---
        st.title("WordCloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc:
            fig, ax = plt.subplots()
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.warning(f"No messages to display for {selected_user}")

        # --- Most common words ---
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        if not most_common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(most_common_df['word'], most_common_df['count'], color='skyblue')
            ax.invert_yaxis()  # highest count on top
            plt.xlabel("Count")
            plt.ylabel("Words")
            st.pyplot(fig)
        else:
            st.warning(f"No words found for {selected_user}")

        # --- Emoji Analysis ---
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        if emoji_df is not None and not emoji_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(
                    emoji_df['count'].head(5),  # top 5 emojis
                    labels=emoji_df['emoji'].head(5),
                    autopct="%0.2f",
                    startangle=90
                )
                ax.axis('equal')  # make pie chart circular
                st.pyplot(fig)
        else:
            st.warning(f"No emojis found for {selected_user}")
        

        # --- Weekly Activity Heatmap ---
        st.title("Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        if not user_heatmap.empty:
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap, cmap="YlGnBu", ax=ax, )
            st.pyplot(fig)
        else:
            st.warning(f"No activity data to display for {selected_user}")
