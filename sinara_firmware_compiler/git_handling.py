import os

from .shell_handling import shell_wrapper


def is_git_repo(repo_path):
    return shell_wrapper("git rev-parse --is-inside-work-tree", cwd=repo_path, strict=False).returncode == 0

def branch_exists(branch, repo_path):
    return shell_wrapper(f"git rev-parse --verify {branch}", cwd=repo_path, strict=False).returncode == 0

def commit_exists(commit, repo_path):
    return shell_wrapper(f"git cat-file -e {commit}", cwd=repo_path, strict=False).returncode == 0

def is_commit_in_branch(commit, branch, repo_path):
    return shell_wrapper(f"git merge-base --is-ancestor {commit} {branch}", cwd=repo_path, strict=False).returncode == 0

def get_commit_date(commit, repo_path):
    # strict ISO 8601 format, see https://git-scm.com/docs/pretty-formats
    return shell_wrapper(f"git show --no-patch --format=%cI {commit}", cwd=repo_path, strict=True).stdout.strip()

def git_reset_hard(repo_path):
    return shell_wrapper("git reset --hard", cwd=repo_path, strict=True)

def git_checkout(branch_or_commit, repo_path):
    return shell_wrapper(f"git checkout {branch_or_commit}", cwd=repo_path, strict=True)

def git_fetch(repo_path):
    return shell_wrapper("git fetch", cwd=repo_path, strict=True)

def git_pull(repo_path):
    return shell_wrapper("git pull", cwd=repo_path, strict=True)

def prepare_repo_in_defined_state(
    repo_path : str, # path of top-level directory inside artiq / artiq-zynq repository, where `flake.nix` is
    branch    : str, # "master" or "release-X" with X in [8, 7, ...]
    commit    : str, # full commit hash, obtain it via `git rev-parse HEAD` or from gitlab (online)
):
    repo_path = os.path.realpath(repo_path, strict=True)
    assert is_git_repo(repo_path)
    assert branch_exists(branch, repo_path)
    assert commit_exists(commit, repo_path)
    assert is_commit_in_branch(commit, branch, repo_path)
    git_reset_hard(repo_path)
    git_checkout(commit, repo_path)
    git_reset_hard(repo_path)