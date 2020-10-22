import prodigy
from prodigy.components.loaders import JSONL


@prodigy.recipe(
    "mcq",
    dataset=("The dataset to save to", "positional", None, str),
    file_path=("Path to texts", "positional", None, str),
)
def mcq(dataset, file_path):
    """Validate the disambiguated LOC of raw locs extracted from ."""

    def add_html(stream):
        for task in stream:
            text = task["text"]
            pubnum = task["eg_publication_number"]
            root = "https://worldwide.espacenet.com/patent/search/publication/"
            gdoc = "https://docs.google.com/document/d/12ABwTdoLEBpf0Rn1cpUsvguMlHTRXSb_P_jO4WnMigU/edit?usp=sharing"

            task["html"] = (
                f"<span style='background-color:#775ec2;color:white;font-size:130%;font-weight:bold;'>  "
                f"{text}</span>"
                f"<br><span style='color: #808080'>Nb occurences: {task['nb_occurences']} (e.g.<a \
                           href={root + pubnum.replace('-','')}> {pubnum}</a>)"
                f"<br><a href={gdoc}>Add a missing entry</a></span>"
            )
            yield task

    stream = JSONL(file_path)  # load in the JSONL file
    stream = add_html(stream)  # add options to each task

    return {
        "dataset": dataset,  # save annotations in this dataset
        "view_id": "blocks",  # use the choice interface
        "stream": stream,
        "config": {
            "blocks": [
                {"view_id": "choice"},
                # {"view_id": "text_input", "field_rows": 3},
                # {"view_id": "html"}
            ]
        },
    }
