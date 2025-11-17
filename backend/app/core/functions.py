coder_tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "This function allows you to execute Python code and retrieve the terminal output. If the code "
            "generates image output, the function will return the text '[image]'. The code is sent to a "
            "Jupyter kernel for execution. The kernel will remain active after execution, retaining all "
            "variables in memory."
            "You cannot show rich outputs like plots or images, but you can store them in the working directory and point the user to them. ",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code text"}
                },
                "required": ["code"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pip_install",
            "description": "Install Python packages using pip. This function executes 'pip install' command for the specified packages. "
            "Note: Common packages like numpy, scipy, pandas, matplotlib, seaborn, scikit-learn, xgboost are already installed.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "packages": {
                        "type": "string",
                        "description": "Package name(s) to install, e.g., 'requests' or 'beautifulsoup4 lxml'",
                    }
                },
                "required": ["packages"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in the current working directory. Can filter by file type (e.g., '.csv', '.xlsx', '.txt', '.png').",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "extension": {
                        "type": "string",
                        "description": "Optional file extension filter (e.g., '.csv', '.xlsx'). If not provided, lists all files.",
                    }
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a file in the working directory. Returns the file content as text for text files, "
            "or basic information for binary files.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read (e.g., 'data.csv', 'readme.txt')",
                    }
                },
                "required": ["filename"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Performs a web search using a configured provider (Tavily or Exa). Use this to find up-to-date information, code examples, documentation, or research papers.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string.",
                    },
                    "search_type": {
                        "type": "string",
                        "description": "The type of search to perform. Options: 'general', 'academic', 'code', 'news', 'research'. Defaults to 'general'.",
                        "enum": ["general", "academic", "code", "news", "research"],
                    },
                    "provider": {
                        "type": "string",
                        "description": "The preferred search provider. Options: 'tavily', 'exa'. Defaults to the system's configured default.",
                        "enum": ["tavily", "exa"],
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "The maximum number of results to return. Defaults to 10.",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
]

# have installed: numpy scipy pandas matplotlib seaborn scikit-learn xgboost


## writeragent tools
writer_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search for papers using a query string.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The query string"}
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Performs a web search using a configured provider (Tavily or Exa). Use this to find up-to-date information, code examples, documentation, or research papers.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string.",
                    },
                    "search_type": {
                        "type": "string",
                        "description": "The type of search to perform. Options: 'general', 'academic', 'code', 'news', 'research'. Defaults to 'general'.",
                        "enum": ["general", "academic", "code", "news", "research"],
                    },
                    "provider": {
                        "type": "string",
                        "description": "The preferred search provider. Options: 'tavily', 'exa'. Defaults to the system's configured default.",
                        "enum": ["tavily", "exa"],
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "The maximum number of results to return. Defaults to 10.",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
]
