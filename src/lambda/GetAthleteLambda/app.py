import json
from dataclasses import dataclass, asdict

# import requests


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    athlete_id = event["pathParameters"].get("athlete_id")
    athlete_record = get_athlete_record_from_db(athlete_id)
    athlete_object = get_athlete_from_input(athlete_record["athlete_id"], athlete_record)

    #query DB for athlete id

    #parse DB result into athlete class

    #athlete object to json

    return {
        "statusCode": 200,
        "body": athlete_object.tojson(),
    }

def get_athlete_record_from_db(athlete_id):
    return {
        "athlete_id": athlete_id,
        "basic_info_1": "test_info",
        "basic_info_2": "test_info",
        "basic_info_3": "test_info",
        "basic_info_4": "test_info",
        "basic_info_5": "test_info",
    }

@dataclass
class AthleteObject:
    """Container for workout file information."""
    athlete_id: str
    basic_info_1: str
    basic_info_2: str
    basic_info_3: str
    basic_info_4: str
    basic_info_5: str

    def __init__(
        self, 
        athlete_id: str,
        basic_info_1: str,
        basic_info_2: str,
        basic_info_3: str,
        basic_info_4: str,
        basic_info_5: str
    ) -> None:
        self.athlete_id = athlete_id
        self.basic_info_1 = basic_info_1
        self.basic_info_2 = basic_info_2
        self.basic_info_3 = basic_info_3
        self.basic_info_4 = basic_info_4
        self.basic_info_5 = basic_info_5
    
    def tojson(self):
        """Returns a JSON string representation of the AthleteObject."""
        return json.dumps(asdict(self))

def get_athlete_from_input(athlete_id, params):
    return AthleteObject(
        athlete_id, 
        params["basic_info_1"], 
        params["basic_info_2"],
        params["basic_info_3"],
        params["basic_info_4"],
        params["basic_info_5"]
    )