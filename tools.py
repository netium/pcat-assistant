import os
from datetime import date, datetime, timedelta

import httpx
from loguru import logger
from pipecat.services.llm_service import FunctionCallParams
from tavily import TavilyClient

WEATHERAPI_BASE_URL = "http://api.weatherapi.com/v1"
WEATHERAPI_TIMEOUT_SECONDS = 10.0

_DATE_FORMATS = ("%Y-%m-%d",)


def _parse_requested_date(date_str: str) -> date:
    """Parse the LLM-supplied date into a ``date`` object."""
    today = datetime.now().date()
    lowered = date_str.strip().lower()
    if lowered == "today":
        return today
    if lowered == "tomorrow":
        return today + timedelta(days=1)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"Unsupported date {date_str!r}. Use 'today', 'tomorrow', or YYYY-MM-DD."
    )


def _select_endpoint(target: date, today: date) -> str:
    """Pick the weatherapi.com endpoint that can serve ``target``."""
    if target == today:
        return "current"
    if target > today:
        return "forecast"
    return "history"


async def get_current_location(params: FunctionCallParams):
    """ Get the current location of the user. """

    await params.result_callback( {
        "city": "Chengdu"
    } )

async def get_current_date(params: FunctionCallParams):
    """ Get the current date. """

    logger.info("Getting current date")

    now = datetime.now()
    await params.result_callback({
        "date": now.strftime("%Y-%m-%d"),
        "weekday": now.strftime("%A"),
    })

async def get_weather(
    params: FunctionCallParams,
    location: str,
    date: str = "today",
    temperature_unit: str = "celsius",
):
    """ Get the weather in a given location for a specific day.

    Args:
        location: The city name or "lat,lon" decimal coordinate to get the weather for.
        date: The day to get the weather for. Use "today", "tomorrow", or a date in
            "YYYY-MM-DD" format. Defaults to "today".
        temperature_unit: The temperature unit to use. MUST BE either "celsius" or
            "fahrenheit". Defaults to "celsius".
    """

    api_key = os.getenv("WEATHERAPI_API_KEY")
    if not api_key:
        await params.result_callback(
            {"error": "WEATHERAPI_API_KEY is not configured"}
        )
        return

    try:
        target_date = _parse_requested_date(date)
    except ValueError as exc:
        await params.result_callback({"error": str(exc)})
        return

    today = datetime.now().date()
    endpoint = _select_endpoint(target_date, today)

    request_params: dict[str, str | int] = {"key": api_key, "q": location, "aqi": "no"}
    if endpoint == "current":
        url = f"{WEATHERAPI_BASE_URL}/current.json"
    elif endpoint == "forecast":
        url = f"{WEATHERAPI_BASE_URL}/forecast.json"
        request_params["days"] = (target_date - today).days + 1
        request_params["alerts"] = "no"
    else:
        url = f"{WEATHERAPI_BASE_URL}/history.json"
        request_params["dt"] = target_date.isoformat()

    logger.info(
        f"Fetching weather from weatherapi.com endpoint={endpoint} "
        f"location={location!r} date={target_date.isoformat()} unit={temperature_unit}"
    )

    try:
        async with httpx.AsyncClient(timeout=WEATHERAPI_TIMEOUT_SECONDS) as client:
            response = await client.get(url, params=request_params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        logger.error(f"weatherapi.com returned status={status}")
        await params.result_callback({"error": f"Weather API error: {status}"})
        return
    except (httpx.RequestError, ValueError) as exc:
        logger.error(f"Failed to call weatherapi.com: {exc}")
        await params.result_callback({"error": f"Failed to fetch weather: {exc}"})
        return

    await params.result_callback(dict(payload))

async def open_window(params: FunctionCallParams, percentage: int):
    """ Open the window by a given percentage.

    Args:
        percentage: The percentage to open the window by.
    """

    logger.info(f"Opening window by {percentage}%")

    await params.result_callback( {
        "status": "success"
    } )

async def launch_app(params: FunctionCallParams, app_name: str):
    """ Launch a given app.

    Args:
        app_name: The name of the app to launch.
    """

    logger.info(f"Launching {app_name}")

    await params.result_callback( {
        "status": "success"
    } )

async def general_web_search(params: FunctionCallParams, query: str):
    """ Perform a general web search.

    Args:
        query: The query to search for.
    """

    logger.info(f'Searching for: "{query}"')

    tavily_client = TavilyClient(
        api_key=os.getenv("TAVILY_API_KEY")
    )
    response = tavily_client.search(query)

    logger.info(f'Search results: {response}')

    await params.result_callback(response)