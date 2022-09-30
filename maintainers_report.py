"""Provide updates in repositories of the bids-standard GitHub organization.

NOTE: This script can take around 10 minutes to run. It's not very efficient.

Information of interest within 1 month time frame:
- PRs opened
- PRs merged (not just closed; and even if opened before time frame)
- Issues opened
- Issues closed (even if opened before time frame)

Maybe for future extensions:
- N files changed on master
- N additions, N deletions on master
- N users involved in issues and PRs

Requirements:
- PyGitHub (https://github.com/PyGithub/PyGithub)
- Matplotlib
- Seaborn
- Pandas

"""

# %%
# Imports
import calendar
import json
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from github import Github
from tqdm import tqdm

# %%
# Settings
# Set a token (or use None)
# NOTE: Never commit a token to git history
token = None
g = Github(login_or_token=token)

# Set a month of interest
month = 9  # integer, e.g., May = 5
user = "bids-standard"

# Set repositories of interest
repos = [
    "bids-specification",
    "bids-examples",
    "bids-validator",
    "bids-website",
    "bids-starter-kit",
    "bids-schema",
    "pybids",
    "bids-matlab",
]
repos = [user + "/" + repo for repo in repos]

# %%
# Parse information

# Calc min and maxdate for a PR/Issue to fall in our timewindow of interest
mindate = datetime(datetime.now().year, month, 1)
if month < 12:
    assert month >= 1, "month must be an int between 1 and 12"
    maxdate = datetime(datetime.now().year, month + 1, 1)
else:
    assert month == 12, "month must be an int between 1 and 12"
    maxdate = datetime(datetime.now().year + 1, 1, 1)

# PRs/issues are ordered newest to oldest by creation date
# we go through them in order, counting closed and created
# once for each repo
log = {}
dfs = []
for repo_name in tqdm(repos):
    log[repo_name] = {}
    repo = g.get_repo(repo_name)
    data = {"PRs": {"Opened": 0, "Closed": 0}, "Issues": {"Opened": 0, "Closed": 0}}
    for item_type in ["PRs", "Issues"]:
        log[repo_name][item_type] = {}
        for state in ["opened", "closed"]:

            log[repo_name][item_type][state] = []

            if item_type == "PRs":
                items = repo.get_pulls(state="open" if state == "opened" else state)
            else:
                assert item_type == "Issues"
                items = repo.get_issues(state="open" if state == "opened" else state)

            for item in items:

                # if looking through issues, clean up: each PR is an issue as
                # well, but we don't want to count these, see:
                # https://github.com/PyGithub/PyGithub/issues/1744
                if (item_type == "Issues") and (item.pull_request is not None):
                    continue

                added = False
                if item.closed_at is not None:
                    if (item.closed_at >= mindate) and (item.closed_at < maxdate):
                        if item_type == "PRs":
                            # ignore PRs that were closed but not merged
                            if not item.is_merged():
                                continue
                        data[item_type]["Closed"] += 1
                        added = True
                if (item.created_at >= mindate) and (item.created_at < maxdate):
                    data[item_type]["Opened"] += 1
                    added = True

                if added:
                    log[repo_name][item_type][state] += [item.html_url]

    df = pd.DataFrame(data).melt(ignore_index=False).reset_index()
    df["repo"] = repo_name.replace(user + "/", "")
    df.columns = ["state", "item_type", "value", "repo"]
    dfs.append(df)

df = pd.concat(dfs)
df

# %%
# print log for double checking / debugging
print(json.dumps(log, indent=4))

# %%
# Plot information
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
        ax.set_xticks(ax.get_xticks(), ax.get_xticklabels(), rotation=45, ha="right")


sns.despine(fig)
months = ["Jan"]
fig.suptitle(f"BIDS: GitHub summary for {calendar.month_name[month]}")


# %%
