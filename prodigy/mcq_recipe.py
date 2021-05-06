import prodigy
from prodigy.components.loaders import JSONL

HEADER_STYLE = [
    "<span style='background-color:#775ec2;color:white;font-size:100%;font-weight:bold;'>",
    "</span>",
]


@prodigy.recipe(
    "mcq.loc",
    dataset=("The dataset to save to", "positional", None, str),
    file_path=("Path to texts", "positional", None, str),
)
def mcq(dataset, file_path):
    """Validate the disambiguated LOC of raw locs extracted from the patent texts."""

    def add_html(stream):
        for task in stream:
            text = task["text"]
            pubnum = str(task.get("eg_publication_number"))
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


@prodigy.recipe(
    "mcq.geoc",
    dataset=("The dataset to save to", "positional", None, str),
    file_path=("Path to texts", "positional", None, str),
)
def mcq(dataset, file_path):
    """Validate the geocoded LOC of raw locs extracted from the patent texts."""

    def add_options(stream):
        # Helper function to add options to every task in a stream

        options = [
            {"id": "country", "text": "country"},
            {"id": "state", "text": "state"},
            {"id": "county", "text": "county"},
            {"id": "city", "text": "city"},
            {"id": "postalCode", "text": "postalCode"},
            {"id": "district", "text": "district"},
            {"id": "street", "text": "street"},
            {"id": "houseNumber", "text": "houseNumber"},
        ]

        def get_options(task):
            if task.get("loc_matchLevel"):
                options_ = []
                for option in options:
                    option_id = option["id"]
                    options_ += [
                        {
                            "id": option_id,
                            "text": f"{option_id} ({task.get(f'loc_{option_id}')})",
                        }
                    ]
                    if option["id"] == task.get("loc_matchLevel"):
                        break
            else:
                options_ = options
            return options_

        for task in stream:
            task["options"] = get_options(task)
            task["html"] = (
                f"{HEADER_STYLE[0]} 🤨 {task['loc_text']} {HEADER_STYLE[1]}<br>"
                f"{HEADER_STYLE[0]} 📍 {task['loc_locationLabel']} {HEADER_STYLE[1]}"
            )
            yield task

    stream = JSONL(file_path)  # load in the JSONL file
    stream = add_options(stream)  # add options to each task

    return {
        "dataset": dataset,  # save annotations in this dataset
        "view_id": "choice",  # use the choice interface
        "stream": stream,
    }
