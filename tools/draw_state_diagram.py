import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

from utils import parse_data_model_transitions

from transitions.extensions import GraphMachine, HierarchicalGraphMachine
import matplotlib.pyplot as plt
from PIL import Image

import argparse
import io


if __name__ == "__main__":

    # 0. Parse args

    parser = argparse.ArgumentParser(description='DataModel transitions diagram visualizer.')

    parser.add_argument("-a", "--alignment", default="vertical", dest="alignment",
                        help="state diagram alignment vertical/horizontal (default: vertical)")
    parser.add_argument("-f", "--file", default="data_model_transitions.log", dest="file",
                        help="path to DataModel transitions log file")
    parser.add_argument("-s", "--save-fig", default=False, dest="save_fig", type=bool,
                        help="save state diagram to file state_diagram.png (default: false)")

    args = parser.parse_args()

    # 1. Parse log file

    with open(args.file, "r") as f:
        log = f.read()

    data_model_transitions = parse_data_model_transitions(log)

    # 2. Construct state machine

    class Model:
        pass

    model = Model()

    states = set()
    transitions = []

    def state_to_short_string(state):
        items = [k + "(%s)" % v[0] for k, v in state.items.items()]

        if args.alignment == "horizontal":
            state_str = "\n".join(items)
        else:
            state_str = "; ".join(items)

        if not state_str:
            state_str = "Empty"

        return state_str

    for t in data_model_transitions:

        states.add(state_to_short_string(t.state1))
        states.add(state_to_short_string(t.state2))

        actions_str = ""

        for a in t.actions_sequence:
            actions_str += "%s %s - %.1f \u03BCs / %i bytes" %\
                           (a.type, a.item_key, a.duration_micro_secs, a.item_size_bytes) + "\n"

        transitions.append([actions_str, state_to_short_string(t.state1), state_to_short_string(t.state2)])

    if args.alignment == "horizontal":
        machine_class = GraphMachine
    else:
        machine_class = HierarchicalGraphMachine

    machine = machine_class(
        model,
        states=list(states),
        title="DataModel Transition Diagram",
        transitions=transitions,
        initial=state_to_short_string(data_model_transitions[0].state1),
        show_conditions=True,
        show_state_attributes=True
    )

    # 3. Draw state diagram

    machine.style_attributes['node']['final'] = {'fillcolor': 'gold'}
    machine.model_graphs[model].set_node_style(state_to_short_string(data_model_transitions[-1].state2), 'final')

    stream = io.BytesIO()
    model.get_graph().draw(stream, prog='dot', format='png')

    if args.save_fig:
        with open("state_diagram.png", "wb") as f:
            f.write(stream.getvalue())

    plt.imshow(Image.open(io.BytesIO(stream.getvalue())))
    plt.show()
