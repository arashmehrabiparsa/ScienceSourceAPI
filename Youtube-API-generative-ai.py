import scipy
import os
import csv
import pickle
import time
import random
import json
import re
import logging
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
MAX_DAILY_REQUESTS = 9900

def get_seconds_until_reset():
    now = datetime.now()
    reset_time = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    return (reset_time - now).total_seconds()

def load_request_count():
    try:
        with open('request_count.json', 'r') as f:
            data = json.load(f)
            if datetime.fromisoformat(data['date']) < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                return 0
            return data['count']
    except FileNotFoundError:
        return 0

def save_request_count(count):
    with open('request_count.json', 'w') as f:
        json.dump({'date': datetime.now().isoformat(), 'count': count}, f)

def increment_request_count():
    global request_count
    request_count += 1
    save_request_count(request_count)
    if request_count >= MAX_DAILY_REQUESTS:
        logging.error("Daily quota limit reached")
        raise Exception("Daily quota limit reached")

def exponential_backoff(attempt):
    return min(32, 2 ** attempt) + random.uniform(0, 1)

def retry_with_backoff(func, max_retries=5, initial_delay=60):
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                increment_request_count()
                return func(*args, **kwargs)
            except HttpError as e:
                if e.resp.status in [403, 429] and 'quota' in str(e):
                    logging.error("Quota exceeded. Stopping execution.")
                    # Save progress with necessary arguments
                    save_progress(*args, **kwargs)
                    delay = initial_delay * (2 ** attempt)
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    if attempt == max_retries - 1:
                        time_to_wait = get_seconds_until_reset()
                        logging.info(f"Max retries reached. Waiting for {time_to_wait} seconds until quota is reset...")
                        time.sleep(time_to_wait)
                    continue
                elif e.resp.status in [500, 503]:
                    if attempt == max_retries - 1:
                        raise
                    delay = exponential_backoff(attempt)
                    logging.info(f"Attempt {attempt + 1} failed. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    raise
        raise Exception("Max retries reached")
    return wrapper

def save_progress(processed_tags, current_tag, processed_channels):
    with open('checkpoint.json', 'w') as f:
        json.dump({
            'processed_tags': processed_tags,
            'current_tag': current_tag,
            'processed_channels': list(processed_channels)  # Ensure it's serializable
        }, f)

def load_checkpoint():
    try:
        with open('checkpoint.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@retry_with_backoff
def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(part="snippet,statistics", id=channel_id)
    response = request.execute()
    channel_data = response['items'][0]['statistics']
    return {
        'subscriberCount': channel_data.get('subscriberCount', '0'),
        'viewCount': channel_data.get('viewCount', '0'),
        'videoCount': channel_data.get('videoCount', '0')
    }

@retry_with_backoff
def analyze_channel(youtube, channel_id):
    request = youtube.search().list(part="snippet", channelId=channel_id, maxResults=50, type="video")
    response = request.execute()
    video_count = 0
    literature_url_count = 0
    literature_urls = []
    
    for video in response['items']:
        description = video['snippet'].get('description', '')
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
    global request_count
    logging.info("Starting script...")
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "/Users/Guest2/Personal/Github/client_secret_786623938253-lsdc687gb1kr4ag6vk8ceve1df4j9hbe.apps.googleusercontent.com.json"
    logging.info(f"Using client secrets file: {client_secrets_file}")

    # Initialize request_count
    request_count = load_request_count()

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube = build(api_service_name, api_version, credentials=creds)
    logging.info("Successfully authenticated and built YouTube API client")

    benchmark_channels = {
        'Anton Petrov': 'UCciQ8wFcVoIIMi-lfu8-cjQ',
        'Merkarenicus': 'UCOHF79UD1z4AQiZq5nNUfEQ'
    }

    benchmark_stats = {}
    for name, channel_id in benchmark_channels.items():
        channel_stats = get_channel_stats(youtube, channel_id)
        analysis = analyze_channel(youtube, channel_id)
        benchmark_stats[name] = {**channel_stats, **analysis}

    avg_subscriber_count = sum(int(stats['subscriberCount']) for stats in benchmark_stats.values()) / len(benchmark_stats)
    avg_literature_url_ratio = sum(stats['literature_url_ratio'] for stats in benchmark_stats.values()) / len(benchmark_stats)

    tags = [
        "#science", "#technology", "#space", "#physics", "#biology", "#tech", "#innovation", "#engineering", "#biotechnology",
        "#nasa", "#datascience", "#artificialintelligence", "#ai", "#robotics", "#coding", "#programming", "#stem", "#research",
        "#healthtech", "#medtech", "#genomics", "#neuroscience", "#cybersecurity", "#iot", "#5g", "#bigdata", "#machinelearning",
        "#deeplearning", "#ar", "#vr", "#cloudcomputing", "#renewableenergy", "#climatechange", "#smarttech", "#edtech",
        "#nanotechnology", "#quantumcomputing", "#spacetech", "#roboticprocessautomation", "#digitaltransformation", "#sustainabletech",
        "#foodtech", "#greentech", "#cleantech", "#wearabletech", "#smarthome", "#smartcities", "#fintech", "#blockchain", 
        "#cryptocurrency", "#bioinformatics", "#bioengineering", "#environmentalscience", "#earthscience", "#astronomy",
        "#astrophysics", "#materialsscience", "#marinebiology", "#geology", "#ecology", "#sciencenews", "#technews",
        "#futuretech", "#agritech", "#edtech", "#spaceexploration", "#spaceresearch", "#techtrends", "#sciencefacts",
        "#techfacts", "#digitalhealth", "#healthinformatics", "#energytech", "#braintech", "#quantumphysics",
        "#medicalscience", "#lifesciences", "#computerscience", "#techadvances", "#sustainableenergy", "#spacemission",
        "#aiforgood", "#techstartups", "#biotechresearch", "#environmentaltech", "#cleanenergy", "#techfuture",
        "#scienceinnovation", "#techinnovation", "#aiandml", "#techworld", "#nac", "#glutathione", "#health", "#stemcells",
        "#inflammation", "#reverseaging", "#resveratrol", "#miconazole", "#dementia", "#inflammation", "#freeenergyprinciple",
        "#activeinference", "#brain", "#prediction", "#miconazole", "#dementia", "#inflammation", "#BacopaMonnieri", "#ginseng", 
        "#circumin", "#circuminoids", "#quercetin", "#gingkobilboa", "#nad", "#alphalinoleic", "#scfa", "#flavonoids", 
        "#ROS", "#inflammation",  "#taurine",  "#SIRT1",  "#resveratrol", "#NADH", "#NAD" 
    ]

    channels_with_literature = []

    checkpoint = load_checkpoint()
    if checkpoint:
        processed_tags = checkpoint['processed_tags']
        current_tag = checkpoint['current_tag']
        processed_channels = set(checkpoint['processed_channels'])
    else:
        processed_tags = []
        current_tag = None
        processed_channels = set()

    if not processed_tags:
        processed_tags = tags

    for tag in processed_tags:
        if current_tag and tag != current_tag:
            logging.info(f"Skipping tag: {tag}")
            continue

        search_request = youtube.search().list(q=tag, type="channel", part="id", maxResults=50)
        search_response = search_request.execute()
        channels = search_response['items']

        for channel in channels:
            channel_id = channel['id']['channelId']
            if channel_id in processed_channels:
                continue

            logging.info(f"Processing channel ID: {channel_id} for tag: {tag}")
            stats = get_channel_stats(youtube, channel_id)
            analysis = analyze_channel(youtube, channel_id)
            subscriber_count = int(stats['subscriberCount'])
            literature_url_ratio = analysis['literature_url_ratio']

            if subscriber_count >= avg_subscriber_count and literature_url_ratio >= avg_literature_url_ratio:
                channels_with_literature.append({
                    'channel_id': channel_id,
                    'tag': tag,
                    'subscriber_count': subscriber_count,
                    'literature_url_ratio': literature_url_ratio
                })

            processed_channels.add(channel_id)
            save_progress(processed_tags, tag, processed_channels)

    with open('channels_with_literature.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Channel ID', 'Tag', 'Subscriber Count', 'Literature URL Ratio'])
        for channel in channels_with_literature:
            writer.writerow([channel['channel_id'], channel['tag'], channel['subscriber_count'], channel['literature_url_ratio']])

    logging.info("Script finished successfully")

if __name__ == '__main__':
    main()