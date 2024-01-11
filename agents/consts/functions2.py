OPENAI_FUNCTIONS = {
    "result_path_selected" :
    {
        "name": "result_path_selected",
        "description": "The result path is selected",
        "parameters": {
            "type": "object",
            "properties": {
                "result_path": {
                    "type": "string",
                    "description": "Result path that is selected",
                },
            }
        },
    },
    "config_selected" :
    {
        "name": "config_selected",
        "description": "The config path is selected",
        "parameters": {
            "type": "object",
            "properties": {
                "config_filename": {
                    "type": "string",
                    "description": "Name of the file of the config that is selected",
                },
            }
        },
    },
    "start_calculation":
    {
        "name": "start_calculation",
        "description": "Activating the state of the system in which the experiment is started",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
    },
    "prior_selection":
    {
        "name": "prior_selection",
        "description": "Selection of the prior file that will be used in the calculation",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
    },
    "prior_selected":
        {
            "name": "prior_selected",
            "description": "User selected the prior",
            "parameters": {
                "type": "object",
                "properties": {
                    "prior_file": {
                        "type": "string",
                        "description": "Name of the file of the prior that is selected",
                    },
                },

            },
        },
    "parameters_modification":
    {
        "name": "parameters_modification",
        "description": "Modification of the parameters of a certain parameterization function",
        "parameters": {
            "type": "object",
            "properties": {
                "parameters": {
                    "type": "string",
                    "description": "Parameters of parametrization",
                },
            },
        },
    },
    "save_to_file":
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
    "load_from_file":
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
    "display_image":
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
    "display_data_table":
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
    "inspect_directory":
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
    "run_experiment":
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
    "generate_graphs":
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
    "generate_parametrization":
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
    "generate_priori":
    {
        "name": "generate_priori",
        "description": "Useful for generating a priori",
        "parameters": {
            "type": "object",
            "properties": {}
        },
    },
}
