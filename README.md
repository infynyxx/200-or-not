A simple Google App Engine service to check if the given site is down or not
============================================================================

* Use Google App Engine's Free Quota to monitor list of sites
* When I say monitoring, I mean checking status code == 200 only; nothing more than that
* It uses [URL Fetch API](http://code.google.com/appengine/docs/python/urlfetch/)
* /downornot is accessed via cron job and can be accessed by admin only
* If given site is down, it will email to specified address

Installaion
------------
* Change application value in app.yaml accordingly after register in [https://appengine.google.com/]
* Change to and sender values in settings.yaml accordingly

Running
--------
    <google_app_engine_sdk_path>/dev_appserver.py <src_folder>
