import logging
from .base_api import BaseAPI
from utils.resources import get_api_key
from openai import OpenAI
from utils.pace_zones import calculate_zones_from_json
import json

logger = logging.getLogger(__name__)

class LlamaAPI(BaseAPI):
    """
    A class to interact with the Llama model (via the Perplexity AI API)
    for generating training plans.
    
    This class extends BaseAPI and implements specific functionality for the Llama model.

    Attributes:
        api_key (str): The API key for authenticating with the Perplexity AI API.
        model (str): The specific GPT model to use, default is "llama-3.1-sonar-small-128k-online".
        client (OpenAI): An instance of the OpenAI client for making API calls to Perplexity AI.

    """
    def __init__(self):
        super().__init__()
        self.api_key = get_api_key("llama")
        self.model = "llama-3.1-sonar-large-128k-online"
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")
        
        # Load Llama-specific prompts
        try:
            with open("prompts/llama/llama_training_plan_generation_system_prompt.txt", "r") as f:
                self.training_plan_prompt = f.read()
        except FileNotFoundError:
            logger.error("System prompt file not found.")
            raise
        except Exception as e:
            logger.error("Error reading system prompt file: %s", str(e))
            raise
        
        # Load Llama-specific example training plan structure.
        # Note: we have to rely on prompt engineering to enforce json structure
        # because Llama does not support the response_format parameter.
        try:
            with open("prompts/llama_example_training_plan_structure.txt", "r") as f:
                self.training_plan_structure = f.read()
        except FileNotFoundError:
            logger.error("Example training plan structure file not found.")
            raise
        except Exception as e:
            logger.error("Error reading example training plan structure file: %s", str(e))
            raise

    def _prepare_plan_structure_context(self) -> str:
        return f"Here is the basic training plan structure:\n{self.training_plan_structure}"

    def generate_plan(self, user_prompt: str) -> str:
        """
        Generate a training plan using the Llama model.

        This method sends a request to the Perplexity AI API to generate a training plan
        based on the provided system and user prompts.

        Args:
            user_prompt (str): The user's specific request or query.

        Returns:
            str: The generated training plan text.

        Raises:
            Exception: If there's an error during the API call or plan generation.

        Note:
            The method uses a fixed max_tokens value of 2000, which may need adjustment
            based on the desired length of the training plan.
        """
        logger.info("Starting plan generation using llama\n")
        logger.info("Model: %s", self.model)
        try:
            zone_context = self._prepare_zone_context(user_prompt)
            plan_structure_context = self._prepare_plan_structure_context()

            response = self.client.chat.completions.create(
                model = self.model,
                messages = [
                    {"role": "system", "content": self.training_plan_prompt},
                    {"role": "system", "content": plan_structure_context},
                    {"role": "system", "content": zone_context},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens = 2000, # This needs to be updated to be proportional to the number of workouts/days/weeks
                temperature = 0.5,
                n = 1
            )
            logger.info("Plan generation completed successfully")
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Error during plan generation: %s", str(e))
            raise
