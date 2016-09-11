from ethereum import abi
from google.appengine.ext import db, ndb



def computeEventId(hook):
    assert hook.abi['type'] == 'event'
    return hex(abi.event_id(hook.abi['name'], [x['type'] for x in hook.abi['inputs']]))[:-1]


class Hook(ndb.Model):
    address = ndb.StringProperty(indexed=True, required=True, default="") # Address of the contract sending the event
    abi = ndb.JsonProperty(indexed=False, required=True)    # ABI for event
    eventId = ndb.ComputedProperty(computeEventId)          # Event ID to filter for
    uri = ndb.StringProperty(indexed=False)                 # URI (possibly templated) to query
    body = ndb.JsonProperty(indexed=False)                  # Body of POST request
    contentType = ndb.StringProperty(indexed=False)         # Content-type of body

    @property
    def interface(self):
        return abi.ContractTranslator([self.abi])


class SyncState(ndb.Model):
    lastBlock = ndb.IntegerProperty(required=True, default=0)

    @classmethod
    def getInstance(cls):
        return cls.get_or_insert('sync')
