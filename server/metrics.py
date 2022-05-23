from prometheus_client import Counter, Summary

SENT_FLAGS = Counter("flags_sent", "Number of flags sent")
RECIEVED_FLAGS = Counter("flags_recieved", "Number of flags queued")

SUBMITTER_LATENCY = Summary("submitter_latency", "Latency of the submitter")
