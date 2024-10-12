import requests
from app.config import load_config
from nostr_sdk import Client, EventId, Kind, Filter, Timestamp, EventSource

config = load_config()

async def getZaps(eventId: str):
    client = Client()

    await client.add_relay("wss://relay.snort.social")
    await client.add_relay("wss://nos.lol")
    await client.add_relay("wss://relay.damus.io")
    await client.add_relay("wss://nostr.wine")

    await client.connect()

    event = EventId.parse(eventId)
    kind = Kind(9735)
    filter = Filter().kind(kind).event(event).until(Timestamp.now())

    source = EventSource.relays()
    zaps = await client.get_events_of([filter], source)
    zaps = sorted(zaps, key=lambda x: x.created_at().as_secs())
    return zaps

async def getZap(zapId: str):
    client = Client()

    await client.add_relay("wss://relay.snort.social")
    await client.add_relay("wss://nos.lol")
    await client.add_relay("wss://relay.damus.io")
    await client.add_relay("wss://nostr.wine")

    await client.connect()

    event = EventId.parse(zapId)
    kind = Kind(9735)

    filter = Filter().id(event).kind(kind).until(Timestamp.now())
    source = EventSource.relays()

    zaps = await client.get_events_of([filter], source)
    return zaps[0]