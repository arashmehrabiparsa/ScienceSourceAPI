import os
import csv
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    channel_data = response['items'][0]['statistics']
    return {
        'subscriberCount': channel_data.get('subscriberCount', '0'),
        'viewCount': channel_data.get('viewCount', '0'),
        'videoCount': channel_data.get('videoCount', '0')
    }

import re

def analyze_channel(youtube, channel_id):
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50,
        type="video"
    )
    response = request.execute()
    video_count = 0
    literature_url_count = 0
    
    # List to store all found URLs
    literature_urls = []

    for video in response['items']:
        description = video['snippet'].get('description', '')
        # Extract URLs using regex
        urls = re.findall(r"(https?://(?:doi\.org|arxiv\.org|ncbi\.nlm\.nih\.gov|researchgate\.net|scholar\.google\.com)/\S+)", description)
        literature_urls.extend(urls)
        literature_url_count += len(urls)
        video_count += 1

    literature_url_ratio = literature_url_count / video_count if video_count > 0 else 0
    return {
        'video_count': video_count,
        'literature_url_count': literature_url_count,
        'literature_url_ratio': literature_url_ratio
    }

def main():
    print("Starting script...")

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "Desktop/client_secret_786623938253-lsdc687gb1kr4ag6vk8ceve1df4j9hbe.apps.googleusercontent.com.json"

    print(f"Using client secrets file: {client_secrets_file}")

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the YouTube API client
    youtube = build(api_service_name, api_version, credentials=creds)
    print("Successfully authenticated and built YouTube API client")

    # Benchmark channels
    benchmark_channels = {
        'Anton Petrov': 'UCciQ8wFcVoIIMi-lfu8-cjQ',
        'Merkarenicus': 'UCOHF79UD1z4AQiZq5nNUfEQ'
    }

    benchmark_stats = {}
    for name, channel_id in benchmark_channels.items():
        channel_stats = get_channel_stats(youtube, channel_id)
        analysis = analyze_channel(youtube, channel_id)
        benchmark_stats[name] = {**channel_stats, **analysis}

    # Calculate average benchmark metrics
    avg_subscriber_count = sum(int(stats['subscriberCount']) for stats in benchmark_stats.values()) / len(benchmark_stats)
    avg_literature_url_ratio = sum(stats['literature_url_ratio'] for stats in benchmark_stats.values()) / len(benchmark_stats)

    # Define your tags
    tags = ["#science", "#technology", "#tech", "#innovation", "#engineering", "#biotechnology", "#space", "#physics", 
            "#chemistry", "#biology", "#nasa", "#datascience", "#artificialintelligence", "#ai", "#robotics", "#coding", 
            "#programming", "#stem", "#research", "#healthtech", "#medtech", "#genomics", "#neuroscience", "#cybersecurity", 
            "#iot", "#5g", "#bigdata", "#machinelearning", "#deeplearning", "#ar", "#vr", "#cloudcomputing", "#renewableenergy", 
            "#climatechange", "#smarttech", "#edtech", "#nanotechnology", "#quantumcomputing", "#spacetech", 
            "#roboticprocessautomation", "#digitaltransformation", "#sustainabletech", "#foodtech", "#greentech", "#cleantech", 
            "#wearabletech", "#smarthome", "#smartcities", "#fintech", "#blockchain", "#cryptocurrency", "#bioinformatics", 
            "#bioengineering", "#environmentalscience", "#earthscience", "#astronomy", "#astrophysics", "#materialsscience", 
            "#marinebiology", "#geology", "#ecology", "#sciencenews", "#technews", "#futuretech", "#agritech", "#edtech", 
            "#spaceexploration", "#spaceresearch", "#techtrends", "#sciencefacts", "#techfacts", "#digitalhealth", 
            "#healthinformatics", "#energytech", "#braintech", "#quantumphysics", "#medicalscience", "#lifesciences", 
            "#computerscience", "#techadvances", "#sustainableenergy", "#spacemission", "#aiforgood", "#techstartups", 
            "#biotechresearch", "#environmentaltech", "#cleanenergy", "#techfuture", "#scienceinnovation", "#techinnovation", 
            "#aiandml", "#techworld"]

    channels_with_literature = []

    for tag in tags:
        try:
            # Search for channels
            request = youtube.search().list(
                part="snippet",
                type="channel",
                q=tag,
                maxResults=50
            )
            response = request.execute()

            for item in response["items"]:
                channel_id = item["snippet"]["channelId"]
                channel_title = item["snippet"]["title"]

                channel_stats = get_channel_stats(youtube, channel_id)
                analysis = analyze_channel(youtube, channel_id)

                # Compare to benchmark
                if (int(channel_stats['subscriberCount']) >= avg_subscriber_count * 0.1 and 
                    analysis['literature_url_ratio'] >= avg_literature_url_ratio * 0.5):
                    channels_with_literature.append({
                        'channel_title': channel_title,
                        'channel_id': channel_id,
                        'subscriber_count': channel_stats['subscriberCount'],
                        'video_count': analysis['video_count'],
                        'literature_url_count': analysis['literature_url_count'],
                        'literature_url_ratio': analysis['literature_url_ratio']
                    })

        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")

    # Save results
    with open("channels_with_literature.csv", 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['channel_title', 'channel_id', 'subscriber_count', 
                                                     'video_count', 'literature_url_count', 'literature_url_ratio'])
        writer.writeheader()
        writer.writerows(channels_with_literature)

    print("Script completed. Results saved in channels_with_literature.csv")

if __name__ == "__main__":
    main()
