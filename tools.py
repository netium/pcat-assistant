from pipecat.services.llm_service import FunctionCallParams

async def get_current_location(params: FunctionCallParams):
    """ Get the current location of the user. """

    await params.result_callback( {
        "city": "Chengdu"
    } )

async def get_current_weather(params: FunctionCallParams, location: str, temperature_unit: str = "celsius"):
    """ Get the current weather in a given location. 
    
    Args:
        location: The city name to get the weather for.
        format: The temperature unit to use. MUST BE either "celsius" or "fahrenheit". By default it's "celsius".
    """

    weather_data = {"conditions": "sunny", "temperature": "25"}
    
    await params.result_callback(weather_data)

async def open_window(params: FunctionCallParams, percentage: int):
    """ Open the window by a given percentage.
    
    Args:
        percentage: The percentage to open the window by.
    """

    await params.result_callback( {
        "status": "success"
    } )
