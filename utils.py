"""Functions that get reused across modules."""
import calendar
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def return_min_max_date(month, year=None):
    """Calculate min and maxdate for our time window of interest."""
    if year is None:
        year = datetime.now().year
    mindate = datetime(year, month, 1)
    if month < 12:
        assert month >= 1, "month must be an int between 1 and 12"
        maxdate = datetime(year, month + 1, 1)
    else:
        assert month == 12, "month must be an int between 1 and 12"
        maxdate = datetime(year + 1, 1, 1)

    return mindate, maxdate


def plot_information(df: pd.DataFrame, month: int, print_to_file=True):
    """Plot maintainers report fig."""
    with sns.plotting_context("talk"):
        fig, axs = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={"hspace": 0.75})
        plt.tight_layout()
        for i, item_type in enumerate(["PRs", "Issues"]):

            ax = axs.flat[i]

            sns.barplot(
                ax=ax,
                x="repo",
                y="value",
                hue="state",
                data=df[df["item_type"] == item_type],
            )

            if i > 0:
                ax.get_legend().remove()

            ax.set(xlabel="", title=item_type)
            ax.set_xticks(
                ax.get_xticks(), ax.get_xticklabels(), rotation=45, ha="right"
            )

    sns.despine(fig)
    fig.suptitle(f"BIDS: GitHub summary for {calendar.month_name[month]}")

    if print_to_file:
        fig.savefig("output.png", bbox_inches="tight")
