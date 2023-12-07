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
    {
        "name": "plot_graphs",
        "description": "Generate several plots, including chain plots, corner plots, and density plots, "
                       "based on the data stored in the experiment results directory",
        "parameters": {
            "type": "object",
            "properties": {
                "experiment_path": {
                    "type": "string",
                    "description": "The path to the experiment results",
                },
            },
        },
    },
    {
        "name": "generate_parametrization",
        "description": "Useful for generating a parametrization",
        "parameters": {
            "type": "object",
            "properties": {
                "parametrization_function_in_latex": {
                    "type": "string",
                    "description": "The parametrization function in Latex markup"
                }
            },
            "required": [],
        },
    },
    {
        "name": "generate_priori",
        "description": "Useful for generating a priori",
        "parameters": {
            "type": "object",
            "properties": {}
        },
    },
]
