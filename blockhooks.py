#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import json
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import models

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_BLOCKHOOKS_LIST_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def blockhooks_key():
    """Constructs a Datastore key for a Blockhooks entity.

    We use DEFAULT_BLOCKHOOKS_LIST_NAME as the key.
    """
    return ndb.Key('Hook', DEFAULT_BLOCKHOOKS_LIST_NAME)

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        blockhooks_query = models.Hook.query(
            ancestor=blockhooks_key()).order(-models.Hook.address)
        blockhooks = blockhooks_query.fetch(10)

        template_values = {
            'blockhooks': blockhooks,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START blockhook]
class BlockHook(webapp2.RequestHandler):

    def post(self):
	if self.request.get('addhook'):
		blockhooks = models.Hook(parent=blockhooks_key())
		blockhooks.address = self.request.get('address')
		blockhooks.abi = json.loads(self.request.get('abi'))
		blockhooks.uri = self.request.get('uri')
		blockhooks.put()

	if self.request.get('clearhooks'):
		for hook in models.Hook.query():
			hook.key.delete()

        self.redirect('/')
# [END blockhook]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/updateblockhooks', BlockHook),
], debug=True)
# [END app]
