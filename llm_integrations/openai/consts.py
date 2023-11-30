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
]
