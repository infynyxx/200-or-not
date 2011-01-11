from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import InvalidURLError, DownloadError, ResponseTooLargeError

from yaml import load

class DownOrNot(webapp.RequestHandler):
    
    _settings = None

    def __init__(self):
        self._settings = load(open('settings.yaml', 'r').read())

    def get(self):
        url_list = self._settings['urls_to_check']
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
                to = self._settings['email']['to']
                sender = self._settings['email']['sender']
                mail.send_mail(sender=sender, to=to, subject=subject, body=message)

class NotFoundHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        self.response.out.write("<html><title>Boo!!!</title><body><h1>Not Found!</h1></body></html>")


app = webapp.WSGIApplication([('/downornot', DownOrNot), ('/.*', NotFoundHandler)], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == 'main':
    main()
