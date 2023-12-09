import json
import logging
import os
import ssl
import sys
from random import randrange

from nostr.event import Event
from nostr.key import PrivateKey, PublicKey
from nostr.relay import RelayPolicy, Relay
from nostr.relay_manager import RelayManager


class XRelay(Relay):
    _event: Event = None
    _logger: logging.Logger = None

    def set_on_open_event(self, event: Event, logger: logging.Logger):
        self._event = event
        self._logger = logger

    def _on_open(self, class_obj):
        self.connected = True
        if self._event is not None:
            msg = self._event.to_message()
            self._logger.debug("Publishing on " + self.url)
            self.publish(msg)
            self._logger.debug("Closing " + self.url)
            self.close()


class XRelayManager(RelayManager):
    def add_x_relay(self, url: str, event: Event, logger: logging.Logger):
        policy = RelayPolicy(True, True)
        relay = XRelay(url, policy, self.message_pool, {})
        relay.set_on_open_event(event, logger)
        self.relays[url] = relay


def _load_relays(type: str = 'default'):
    """
    Load 'type'_relays.json urls from x_relays.json file and return as string[]
    :return: string[] of relay urls
    """
    f = open(f'{type}_relays.json')
    relays = json.load(f)
    f.close()
    return relays


def _load_quotes():
    f = open('adv-qoutes.json')
    q = json.load(f)
    f.close()
    return q


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ADV_KEY = os.environ.get("ADV_KEY", "please set")
    _private_key: PrivateKey = PrivateKey(bytes.fromhex(ADV_KEY))
    _public_key: PublicKey = _private_key.public_key
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format="[%(asctime)s - %(levelname)s] %(message)s")
    logger = logging.getLogger("nostrich.house-adv")
    sleepy = randrange(30, 180)
    lines = _load_quotes()
    lineOfTheDay = randrange(0, len(lines))
    the_line = lines[lineOfTheDay]
    logger.info(the_line)
    relays = _load_relays()
    event = Event(content=the_line, kind=1, public_key=_public_key.hex())
    _private_key.sign_event(event)
    relay_manager = XRelayManager()
    for r in relays:
        relay_manager.add_x_relay(r, event, logger)
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})
