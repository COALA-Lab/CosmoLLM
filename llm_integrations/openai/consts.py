OPENAI_FUNCTIONS = [
    {
        "name": "save_to_file",
        "description": "Save arbitrary data to a file",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "The data to save to the file",
                },
                "filename": {
                    "type": "string",
                    "description": "The path to the file to save the data to",
                },
            },
        },
    },
    {
        "name": "load_from_file",
        "description": "Load arbitrary data from a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The path to the file to load the data from",
                },
                "characters": {
                    "type": "integer",
                    "description": "The number of characters to read from the file (-1 for all)",
                },
            },
        },
    },
]
