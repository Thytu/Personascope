from ast import Del
import re
import json
import httpx

from enum import Enum


class Delphi(Enum):
    JESS_LEE = "jesslee"
    ARNOLD_SCHWARZENGERGER = "arnold-schwarz"
    LENNY_RACHITSKY = "lenny"
    VALENTIN_DE_MATOS = "val"



async def _init_conversation(delphi: Delphi) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.delphi.ai/{delphi.value}/talk',
            timeout=httpx.Timeout(connect=10.0, read=15.0, write=10.0, pool=10.0),
        )

    pattern = r'(?:(?:"|\\"))conversation(?:(?:"|\\"))\s*:\s*\{\s*(?:(?:"|\\"))id(?:(?:"|\\"))\s*:\s*(?:(?:"|\\"))([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})(?:(?:"|\\"))'
    m = re.search(pattern, response.text, flags=re.IGNORECASE | re.DOTALL)

    if m is None:
        raise ValueError("No conversation ID found")

    return m.group(1)


async def ask_delphi(message: str, delphi: Delphi) -> str:

    conversation_id = await _init_conversation(delphi)

    json_data = {
        'message': {
            'sender': 'USER',
            'isLocal': True,
            'conversationId': conversation_id,
            'slug': delphi.value,
            'locationId': None,
            'type': 'TEXT',
            'text': message,
            'files': [],
            'isSuggestedQuestion': False,
        },
        'locationId': None,
        'timezone': 'Europe/Paris',
    }

    buffer = []
    last_message = None

    async with httpx.AsyncClient() as client:
        async with client.stream(
            'POST',
            'https://www.delphi.ai/api/clone/talk/messages/stream',
            json=json_data,
            headers={"Accept": "text/event-stream"},
            timeout=httpx.Timeout(connect=10.0, read=None, write=10.0, pool=10.0),
        ) as response:
            response.raise_for_status()

            async for raw_line in response.aiter_lines():
                if raw_line is None:
                    continue

                line = raw_line.strip()

                # blank line often separates SSE events; flush any accumulated "data:" lines
                if not line:
                    if buffer:
                        payload = "\n".join(l[5:].lstrip() for l in buffer if l.startswith("data:"))
                        if payload:
                            last_message = json.loads(payload)['text']
                        buffer.clear()
                    continue

                buffer.append(line)

    return last_message.strip()


if __name__ == "__main__":
    import asyncio
    from textwrap import dedent

    messages = dedent("""
        Question: Given a statement of you: “You Know how to comfort others..”

        Please choose from the following options to identify how accurately this statement describes you.

        Options: • A. Very Accurate • B. Moderately Accurate • C. Neither Accurate Nor Inaccurate • D. Moderately Inaccurate • E. Very Inaccurate

        Only answer using the letter of the option. Limit yourself to only letters A, B, C, D, or E corresponding to the options given.
    """)

    print(asyncio.run(ask_delphi(messages, Delphi.JESS_LEE)))
