from fastapi import APIRouter


router = APIRouter()


@router.post("/subscription/{user_id}/{event_type}")
def handle_subscription_event(user_id: str, event_type: str):
    # TODO: Reset user's usage to zero.
    print(
        {
            "message": "Subscription event received successfully",
            "user_id": user_id,
            "event_type": event_type,
        }
    )
