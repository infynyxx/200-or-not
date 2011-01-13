from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import InvalidURLError, DownloadError, ResponseTooLargeError

from yaml import load
import twilio

class TwilioSmsHandler:
    def __init__(self, sms_options):
        self._account = twilio.Account(sms_options['twilio_sid'], sms_options['twilio_auth_token'])
        self._request_path = '/2010-04-01/Accounts/%s/SMS/Messages.json' % (sms_options['twilio_sid'])
        self._twilio_number = sms_options['twilio_number']

    def send(self, number, body):
        data = {}
        data['From'] = self._twilio_number
        data['To'] = number
        data['Body'] = body
        return self._account.request(path=self._request_path, method='POST', vars=data);

class DownOrNot(webapp.RequestHandler):
    
    _settings = None

    def __init__(self):
        self._settings = load(open('settings.yaml', 'r').read())

    def get(self):
        url_list = self._settings['urls_to_check']
        for url in url_list:
            subject = '%s is down!' % (url)
            message = subject + '\n'
            has_error = True
            try:
                result = urlfetch.fetch(url, follow_redirects=False)
                status_code = result.status_code
                if status_code == 200:
                    has_error = False
                else:
                    message = message + '\n Status code of %d instead of 200' % (status_code)
            except InvalidURLError, e:
                message = message + '\n Exception: The URL of the request was not a valid URL'
            except DownloadError, e:
                message = message + '\nException: There was an error retrieving the data.'
            except ResponseTooLargeError, e:
                message = message + '\nThe response data exceeded the maximum allowed size'
            

            if has_error == True:
                #send email
                to = self._settings['email']['to']
                sender = self._settings['email']['sender']
                mail.send_mail(sender=sender, to=to, subject=subject, body=message)
                #if sms options is enabled send SMS using Twilio API
                if (self._settings.has_key('sms') == True):
                    sms_options = self._settings['sms']
                    to_list = sms_options['to']
                    sms_handler = TwilioSmsHandler(sms_options)
                    for number in to_list:
                        sms_handler.send(number, subject)


class NotFoundHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        self.response.out.write("<html><title>Boo!!!</title><body><h1>Not Found!</h1></body></html>")


app = webapp.WSGIApplication([('/downornot', DownOrNot), ('/.*', NotFoundHandler)], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == 'main':
    main()
