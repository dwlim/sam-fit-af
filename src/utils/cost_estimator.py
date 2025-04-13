class BaseCostEstimator:
    """
    Base class for estimating API usage costs.

    This class provides a foundation for calculating costs based on fixed request fees
    and token usage for both input and output.
    """

    def __init__(self, fixed_cost_per_request: float, input_token_cost_per_1000: float, output_token_cost_per_1000: float):
        """
        Initialize the BaseCostEstimator with cost parameters.

        Args:
            fixed_cost_per_request (float): Fixed cost per API request.
            input_token_cost_per_1000 (float): Cost per 1000 input tokens.
            output_token_cost_per_1000 (float): Cost per 1000 output tokens.
        """
        self.fixed_cost_per_request = fixed_cost_per_request
        self.input_token_cost_per_token = input_token_cost_per_1000 / 1000
        self.output_token_cost_per_token = output_token_cost_per_1000 / 1000

    def estimate_cost(self, duration_weeks: int, days_per_week: int, extra_response_tokens: int = 300, 
                      tokens_per_day: int = 150, input_tokens: int = 1000) -> float:
        """
        Estimate the total cost of generating a training plan.

        Args:
            duration_weeks (int): Number of weeks for the training plan.
            days_per_week (int): Number of training days per week.
            extra_response_tokens (int, optional): Additional tokens for the response. Defaults to 300.
            tokens_per_day (int, optional): Tokens required per training day. Defaults to 150.
            input_tokens (int, optional): Number of input tokens. Defaults to 1000.

        Returns:
            float: Total estimated cost.
        """
        output_tokens = duration_weeks * days_per_week * tokens_per_day + extra_response_tokens
        token_cost = (input_tokens * self.input_token_cost_per_token + 
                      output_tokens * self.output_token_cost_per_token)
        return self.fixed_cost_per_request + token_cost


class LlamaCostEstimator(BaseCostEstimator):
    """Cost estimator for the Llama Model(s)."""

    def __init__(self, model: str = "small"):
        """
        Initialize the LlamaCostEstimator with cost parameters for the specified Llama model.

        Args:
            model (str, optional): Llama model size. Either "small" or "large". Defaults to "small".
        """
        if model == "small":
            super().__init__(fixed_cost_per_request=0.005, input_token_cost_per_1000=0.0002, output_token_cost_per_1000=0.0002)
        elif model == "large":
            super().__init__(fixed_cost_per_request=0.005, input_token_cost_per_1000=0.001, output_token_cost_per_1000=0.001)
        else:
            raise ValueError("Invalid model. Choose either 'small' or 'large'.")


class GPTCostEstimator(BaseCostEstimator):
    """Cost estimator for the GPT Models."""

    def __init__(self):
        """Initialize the GPTCostEstimator with cost parameters for the gpt-4o-mini model."""
        super().__init__(fixed_cost_per_request=0.0002, input_token_cost_per_1000=0.00015, output_token_cost_per_1000=0.0006)
