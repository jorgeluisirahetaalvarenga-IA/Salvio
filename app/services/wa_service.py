from app.models.wa import WaMessage


def enqueue_wa_message(message: WaMessage) -> None:
    # Celery integration will bind here in the worker block.
    return None
