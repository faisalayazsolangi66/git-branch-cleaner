# git-branch-cleaner

Delete local git branches already merged into a base branch (default `main`).

## Requirements

- Python 3 (standard library only — no third-party packages)

## How to run

```bash
cd 051-git-branch-cleaner
python3 main.py --base main
```

Run `python3 main.py --help` to see all options.

## Example

```bash
python3 main.py --base main
```

Sample output:

```
Merged into main: 1 branch(es)
  old-feature

Dry run: nothing was deleted.
Run again with --confirm to delete these branches.
```

## Notes

Run it inside a git repository. **Dry run is the default**: the tool only lists branches unless you pass `--confirm`. Use `--exclude` to protect extra branches and `--force` to use `git branch -D` instead of `-d`.

## License

MIT — see [LICENSE](LICENSE).
