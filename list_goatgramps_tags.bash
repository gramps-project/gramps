#!/usr/bin/env bash
#set -euo pipefail

# -------------------------------------------------
# list_goatgramps_tags.bash
# Shows tags that are reachable from any goatgramps/* branch
# but NOT reachable from the repository's default branch.
# -------------------------------------------------

# 1️⃣ Detect default remote branch (origin/HEAD)
DEFAULT_REMOTE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
                 | sed 's@^refs/remotes/origin/@@')
if [[ -z $DEFAULT_REMOTE ]]; then
    echo "⚠️  Could not determine default branch; falling back to 'master'."
    DEFAULT_REMOTE=master
fi
echo "Default branch (remote) detected: $DEFAULT_REMOTE"

# 2️⃣ Gather all local goatgramps/* branches
local_branches=$(git for-each-ref --format='%(refname:short)' refs/heads/goatgramps/*)
#printf "local branches: %s\n" $local_branches

# 3️⃣ Gather all remote goatgramps/* branches (strip leading origin/)
remote_branches=$(git branch -r | grep '^origin/goatgramps/' | sed 's#origin/##')
#printf "remote branches: %s\n" $remote_branches

# Combine, drop empty lines
branches=$(printf "%s\n%s\n" "$local_branches" "$remote_branches" | grep -v '^$')
#printf "combined branches: %s\n" $branches

# 4️⃣ Tags reachable from any goatgramps branch (collect and sort)
# Use an array to handle branch names with spaces safely.
declare -a goat_branches=()
while IFS= read -r br; do
    [[ -n $br ]] && goat_branches+=("$br")
done <<< "$branches"

goat_tags=$(for br in "${goat_branches[@]}"; do
    if git rev-parse --verify "$br" >/dev/null 2>&1; then
        git tag --merged "$br"
    fi
done | sort -u)

# 5️⃣ Tags reachable from the default branch (remote) – already sorted
parent_tags=$(git tag --merged "origin/$DEFAULT_REMOTE" | sort -u)

# 6️⃣ Exclusive tags = goat_tags – parent_tags
# Use `comm -23` on the *sorted* lists. Ensure proper quoting to handle tags
# containing spaces. Append `|| true` to avoid `set -e` termination when the
# lists differ.
exclusive=$(comm -23 <(printf "%s\n" "$goat_tags" | sort) \
                     <(printf "%s\n" "$parent_tags" | sort) || true)

# 7️⃣ Output – list newest tags first
if [[ -n $exclusive ]]; then
    echo "Tags that exist ONLY in the goatgramps series (not in $DEFAULT_REMOTE):"
    # Sort the exclusive tags by creation date, newest first
    # `git tag --list --sort=-creatordate` respects the order we pass
    # the tag names, so we feed the list via word‑splitting.
    sorted_exclusive=$(git tag --list --sort=-creatordate $exclusive)
    printf "  %s\n" $sorted_exclusive
else
    echo "No exclusive tags – every tag reachable from goatgramps/* is also on $DEFAULT_REMOTE."
fi
