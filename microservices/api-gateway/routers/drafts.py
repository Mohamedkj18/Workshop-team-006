from fastapi                    import APIRouter, HTTPException, status, Query
from config.database            import collection_name
from schema.schemas             import list_serial
from pymongo                    import ReturnDocument

# my modules
from models.drafts              import *
from utils.draft_utils          import *
from utils.time_utils           import *



router = APIRouter()

##########################################################
###################                    ###################
###################        GET         ###################
###################                    ###################
##########################################################

@router.get('/drafts', response_model = list[DraftDB])
async def router_get_drafts(user_id: str = Query(None)):
    drafts = list_serial(collection_name.find({'user_id' : user_id} if user_id else {}))
    return drafts



##########################################################
###################                    ###################
###################        POST        ###################
###################                    ###################
##########################################################

@router.post('/drafts/{user_id}', response_model = DraftDB)
async def router_post_draft(user_id: str, draft: DraftCreate):
    
    # prepare the data
    draft_db = prepare_draft_create(user_id, draft)

    # insert the data
    collection_name.insert_one(draft_db.model_dump(mode = "json"))

    return draft_db



##########################################################
###################                    ###################
###################        PUT         ###################
###################                    ###################
##########################################################
@router.put('/drafts/{draft_id}', response_model = DraftDB)
async def router_put_draft(draft_id: str, draft: DraftUpdate):
    
    # prepare the data updates
    update_data = prepare_draft_update(draft).model_dump(mode = "json")

    # insert the data updates
    updated_draft = collection_name.find_one_and_update(
        {"draft_id": draft_id},                 # filter
        {"$set": update_data},                  # update
        return_document = ReturnDocument.AFTER  # return value
    )

    # error handling
    if updated_draft is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail = "Draft not found")
    
    return DraftDB(**updated_draft)


@router.put("/drafts/{draft_id}/approve")
def router_approve_draft(draft_id: str):
    '''
    changes the status from 'pending' to 'approved'.
    if it's aleady 'approved', do noting.
    if it's aleady 'sent', raise HTTP Exception 400 (bad request).
    if drant not found, raise HTTP Exception 404 (not found).
    Args:
        draft_id (str): the id of the draft
    Returns:
        json: the updated draft, or exception
    '''
    pass


##########################################################
###################                    ###################
###################       DELETE       ###################
###################                    ###################
##########################################################

@router.delete('/drafts/{user_id}/{draft_id}', response_model = DraftDB)
async def router_delete_draft(draft_id: str, draft: DraftUpdate):
    deleted_draft = collection_name.find_one_and_delete(
        {"draft_id": draft_id}                   # filter
    )
    if deleted_draft is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail = "Draft not found")
    return DraftDB(**deleted_draft)
