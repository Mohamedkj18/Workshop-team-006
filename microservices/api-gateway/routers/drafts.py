from fastapi import APIRouter, Request, HTTPException, status, Query, Body
import httpx

router = APIRouter()
DRAFTS_SERVICE_URL = "http://drafts-service:8002"  

UNREACHABLE_ERROR_MSG   = "drafts-service unreachable"
GENERAL_ERROR_MSG       = "error"

#######################
########  GET  ########
#######################

@router.get("/drafts")
async def get_all_drafts(user_id: str = Query(...)):
    """Get all drafts for the user specified in query string.
    Args:
        user_id (str): The ID of the user whose drafts are to be fetched. This is 
                       passed as a query parameter.
    Returns:
        dict: A JSON response containing the user's drafts.
    Raises:
        HTTPException: If the drafts service is unreachable or returns an error status code.
            - 503 Service Unavailable: If there is a request error (e.g., network issue).
            - Other status codes: If the drafts service returns an HTTP error.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DRAFTS_SERVICE_URL}/drafts/{user_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{UNREACHABLE_ERROR_MSG}: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"{GENERAL_ERROR_MSG}: {e.response.text}"
        )


@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: str, user_id: str = Query(...)):
    """Get a specific draft by ID.
    Args:
        draft_id (str): The unique identifier of the draft to retrieve.
        user_id (str): The unique identifier of the user. This is passed as a query parameter.
    Returns:
        dict: The JSON response from the drafts service containing the draft details.
    Raises:
        HTTPException: Raised with status 503 if the drafts service is unreachable.
        HTTPException: Raised with the status code from the drafts service if an HTTP error occurs.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DRAFTS_SERVICE_URL}/drafts/{user_id}/{draft_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{UNREACHABLE_ERROR_MSG}: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"{GENERAL_ERROR_MSG}: {e.response.text}"
        )

########################
########  POST  ########
########################

@router.post("/drafts")
async def create_draft(request: Request, body: dict = Body(None), user_id: str = Query(...)):
    """
    Create a new draft.
    Args:
        request (Request): The incoming HTTP request containing the draft data.
        user_id (str): The ID of the user for whom the draft is being created. 
                       This is provided as a query parameter.
    Returns:
        dict: The JSON response from the drafts service containing the created draft details.
    Raises:
        HTTPException: If there is an issue with the drafts service, such as:
            - Service is unreachable (503 Service Unavailable).
            - An HTTP error occurs (status code and error details are included).
    """
    
    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DRAFTS_SERVICE_URL}/drafts/{user_id}",
                json = data
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{UNREACHABLE_ERROR_MSG}: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"{GENERAL_ERROR_MSG}: {e.response.text}"
        )

#######################
########  PUT  ########
#######################

@router.put("/drafts/{draft_id}")
async def update_draft(request: Request, draft_id: str, body: dict = Body(None), user_id: str = Query(...)):
    """
    Update an existing draft by ID.
    Args:
        request (Request): The incoming HTTP request containing the draft data in JSON format.
        draft_id (str): The unique identifier of the draft to be updated.
        user_id (str): The unique identifier of the user, passed as a query parameter.
    Returns:
        dict: The JSON response from the drafts service after successfully updating the draft.
    Raises:
        HTTPException: If the drafts service is unreachable or returns an error response.
            - 503 Service Unavailable: When there is a request error (e.g., network issue).
            - HTTP status code from the drafts service: When the service returns an error response.
    """

    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{DRAFTS_SERVICE_URL}/drafts/{user_id}/{draft_id}",
                json = data
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{UNREACHABLE_ERROR_MSG}: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"{GENERAL_ERROR_MSG}: {e.response.text}"
        )

@router.put("/drafts/mark-draft-as-approved/{draft_id}")
async def approve_draft(request: Request, draft_id: str, body: dict = Body(None), user_id: str = Query(...)):
    """
    """

    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{DRAFTS_SERVICE_URL}/drafts/mark-draft-as-approved/{user_id}/{draft_id}",
                json = data
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{UNREACHABLE_ERROR_MSG}: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"{GENERAL_ERROR_MSG}: {e.response.text}"
        )

@router.put("/drafts/mark-draft-as-sent/{draft_id}")
async def send_draft(request: Request, draft_id: str, body: dict = Body(None), user_id: str = Query(...)):
    """
    """

    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{DRAFTS_SERVICE_URL}/drafts/mark-draft-as-sent/{user_id}/{draft_id}",
                json = data
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{UNREACHABLE_ERROR_MSG}: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"{GENERAL_ERROR_MSG}: {e.response.text}"
        )

##########################
########  DELETE  ########
##########################

@router.delete("/drafts/{draft_id}")
async def delete_draft(draft_id: str, user_id: str = Query(...)):
    """
    Delete a draft by ID.
    Deletes a draft for a specific user by making an HTTP request to the drafts service.
    Args:
        draft_id (str): The unique identifier of the draft to be deleted.
        user_id (str): The unique identifier of the user. This is passed as a query parameter.
    Returns:
        dict: The JSON response from the drafts service if the request is successful.
    Raises:
        HTTPException: If the drafts service is unreachable or returns an error status code.
            - 503 Service Unavailable: If there is a network issue or the service is unreachable.
            - Other status codes: If the drafts service returns an error response.
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{DRAFTS_SERVICE_URL}/drafts/{user_id}/{draft_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{UNREACHABLE_ERROR_MSG}: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"{GENERAL_ERROR_MSG}: {e.response.text}"
        )

