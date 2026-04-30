"""Git history mining — blame, log, churn, and decision archaeology."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitCommit:
    hash: str
    author: str
    date: str
    subject: str
    body: str
    files: list[str]


def get_log(repo_path: str, max_commits: int = 100) -> list[GitCommit]:
    """Extract recent commit history."""
    try:
        output = subprocess.check_output(
            ["git", "-C", repo_path, "log", f"-{max_commits}",
             "--format=%H%n%an%n%ad%n%s%n%b%n---FILE---",
             "--name-only"],
            text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return []
    return _parse_log(output)


def get_blame(repo_path: str, file_path: str) -> list[dict]:
    """Get line-by-line authorship for a file."""
    try:
        output = subprocess.check_output(
            ["git", "-C", repo_path, "blame", "--line-porcelain", file_path],
            text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return []
    entries: list[dict] = []
    current: dict = {}
    for line in output.splitlines():
        if line.startswith("author "):
            current["author"] = line[7:]
        elif line.startswith("author-time "):
            current["time"] = int(line[12:])
        elif line.startswith("summary "):
            current["summary"] = line[8:]
        elif line.startswith("\t"):
            current["line"] = line[1:]
            entries.append(current)
            current = {}
    return entries


def get_churn(repo_path: str, max_files: int = 30) -> list[tuple[str, int]]:
    """Return most-frequently-changed files (churn metric)."""
    try:
        output = subprocess.check_output(
            ["git", "-C", repo_path, "log", "--format=", "--name-only",
             f"-{max_files * 10}"],
            text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return []
    counts: dict[str, int] = {}
    for line in output.splitlines():
        line = line.strip()
        if line:
            counts[line] = counts.get(line, 0) + 1
    return sorted(counts.items(), key=lambda x: -x[1])[:max_files]


def get_contributors(repo_path: str) -> list[tuple[str, int]]:
    """Return contributors sorted by commit count."""
    try:
        output = subprocess.check_output(
            ["git", "-C", repo_path, "shortlog", "-sn", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return []
    result: list[tuple[str, int]] = []
    for line in output.splitlines():
        parts = line.strip().split("\t")
        if len(parts) == 2:
            result.append((parts[1].strip(), int(parts[0])))
    return result


def _parse_log(output: str) -> list[GitCommit]:
    commits: list[GitCommit] = []
    current: dict | None = None
    for line in output.splitlines():
        if line == "---FILE---":
            continue
        if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
            if current:
                commits.append(GitCommit(**current))
            current = {"hash": line, "files": []}
        elif current is not None:
            if "author" not in current:
                current["author"] = line
            elif "date" not in current:
                current["date"] = line
            elif "subject" not in current:
                current["subject"] = line
            elif "body" not in current:
                current["body"] = line
            elif line.strip():
                current["files"].append(line)
    if current and "author" in current:
        commits.append(GitCommit(**current))
    return commits
