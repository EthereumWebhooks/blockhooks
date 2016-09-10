from ethereum import abi
from google.appengine.ext import ndb



def computeEventId(hook):
    abi = hook.abi
    assert abi['type'] == 'event'
    return abi.method_id(abi['name'], [x['type'] for x in abi['inputs']])


class Hook(ndb.Model):
    address = ndb.BlobProperty(indexed=True)                # Address of the contract sending the event
    abi = ndb.JsonProperty(indexed=False, required=True)    # ABI for event
    eventId = ndb.ComputedProperty(computeEventId)          # Event ID to filter for
    uri = ndb.StringProperty(indexed=False)                 # URI (possibly templated) to query
    body = ndb.JsonProperty(indexed=False)                  # Body of POST request
    contentType = ndb.StringProperty(indexed=False)         # Content-type of body
