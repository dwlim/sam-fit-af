import logging
from .base_api import BaseAPI
from utils.resources import get_api_key
from openai import OpenAI
from schemas.training_plan import TrainingPlan
import json

logger = logging.getLogger(__name__)

class GPTAPI(BaseAPI):
    """
    A class to interact with the OpenAI API for generating training plans.
    This class extends BaseAPI and implements specific functionality for the GPT model.

    Attributes:
        api_key (str): The API key for authenticating with the OpenAI API.
        model (str): The specific GPT model to use, default is "gpt-4o-mini".
        client (OpenAI): An instance of the OpenAI client for making API calls.

    """
    def __init__(self):
        super().__init__()
        self.api_key = get_api_key("openai")
        self.model = "gpt-4o-mini"
        self.client = OpenAI(api_key=self.api_key)

        # Load GPT-specific prompt
        try:
            with open("prompts/gpt/gpt_training_plan_generation_system_prompt.txt", "r") as f:
                self.training_plan_prompt = f.read()
        except FileNotFoundError:
            logger.error("System prompt file not found.")
            raise
        except Exception as e:
            logger.error("Error reading system prompt file: %s", str(e))
            raise

    def generate_plan(self, user_prompt: str) -> str:
        """
        Generate a training plan using the GPT model.

        This method sends a request to the OpenAI API to generate a training plan
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
        logger.info("Starting plan generation using GPT")
        logger.info("Model: %s", self.model)
        try:
            zone_context = self._prepare_zone_context(user_prompt)

            response = self.client.beta.chat.completions.parse(
                model = self.model,
                messages = [
                    {"role": "system", "content": self.training_plan_prompt},
                    {"role": "system", "content": zone_context},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens = 4000, # This needs to be updated to be proportional to the number of workouts/days/weeks
                temperature = 0.5,
                n = 1,
                response_format = TrainingPlan
            )
            logger.info("Plan generation completed successfully")
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Error during plan generation: %s", str(e))
            raise
