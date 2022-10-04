
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import calendar

dfs = []
month = 9

def test_ploting():

    data = {"PRs": {"Opened": 1, "Closed": 2}, "Issues": {"Opened": 3, "Closed": 4}}
    df = pd.DataFrame(data).melt(ignore_index=False).reset_index()
    df["repo"] = "bids-specification"
    df.columns = ["state", "item_type", "value", "repo"]

    data = {"PRs": {"Opened": 1, "Closed": 2}, "Issues": {"Opened": 3, "Closed": 4}}
    df = pd.DataFrame(data).melt(ignore_index=False).reset_index()
    df["repo"] = "bids-schema"
    df.columns = ["state", "item_type", "value", "repo"]

    dfs.append(df)
    df = pd.concat(dfs)

# with sns.plotting_context("talk"):
#     fig, axs = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={"hspace": 0.75})
#     plt.tight_layout()
#     for i, item_type in enumerate(["PRs", "Issues"]):

#         ax = axs.flat[i]

#         sns.barplot(
#             ax=ax,
#             x="repo",
#             y="value",
#             hue="state",
#             data=df[df["item_type"] == item_type],
#         )

#         if i > 0:
#             ax.get_legend().remove()

#         ax.set(xlabel="", title=item_type)
#         ax.set_xticks(ax.get_xticks(), ax.get_xticklabels(), rotation=45, ha="right")


# sns.despine(fig)
# fig.suptitle(f"BIDS: GitHub summary for {calendar.month_name[month]}")

# fig.savefig("output.png")
