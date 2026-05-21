import os
import feedparser
import requests
import time
import schedule
import re
from datetime import datetime

# ============================================================
#   SK AFFILIATE HUB BOT - CONFIGURATION
#   இங்க உங்க details fill பண்ணுங்க
# ============================================================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

TELEGRAM_CHANNEL_ID = "-1001222483575"

AMAZON_AFFILIATE_TAG = "saravanakmr97-21"

# ============================================================
#   AMAZON RSS FEEDS - Different Categories
# ============================================================

RSS_FEEDS = [
    
{
        "name": "Desidime Hot Deals",
        "url": "https://www.desidime.com/feed",
        "emoji": "🔥"
    },
    {
        "name": "Desidime Electronics",
        "url": "https://www.desidime.com/deals/electronics.rss",
        "emoji": "📱"
    },
    {
        "name": "Desidime Fashion",
        "url": "https://www.desidime.com/deals/fashion.rss",
        "emoji": "👗"
    },
    {
        "name": "Desidime Home",
        "url": "https://www.desidime.com/deals/home-kitchen.rss",
        "emoji": "🏠"
    },
    {
        "name": "Desidime Beauty",
        "url": "https://www.desidime.com/deals/health-beauty.rss",
        "emoji": "💄"
    }
    ]

# ============================================================
#   ALREADY POSTED LINKS TRACKER (Duplicate avoid பண்ண)
# ============================================================

posted_links = set()

# ============================================================
#   AFFILIATE TAG ADD FUNCTION
# ============================================================

def add_affiliate_tag(url):
    """Amazon URL-ல affiliate tag add பண்ணும்"""
    if not url:
        return url
    
    # Clean the URL
    url = url.split("?")[0]  # Remove existing params
    
    # Extract ASIN if possible
    asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if asin_match:
        asin = asin_match.group(1)
        return f"https://www.amazon.in/dp/{asin}?tag={AMAZON_AFFILIATE_TAG}"
    
    # If no ASIN, just add tag
    return f"{url}?tag={AMAZON_AFFILIATE_TAG}"

# ============================================================
#   TELEGRAM MESSAGE SEND FUNCTION
# ============================================================

def send_telegram_message(message):
    """Telegram channel-ல message send பண்ணும்"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Message sent successfully at {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"❌ Failed: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================================
#   RSS FEED FETCH & POST FUNCTION
# ============================================================

def fetch_and_post_deals():
    """RSS Feed-லிருந்து deals fetch பண்ணி post பண்ணும்"""
    print(f"\n🔄 Fetching deals at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    posted_count = 0
    
    for feed_info in RSS_FEEDS:
        try:
            print(f"📡 Fetching: {feed_info['name']}")
            feed = feedparser.parse(feed_info["url"])
            
            if not feed.entries:
                print(f"  ⚠️ No entries found")
                continue
            
            # First 2 items மட்டும் per feed
            for entry in feed.entries[:2]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                
                if not title or not link:
                    continue
                
                # Duplicate check
                if link in posted_links:
                    continue
                
                # Affiliate tag add
                affiliate_link = add_affiliate_tag(link)
                
                # Message format
                message = (
                    f"{feed_info['emoji']} <b>SK Affiliate Hub</b>\n\n"
                    f"🛒 <b>{title}</b>\n\n"
                    f"🏷️ <b>Amazon India Deal</b>\n\n"
                    f"👇 <b>Buy Now:</b>\n"
                    f"{affiliate_link}\n\n"
                    f"⚡ Limited time offer!\n"
                    f"📢 @SKAffiliateHub"
                )
                
                # Send to Telegram
                success = send_telegram_message(message)
                
                if success:
                    posted_links.add(link)
                    posted_count += 1
                    time.sleep(3)  # 3 second delay between posts
                    
        except Exception as e:
            print(f"  ❌ Error fetching {feed_info['name']}: {e}")
            continue
    
    print(f"✅ Posted {posted_count} deals this round")

# ============================================================
#   WELCOME MESSAGE
# ============================================================

def send_welcome():
    """Bot start ஆனதும் welcome message"""
    message = (
        "🚀 <b>SK Affiliate Hub Bot Started!</b>\n\n"
        "✅ Amazon India Deals\n"
        "✅ Auto posting every 2 hours\n"
        "✅ Affiliate links active\n\n"
        "🛒 Best deals coming soon!"
    )
    send_telegram_message(message)

# ============================================================
#   SCHEDULER SETUP
# ============================================================

def main():
    print("=" * 50)
    print("  SK AFFILIATE HUB BOT")
    print("  Amazon India Deals Auto-Poster")
    print("=" * 50)
    
    # Test connection
    print("\n🔗 Testing Telegram connection...")
    send_welcome()
    
    # First run immediately
    fetch_and_post_deals()
    
    # Schedule every 2 hours
    schedule.every(2).hours.do(fetch_and_post_deals)
    
    # Also schedule specific times
    schedule.every().day.at("09:00").do(fetch_and_post_deals)
    schedule.every().day.at("12:00").do(fetch_and_post_deals)
    schedule.every().day.at("18:00").do(fetch_and_post_deals)
    schedule.every().day.at("21:00").do(fetch_and_post_deals)
    
    print("\n⏰ Scheduled: 9AM, 12PM, 6PM, 9PM daily")
    print("🔄 Also running every 2 hours")
    print("\n▶️  Bot is running... Press Ctrl+C to stop\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()

