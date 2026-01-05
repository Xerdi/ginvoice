#!/bin/bash
# GinVoice - Creating LaTeX invoices with a GTK GUI
# Copyright (C) 2021  Erik Nijenhuis <erik@xerdi.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
      echo "ginvoice ($cur) noble; urgency=medium"
      echo ""
      git log --no-merges --pretty=format:"  * %s" "$cur...$tag"
      echo ""
#      git show -1 -s --tags 0.0.1 --format=' -- %an <%ae>  %aD'
      git for-each-ref --format="%(refname:short) -- %(if)%(taggername)%(then)%(taggername) %(taggeremail)%(else)%(authorname) %(authoremail)%(end)  %(creatordate:rfc)" refs/tags \
          | grep -e "^$cur" | sed "s/^$cur//"
      echo ""
    fi
    cur=$tag
  done
}

list_changes
