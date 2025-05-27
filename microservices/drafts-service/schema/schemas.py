from models.drafts              import DraftDB



def individual_serial(draftDB_as_dict: dict) -> dict:
    return DraftDB(**draftDB_as_dict).model_dump()

def list_serial(drafts: list[dict]) -> list[dict]:
    return [individual_serial(d) for d in drafts]