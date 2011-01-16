import datetime
from google.appengine.ext import db

class DownLog(db.Model):
    log_timestamp = db.DateProperty(required=True, auto_now_add=True)
    url = db.StringProperty(required=True)
    description = db.StringProperty(required=False, multiline=True)
    
    @staticmethod
    def get_last_log(url):
        downlogs = DownLog.all();
        downlogs.filter('url = ', url)
        downlogs.order('-log_timestamp')
        results = downlogs.fetch(1)
        if len(results) == 1:
            return results[0]
        return None
