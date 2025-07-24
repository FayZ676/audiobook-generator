from typing import Literal
from datetime import datetime

from fastapi import APIRouter

from tta_service.utils import calculate_user_total_cost, calculate_cost, add_file
from tta_service.types import LogEntry
from tta_service.config import LOGS_BUCKET


router = APIRouter()


SubscriptionEvents = Literal["subscriptionItem.active"]


# TODO: I don't think we need this separate endpoint. We should be able to handle this in the webhook endpoint. Rename webhook to "events".
@router.post("/subscription/{user_id}/{event}")
def handle_subscription_event(user_id: str, event: SubscriptionEvents):
    match event:
        case "subscriptionItem.active":
            current_cost = calculate_cost(
                request_word_count=0, job_type="subscription_reset"
            )
            total_cost = calculate_user_total_cost(
                user_id=user_id, event="subscription_reset", current_cost=current_cost
            )
            log_entry = LogEntry(
                event="subscription_reset", total_cost=total_cost, cost=current_cost
            )
            add_file(
                data=log_entry.model_dump(),
                filename=f"{user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                bucket_name=LOGS_BUCKET,
            )
        case _:
            raise ValueError(f"Unknown event: {event}")
