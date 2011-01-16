import logging
import time, os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import InvalidURLError, DownloadError, ResponseTooLargeError

try:
    from google.appengine.runtime import DeadlineExceededError
except ImportError:
    from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

from yaml import load

import twilio
from model import DownLog

os.environ['TZ'] = 'EST+05EDT,M4.1.0,M10.5.0'
time.tzset()

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
            message = ''
            has_error = True
            try:
                result = urlfetch.fetch(url, follow_redirects=False, deadline=self._settings['request_timeout'], method=urlfetch.HEAD)
                status_code = result.status_code
                if status_code == 200:
                    has_error = False
                else:
                    message = message + 'Status code of %d instead of 200' % (status_code)
            except InvalidURLError, e:
                message = message + 'Exception: The URL of the request was not a valid URL'
            except DownloadError, e:
                message = message + 'Exception: There was an error retrieving the data.'
            except ResponseTooLargeError, e:
                message = message + 'The response data exceeded the maximum allowed size'
            except DeadlineExceededError:
                message = message + 'DeadlineExceededError: Operation could not be completed in time...'
            
            if has_error == True:
                #get last log
                last_log = DownLog.get_last_log(url=str(url))
                if last_log is not None:
                    message = message + '\nLast downtime: ' + last_log.log_timestamp.ctime()

                #save into database
                downlog = DownLog(url=url, description=message)
                downlog.put()
                
                logging.debug('Message: ', message)
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
                        sms_handler.send(number, subject + '\n' + message)


class NotFoundHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        self.response.out.write("<html><title>Boo!!!</title><body><h1>Not Found!</h1></body></html>")


app = webapp.WSGIApplication([('/downornot', DownOrNot), ('/.*', NotFoundHandler)], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == 'main':
    main()
