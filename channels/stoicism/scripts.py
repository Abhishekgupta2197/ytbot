import requests
from groq import Groq
import random
import json
import re
import sys
sys.path.append('/home/ubuntu/ytbot')
from config import GROQ_API_KEY

def get_trending_topics():
    print("🌐 Searching Reddit for trending stoicism topics...")
    try:
        headers = {"User-Agent": "YTBot/1.0"}
        subreddits = ["stoicism", "selfimprovement", "Marcus_Aurelius", "philosophy"]
        posts = []
        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=10"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for post in data["data"]["children"]:
                    title = post["data"]["title"]
                    if len(title) > 20:
                        posts.append(title)
        if posts:
            topic = random.choice(posts)
            print(f"✅ Found topic: {topic}")
            return topic
    except Exception as e:
        print(f"⚠️ Reddit search failed: {e}")

    fallbacks = [
        "Marcus Aurelius lessons on handling difficult people",
        "Stoic secrets to mental strength",
        "How to stop caring what people think",
        "The stoic way to deal with failure",
        "Why stoics never get angry",
        "Ancient wisdom that still works today",
        "How Marcus Aurelius dealt with pain",
        "Stoic habits that change your life",
        "Why most people will never be mentally strong",
        "The stoic secret to inner peace"
    ]
    topic = random.choice(fallbacks)
    print(f"✅ Using fallback topic: {topic}")
    return topic

def generate_script(topic):
    print("🤖 Generating AI script with Groq...")
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""You are a viral YouTube Shorts script writer for stoicism and mindset content.
Write a 30-40 second script about: {topic}
Rules:
- Start with a powerful stoic truth or quote
- 3-5 practical stoic lessons
- End with a call to follow for daily stoic wisdom
- NO apostrophes commas colons periods or special characters in script field
- Short punchy sentences
- Speak directly to viewer
- Reference Marcus Aurelius Seneca or Epictetus where relevant
Return ONLY this raw JSON no markdown no backticks:
{{"title": "title here", "hook": "hook here", "script": "full script here"}}"""

    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = message.choices[0].message.content.strip()
    print(f"🔍 Raw: {response_text[:80]}...")
    response_text = re.sub(r'[\x00-\x1f\x7f]', ' ', response_text)
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    if start == -1 or end == 0:
        raise Exception("No JSON found in response")
    response_text = response_text[start:end]
    data = json.loads(response_text)
    print(f"✅ Script generated: {data['title']}")
    return data["title"], data["hook"], data["script"]

def get_script():
    topic = get_trending_topics()
    return generate_script(topic)
