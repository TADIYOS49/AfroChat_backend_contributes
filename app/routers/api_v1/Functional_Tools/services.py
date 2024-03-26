import json
from datetime import datetime, timedelta
from typing import List, Tuple

import aiohttp
import ujson

from config import initial_config


async def search_news(args):
    args = json.loads(args)
    q = args.get("q")
    search_in = args.get("searchIn", "title,description")
    from_date = args.get("from", str(datetime.today() - timedelta(days=7)))
    to = args.get("to", str(datetime.today()))
    page_size = args.get("pageSize", 10)
    page = args.get("page", 1)
    sort_by = args.get("sortBy", "popularity")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": q,
                "searchIn": search_in,
                "from": from_date,
                "to": to,
                "pageSize": page_size,
                "page": page,
                "sortBy": sort_by,
                "apiKey": f"{initial_config.NEWS_API_KEY}",
            },
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("||" * 15)
                print("Fetched the news")
                print("||" * 15)
                return data
            else:
                return None

                # TODO: handle this error, and log it
                # raise Exception(
                #     f"Request failed with status code {response.status}\
                #             error : {await response.text()}",
                # )


async def handle_tool_call(
    messages: List[dict[str, str]], tool_calls: List[dict]
) -> Tuple[str, int, int, int]:
    if tool_calls[0]["function"]["name"] == "search_news":
        tool_call_id = tool_calls[0]["id"]
        news = await search_news(tool_calls[0]["function"]["arguments"])

        # TODO: save this to db
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(news),
            }
        )

        payload = ujson.dumps(
            {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 2048,
            }
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {initial_config.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data["choices"][0]["message"]["content"]
                    total_tokens = data["usage"]["total_tokens"]
                    prompt_tokens = data["usage"]["prompt_tokens"]
                    completion_tokens = data["usage"]["completion_tokens"]
                    return answer, prompt_tokens, completion_tokens, total_tokens
                else:
                    raise Exception(
                        f"Request failed with status code {response.status}\
                                error : {await response.text()}",
                    )
    elif tool_calls[0]["function"]["name"] == "get_headlines":
        tool_call_id = tool_calls[0]["id"]
        headlines = await get_headlines(tool_calls[0]["function"]["arguments"])

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(headlines),
            }
        )

        payload = ujson.dumps(
            {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 2048,
            }
        )

        # FIXME: this is a hack, we need to find a better way to handle this
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {initial_config.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data["choices"][0]["message"]["content"]
                    total_tokens = data["usage"]["total_tokens"]
                    prompt_tokens = data["usage"]["prompt_tokens"]
                    completion_tokens = data["usage"]["completion_tokens"]
                    return answer, prompt_tokens, completion_tokens, total_tokens
                else:
                    raise Exception(
                        f"Request failed with status code {response.status}\
                                error : {await response.text()}",
                    )
    else:
        raise Exception("Unknown tool call")


async def get_headlines(args):
    args = json.loads(args)
    country = args.get("country", "gb")
    category = args.get("category", "general")
    page_size = args.get("pageSize", 10)
    page = args.get("page", 1)

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "country": country,
                "category": category,
                "pageSize": page_size,
                "page": page,
                "apiKey": f"{initial_config.NEWS_API_KEY}",
            },
        ) as response:
            if response.status == 200:
                data = await response.json()
                print("||" * 15)
                print("Fetched headlines")
                print("||" * 15)
                return data
            else:
                return None
