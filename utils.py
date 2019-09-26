import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__))))

from base import DataModelTransition


class CacheSummary:
    def __init__(self):
        self.num_accesses = 0
        self.num_misses = 0
        self.num_hits = 0
        self.hit_ratio = 0
        self.total_get_duration_micro_s = 0
        self.total_set_duration_micro_s = 0

    def __str__(self):
        return "Cache summary:\n  num_accesses = %i\n  num_misses = %i\n  num_hits = %i\n  hit_ratio = %.2f\n" \
               "  total_get_duration_micro_s = %.1f\n  total_set_duration_micro_s = %.1f\n" %\
               (self.num_accesses, self.num_misses, self.num_hits, self.hit_ratio, self.total_get_duration_micro_s,
                self.total_set_duration_micro_s)

    def __repr__(self):
        return str(self)


def parse_data_model_transitions(str_repr):
    data_model_transitions = []

    for t in str_repr.split("\n\n"):
        if t:
            data_model_transitions.append(DataModelTransition(t))

    return data_model_transitions


def find_longest_transition(transitions):
    longest_duration = 0
    longest_transition = None

    for t in transitions:
        for a in t.actions_sequence:
            if a.duration_micro_secs > longest_duration:
                longest_duration = a.duration_micro_secs
                longest_transition = t

    return longest_transition


def get_cache_summary(transitions):
    summary = CacheSummary()

    for t in transitions:
        is_get_action = False
        is_hit = True

        for a in t.actions_sequence:
            if a.type == "Load":
                summary.num_misses += 1
                is_hit = False
            elif a.type == "Get":
                summary.num_accesses += 1
                is_get_action = True
                summary.total_get_duration_micro_s += a.duration_micro_secs
            elif a.type == "Set":
                summary.total_set_duration_micro_s += a.duration_micro_secs

        if is_hit and is_get_action:
            summary.num_hits += 1

    summary.hit_ratio = summary.num_hits / summary.num_accesses

    return summary
