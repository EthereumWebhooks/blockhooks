from ethereum import abi
from google.appengine.ext import db, ndb
import logging
import urllib
import urllib2
import webapp2
from web3 import Web3, RPCProvider

import models


NUM_CONFIRMATIONS = 5


web3 = Web3(RPCProvider(host='10.3.3.21'))


def sendRequest(url, body, contentType):
    request = urllib2.Request(url, body, {'Content-Type': contentType})
    response = urllib2.urlopen(request)
    if 200 <= response.getcode() < 300:
        logging.warn("POST to %r got response code %d: %r", url, response.getcode(), response.read())
    else:
        logging.info("POST to %r", url)


def notifyHook(hook, log):
    topics = [int(x[2:], 16) for x in log['topics']]
    data = log['data'][2:].decode('hex')
    event = hook.interface.decode_event(topics, data)

    eventData = dict(log)
    eventData.update(event)

    url = hook.uri % eventData
    if hook.body:
        body = {}
        for k, v in hook.body.iteritems():
            body[k] = v % eventData

        if hook.contentType.lower() == 'text/x-www-form-urlencoded':
            body = urllib.urlencode(body)
        else:
            body = json.dumps(body)
    else:
        body = ""

    sendRequest(url, body, hook.contentType)


def processLog(log):
    topics = log['topics']
    eventId = topics[0].lower()
    address = log['address'].lower()
    logging.info("Log for %s from %s", eventId, address)
    if len(topics) == 0:
        return
    q = models.Hook.query(models.Hook.eventId == eventId, ndb.OR(
        models.Hook.address == address, models.Hook.address == ""))
    for hook in q:
        notifyHook(hook, log)


class BlockLoadHandler(webapp2.RequestHandler):
    def get(self):
        lastBlock = web3.eth.blockNumber - NUM_CONFIRMATIONS
        sync = models.SyncState.getInstance()
        for blocknum in range(sync.lastBlock, lastBlock + 1):
            logging.info("Processing block %d", blocknum)
            block = web3.eth.getBlock(blocknum)
            for tx in block['transactions']:
                receipt = web3.eth.getTransactionReceipt(tx)
                for log in receipt['logs']:
                    processLog(log)
        logging.info("Done processing new blocks.")
        sync.lastBlock = lastBlock
        sync.put()


app = webapp2.WSGIApplication([
    ('/_tasks/blockLoader', BlockLoadHandler),
], debug=True)
