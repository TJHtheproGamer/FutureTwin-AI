# Create a new GitHub repository without workspace history

**Do not execute the push until the owner approves and the release gates in
[the final review](final-review.md) are cleared.** No push was performed during
preparation.

1. Create a new, **empty** GitHub repository using the GitHub UI. Do not add a
   README, license, or `.gitignore` there. Choose visibility only after reviewing
   dataset redistribution and privacy.
2. Replace the pending GitHub URL in the README with that repository's actual
   URL. Update demo, slides, video, and evidence links only when genuine.
3. In the original Replit Shell, use **this export directory**, never the
   workspace root. The placeholders below must be replaced with the real owner
   and repository name. Authenticate through GitHub's normal secure flow;
   never embed a token or password in the remote URL.

```bash
cd /home/runner/workspace/generated-artifacts/github-source

# Stop if a repository already exists here; do not delete/rewrite it.
test ! -e .git || { echo "Existing Git metadata: stop and review."; exit 1; }
python3 scripts/repository_safety.py --history
# Review the JSON: all finding lists must be empty before continuing.

git init --initial-branch=main
git add --all
git diff --cached --check
git diff --cached --stat
git status --short
# Review the staged paths. No models, archives, .env, databases, uploads, or
# Replit artifacts should be staged.
git commit -m "Initial FutureTwin AI SDC Hackathon 2026 submission"
git remote add origin "https://github.com/<GITHUB_OWNER>/<GITHUB_REPOSITORY>.git"
git remote -v

# Only after the owner approves:
git push --set-upstream origin main
```

This creates new history from source files only. It does not copy the workspace
`.git`, Git objects, or LFS storage. Do not run `git lfs migrate`, copy a workspace
backup, force-push, or provision private runtime assets into the export before
staging.

The largest source CSV exceeds GitHub's 25 MiB browser-upload limit, so use the
Git CLI rather than uploading the folder through a browser. No file currently
requires Git LFS.
