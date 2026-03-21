import os
import json
import requests
from datetime import datetime, timedelta, timezone
from github import Github, GithubException
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN not found in .env file.")
        self.gh = Github(token)

    #  Core helpers
    def fetch_repo(self, repo_url: str):
        """Parse a GitHub URL or 'owner/repo' string and return a repo object."""
        slug = repo_url.strip().rstrip("/")
        if "github.com" in slug:
            slug = slug.split("github.com/")[-1]
        try:
            return self.gh.get_repo(slug)
        except GithubException as e:
            raise ValueError(f"Could not find repo '{slug}': {e.data.get('message', str(e))}")

    def get_readme(self, repo, max_chars: int = 4000) -> str:
        """Fetch README contents, truncated to max_chars."""
        for name in ["README.md", "readme.md", "README.rst", "README"]:
            try:
                return repo.get_contents(name).decoded_content.decode()[:max_chars]
            except Exception:
                continue
        return "No README found."

    def get_file_tree(self, repo, max_files: int = 80) -> list:
        """Recursively fetch the full file tree up to max_files entries."""
        try:
            tree = repo.get_git_tree(repo.default_branch, recursive=True)
            return [item.path for item in tree.tree if item.type == "blob"][:max_files]
        except Exception:
            contents = repo.get_contents("")
            return [f.path for f in contents][:max_files]

    def get_file(self, repo, file_path: str, max_chars: int = 6000) -> str:
        """Fetch raw contents of a specific file."""
        try:
            return repo.get_contents(file_path).decoded_content.decode()[:max_chars]
        except GithubException as e:
            raise ValueError(f"Could not fetch '{file_path}': {e.data.get('message', str(e))}")


    #  Recent changes
    def get_recent_commits(self, repo, days: int = 7) -> list:
        """Return commits from the last N days."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        commits = repo.get_commits(since=since)
        return [
            {
                "message": c.commit.message.splitlines()[0],
                "author":  c.commit.author.name,
                "date":    c.commit.author.date.strftime("%Y-%m-%d"),
            }
            for c in commits
        ]

    def get_recent_prs(self, repo, days: int = 7) -> list:
        """Return merged PRs from the last N days."""
        since  = datetime.now(timezone.utc) - timedelta(days=days)
        prs    = repo.get_pulls(state="closed", sort="updated", direction="desc")
        result = []
        for pr in prs:
            if pr.merged_at and pr.merged_at >= since:
                result.append({
                    "number":    pr.number,
                    "title":     pr.title,
                    "author":    pr.user.login,
                    "merged_at": pr.merged_at.strftime("%Y-%m-%d"),
                })
            if pr.updated_at < since:
                break
        return result


    #  Dependency analysis
    def get_dependencies(self, repo) -> dict:
        """Parse requirements.txt or package.json and check for outdated packages."""
        try:
            content = repo.get_contents("requirements.txt").decoded_content.decode()
            packages = self._parse_requirements(content)
            return {"found": True, "file": "requirements.txt", "packages": packages}
        except Exception:
            pass

        try:
            content = repo.get_contents("package.json").decoded_content.decode()
            packages = self._parse_package_json(content)
            return {"found": True, "file": "package.json", "packages": packages}
        except Exception:
            pass

        return {"found": False, "file": None, "packages": []}

    def _parse_requirements(self, content: str) -> list:
        """Parse requirements.txt and check latest PyPI version for each package."""
        packages = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                name, current = line.split("==", 1)
                current = current.strip()
            else:
                name    = line.split(">=")[0].split(">")[0].split("[")[0].strip()
                current = "unspecified"

            latest   = self._get_latest_pypi_version(name)
            outdated = current != "unspecified" and latest and current != latest

            packages.append({
                "name":     name,
                "current":  current,
                "latest":   latest or "unknown",
                "outdated": outdated,
            })
        return packages

    def _parse_package_json(self, content: str) -> list:
        """Parse package.json dependencies."""
        data = json.loads(content)
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        return [
            {"name": name, "current": ver, "latest": "check npm", "outdated": False}
            for name, ver in deps.items()
        ]

    def _get_latest_pypi_version(self, package_name: str) -> str:
        """Fetch the latest version of a package from PyPI."""
        try:
            r = requests.get(
                f"https://pypi.org/pypi/{package_name}/json",
                timeout=3
            )
            if r.status_code == 200:
                return r.json()["info"]["version"]
        except Exception:
            pass
        return None