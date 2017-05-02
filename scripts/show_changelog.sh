#!/bin/bash

PROJECT_DIRECTORY="$(git rev-parse --show-toplevel)"

set -e

cd "$PROJECT_DIRECTORY"

list_changes () {
  tags=$(git tag -l --sort=-v:refname)
  tags+="
  $(git rev-list --max-parents=0 HEAD)"

  cur=

  for tag in $tags; do
    if [ -n "$cur" ]; then
      echo "ginvoice ($cur) experimental; urgency=medium"
      echo ""
      git log --no-merges --pretty=format:"  * %s" "$cur...$tag"
      echo ""
#      git show -1 -s --tags 0.0.1 --format=' -- %an <%ae>  %aD'
      git for-each-ref --format="%(refname:short) -- %(taggername) %(taggeremail)  %(taggerdate:rfc)" refs/tags \
          | grep -e "^$cur" | sed "s/^$cur//"
      echo ""
    fi
    cur=$tag
  done
}

list_changes
