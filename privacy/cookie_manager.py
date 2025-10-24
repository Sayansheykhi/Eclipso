import requests

class cookie_manager:
    def __init__(self):
        self.session = requests.Session()

        # Options: 'block_all', 'block_third_party', 'allow_all'
        self.cookie_policy = 'block_third_party'

    def should_accept_cookie(self, cookie, domain):
        """smart cookie filtering"""
        if self.cookie_policy == 'block_all':
            return False 
        elif self.cookie_policy == 'block_third_party':
            return domain in cookie.domain 
        return True   
           