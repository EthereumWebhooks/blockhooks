from google.appengine.ext import ndb


class Hook(ndb.Model):
    address = ndb.BlobProperty(indexed=True)                # Address of the contract sending the event
    topic0 = ndb.BlobProperty(indexed=True, required=True)  # First log topic, usually event ID
    topics = ndb.BlobProperty(indexed=False, repeated=True) # List of log topics to filter on
    abi = ndb.JsonProperty(indexed=False)                   # ABI for event
    uri = ndb.StringProperty(indexed=False)                 # URI (possibly templated) to query
    body = ndb.JsonProperty(indexed=False)                  # Body of POST request
    contentType = ndb.StringProperty(indexed=False)         # Content-type of body
