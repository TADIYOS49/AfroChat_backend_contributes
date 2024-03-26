functional_tools = {
    "search_news": {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "This endpoint suits article discovery and analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Keywords or phrases to search for in the article title and body.",
                    },
                    "searchIn": {
                        "type": "string",
                        "description": "The fields to restrict your q search to. Possible options are: title, "
                        "description, content. Default: all 3 fields. You can also use any combination "
                        "of those 3 fields separated by commas (e.g. title,description).",
                        "enum": ["title", "description", "content"],
                    },
                    "from": {
                        "type": "string",
                        "description": "A date and optional time for the oldest article allowed. This should be in "
                        "ISO 8601 format (e.g. 2021-06-25 or 2021-06-25T00:00:00) Default: the oldest "
                        "according to your plan.",
                    },
                    "to": {
                        "type": "string",
                        "description": "A date and optional time for the newest article allowed. This should be in "
                        "ISO 8601 format (e.g. 2021-06-25 or 2021-06-25T00:00:00) Default: the newest "
                        "according to your plan.",
                    },
                    "pageSize": {
                        "type": "integer",
                        "description": "The number of results to return per page (request). 20 is the default, "
                        "100 is the maximum.",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "page": {
                        "type": "integer",
                        "description": "Use this to page through the results.",
                        "minimum": 1,
                    },
                    "sortBy": {
                        "type": "string",
                        "description": "The order to sort the articles in. Possible options: relevancy, popularity, "
                        "publishedAt. relevancy = articles more closely related to q come first. "
                        "popularity = articles from popular sources and publishers come first. "
                        "publishedAt = newest articles come first. Default: publishedAt",
                        "enum": ["relevancy", "popularity", "publishedAt"],
                    },
                },
                "required": ["q"],
            },
        },
    },
    "get_headlines": {
        "type": "function",
        "function": {
            "name": "get_headlines",
            "description": "Locate articles and breaking news headlines from news sources and blogs across the web",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "The 2-letter ISO 3166-1 code of the country to get headlines for.",
                    },
                    "category": {
                        "type": "string",
                        "description": "The category of news to search for",
                        "enum": [
                            "business",
                            "entertainment",
                            "general",
                            "health",
                            "science",
                            "sports",
                            "technology",
                        ],
                    },
                    "pageSize": {
                        "type": "integer",
                        "description": "The number of results to return per page (request). 20 is the default, 100 is the maximum.",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "page": {
                        "type": "integer",
                        "description": "Use this to page through the results.",
                        "minimum": 1,
                    },
                },
                "required": ["country"],
            },
        },
    },
}
