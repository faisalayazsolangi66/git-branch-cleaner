#!/usr/bin/env python3
"""Delete local git branches already merged into a base branch.

By default this only lists what *would* be deleted (dry run).
Pass --confirm to actually delete the branches.
"""
import argparse
import subprocess
import sys


def run_git(args, cwd=None):
    """Run a git command and return its stdout, or raise on failure."""
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def current_branch(repo):
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo).strip()


def merged_branches(base, repo):
    out = run_git(["branch", "--merged", base], cwd=repo)
    branches = []
    for line in out.splitlines():
        name = line.strip().lstrip("*").strip()
        if name:
            branches.append(name)
    return branches


def main():
    parser = argparse.ArgumentParser(
        description="Delete local branches already merged into a base branch."
    )
    parser.add_argument("repo", nargs="?", default=".",
                        help="Path to the git repository (default: current directory)")
    parser.add_argument("--base", default="main",
                        help="Base branch branches must be merged into (default: main)")
    parser.add_argument("--exclude", default="main,master,develop",
                        help="Comma-separated branches never to delete "
                             "(default: main,master,develop)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only list branches that would be deleted (default behaviour)")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually delete the branches (required for deletion)")
    parser.add_argument("--force", action="store_true",
                        help="Use 'git branch -D' instead of '-d' for unmerged leftovers")
    args = parser.parse_args()

    try:
        current = current_branch(args.repo)
    except RuntimeError as exc:
        print(f"Error: not a git repository or git failed: {exc}", file=sys.stderr)
        return 1

    protected = {b.strip() for b in args.exclude.split(",") if b.strip()}
    protected.add(args.base)
    protected.add(current)

    try:
        merged = merged_branches(args.base, args.repo)
    except RuntimeError as exc:
        print(f"Error: could not list merged branches: {exc}", file=sys.stderr)
        return 1

    candidates = [b for b in merged if b not in protected]

    if not candidates:
        print(f"No merged branches to delete (base: {args.base}, "
              f"current: {current}).")
        return 0

    print(f"Merged into {args.base}: {len(candidates)} branch(es)")
    for branch in candidates:
        print(f"  {branch}")

    if not args.confirm:
        print("\nDry run: nothing was deleted.")
        print("Run again with --confirm to delete these branches.")
        return 0

    flag = "-D" if args.force else "-d"
    deleted, failed = [], []
    for branch in candidates:
        try:
            run_git(["branch", flag, branch], cwd=args.repo)
            deleted.append(branch)
        except RuntimeError as exc:
            failed.append((branch, exc))
    for branch in deleted:
        print(f"Deleted {branch}")
    for branch, exc in failed:
        print(f"Failed to delete {branch}: {exc}", file=sys.stderr)
    print(f"\nDeleted {len(deleted)} branch(es), {len(failed)} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
