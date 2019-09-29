import re


class DataModelState:
    regexp = re.compile(r"DataModelState\{(.*?)\}")

    def __init__(self, state_str):
        self.items = {}

        items = DataModelState.regexp.search(state_str).group(1)

        if not items:
            return

        items = [i.strip().replace("<", "").replace(">", "") for i in items.split(";")]
        items.remove("")

        for i in items:
            key, location = i.split(" : ")
            self.items[key] = location

    def __str__(self):
        return "DataModelState{%s}" % str(self.items)

    def __repr__(self):
        return str(self)


class DataModelAction:
    regexp = re.compile(r"DataModelAction\{(.*?)\}")

    def __init__(self, action_str):
        fields = DataModelAction.regexp.search(action_str).group(1)

        fields = [i.strip() for i in fields.split(";")]

        for f in fields:
            field, value = f.split(": ")

            if field == "level":
                self.level = int(value)
            elif field == "itemKey":
                self.item_key = value
            elif field == "type":
                self.type = value
            elif field == "itemSizeBytes":
                self.item_size_bytes = int(value)
            elif field == "durationMicroSecs":
                self.duration_micro_secs = float(value)

    def __str__(self):
        return "DataModelAction{level: %i; item_key: %s; type: %s; item_size_bytes: %i; duration_micro_secs: %i}" % (
                self.level, self.item_key, self.type, self.item_size_bytes, self.duration_micro_secs
        )

    def __repr__(self):
        return str(self)


class DataModelTransition:
    def __init__(self, transition_str):
        self.actions_sequence = []

        for t in transition_str.split("\n"):
            if t.startswith("state1"):
                self.state1 = DataModelState(t)
            elif t.startswith("DataModelAction"):
                self.actions_sequence.append(DataModelAction(t))
            elif t.startswith("state2"):
                self.state2 = DataModelState(t)

    def __str__(self):
        actions_str = ""

        for a in self.actions_sequence:
            actions_str += str(a) + "\n"

        return "DataModelTransition{\nstate1: %s\nactions: %sstate2: %s\n}" % (str(self.state2), str(actions_str), str(self.state2))

    def __repr__(self):
        return str(self)
