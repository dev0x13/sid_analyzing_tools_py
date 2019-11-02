import sys
import os
import argparse
import re
import random

import pygraphviz as pgv
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
TMP_FILE = "tmp.png"
DPI = 200

if __name__ == "__main__":

    # 0. Parse args

    parser = argparse.ArgumentParser(description='')

    parser.add_argument("-f", "--file", default="ds_deps.log", dest="file",
                        help="path to ds_deps.log (default: ds_deps.log)")
    parser.add_argument("-s", "--save-fig", default=False, dest="save_fig", type=bool,
                        help="save dependency graph image to file dependency_graph.png (default: false)")

    args = parser.parse_args()

    # 1. Parse log file

    with open(args.file, "r") as f:
        log = f.read()

    regexp = re.compile(r"(.*?)\[(.*?)\]")

    deps = pgv.AGraph(directed=True)

    nodes = {"0": "0"}
    edges = []

    estimators_colors = {}
    nodes_user_estimators = {}

    for n, t in enumerate(log.split("\n")):
        if t:
            # sample `t` - DS_arithmetics : [ 4 [ 0] ] ; [ 7 [ 1] ]

            it1 = t.split(" : ")
            estimator_name = it1[0] + " (%i)" % n

            if estimator_name not in estimators_colors:
                # Assign random color
                estimators_colors[estimator_name] = "#%06x" % random.randint(0, 0xFFFFFF)

            it2 = it1[1].split(" ; ")

            for i in it2:
                # Remove square brackets
                it3 = i[2:-2]

                # Get Repo entry index
                repo_entry_index = regexp.search(it3).group(1).strip()
                nodes[repo_entry_index] = it3

                # Assign estimators using node
                if it3 not in nodes_user_estimators:
                    nodes_user_estimators[it3] = []
                else:
                    if len(nodes_user_estimators[it3]) > 2:
                        raise NotImplementedError("Visualization for >2 estimators using DS is not implemented")

                nodes_user_estimators[it3].append(estimator_name)

                # Find parent Repo entry
                parent_repo_entries_indexes = regexp.search(it3).group(2).split(",")

                # Build dependencies between DS
                for p in parent_repo_entries_indexes:
                    edges.append((nodes[p.strip()], it3))

    # 2. Build dependency graph

    for k, v in nodes.items():
        # 2.1. Skip root
        if v == "0":
            deps.add_node("0", style="filled", label='<<b>0</b>>', fontsize='15', fontname="Arial")
            continue

        # 2.2. Build node color according to the number of its users
        num_user_estimators = len(nodes_user_estimators[v])
        part = 1.0 / num_user_estimators
        result_color = ""

        for e in nodes_user_estimators[v]:
            result_color += (";%.2f:" % part if result_color != "" else "") + "%s" % estimators_colors[e]

        # 2.3. Add node
        deps.add_node(v, style="filled", label='<<b>%s</b>>' % v, gradientangle=180, color=result_color, fontsize='15', fontname="Arial")

    # 2.4. Add edges

    for e in edges:
        deps.add_edge(e[0], e[1])

    # 3. Draw dependency graph

    # 3.1. PyGraphviz part
    deps.layout()
    deps.draw(TMP_FILE, args="-Gdpi=%i" % DPI)

    # 3.2. Matplotlib part
    plt.figure(figsize=(10, 10))
    plt.imshow(Image.open(TMP_FILE))
    os.remove(TMP_FILE)

    plt.legend(
        [Line2D([0], [0], color=v, lw=4) for v in estimators_colors.values()],
        estimators_colors.keys(),
        loc="upper center",
        bbox_to_anchor=(0.5, 0.01),
        shadow=True,
        fancybox=True,
        ncol=2,
        prop={'size': 22}
    )
    plt.axis('off')

    if args.save_fig:
        plt.savefig("dependency_graph.png", dpi=DPI)

    plt.show()
