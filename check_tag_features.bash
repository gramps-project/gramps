#!/usr/bin/env bash
#set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIST_TAGS_SCRIPT="$SCRIPT_DIR/list_goatgramps_tags.bash"
if [[ ! -f "$LIST_TAGS_SCRIPT" ]]; then
    LIST_TAGS_SCRIPT="c:/workspace/gramps/list_goatgramps_tags.bash"
fi

# ---- 1️⃣  Get exclusive goatgramps tags and target tag ----
EXCLUSIVE_TAGS=$(bash "$LIST_TAGS_SCRIPT" | sed -n 's/^  //p')

# If no argument is given, use the newest exclusive goatgramps tag.
if [[ -n ${1:-} ]]; then
    TAG="$1"
else
    TAG=$(echo "$EXCLUSIVE_TAGS" | head -n1)
fi

# ---- 2️⃣  Determine the next older exclusive tag ----
# Find the tag that appears immediately after the supplied TAG in the
# exclusive tags list (which is already ordered from newest to oldest).
# If there is no older tag we treat it as the beginning of history
# (i.e. compare against the default branch).
prev_tag=""
found=0
while IFS= read -r t; do
    if [[ $found -eq 1 ]]; then
        prev_tag=$t
        break
    fi
    if [[ $t == "$TAG" ]]; then
        found=1
    fi
done <<< "$EXCLUSIVE_TAGS"

# Determine the base reference to compare against.
# If there is no older tag, compare against the default branch (e.g. origin/master).
if [[ -n "$prev_tag" ]]; then
    base="$prev_tag"
else
    DEFAULT_REMOTE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
                     | sed 's@^refs/remotes/origin/@@')
    if [[ -z $DEFAULT_REMOTE ]]; then
        DEFAULT_REMOTE=master
    fi
    base="origin/$DEFAULT_REMOTE"
fi

# ---- 2️⃣  Determine branches introduced after the previous exclusive tag ----
# A feature branch is introduced in TAG if it is reachable from (merged into) TAG
# but not yet reachable from the previous tag (or the default branch if no older tag).
FEATURE_PATTERN='^origin/'

# Keep branch hashes internally for inspecting branch state
declare -A branch_hashes
feature_branches=()

# Gather branches merged into base
declare -A base_branches
while IFS= read -r br; do
    [[ -n "$br" ]] && base_branches["$br"]=1
done < <(git branch -r --merged "$base" 2>/dev/null | sed 's/^[ *]*//' | grep -v ' -> ')

# Gather remote branches merged into TAG
while IFS= read -r br; do
    [[ -z "$br" ]] && continue
    # Skip if already merged in base
    [[ -n ${base_branches["$br"]:-} ]] && continue
    # Skip internal goatgramps branches, HEAD, and base itself
    [[ $br == *goatgramps/* || $br == "origin/HEAD" || $br == "$base" ]] && continue
    # Must match feature pattern
    [[ ! $br =~ $FEATURE_PATTERN ]] && continue

    full="$br"
    [[ $full != origin/* ]] && full="origin/$full"
    hash=$(git rev-parse --verify "$full" 2>/dev/null || echo "<no-hash>")
    branch_hashes["$br"]="$hash"
    feature_branches+=("$br")
done < <(git branch -r --merged "$TAG" 2>/dev/null | sed 's/^[ *]*//' | grep -v ' -> ')

# Sort branches alphabetically for consistent output
if (( ${#feature_branches[@]} )); then
    IFS=$'\n' feature_branches=($(sort <<<"${feature_branches[*]}"))
    unset IFS
fi

# Determine the latest reference (origin/goatgramps/gg_beta or newest exclusive tag)
LATEST="origin/goatgramps/gg_beta"
if ! git rev-parse --verify "$LATEST" >/dev/null 2>&1; then
    LATEST=$(echo "$EXCLUSIVE_TAGS" | head -n1)
fi

# ---- 3️⃣  Print results and compare hashes (up-to-date vs needs updating) ----
if (( ${#feature_branches[@]} )); then
    if [[ -n $prev_tag ]]; then
        echo "Feature branches introduced between $prev_tag..$TAG (matching pattern):"
    else
        echo "Feature branches that contain tag $TAG (matching pattern):"
    fi
    for br in "${feature_branches[@]}"; do
        full="$br"
        [[ $full != origin/* ]] && full="origin/$full"
        branch_hash="${branch_hashes[$br]:-$(git rev-parse --verify "$full" 2>/dev/null || echo "<no-hash>")}"
        latest_hash=$(git merge-base "$LATEST" "$full" 2>/dev/null || echo "<no-hash>")
        tag_hash=$(git merge-base "$TAG" "$full" 2>/dev/null || echo "<no-hash>")

        if [[ "$branch_hash" != "<no-hash>" && "$branch_hash" == "$latest_hash" ]]; then
            if [[ "$TAG" != "$LATEST" && "$branch_hash" != "$tag_hash" ]]; then
                status="up-to-date with latest (updated since $TAG)"
            else
                status="up-to-date"
            fi
        else
            status="needs updating (branch tip: ${branch_hash:0:10}, latest merged: ${latest_hash:0:10})"
        fi
        printf "  %s  %s  [%s]\n" "$br" "$branch_hash" "$status"
    done
else
    if [[ -n $prev_tag ]]; then
        echo "No feature branches (matching pattern) were introduced between $prev_tag and $TAG."
    else
        echo "No feature branches (matching pattern) contain tag $TAG."
    fi
fi
