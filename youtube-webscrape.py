import scipy
import feedparser
import re
import csv
from urllib.parse import urlparse, parse_qs
from pulp import *

def get_channel_id_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'www.youtube.com':
        if parsed_url.path == '/channel/':
            return parsed_url.path.split('/')[-1]
        elif parsed_url.path == '/user/':
            # Note: This won't always work as usernames don't always correspond to channel IDs
            return parsed_url.path.split('/')[-1]
    return None

def search_channels_by_tag(tag):
    url = f"https://www.youtube.com/feeds/videos.xml?search_query={tag}"
    feed = feedparser.parse(url)
    
    print(f"Feed entries for tag {tag}: {len(feed.entries)}")
    
    channels = set()
    for entry in feed.entries:
        channel_id = get_channel_id_from_url(entry.author_detail.href)
        if channel_id:
            channels.add(channel_id)
        else:
            print(f"Couldn't extract channel ID from {entry.author_detail.href}")
    
    return list(channels)

def get_channel_videos(channel_id):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(url)
    
    videos = []
    for entry in feed.entries:
        video = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'description': entry.summary
        }
        videos.append(video)
    
    return videos

def analyze_channel(channel_id):
    videos = get_channel_videos(channel_id)
    literature_url_count = 0
    
    for video in videos:
        urls = re.findall(r"(https?://(?:doi\.org|arxiv\.org|ncbi\.nlm\.nih\.gov|researchgate\.net|scholar\.google\.com)/\S+)", video['description'])
        literature_url_count += len(urls)
    
    literature_url_ratio = literature_url_count / len(videos) if videos else 0
    return {
        'video_count': len(videos),
        'literature_url_count': literature_url_count,
        'literature_url_ratio': literature_url_ratio
    }

def main():
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
    total_channels_found = 0

    for tag in tags:
        print(f"Searching for channels with tag: {tag}")
        channels = search_channels_by_tag(tag)
        total_channels_found += len(channels)
        print(f"Found {len(channels)} channels for tag {tag}")
        
        for channel_id in channels:
            print(f"Analyzing channel: {channel_id}")
            try:
                analysis = analyze_channel(channel_id)
                print(f"Analysis results: {analysis}")
                
                # Include all channels that have at least one literature URL
                if analysis['literature_url_count'] > 0:
                    channels_with_literature.append({
                        'channel_id': channel_id,
                        'tag': tag,
                        'video_count': analysis['video_count'],
                        'literature_url_count': analysis['literature_url_count'],
                        'literature_url_ratio': analysis['literature_url_ratio']
                    })
            except Exception as e:
                print(f"Error analyzing channel {channel_id}: {str(e)}")

    print(f"Total channels found: {total_channels_found}")
    print(f"Channels with literature: {len(channels_with_literature)}")

    with open('channels_with_literature.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Channel ID', 'Tag', 'Video Count', 'Literature URL Count', 'Literature URL Ratio'])
        for channel in channels_with_literature:
            writer.writerow([
                channel['channel_id'], 
                channel['tag'], 
                channel['video_count'], 
                channel['literature_url_count'],
                channel['literature_url_ratio']
            ])

    print("Analysis complete. Results saved to channels_with_literature.csv")

if __name__ == '__main__':
    main()




    