from mcp.server.fastmcp import FastMCP
from github_client import GitHubClient

mcp    = FastMCP("github-repo-explainer")
client = GitHubClient()



@mcp.tool()
def summarize_repo(repo_url: str) -> str:
    """Summarize a GitHub repo: its purpose, language, structure, and key files.

    Args:
        repo_url: Full GitHub URL or 'owner/repo' (e.g. 'openai/openai-python')
    """
    repo   = client.fetch_repo(repo_url)
    tree   = client.get_file_tree(repo)
    readme = client.get_readme(repo)

    return f"""
        Repository: {repo.full_name}
        Description: {repo.description or 'No description.'}
        Language: {repo.language}
        Stars: {repo.stargazers_count}
        Forks: {repo.forks_count}
        Last updated: {repo.updated_at}

        File tree:
        {chr(10).join(f'  {f}' for f in tree[:50])}

        README:
        {readme}
        """.strip()


@mcp.tool()
def explain_file(repo_url: str, file_path: str) -> str:
    """Fetch a specific file from a repo so the AI can explain what it does.

    Args:
        repo_url:  Full GitHub URL or 'owner/repo'
        file_path: Path to the file inside the repo (e.g. 'src/main.py')
    """
    repo    = client.fetch_repo(repo_url)
    content = client.get_file(repo, file_path)
    return f"File: {file_path}\n\n{content}"


@mcp.tool()
def ask_repo(repo_url: str, question: str) -> str:
    """Answer a freeform question about a repo using its README and file tree.

    Args:
        repo_url: Full GitHub URL or 'owner/repo'
        question: Any question e.g. 'How do I run this locally?'
    """
    repo   = client.fetch_repo(repo_url)
    tree   = client.get_file_tree(repo)
    readme = client.get_readme(repo)

    return f"""
        Question: {question}

        Repo: {repo.full_name}
        Description: {repo.description or 'No description.'}
        Language: {repo.language}

        File tree:
        {chr(10).join(f'  {f}' for f in tree[:50])}

        README:
        {readme}
        """.strip()


@mcp.tool()
def recent_changes(repo_url: str, days: int = 7) -> str:
    """Show commits and merged PRs from the last N days.

    Args:
        repo_url: Full GitHub URL or 'owner/repo'
        days:     How many days back to look (default: 7)
    """
    repo    = client.fetch_repo(repo_url)
    commits = client.get_recent_commits(repo, days)
    prs     = client.get_recent_prs(repo, days)

    commit_lines = [
        f"  [{c['date']}] {c['author']}: {c['message']}"
        for c in commits[:20]
    ]
    pr_lines = [
        f"  [{p['merged_at']}] #{p['number']} {p['title']} by {p['author']}"
        for p in prs[:10]
    ]

    return f"""
        Recent activity in {repo.full_name} (last {days} days):

        Commits ({len(commits)} total):
        {chr(10).join(commit_lines) or '  None'}

        Merged PRs ({len(prs)} total):
        {chr(10).join(pr_lines) or '  None'}
        """.strip()


@mcp.tool()
def analyze_dependencies(repo_url: str) -> str:
    """List dependencies from requirements.txt or package.json and flag outdated ones.

    Args:
        repo_url: Full GitHub URL or 'owner/repo'
    """
    repo = client.fetch_repo(repo_url)
    deps = client.get_dependencies(repo)

    if not deps["found"]:
        return "No supported dependency file found (requirements.txt or package.json)."

    lines = [
        f"  {d['name']}=={d['current']} → latest: {d['latest']} {'⚠️ outdated' if d['outdated'] else '✅'}"
        for d in deps["packages"]
    ]

    return f"""
        Dependencies in {repo.full_name} ({deps['file']}):

        {chr(10).join(lines) or '  None found'}

        {sum(1 for d in deps['packages'] if d['outdated'])} outdated out of {len(deps['packages'])} total.
        """.strip()


if __name__ == "__main__":
    mcp.run(transport="stdio")