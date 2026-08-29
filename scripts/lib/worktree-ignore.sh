#!/usr/bin/env bash

_smu_has_worktree_changes() {
	local home_dir="${1:?home dir required}"
	local ignored_paths="${2:-dotfiles/local|dotfiles/tag-local|dotfiles/tag-smu}"
	local status_line rel_path prefix

	while IFS= read -r status_line; do
		[[ -z "$status_line" ]] && continue
		rel_path="${status_line#???}"
		if [[ "$rel_path" == *" -> "* ]]; then
			rel_path="${rel_path##* -> }"
		fi
		rel_path="${rel_path#\"}"
		rel_path="${rel_path%\"}"
		rel_path="${rel_path#./}"
		rel_path="${rel_path%/}"

		local ignored=false
		IFS='|' read -r -a ignored_list <<<"$ignored_paths"
		for prefix in "${ignored_list[@]}"; do
			prefix="${prefix#/}"
			prefix="${prefix%/}"
			[[ -z "$prefix" ]] && continue
			if [[ "$rel_path" == "$prefix" || "$rel_path" == "$prefix/"* ]]; then
				ignored=true
				break
			fi
			if [[ -n "$rel_path" && "$prefix" == "$rel_path/"* ]]; then
				ignored=true
				break
			fi
		done
		[[ "$ignored" == true ]] && continue
		return 0
	done < <(git -C "$home_dir" status --porcelain 2>/dev/null)

	return 1
}
