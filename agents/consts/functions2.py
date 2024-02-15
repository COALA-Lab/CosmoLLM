OPENAI_FUNCTIONS = {

    "define_parameters_intervals": {
        "name": "define_parameters_intervals",
        "description": "Define parameters within specified intervals",
        "parameters": {
            "type": "object",
            "properties": {
                "intervals_for_parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "param_name": {
                                "type": "string",
                                "description": "The name of the parameter"
                            },
                            "low": {
                                "type": "number",
                                "description": "Minimum value of the parameter"
                            },
                            "high": {
                                "type": "number",
                                "description": "Maximum value of the parameter"
                            },

                        },
                        "required": ['param_name', 'low', 'high'],
                    },
                },

            },
            "required": ['intervals_for_parameters'],
        },
    },

    "define_parametrization":
    {
        "name": "define_parametrization",
        "description": "Defining parameterization",
        "parameters": {
            "type": "object",
                "properties": {
                    "parametrization_function_in_latex": {
                        "type": "string",
                        "description": "The parametrization function in Latex markup"
                    }
                }
        },
    },
    "transition_new_state_selected":
        {
            "name": "transition_new_state_selected",
            "description": "Handle when the user select transition to the new state option",
            "parameters": {
                "type": "object",
                "properties": {


                }
            },
        },
    "modify_parameterization_selected":
        {
            "name": "modify_parameterization_selected",
            "description": "Handle when the user select modify the parametrization option",
            "parameters": {
                "type": "object",
                "properties": {


                }
            },
        },
    "modify_parameter_names_selected":
        {
            "name": "modify_parameter_names_selected",
            "description": "Handle when the user select modify the parameter names option",
            "parameters": {
                "type": "object",
                "properties": {


                }
            },
        },

    "modify_parameter_intervals_selected":
        {
            "name": "modify_parameter_intervals_selected",
            "description": "Handle when the user select modify the parameter intervals option",
            "parameters": {
                "type": "object",
                "properties": {

                }
            },
        },


    "define_parameter_names":
        {
            "name": "define_parameter_names",
            "description": "Specifying parameter names",
            "parameters": {
                "type": "object",
                "properties": {
                    "parameters": {
                        "type": "array",
                        "description": "Array of parameters",
                        "items": {
                            "type": "string"
                        }
                    },
                }
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
}
