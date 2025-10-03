
import threading
import time

import cachetools
import pm4py
from fastapi import HTTPException

import constants

cache = cachetools.LRUCache(maxsize=100)


# cache the log so it does not have to constantly be reloaded.
def cache_log(log_id: int, file: str) -> None:
    # load event log into cache
    try:
        log_data = pm4py.convert_to_dataframe(pm4py.read_xes("./uploads/" + file))
    except Exception:
        raise HTTPException(status_code=400, detail={'err': constants.INVALID_EVENT_LOG_ERROR, 'id': log_id})
    cache[log_id] = {
        "loading": False,
        "log": log_data,
        "cached_at": time.time(),
    }


# retrieve log from cache, if not existent, lazy load
def get_log_data(event_log):
    # Check if the log is already in the cache
    if event_log.id not in cache:
        # set the current state of the cache to loading, such that no other thread can will load it redundantly
        # Create an empty event for other threads to wait on
        event = threading.Event()
        cache[event_log.id] = {
            "loading": True,
            'event': event
        }
        cache_log(event_log.id, event_log.path)
        event.set()

    # If the event log is currently being loaded, wait for it to finish
    if cache[event_log.id]["loading"]:
        # Wait for the loading to finish
        cache[event_log.id]["event"].wait()

    return cache.get(event_log.id)["log"]


def remove_from_cache(event_log):
    if event_log.id in cache:
        del cache[event_log.id]