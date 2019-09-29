import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

from utils import parse_data_model_transitions, get_cache_summary, get_opt_beladi_cache_hit_ratio


if __name__ == "__main__":

    # 0. Parse args

    parser = argparse.ArgumentParser(description='DataModel transitions diagram visualizer.')

    parser.add_argument("-f", "--file", default="data_model_transitions.log", dest="file",
                        help="path to DataModel transitions log file")
    parser.add_argument("-c", "--cache-size", dest="cache_size", type=int, required=True,
                        help="cache size in bytes for OPT algorithm evaluation")

    args = parser.parse_args()

    # 1. Parse log file

    with open(args.file, "r") as f:
        log = f.read()

    data_model_transitions = parse_data_model_transitions(log)

    # 2. Print cache summary

    print(get_cache_summary(data_model_transitions))
    print("Bélády's (OPT) algorithm hit ratio: %.2f" % get_opt_beladi_cache_hit_ratio(data_model_transitions, args.cache_size))
