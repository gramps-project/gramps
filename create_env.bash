#!/usr/bin/bash

#Ensure our local environment knows about any new updates from the official project.
git fetch origin
git remote add upstream https://github.com/gramps-project/gramps.git
git fetch upstream

#fix Windows line-endings conflict
# 1. Force Git to clear out the false modifications and match the server exactly
git reset --hard HEAD

#create our new branch based upon the upstream maintenance branch
git checkout -b goatgramps/gg_beta upstream/maintenance/gramps61

#Merge each of your open PR branches into this new combined branch one by one
git merge origin/gedcom_warning_improvements
git merge origin/legacy_import
git merge origin/display_age

#Resolve any conflicts

#Crucial Safety Tips
#• 💡 Do not push this branch to your PRs: Keep this combined branch strictly local, or push it to a brand-new branch name on your fork (e.g., git push origin my-combined-gramps). Never push it into the existing branches that have open PRs, or your PRs will automatically update and combine, ruining the clean code review for the maintainers.
#• 🔄 Handling Updates: When the main Gramps repository eventually updates, or when you add a new feature, you can simply checkout your my-combined-gramps branch and run git merge upstream/master or git merge new-feature to keep your personal application completely up to date.

export TMPDIR=$USERPROFILE/AppData/Local/Temp
export TMP=$USERPROFILE/AppData/Local/Temp
git push -u origin goatgramps/gg_beta
