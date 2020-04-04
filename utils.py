import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__))))

from base import DataModelTransition


class CacheStats:
    def __init__(self):
        self.num_accesses = 0
        self.num_misses = 0
        self.num_hits = 0
        self.hit_ratio = 0
        self.num_loads = 0
        self.num_unloads = 0
        self.mean_load_duration_ms = 0
        self.mean_unload_duration_ms = 0

    def __str__(self):
        return "Cache stats:\n  num_accesses = %i\n  num_misses = %i\n  num_hits = %i\n  hit_ratio = %.2f\n" \
               "  num_loads = %i\n  num_unloads = %i\n  mean_load_duration_ms = %.3f\n  mean_unload_duration_ms = %.3f\n" %\
               (self.num_accesses, self.num_misses, self.num_hits, self.hit_ratio,
                self.num_loads, self.num_unloads, self.mean_load_duration_ms, self.mean_unload_duration_ms)

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


def get_opt_beladi_cache_hit_ratio(transitions, cache_size_bytes):
    actions_seq = []
    get_keys_seq = []
    items_sizes = {}

    for t in transitions:
        for a in t.actions_sequence:
            if a.type == "Get":
                get_keys_seq.append(a.item_key)
                items_sizes[a.item_key] = a.item_size_bytes
                actions_seq.append(a)
            elif a.type == "Set":
                items_sizes[a.item_key] = a.item_size_bytes
                actions_seq.append(a)

    current_cache_items = {}
    num_hits = 0
    num_misses = 0
    num_accesses = 0

    def current_cache_size():
        return sum(current_cache_items.values())

    for a in actions_seq:
        if a.type == "Set":
            if a.item_size_bytes <= cache_size_bytes:
                if a.item_size_bytes <= cache_size_bytes - current_cache_size():
                    current_cache_items[a.item_key] = a.item_size_bytes
                else:
                    while a.item_size_bytes > cache_size_bytes - current_cache_size():
                        garbage = []

                        for k in current_cache_items:
                            if k not in get_keys_seq:
                                garbage.append(k)

                        if len(garbage) != 0:
                            for g in garbage:
                                del current_cache_items[g]
                        else:
                            eviction_candidates = {}

                            for i, key_to_get in enumerate(reversed(get_keys_seq)):
                                if key_to_get in current_cache_items:
                                    eviction_candidates[key_to_get] = i

                            key_to_evict = None
                            key_to_evict_distance = 0

                            for key, dist in eviction_candidates.items():
                                if dist > key_to_evict_distance:
                                    key_to_evict_distance = dist
                                    key_to_evict = key

                            del current_cache_items[key_to_evict]

                    current_cache_items[a.item_key] = a.item_size_bytes

        elif a.type == "Get":
            num_accesses += 1
            if a.item_key not in current_cache_items:
                num_misses += 1
            else:
                num_hits += 1
            get_keys_seq.remove(a.item_key)

    return num_hits / num_accesses


def compute_cache_stats(transitions):
    stats = CacheStats()

    for t in transitions:
        is_get_action = False
        is_hit = True

        for a in t.actions_sequence:
            if a.type == "Load":
                stats.num_misses += 1
                stats.mean_load_duration_ms += a.duration_micro_secs
                stats.num_loads += 1
                is_hit = False
            elif a.type == "Unload":
                stats.mean_unload_duration_ms += a.duration_micro_secs
                stats.num_unloads += 1
            elif a.type == "Get":
                stats.num_accesses += 1
                is_get_action = True

        if is_hit and is_get_action:
            stats.num_hits += 1

    stats.hit_ratio = stats.num_hits / stats.num_accesses
    stats.mean_load_duration_ms /= stats.num_loads * 1000
    stats.mean_unload_duration_ms /= stats.num_unloads * 1000

    return stats
