LABELS = ["LOC", "CIT", "OCC"]
POSITIONS = ["before", "after", "any"]
RELATIONS = {"LOC": "LOCATION", "CIT": "CITIZENSHIP", "OCC": "OCCUPATION"}


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


def format_line(d, label: str = None):
    label = label if label else d["label"].lower()
    return {"_".join([label, k]): v for k, v in d.items()}
