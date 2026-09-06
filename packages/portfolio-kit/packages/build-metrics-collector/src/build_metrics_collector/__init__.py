"""Build Metrics Collector public API."""

from .models import AdapterResult, Event, EventError, Summary
from .store import EventStore, StoreError
from .summary import summarize

__all__ = ["AdapterResult", "Event", "EventError", "EventStore", "StoreError", "Summary", "summarize"]
__version__ = "0.1.0"

