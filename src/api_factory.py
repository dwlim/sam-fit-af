from utils.config import API_TO_USE
from apis.llama_api import LlamaAPI
from apis.gpt_api import GPTAPI
from apis.base_api import BaseAPI

def create_api() -> BaseAPI:
    """
    Create and return an instance of the appropriate API class based on the global API_TO_USE setting.
    See the utils/.config file.

    Returns:
        BaseAPI: An instance of a class derived from BaseAPI (either LlamaAPI or GPTAPI).

    Raises:
        ValueError: If API_TO_USE is set to an unknown or unsupported value.

    Usage:
        api = create_api()
        # api will be an instance of LlamaAPI or GPTAPI, depending on API_TO_USE

    Note:
        The global variable API_TO_USE must be set before calling this function.
        Valid values are "llama" for LlamaAPI and "gpt" for GPTAPI.
    """
    if API_TO_USE == "llama":
        # TODO: remove this once we have a working llama api implementation (https://trello.com/c/Eg1FQ55N)
        raise ValueError(f"Unknown API: {API_TO_USE}")
        # return LlamaAPI()
    elif API_TO_USE == "gpt":
        return GPTAPI()
    else:
        raise ValueError(f"Unknown API: {API_TO_USE}")
