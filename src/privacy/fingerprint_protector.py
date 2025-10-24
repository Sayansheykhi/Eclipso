import random
class FingerPrintProtector:
    def __init__(self):
    # Different browser signatures to choose from
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        ]    
        self.screen_resolution = [
            '1920x1080',
            '1366x768',
            '1280x720',
            '1024x768',
            '800x600',
            '640x480',
            '320x240'
    ]    
        
        self.timezone = [
            'America/New_York',
            'America/Los_Angeles',
            'America/Chicago',
            'America/Denver',
            'America/Phoenix',
            'America/New_York',
            'America/Los_Angeles',
            'America/Chicago',
            'America/Denver',
            'America/Phoenix',
            'America/New_York',
            'America/Los_Angeles',
    ]
        self.language = [
            'en-US',
            'en-GB',
            'en-CA',
            'en-AU',
            'en-NZ',
            'en-ZA',
    ]
        self.plugins = [
            'Flash',
            'Java',
            'Silverlight',
            'QuickTime',
            'RealPlayer',
    ]
    def generate_random_fingerprint(self):
        """Generate a unique fingerprint for the browser"""
        
        return {
            'user_agent': random.choice(self.user_agents),
            'screen_resolution': random.choice(self.screen_resolution),
            'timezone': random.choice(self.timezone),
            'language': random.choice(self.language),
            'plugins': random.choice(self.plugins),
            'platform': random.choice(['MacIntel', 'Win32', 'Linux x86_64', 'iPhone', 'iPad']),
            'color_depth': random.choice(['8', '16', '24', '32']),
            'pixel_ratio': random.choice([1,2,1.5]),
            'webgl_vendor': random.choice(['Google', 'Mozilla', 'Apple', 'Microsoft']),
            'webgl_renderer': random.choice(['Intel', 'NVIDIA', 'AMD', 'Apple']),
            'webgl_version': random.choice(['1', '2', '3']),
            'webgl_extensions': random.choice(['WEBGL_depth_texture', 'WEBGL_draw_buffers', 'WEBGL_lose_context']),
            'webgl_shading_language_version': random.choice(['1.0', '1.1', '1.2', '1.3', '1.4', '1.5']),
            'webgl_vendor': random.choice(['Google', 'Mozilla', 'Apple', 'Microsoft']),
            'webgl_renderer': random.choice(['Intel', 'NVIDIA', 'AMD', 'Apple']),
        }

    def get_headers_with_random_fingerprints(self):
        """ Get HTTP Headers with randomized fingerprint"""
        fingerprint = self.generate_random_fingerprint()
        return {
            'User-Agent': fingerprint['user_agent'],
            'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',
            'Accept-Language': fingerprint['language'],
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'Keep-alive',
            'Upgrade-Insecure-Requests': '1',
            # Add more headers that websites use for fingerprinting
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': f'"{fingerprint["platform"]}"',
            
        }

    
