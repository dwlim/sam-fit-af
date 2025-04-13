import openai
from utils.pace_zones import calculate_zones_from_json
import json

class BaseAPI:
    """
    Abstract base class for API interactions in the AI fitness project.

    This class defines the interface that all specific API implementations
    should follow. It provides a common structure for generating training plans
    across different AI models or services.
    """

    def _prepare_zone_context(self, user_prompt: str) -> str:
        """
        Calculate and format training zones based on user data.
        
        Args:
            user_prompt (str): JSON string containing user data
            
        Returns:
            str: Formatted string containing pace zones and VDOT information
        """
        user_prompt_json = json.loads(user_prompt)
        context = calculate_zones_from_json(user_prompt_json)
        # TODO: error handling for context
        return (
            f"- Estimated VO2max: {round(context['vdot'], 2)}. \n"
            f"- Speed zones in meters per second:\n"
            f"{json.dumps(context['zones'], indent=4)}\n"
            f"- Recent time trial pace: {context['time_trial_speed']} m/s for {user_prompt_json['recent_time_trial']['event']} meters.\n"
            f"- Goal event pace: {context['goal_event_speed']} m/s for {user_prompt_json['goal_event']['event']} meters."
        )

    def generate_plan(self, user_prompt: str) -> str:
        """
        Generate a training plan based on the given prompts.

        This method should be implemented by all subclasses to provide
        specific functionality for different AI models or services.

        Args:
            user_prompt (str): The user's specific request or query.

        Returns:
            str: The generated training plan text.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
    