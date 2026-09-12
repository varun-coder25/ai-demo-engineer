import pandas as pd


DATASET_URL = (
    "https://huggingface.co/datasets/"
    "pwc-archive/links-between-paper-and-code/"
    "resolve/main/data/train-00000-of-00001.parquet"
)


def load_paper_code_mapping():
    columns = [
        "paper_arxiv_id",
        "paper_title",
        "paper_url_abs",
        "repo_url",
        "is_official",
        "mentioned_in_paper",
        "mentioned_in_github",
    ]

    return pd.read_parquet(DATASET_URL, columns=columns)


def get_papers_with_repositories(df, limit=10):
    df = df.dropna(subset=["paper_arxiv_id", "repo_url"])

    df = df[df["repo_url"].str.startswith("https://github.com/")]

    official = df[df["is_official"] == True]

    if len(official) >= limit:
        df = official

    df = df.drop_duplicates(subset=["paper_arxiv_id"])

    return df.head(limit)