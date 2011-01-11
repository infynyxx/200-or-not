from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import InvalidURLError, DownloadError, ResponseTooLargeError

import os
from yaml import load 

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello world!')

class DownOrNot(webapp.RequestHandler):
    def _get_urls(self):
        settings = load(open('settings.yaml', 'r').read())
        return settings['urls_to_check']

    def get(self):
        url_list = self._get_urls()
        for url in url_list:
            subject = '%s is down!' % (url)
            message = subject + '\n'
            send_mail = True
            try:
                result = urlfetch.fetch(url)
                status_code = result.status_code
                if status_code == 200:
                    send_mail = False
                else:
                    message = message + '\n Status code of %d instead of 200' % (status_code)
            except InvalidURLError, e:
                message = message + '\n Exception: The URL of the request was not a valid URL'
            except DownloadError, e:
                message = message + '\nException: There was an error retrieving the data.'
            except ResponseTooLargeError, e:
                message = message + '\nThe response data exceeded the maximum allowed size'

            if send_mail == True:
                mail.send_mail(sender="Google App Engine Site Monitoring <dynamism360@gmail.com>", to="Praj <praj@prajwal-tuladhar.net.np>", subject=subject, body=message);

app = webapp.WSGIApplication([('/', MainPage), ('/downornot', DownOrNot)], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == 'main':
    main()
