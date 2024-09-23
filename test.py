import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import re
import csv

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()
    return response['items'][0]['statistics']

def analyze_channel(youtube, channel_id):
    videos_request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        maxResults=50
    )
    videos_response = videos_request.execute()

    literature_urls = []
    video_count = 0

    for video in videos_response["items"]:
        video_id = video["id"]["videoId"]
        video_request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        video_response = video_request.execute()
        description = video_response["items"][0]["snippet"]["description"]

        urls = re.findall(r"(https?://(?:doi\.org|arxiv\.org|ncbi\.nlm\.nih\.gov|researchgate\.net|scholar\.google\.com)/\S+)", description)
        literature_urls.extend(urls)
        video_count += 1

    return {
        'video_count': video_count,
        'literature_url_count': len(literature_urls),
        'literature_url_ratio': len(literature_urls) / video_count if video_count > 0 else 0
    }

def main():
    print("Starting script...")

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import re
import csv

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()
    return response['items'][0]['statistics']

def analyze_channel(youtube, channel_id):
    videos_request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        maxResults=50
    )
    videos_response = videos_request.execute()

    literature_urls = []
    video_count = 0

    for video in videos_response["items"]:
        video_id = video["id"]["videoId"]
        video_request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        video_response = video_request.execute()
        description = video_response["items"][0]["snippet"]["description"]

        urls = re.findall(r"(https?://(?:doi\.org|arxiv\.org|ncbi\.nlm\.nih\.gov|researchgate\.net|scholar\.google\.com)/\S+)", description)
        literature_urls.extend(urls)
        video_count += 1

    return {
        'video_count': video_count,
        'literature_url_count': len(literature_urls),
        'literature_url_ratio': len(literature_urls) / video_count if video_count > 0 else 0
    }

def main():
    print("Starting script...")

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "Desktop/client_secret_786623938253-lsdc687gb1kr4ag6vk8ceve1df4j9hbe.apps.googleusercontent.com.json"  # Update this path

    print(f"Using client secrets file: {client_secrets_file}")

    try:
        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
        print("Successfully authenticated and built YouTube API client")
    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        return

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
    main()  # Update this path

    print(f"Using client secrets file: {client_secrets_file}")

    try:
        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
        print("Successfully authenticated and built YouTube API client")
    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        return

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