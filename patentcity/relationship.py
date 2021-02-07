import spacy
from spacy import Language
from spacy.tokens import Doc

"""
WARNING: functions below are copy-pasted in the relation_extractor factory for the sake of efficiency.
If you modify a function, make sure that you do the exact same modification on its twin function.
"""

LABELS = ["LOC", "CIT", "OCC"]
POSITIONS = ["before", "after", "any"]
RELATIONS = {"LOC": "LOCATION", "CIT": "CITIZENSHIP", "OCC": "OCCUPATION"}
default_config = {
    "LOC": {"max_length": None, "position": "after", "max_n": 1},
    "CIT": {"max_length": None, "position": "after", "max_n": 1},
    "OCC": {"max_length": None, "position": "after", "max_n": 1},
}

Doc.set_extension("patentees", default=[], force=True)


@spacy.Language.factory("relation_extractor", default_config={"config": default_config})
def create_relationship_component(nlp: Language, name: str, config: dict):
    return EntityRelationshipComponent(config)


class EntityRelationshipComponent:
    def __init__(self, config: dict):
        self.config = config
        if not Doc.has_extension("patentees"):
            Doc.set_extension("patentees", default=[])

    def __get_span(self, ent):
        return {
            "token_start": ent.start,
            "token_end": ent.end,
            "start": ent.start_char,
            "end": ent.end_char,
            "text": ent.text,
            "label": ent.label_,
        }

    def __harvest_candidates(
        self, head: dict, children: list, label: str, max_length: int, position: str
    ):
        """Return all candidate ent satisfying the conditions defined by max_length and position.
        POSITION refers to the relative place of the child wrt the head and MAX_LENGTH is the max
        number of tokens away from the head which are considered for the start of a child."""
        assert label in LABELS
        assert position in POSITIONS
        candidates_ = [child for child in children if child["label"] == label]

        candidates = []
        if position in ["after", "any"]:
            # we keep the candidates located after the head at a max_length dist
            candidates += [
                candidate
                for candidate in candidates_
                if 0 <= candidate["token_start"] - head["token_end"] <= max_length
            ]
        if position in ["before", "any"]:
            # we keep the candidates located before the head at a max_length dist
            candidates += [
                candidate
                for candidate in candidates_
                if 0 <= head["token_start"] - candidate["token_end"] <= max_length
            ]

        return candidates

    def __select_candidates(
        self, head: dict, candidates: list, max_n: int, position: str
    ):
        """Return the the closest MAX_N candidate(s) (wrt head)"""
        assert position in POSITIONS
        if len(candidates) > max_n:
            if position == "after":
                candidates = sorted(
                    candidates,
                    key=lambda candidate: candidate["token_start"] - head["token_end"],
                )[:max_n]

            elif position == "before":
                candidates = sorted(
                    candidates,
                    key=lambda candidate: head["token_start"] - candidate["token_end"],
                )[:max_n]
            else:  # any
                head_center = head["token_start"] + int(
                    (head["token_end"] - head["token_start"]) / 2
                )
                candidates = sorted(
                    candidates,
                    key=lambda candidate: abs(head_center - candidate["token_end"]),
                )[:max_n]
        return candidates

    def __get_child(self, head, children, label, max_length, position, max_n=1):
        candidates = self.__harvest_candidates(
            head, children, label, max_length, position
        )
        child = self.__select_candidates(head, candidates, max_n, position)
        return child

    def __format_line(self, d, label: str = None):
        label = label if label else d["label"].lower()
        return {"_".join([label, k]): v for k, v in d.items()}

    def __call__(self, doc: Doc):
        ents = [self.__get_span(ent) for ent in doc.ents]
        heads = [ent for ent in ents if ent["label"] in ["ASG", "INV"]]
        children = [ent for ent in ents if ent["label"] not in ["ASG", "INV"]]

        for head in heads:
            line = self.__format_line(head, label="name")
            for label in ["LOC", "OCC", "CIT"]:
                cfg_ = self.config[label]
                child = self.__get_child(
                    head,
                    children,
                    label,
                    cfg_["max_length"],
                    cfg_["position"],
                    cfg_["max_n"],
                )
                if child:
                    line.update(self.__format_line(child[0]))
            doc._.patentees.append(line)
        return doc


def harvest_candidates(
    head: dict, children: list, label: str, max_length: int, position: str
):
    """Return all candidate ent satisfying the conditions defined by max_length and position.
    POSITION refers to the relative place of the child wrt the head and MAX_LENGTH is the max
    number of tokens away from the head which are considered for the start of a child."""
    assert label in LABELS
    assert position in POSITIONS
    candidates_ = [child for child in children if child["label"] == label]

    candidates = []
    if position in ["after", "any"]:
        # we keep the candidates located after the head at a max_length dist
        candidates += [
            candidate
            for candidate in candidates_
            if 0 <= candidate["token_start"] - head["token_end"] <= max_length
        ]
    if position in ["before", "any"]:
        # we keep the candidates located before the head at a max_length dist
        candidates += [
            candidate
            for candidate in candidates_
            if 0 <= head["token_start"] - candidate["token_end"] <= max_length
        ]

    return candidates


def select_candidates(head: dict, candidates: list, max_n: int, position: str):
    """Return the the closest MAX_N candidate(s) (wrt head)"""
    # TODO: test it!
    assert position in POSITIONS
    if len(candidates) > max_n:
        if position == "after":
            candidates = sorted(
                candidates,
                key=lambda candidate: candidate["token_start"] - head["token_end"],
            )[:max_n]

        elif position == "before":
            candidates = sorted(
                candidates,
                key=lambda candidate: head["token_start"] - candidate["token_end"],
            )[:max_n]
        else:  # any
            head_center = head["token_start"] + int(
                (head["token_end"] - head["token_start"]) / 2
            )
            candidates = sorted(
                candidates,
                key=lambda candidate: abs(head_center - candidate["token_end"]),
            )[:max_n]
    return candidates


def get_child(head, children, label, max_length, position, max_n=1):
    candidates = harvest_candidates(head, children, label, max_length, position)
    child = select_candidates(head, candidates, max_n, position)
    return child
