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
        "name": "display_image",
        "description": "Display an image",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "The path to the image to display",
                },
            },
        },
    },
    {
        "name": "display_data_table",
        "description": "Display a table of data in various file formats (json, csv...)",
        "parameters": {
            "type": "object",
            "properties": {
                "data_table_path": {
                    "type": "string",
                    "description": "The data to display in the table",
                },
            },
        },
    },
    {
        "name": "inspect_directory",
        "description": "Inspect the contents of a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The path to the directory to inspect",
                },
            },
        },
    },
    {
        "name": "run_experiment",
        "description": "Run the MCMC simulation for the experiment specified in the configuration file",
        "parameters": {
            "type": "object",
            "properties": {
                "config_path": {
                    "type": "string",
                    "description": "The path to the experiment configuration file",
                },
                "results_path": {
                    "type": "string",
                    "description": "The path to the directory where the results will be saved",
                },
            },
        },
    },
    {
        "name": "generate_graphs",
        "description": "Generate several plot images, including chain plots, corner plots, and density plots, "
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
