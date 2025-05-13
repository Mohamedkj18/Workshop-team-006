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

######### temprorly disable user existance validation #########
DISABLE_USER_CHECK = True
###############################################################

router = APIRouter()

##########################################################
###################                    ###################
###################        GET         ###################
###################                    ###################
##########################################################

@router.get('/users/{user_id}/drafts', response_model=dict)
async def get_drafts(
    user_id: str,
    skip: int = DEFULT_SKIP,
    limit: int = DEFULT_LIMIT,
    status: Optional[DraftStatus] = Query(None)
):
    if not DISABLE_USER_CHECK:
        # validate that user exists
        if not users_collection.find_one({"user_id": user_id}):
            raise HTTPException(status_code=404, detail="User not found")

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

@router.get('/users/{user_id}/drafts/{draft_id}', response_model=dict)
async def get_draft_by_id(
    user_id: str,
    draft_id: str
):
    if not DISABLE_USER_CHECK:
        # validate that user exists
        if not users_collection.find_one({"user_id": user_id}):
            raise HTTPException(status_code=404, detail="User not found")

    # Build query
    query = {'user_id': user_id, 'draft_id': draft_id}

    # Paginate and serialize
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

@router.post('/users/{user_id}/drafts', response_model = DraftDB)
async def post_draft(user_id: str, draft: DraftCreate):

    if not DISABLE_USER_CHECK:
        # validate that user exists
        if not users_collection.find_one({"user_id": user_id}):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    # prepare the data
    draft_db = prepare_draft_create(user_id, draft)

    # insert the data
    try:
        drafts_collection.insert_one(draft_db.model_dump(mode="json"))
    except DuplicateKeyError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Duplicate draft: draft already exists")

    # return the inserted draft
    return draft_db


##########################################################
###################                    ###################
###################        PUT         ###################
###################                    ###################
##########################################################
@router.put('/users/{user_id}/drafts/{draft_id}', response_model = DraftDB)
async def put_draft(user_id: str, draft_id: str, draft: DraftUpdate):
    
    if not DISABLE_USER_CHECK:
        # check if the draft exists and if it belongs to the
        existing_draft = drafts_collection.find_one({"draft_id": draft_id, "user_id": user_id})

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



@router.put("/users/{user_id}/drafts/{draft_id}/approve", response_model = DraftDB)
def approve_draft(user_id: str, draft_id: str):
    
    # find draft
    draft = drafts_collection.find_one({"draft_id": draft_id})
    if not draft:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found"
        )
    
    if not DISABLE_USER_CHECK:
        
        # validate that user exists
        if not users_collection.find_one({"user_id": user_id}):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail = "User not found")
        
        # check if the draft belongs to the user
        if draft['user_id'] != user_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail = "Draft does not belong to the specified user"
            )
    
    # varify status update rules
    status_val = draft.get("status")
    if status_val == DraftStatus.sent.value:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail = "Cannot approve a sent draft"
        )
    
    if status_val == DraftStatus.approved.value:
        return DraftDB(**draft)  # already approved -> return as is

    # update status
    updated = drafts_collection.find_one_and_update(
        {"draft_id": draft_id},
        {"$set": {"status": DraftStatus.approved.value}},
        return_document = ReturnDocument.AFTER
    )

    return DraftDB(**updated)

@router.put("/users/{user_id}/drafts/{draft_id}/send", response_model = DraftDB)
def send_draft(user_id: str, draft_id: str):
    
    # find draft
    draft = drafts_collection.find_one({"draft_id": draft_id})
    if not draft:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found"
        )
    
    if not DISABLE_USER_CHECK:
        
        # validate that user exists
        if not users_collection.find_one({"user_id": user_id}):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail = "User not found")
        
        # check if the draft belongs to the user
        if draft['user_id'] != user_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail = "Draft does not belong to the specified user"
            )
    
    # varify status update rules
    status_val = draft.get("status")
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

@router.delete('/users/{user_id}/drafts/{draft_id}', response_model = DraftDB)
async def delete_draft(user_id: str, draft_id: str):
    
    # attempt to delete matching draft
    deleted_draft = drafts_collection.find_one_and_delete(
        {"user_id": user_id, "draft_id": draft_id} # filter
    )
    
    # handling not found
    if deleted_draft is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail = "Draft not found or does not belong to the specified user"
        )
    
    
    return DraftDB(**deleted_draft)