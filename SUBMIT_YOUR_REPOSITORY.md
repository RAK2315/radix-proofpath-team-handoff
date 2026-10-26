# Publish YOUR verified module work to YOUR GitHub

1. Clone this full private repository after the Scrum Master grants you access. Keep the common support files.
2. Read your module README/PDF and assume you own the module. Run its API, frontend, check script and tests.
3. Make your changes, retest, fill your `DELIVERY.md` and include only synthetic screenshots/test evidence.
4. Create a **new private repository on your own GitHub account**, with no generated README or license
   (an empty repository). Do not overwrite an existing unrelated repository.
5. From your local checkout, inspect/remap the remote so you do not push to the Scrum Master's repository:

```powershell
git remote -v
git remote rename origin scrum-master
git remote add origin https://github.com/YOUR_USERNAME/YOUR_MODULE_REPOSITORY.git
git status --short
```

6. Review every intended file. Keep `.env`, private uploads/databases, credentials, `node_modules` and `.venv`
   excluded. Run `python scripts/scan_handoff.py` after staging; it prints paths/errors, never key values.

```powershell
git add YOUR_MODULE_FOLDER
# Explicitly add any other reviewed synthetic documentation/screenshots you authored.
git diff --cached --stat
.\.venv\Scripts\python.exe scripts/scan_handoff.py --staged
git commit -m "Complete and verify my RADIX module"
git push -u origin main
```

Use your current branch name from `git branch --show-current` if it is not `main`. The original cloned
baseline remains in history, so the whole working repository is pushed even when your new commit changes
only your module. Do not use force-push. If your own repository is private, grant the Scrum Master access.

7. Return: repository URL, commit SHA (`git rev-parse HEAD`), module name, working commands, actual test
   outputs, synthetic screenshots, known failures and honest Groq/Supabase status. Your `DELIVERY.md`
   is the checklist. An HTTP 200 or a screenshot alone does not prove correct extraction or calculations.

No website deployment, billable account setup, teammate messaging or PR to this repository is required.
