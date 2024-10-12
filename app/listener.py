import json
import asyncio
from app.zaps import getZaps
from app.audiogen import audiogen
from app.config import load_config
from nostr_sdk import Client, EventId, Kind, Filter, Timestamp, EventSource, TagKind

config = load_config()

async def listener(app):
    lastZap = ""
    while True:
        try:
            zaps = await getZaps(config.EVENTID)

            if (zaps[-1] == lastZap):
                continue

            lastZap = zaps[-1]

            content = json.loads(lastZap.content())

            description = lastZap.get_tag_content(TagKind.DESCRIPTION())
            tags = json.loads(description)["tags"]

            amount = 0
            for x in tags:
                if x[0] == "amount":
                    amount = int(int(x[1]) / 1000)

            if not amount:
                continue

            name = content["name"]
            text = content["comment"]
            model = content["model"]

            if not text:
                continue

            text = f"{name} enviou {amount} satoshis: {text}"

            audio_data = await audiogen(text=text, model_name=model)

            await app.queue.put(json.dumps({
                "text": text,
                "audio": audio_data.decode("utf-8"),
            }))
        except Exception as e:
            break
        
        await asyncio.sleep(5)