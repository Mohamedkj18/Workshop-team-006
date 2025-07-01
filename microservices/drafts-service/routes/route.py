from fastapi                    import APIRouter, HTTPException, status, Query
from schema.schemas             import individual_serial, list_serial
from pymongo                    import ReturnDocument
from pymongo.errors             import DuplicateKeyError

# my modules
from config.database            import drafts_collection, users_collection
from config.paging              import DEFULT_SKIP, DEFULT_LIMIT
from models.drafts              import *
from utils.drafts_utils         import *
from utils.time_utils           import *

###############################################################

router = APIRouter()

##########################################################
###################                    ###################
###################        GET         ###################
###################                    ###################
##########################################################

@router.get('/drafts/{user_id}', response_model=dict)
async def get_drafts(
    user_id: str,
    skip: int = DEFULT_SKIP,
    limit: int = DEFULT_LIMIT, status: Optional[DraftStatus] = Query(None)
):
    """
    Retrieve a paginated list of drafts for a specific user.
    Args:
        user_id (str): The ID of the user whose drafts are to be retrieved.
        skip (int, optional): The number of drafts to skip for pagination. Defaults to DEFULT_SKIP.
        limit (int, optional): The maximum number of drafts to return. Defaults to DEFULT_LIMIT.
        status (Optional[DraftStatus], optional): Filter drafts by their status. Defaults to None.
    Returns:
        dict: A dictionary containing the total number of drafts and a list of draft items.
            - total (int): The total number of drafts matching the query.
            - items (list): A list of serialized draft objects.
    """

    # Build query
    query = {'user_id': user_id}
    if status:
        query['status'] = status.value

    # Paginate and serialize
    total = drafts_collection.count_documents(query)
    cursor = drafts_collection.find(query).skip(skip).limit(limit)
    drafts = list_serial(list(cursor))

    return {
        "total": total,
        "items": drafts
    }

@router.get('/drafts/{user_id}/{draft_id}', response_model=dict)
async def get_draft_by_id(
    user_id: str,
    draft_id: str
):
    """
    Retrieve a draft document by its ID and associated user ID.
    Args:
        user_id (str): The ID of the user who owns the draft.
        draft_id (str): The unique identifier of the draft.
    Returns:
        dict: The draft document if found.
    Raises:
        HTTPException: If no draft is found for the given user and draft ID, 
                       or if there is more than one draft with the same ID.
    """

    # Build query
    query = {'user_id': user_id, 'draft_id': draft_id}

    # serialize
    cursor = drafts_collection.find(query)
    drafts = list_serial(list(cursor))

    if len(drafts) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found or does not belong to the specified user"
        )

    if len(drafts) > 1:
        raise HTTPException(
            # This means that there is more than one draft with the same ID.
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error! There is more than one draft with the same ID."
        )
    return drafts[0]

##########################################################
###################                    ###################
###################        POST        ###################
###################                    ###################
##########################################################

@router.post('/drafts/{user_id}', response_model = DraftDB)
async def post_draft(user_id: str, draft: DraftCreate):
    """
    Handles the creation of a new draft for a given user.
    Args:
        user_id (str): The unique identifier of the user creating the draft.
        draft (DraftCreate): The draft data provided by the user.
    Raises:
        HTTPException: If a draft with the same unique identifier already exists,
                       an HTTP 409 Conflict error is raised.
    Returns:
        DraftCreate: The draft object that was successfully inserted into the database.
    """

    # prepare the data
    draft_db = prepare_draft_create(user_id, draft)

    # insert the data
    try:
        drafts_collection.insert_one(draft_db.model_dump(mode="json"))
    except DuplicateKeyError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Duplicate draft: draft already exists"
        )

    # return the inserted draft
    return draft_db


##########################################################
###################                    ###################
###################        PUT         ###################
###################                    ###################
##########################################################
@router.put('/drafts/{user_id}/{draft_id}', response_model = DraftDB)
async def put_draft(user_id: str, draft_id: str, draft: DraftUpdate):
    """
    Update an existing draft for a specific user.
    Args:
        user_id (str): The ID of the user who owns the draft.
        draft_id (str): The ID of the draft to be updated.
        draft (DraftUpdate): The updated draft data.
    Raises:
        HTTPException: If the draft does not exist or does not belong to the specified user.
        HTTPException: If the draft cannot be found during the update process.
    Returns:
        DraftDB: The updated draft object.
    """

    # Build query
    query = {'user_id': user_id, 'draft_id': draft_id}

    existing_draft = drafts_collection.find_one(query)

    if not existing_draft:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found or does not belong to the specified user"
        )

    # prepare the data updates
    update_data = prepare_draft_update(draft).model_dump(
        mode = "json",
        exclude_unset = True
    )

    # preform the update
    updated_draft = drafts_collection.find_one_and_update(
        {"draft_id": draft_id}, # filter
        {"$set": update_data}, # update
        return_document = ReturnDocument.AFTER # return value
    )

    # handling not found
    if updated_draft is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found"
        )
    
    return DraftDB(**updated_draft)



@router.put("/drafts/mark-draft-as-approved/{user_id}/{draft_id}", response_model = DraftDB)
def approve_draft(user_id: str, draft_id: str):
    """
    Approves a draft for a specified user if it meets the required conditions.
    Args:
        user_id (str): The ID of the user who owns the draft.
        draft_id (str): The ID of the draft to be approved.
    Raises:
        HTTPException: 
            - If the draft does not exist or does not belong to the specified user (404).
            - If the draft has already been sent and cannot be approved (400).
    Returns:
        DraftDB: The updated draft object with the approved status, or the existing draft 
        if it was already approved.
    """

    # Build query
    query = {'user_id': user_id, 'draft_id': draft_id}

    existing_draft = drafts_collection.find_one(query)

    if not existing_draft:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found or does not belong to the specified user"
        )
    
    # varify status update rules
    status_val = existing_draft.get("status")
    if status_val == DraftStatus.sent.value:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail = "Cannot approve a sent draft"
        )
    
    if status_val == DraftStatus.approved.value:
        return DraftDB(**existing_draft)  # already approved -> return as is

    # update status
    updated = drafts_collection.find_one_and_update(
        {"draft_id": draft_id},
        {"$set": {"status": DraftStatus.approved.value}},
        return_document = ReturnDocument.AFTER
    )

    return DraftDB(**updated)


@router.put("/drafts/mark-draft-as-sent/{user_id}/{draft_id}", response_model = DraftDB)
def send_draft(user_id: str, draft_id: str):
    """
    Sends a draft by updating its status to 'sent' in the database.
    Args:
        user_id (str): The ID of the user who owns the draft.
        draft_id (str): The ID of the draft to be sent.
    Raises:
        HTTPException: If the draft does not exist or does not belong to the specified user.
        HTTPException: If the draft has already been sent.
        HTTPException: If the draft has not been approved before sending.
    Returns:
        DraftDB: The updated draft object with the new status.
    """

    # Build query
    query = {'user_id': user_id, 'draft_id': draft_id}

    existing_draft = drafts_collection.find_one(query)

    if not existing_draft:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found or does not belong to the specified user"
        )
    
    
    # varify status update rules
    status_val = existing_draft.get("status")
    if status_val == DraftStatus.sent.value:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail = "draft already sent"
        )
    elif status_val != DraftStatus.approved.value:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail = "draft must be approved before sending"
        )

    # update status
    updated = drafts_collection.find_one_and_update(
        {"draft_id": draft_id},
        {"$set": {"status": DraftStatus.sent.value}},
        return_document = ReturnDocument.AFTER
    )

    return DraftDB(**updated)

##########################################################
###################                    ###################
###################       DELETE       ###################
###################                    ###################
##########################################################

@router.delete('/drafts/{user_id}/{draft_id}', response_model = DraftDB)
async def delete_draft(user_id: str, draft_id: str):
    """
    Deletes a draft document from the database for a specified user.
    Args:
        user_id (str): The ID of the user who owns the draft.
        draft_id (str): The ID of the draft to be deleted.
    Raises:
        HTTPException: If no draft is found matching the given user_id and draft_id,
                       or if the draft does not belong to the specified user.
    Returns:
        DraftDB: The deleted draft document as a DraftDB object.
    """
    
    # build query
    query = {"user_id": user_id, "draft_id": draft_id}

    # attempt to delete matching draft
    deleted_draft = drafts_collection.find_one_and_delete(query)
    
    # handling not found
    if deleted_draft is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found or does not belong to the specified user"
        )
    
    
    return DraftDB(**deleted_draft)