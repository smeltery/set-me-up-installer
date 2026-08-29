from ..core import *


def _normalize_worktree_relative_path(path):
    return path.strip().strip('"').strip().lstrip("./")


def _path_matches_ignored_prefix(rel_path, ignored_prefixes):
    rel_path = _normalize_worktree_relative_path(rel_path).rstrip("/")
    for prefix in ignored_prefixes:
        normalized = prefix.strip("/")
        if not normalized:
            continue
        if rel_path == normalized or rel_path.startswith(f"{normalized}/"):
            return True
        if rel_path and normalized.startswith(f"{rel_path}/"):
            return True
    return False


def _porcelain_status_path(line):
    if len(line) < 4:
        return line.strip()
    entry = line[3:]
    if " -> " in entry:
        return entry.split(" -> ", 1)[1]
    return entry


def read_local_config_values():
    values = {}
    if not os.path.exists(local_config_path):
        return values
    try:
        with open(local_config_path) as f:
            for line in f:
                key, value = _parse_profile_line(line)
                if key:
                    values[key] = value
    except (IOError, OSError) as e:
        warn(f"Could not read '{local_config_path}': {e}")
    return values


def configured_worktree_ignored_paths():
    paths = list(DEFAULT_WORKTREE_IGNORED_PATHS)
    raw = os.environ.get("SMU_IGNORED_PATHS") or read_local_config_values().get("SMU_IGNORED_PATHS", "")
    if raw:
        for part in raw.split("|"):
            normalized = part.strip().strip("/")
            if normalized:
                paths.append(normalized)
    deduped = []
    seen = set()
    for path in paths:
        if path not in seen:
            seen.add(path)
            deduped.append(path)
    return tuple(deduped)


def git_worktree_status_lines(path):
    try:
        result = subprocess.run(
            ["git", "-C", path, "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        return [line for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, OSError):
        return None


def git_has_worktree_changes(path, ignored_paths=None):
    lines = git_worktree_status_lines(path)
    if lines is None:
        return False
    ignored = ignored_paths if ignored_paths is not None else configured_worktree_ignored_paths()
    for line in lines:
        if not _path_matches_ignored_prefix(_porcelain_status_path(line), ignored):
            return True
    return False


LOCAL_RCM_README = """# Machine-local dotfiles

Files in this directory are applied by rcm but ignored by set-me-up update
checks. Nothing here needs to be committed to your blueprint fork.

Add `local` to the TAGS line in `dotfiles/rcrc`, then run `rcup`.
"""


def _rcrc_tags():
    if not os.path.exists(rcrc):
        return ()
    try:
        with open(rcrc) as f:
            for line in f:
                if line.strip().startswith("TAGS="):
                    value = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return tuple(part for part in value.split() if part)
    except (IOError, OSError):
        return ()
    return ()


def _gitignore_contains_local(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if stripped.rstrip("/") in ("dotfiles/local", "dotfiles/tag-local", "dotfiles/tag-smu"):
                    return True
    except (IOError, OSError):
        return False
    return False


def local_setup_payload():
    ignored = "|".join(configured_worktree_ignored_paths())
    os.makedirs(local_dotfiles_dir, exist_ok=True)
    readme_path = os.path.join(local_dotfiles_dir, "README.md")
    readme_written = False
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(LOCAL_RCM_README)
        readme_written = True

    os.makedirs(config_dir, exist_ok=True)
    local_env_written = False
    if not os.path.exists(local_config_path):
        with open(local_config_path, "w") as f:
            f.write("\n".join([
                "# Machine-local set-me-up settings (not tracked by git).",
                f'export SMU_IGNORED_PATHS="{ignored}"',
                "",
            ]))
        local_env_written = True

    tags = _rcrc_tags()
    return {
        "local_dotfiles_dir": local_dotfiles_dir,
        "local_config_path": local_config_path,
        "ignored_paths": list(configured_worktree_ignored_paths()),
        "readme_written": readme_written,
        "local_env_written": local_env_written,
        "rcrc_path": rcrc,
        "rcrc_tags": list(tags),
        "rcrc_includes_local_tag": "local" in tags,
        "gitignore_path": os.path.join(smu_home_dir, ".gitignore"),
        "gitignore_covers_local": _gitignore_contains_local(os.path.join(smu_home_dir, ".gitignore")),
    }


def local_doctor_payload():
    payload = local_setup_payload()
    dirty = git_has_worktree_changes(smu_home_dir)
    payload.update({
        "blueprint_dirty_for_updates": dirty,
        "update_ready": not dirty,
    })
    warnings = []
    if not payload["rcrc_includes_local_tag"]:
        warnings.append("Add `local` to TAGS in dotfiles/rcrc so rcm applies dotfiles/local.")
    if not payload["gitignore_covers_local"]:
        warnings.append("Add dotfiles/local to your blueprint .gitignore so accidental commits stay unlikely.")
    if not os.path.exists(local_config_path):
        warnings.append(f"Run `smu local init` to create {local_config_path}.")
    payload["warnings"] = warnings
    payload["ready"] = not warnings and payload["update_ready"]
    return payload


def local_init_command(json_output=False):
    payload = local_setup_payload()
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        success(f"Machine-local dotfiles directory: {local_dotfiles_dir}")
        if payload["local_env_written"]:
            success(f"Wrote ignored-path settings to {local_config_path}")
        else:
            success(f"Using existing {local_config_path}")
        if not payload["rcrc_includes_local_tag"]:
            warn("Add `local` to TAGS in dotfiles/rcrc, then run `rcup`.")
        if not payload["gitignore_covers_local"]:
            warn("Consider adding dotfiles/local to your blueprint .gitignore.")
    return 0


def local_doctor_command(json_output=False):
    payload = local_doctor_payload()
    exit_code = 0 if payload["ready"] else 1
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if payload["update_ready"]:
            success("Blueprint checkout is update-ready (ignoring machine-local paths).")
        else:
            warn("Blueprint checkout still has non-local changes that block updates.")
        for message in payload["warnings"]:
            warn(message)
    return exit_code


def local_command(argv):
    if not argv or argv[0] in ("-h", "--help"):
        die("Usage: smu local [init|doctor] [--json]")
    json_output = "--json" in argv
    subcommand = argv[0]
    if subcommand == "init":
        return local_init_command(json_output=json_output)
    if subcommand == "doctor":
        return local_doctor_command(json_output=json_output)
    die(f"Unknown local subcommand '{subcommand}'. Valid values: init, doctor.")


__all__ = [name for name in globals() if not name.startswith("__")]
