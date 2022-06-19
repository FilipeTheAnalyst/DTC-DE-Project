from googleapiclient.discovery import build
import pandas as pd
import os
from datetime import datetime
import pyarrow

API_KEY = os.environ.get('API_KEY')

channel_ids = ['UCnz-ZXXER4jOvuED5trXfEA', # techTFQ
               'UCLLw7jmFsvfIVaUFsLs8mlQ', # Luke Barousse 
               'UCiT9RITQ9PW6BhXK0y2jaeg', # Ken Jee
               'UC7cs8q-gJRlGwj4A8OmCmXg', # Alex the analyst
               'UC2UXDak6o7rBm23k3Vv5dww', # Tina Huang
               'UCvZnwzmc3m1Eush-Or8Z6DA', # Shashank Kalanithi
               'UCq6XkhO5SZ66N04IcPbqNcw', # Keith Galli
               'UCW8Ews7tdKKkBT6GdtQaXvQ', # Nate StrataScratch
               'UCmLGJ3VYBcfRaWbP6JLJcpA', # Seattle Data Guy
               'UCV8e2g4IWQqK71bbzGDEI4Q'  # Data Professor
              ]

youtube = build('youtube', 'v3', developerKey=API_KEY)
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

CHANNEL_FILE = f'{AIRFLOW_HOME}/channels_' + datetime.now().strftime('%Y-%m-%d')+'.parquet'
VIDEO_FILE = f'{AIRFLOW_HOME}/videos_' + datetime.now().strftime('%Y-%m-%d')+'.parquet'

def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(part='snippet,contentDetails,statistics',id=','.join(channel_ids))
    response = request.execute()

    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                        Subscribers = response['items'][i]['statistics']['subscriberCount'],
                        Views = response['items'][i]['statistics']['viewCount'],
                        Total_videos = response['items'][i]['statistics']['videoCount'],
                        playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
                        Published_date = response['items'][i]['snippet']['publishedAt'],
                    )
        all_data.append(data)

    return all_data

# ### Create channel stats
channel_statistics = get_channel_stats(youtube,channel_ids)

# ### Convert channel stats into a pandas dataframe
channel_data = pd.DataFrame(channel_statistics)

# ### Convert the columns to the correct data type

channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])
channel_data['Published_date'] = pd.to_datetime(channel_data['Published_date'], format='%Y-%m-%d %H:%M:%S')

channel_data.dtypes

# ### Get playlists with all videos for each channel
playlist_id = channel_data['playlist_id']
playlist_id

# ### Function to get video ids from each channel
def get_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(part='contentDetails',playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()

    video_ids = []

    for i in range(len(response['items'])):
        video_ids_dict = dict(Video_id = response['items'][i]['contentDetails']['videoId'],
                                        Playlist_id = playlist_id)
        video_ids.append(video_ids_dict)

    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(part='contentDetails',playlistId = playlist_id,
            maxResults = 50, pageToken = next_page_token)
            response = request.execute()

            for i in range(len(response['items'])):
                video_ids_dict = dict(Video_id = response['items'][i]['contentDetails']['videoId'],
                                        Playlist_id = playlist_id)
                video_ids.append(video_ids_dict)

            next_page_token = response.get('nextPageToken')

    return video_ids

# #### Execute function for all channels and save in a list

video_ids = []
for video in range(len(playlist_id)):
    video_ids.append(get_video_ids(youtube, playlist_id[video]))

# ### Function to get video details from all channels
def get_video_details(youtube, video_ids):
    all_video_stats = []
    for channel in range(len(video_ids)):
        video_ids_values = [a_dict['Video_id'] for a_dict in video_ids[channel]]
        for i in range(0, len(video_ids_values), 50):
            request = youtube.videos().list(
                        part='snippet,statistics,contentDetails',
                        id = ','.join(video_ids_values[i:i+50]))
            response = request.execute()
            for video in response['items']:
                video_stats = dict(Video_id = video['id'],
                                    Title = video['snippet']['title'],
                                    Title_length = len(video['snippet']['title']),
                                    Title_word_count = len(video['snippet']['title'].split()),
                                    Published_date = video['snippet']['publishedAt'],
                                    Tags = video['snippet'].get('tags',[]),
                                    Tag_count = len(video['snippet'].get('tags',[])),
                                    Views = video['statistics']['viewCount'],
                                    Likes = video['statistics']['likeCount'],
                                    Comments = video['statistics']['commentCount'],
                                    Channel_name = video['snippet']['channelTitle'],
                                    Duration = video['contentDetails']['duration']
                                    )
                all_video_stats.append(video_stats)

    return all_video_stats

# #### Execute function for all channels and save in a list
video_details = get_video_details(youtube, video_ids)

# #### Save video details into a Dataframe
video_data = pd.DataFrame(video_details)

# ### Convert Duration from ISO 8601 date and time format using to_timedelta function

#video_data['Duration'] = pd.to_timedelta(video_data['Duration'])

# ### Convert object types columns to the correct type
video_data['Published_date'] = pd.to_datetime(video_data['Published_date'], format='%Y-%m-%d %H:%M:%S')
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])

# #### Remove timezone from Published Date
video_data['Published_date'] = video_data['Published_date'].dt.tz_convert(None)

channel_data.to_parquet(CHANNEL_FILE, engine='pyarrow')
video_data.to_parquet(VIDEO_FILE, engine='pyarrow')
