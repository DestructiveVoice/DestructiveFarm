from prometheus_client import Counter, Gauge, Summary

from server.models import FlagStatus

# Updated every submitter cycle
QUEUED_FLAGS = Gauge("flags_queued", "Number of queued flags")
FLAGS = {
    FlagStatus.ACCEPTED: Counter(
        "flags_accepted", "Number of sent flags", ["sploit", "team"]
    ),
    FlagStatus.SKIPPED: Counter(
        "flags_skipped", "Number of skipped flags", ["sploit", "team"]
    ),
    FlagStatus.REJECTED: Counter(
        "flags_rejected", "Numbers of rejected flags", ["sploit", "team"]
    ),
}

SUBMITTER_LATENCY = Summary("submitter_latency", "Latency of the submitter")
