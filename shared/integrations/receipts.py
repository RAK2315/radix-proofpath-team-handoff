from shared.contracts.models import uid
from shared.integrations import store
from shared.integrations.auth import Identity


def record(user: Identity, kind: str, inputs: dict, result: dict) -> dict:
    receipt = {"id": uid(), "kind": kind, "created_at": store.now(), "inputs": inputs, "result": result}
    store.save(user, "receipt", receipt)
    return {**result, "receipt_id": receipt["id"]}
