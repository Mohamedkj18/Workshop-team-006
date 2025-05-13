from uuid                       import uuid4
from utils.time_utils           import *
from models.drafts              import *

def prepare_draft_create(user_id: str, draft_data: DraftCreate) -> DraftDB:
    now = getTime_now()
    return DraftDB(
        draft_id    = str(uuid4()),
        user_id     = user_id,
        subject     = draft_data.subject,
        body        = draft_data.body,
        to          = draft_data.to,
        thread_id   = draft_data.thread_id,
        from_ai     = draft_data.from_ai,
        status      = DraftStatus.pending,
        created_at  = now,
        updated_at  = now,
        sent_at     = None
    )

def prepare_draft_update(draft_update_data: DraftUpdate) -> DraftUpdateDB:
    return DraftUpdateDB(
        subject     = draft_update_data.subject,
        body        = draft_update_data.body,
        to          = draft_update_data.to,
        updated_at  = getTime_now() 
    )