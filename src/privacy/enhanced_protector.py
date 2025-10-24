from bs4 import BeautifulSoup

class EnhancedPrivacyProtector:
    def __init__(self):
        self.trackers = {
            # Social Media Tracking
            'facebook.com', 'facebook.net', 'fbcdn.net',
            'instagram.com', 'instagram.net',
            'twitter.com', 'twimg.com', 't.co',
            'linkedin.com', 'licdn.com',
            'tiktok.com', 'tiktokcdn.com',

            #Google Tracking
            'google-analytics.com', 'googletagmanager.com',
            'googleadservices.com', 'doubleclick.net',
            'googlesyndication.com', 'google.com/ads',

            #Other Major Trackers
            'amazon-adsystem.com', 'amazon.com/ads',
            'bing.com/ads', 'yahoo.com/ads',
            'hotjar.com', 'mixpanel.com', 'amplitude.com',
            'segment.com', 'optimizely.com', 'crazyegg.com',

            ## Ad Networks
            'adnxs.com', 'adsystem.com', 'adtech.com',
            'criteo.com', 'taboola.com', 'outbrain.com',
            'adroll.com', 'adform.com', 'pubmatic.com'
        }
        
        # Add the missing ad_domains attribute
        self.ad_domains = {
            'googlesyndication.com',   # Google's ad serving
            'doubleclick.net',         # Google's ad network
            'amazon-adsystem.com',      # Amazon's ad network
            'adnxs.com',               # AppNexus ad platform
            'adsystem.com',            # Generic ad systems
            'adtech.com'               # Ad technology platforms
        }
        
        self.search_trackers = {
            'google.com/search', 'bing.com/search', 'yahoo.com/search',
            'duckduckgo.com/search', 'search.yahoo.com'
        }

    def clean_html(self, html_content):
        """
        Disabled HTML cleaning to preserve site functionality and styling
        """
        # Return original HTML without modification to preserve site styling
        return html_content

    def get_privacy_headers(self):
        """
        Get HTTP headers that protect your privacy
        These headers tell websites not to track you
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',  # Do Not Track - tells websites not to track you
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
    
    def count_blocked_items(self, original_html, cleaned_html):
        """Count how many items were blocked"""
        original_soup = BeautifulSoup(original_html, 'html.parser')
        cleaned_soup = BeautifulSoup(cleaned_html, 'html.parser')
        
        scripts_blocked = len(original_soup.find_all('script')) - len(cleaned_soup.find_all('script'))
        iframes_blocked = len(original_soup.find_all('iframe')) - len(cleaned_soup.find_all('iframe'))
        
        return scripts_blocked, iframes_blocked
        
        
    
    # Block search-related tracking
    

      