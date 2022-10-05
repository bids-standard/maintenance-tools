"""
Pings neurostars discourse API to:

- get all of topics for a list of tags
- saves the requests content to TSV for each tag
- prints some info for each tag

API doc: https://docs.discourse.org/

Note: 
- some topics have several tags so they may be counted twice
- some topics may not be tagged so numbers here may be an underestimation
"""

from datetime import datetime

import pandas as pd
import requests
from rich import print

from utils import return_min_max_date

"""
list of tags
GET https://neurostars.org/tags.json 
"""

tags = [
    "bids",
    "bids-specification",
    "bids-validator",
    "bids-app",
    "bidskit",
    "pybids",
    "bidsonym",
    "dcm2bids",
    "heudiconv",
    "mriqc",
    "fmriprep-report",
    "fmriprep",
    "dmriprep",
    "qsiprep",
    "aslprep",
    "smriprep",
    "dtiprep",
    "nipreps",
    "niprep",
    "fitlins",
    "openneuro",
    "openneuro-cli",
]

# Gets only the first 2 pages of topics if True
debug = True

# Set a month of interest
month = 9  # integer, e.g., May = 5


def get_topics_for_tag(tag: str, debug=False, verbose=False) -> pd.DataFrame:
    """Return a dataframe of neurostars topics for a given tag

    :param tag: neurostars tag
    :type tag: string
    :param debug: if ``True``, only gets topics of the first 2 pages. Defaults to False.
    :type debug: bool, optional
    :param verbose: defaults to False
    :type verbose: bool, optional
    :return: _description_
    :rtype: pandas.DataFrame
    """

    base_url = f"https://neurostars.org/tag/{tag}.json"

    if verbose:
        print(f"\nGET {base_url}")

    page = 1

    df = None

    dfs = []

    while True:

        url = f"{base_url}?match_all_tags=true&page={page}&tags%5B%5D={tag}"

        response = requests.get(url)

        if response.status_code != 200:
            print(f"[red]request failed: {url}[/red]")
            break

        if debug and page == 3:
            break

        if len(response.json()["topic_list"]["topics"]) == 0:
            break

        if verbose:
            print(f"[red]Page {page}[/red]")

        for i, topic in enumerate(response.json()["topic_list"]["topics"]):
            if verbose:
                print(f"{i}. {topic['created_at']} {topic['title']}")

            df = pd.json_normalize(topic)
            dfs.append(df)

        page += 1

    if dfs != []:
        df = pd.concat(dfs)

    return df


def return_posts_for_month(df: pd.DataFrame, month: int, year: int):
    (mindate, maxdate) = return_min_max_date(month, year)
    created_at = pd.to_datetime(df["created_at"], infer_datetime_format=True).dt.date
    return (created_at > mindate.date()) & (created_at < maxdate.date())


def return_stats(df):
    stats = {
        "nb_posts": len(df),
        "post_with_no_reply": len(df[df["posts_count"] == 1]),
        "post_with_accepted_answer": len(df[df["has_accepted_answer"] == True]),
        "percent_with_no_reply": 0,
        "percent_with_accepted_answer": 0,
    }

    if stats["nb_posts"] > 0:
        stats["percent_with_no_reply"] = (
            stats["post_with_no_reply"] / stats["nb_posts"] * 100
        )
        stats["percent_with_accepted_answer"] = (
            stats["post_with_accepted_answer"] / stats["nb_posts"] * 100
        )
    return stats


def main():

    year = datetime.now().year

    print(f"Neurostats stats for the {datetime.now().strftime('%B')} {year}")

    (mindate, maxdate) = return_min_max_date(month, year)
    print(f"New posts counted between {mindate.date()} and {maxdate.date()}")

    for tag in tags:

        df = get_topics_for_tag(tag, debug=debug, verbose=False)

        if df is not None:

            df.to_csv(f"{tag}.tsv", index=False, sep="\t")

            stats = return_stats(df)

            recent_post = return_posts_for_month(df, month, year)

            print(f"\nneurostars tag '{tag}':")
            print(
                f"""\t{stats['nb_posts']} posts
            {stats['post_with_no_reply']} ({stats['percent_with_no_reply']:.2f}%) with no reply
            {stats['post_with_accepted_answer']} ({stats['percent_with_accepted_answer']:.2f}%) with accepted answers"""
            )
            print(f"\t{recent_post.sum()} new posts")

            tmp_month = month
            tmp_year = year
            monthly_stats = {}
            for _ in range(1, 11):

                post_in_that_month = return_posts_for_month(df, tmp_month, tmp_year)
                df_this_month = df[post_in_that_month]

                monthly_stats[f"{tmp_year}/{tmp_month}"] = return_stats(df_this_month)

                tmp_month = tmp_month - 1
                if tmp_month <= 0:
                    tmp_month = 12
                    tmp_year = tmp_year - 1

            monthly_stats = pd.DataFrame.from_dict(monthly_stats)
            if tag == "bids":
                print(monthly_stats)


if __name__ == "__main__":
    main()
