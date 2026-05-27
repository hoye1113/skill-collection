from __future__ import annotations

from typing import Any

from spec_contract import ensure_mapping, ensure_string, ensure_string_list


def render_memory_section(config: Any) -> str | None:
    if not isinstance(config, dict) or not config.get("enabled"):
        return None
    what = config.get("what_to_capture", ["decisions", "context", "lessons", "mistakes"])
    what_str = ", ".join(str(item) for item in what) if isinstance(what, list) else "decisions, context, lessons"
    return (
        "## Memory\n\n"
        "You wake up fresh each session. These files are your continuity:\n\n"
        "- **Daily notes:** `memory/YYYY-MM-DD.md` (create `memory/` if needed) — raw logs of what happened\n"
        "- **Long-term:** `MEMORY.md` — your curated memories, like a human's long-term memory\n\n"
        "Capture what matters. " + what_str + ". Skip the secrets unless asked to keep them.\n\n"
        "### MEMORY.md\n\n"
        "- **ONLY load in main session** (direct chats with your human)\n"
        "- **DO NOT load in shared contexts** (Discord, group chats, sessions with other people)\n"
        "- This is for **security** — contains personal context that shouldn't leak to strangers\n"
        "- You can **read, edit, and update** MEMORY.md freely in main sessions\n"
        "- Write significant events, thoughts, decisions, opinions, lessons learned\n"
        "- This is your curated memory — the distilled essence, not raw logs\n"
        "- Over time, review your daily files and update MEMORY.md with what's worth keeping\n\n"
        "### Write It Down\n\n"
        "- **Memory is limited** — if you want to remember something, WRITE IT TO A FILE\n"
        "- 'Mental notes' don't survive session restarts. Files do.\n"
        "- When someone says 'remember this' → update `memory/YYYY-MM-DD.md` or relevant file\n"
        "- When you learn a lesson → update AGENTS.md, TOOLS.md, or the relevant skill\n"
        "- When you make a mistake → document it so future-you doesn't repeat it\n\n"
        "### Memory Maintenance\n\n"
        "Periodically (every few days), use a heartbeat to:\n\n"
        "1. Read through recent `memory/YYYY-MM-DD.md` files\n"
        "2. Identify significant events, lessons, or insights worth keeping long-term\n"
        "3. Update `MEMORY.md` with distilled learnings\n"
        "4. Remove outdated info from MEMORY.md that's no longer relevant\n"
    )


def render_heartbeat_section(config: Any) -> str | None:
    if not isinstance(config, dict) or not config.get("enabled"):
        return None
    quiet = config.get("quiet_hours", "23:00-08:00")
    state_file = config.get("state_file", "memory/heartbeat-state.json")
    return (
        "## Heartbeats\n\n"
        "When you receive a heartbeat poll, don't just reply `HEARTBEAT_OK` every time. "
        "Use heartbeats productively!\n\n"
        "**Things to check (rotate through these, 2-4 times per day):**\n\n"
        "- Review and update MEMORY.md (see Memory Maintenance)\n"
        "- Check on projects (git status, etc.)\n"
        "- Update documentation\n"
        "- Commit and push your own changes\n\n"
        "**Track your checks** in `" + state_file + "`.\n\n"
        "**When to reach out:**\n\n"
        "- Important email arrived\n"
        "- Calendar event coming up (<2h)\n"
        "- Something interesting you found\n\n"
        "**When to stay quiet (HEARTBEAT_OK):**\n\n"
        "- Late night (" + quiet + ") unless urgent\n"
        "- Human is clearly busy\n"
        "- Nothing new since last check\n"
    )


MEMORY_BASELINE_SECTION = (
    "## Memory\n\n"
    "You have memory capabilities available. If the runtime provides heartbeat polls or memory prompts:\n\n"
    "- Daily notes: `memory/YYYY-MM-DD.md` (create `memory/` if needed)\n"
    "- Long-term: `MEMORY.md` — curated memories, only load in main session\n"
    "- When someone says 'remember this' → write to a file, not just 'mental notes'\n"
    "- When you learn a lesson → update the relevant root file\n\n"
    "Full memory configuration is not enabled for this workspace.\n"
)


def render_group_chat_section(config: Any) -> str | None:
    if not isinstance(config, dict) or not config.get("enabled"):
        return None
    respond = config.get("respond_when", ["mentioned", "can_add_value"])
    silent = config.get("stay_silent_when", ["casual_banter", "already_answered"])
    respond_str = "\n".join(f"- {item}" for item in respond) if isinstance(respond, list) else "- When mentioned"
    silent_str = "\n".join(f"- {item}" for item in silent) if isinstance(silent, list) else "- Casual banter"
    return (
        "## Group Chats\n\n"
        "You have access to your human's stuff. That doesn't mean you _share_ their stuff. "
        "In groups, you're a participant — not their voice, not their proxy. Think before you speak.\n\n"
        "**Respond when:**\n\n" + respond_str + "\n\n"
        "**Stay silent when:**\n\n" + silent_str + "\n\n"
        "Participate, don't dominate.\n"
    )


def format_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def format_subsections(mapping: dict[str, list[str]], title_map: dict[str, str]) -> str:
    sections: list[str] = []
    for key, title in title_map.items():
        raw_items = mapping.get(key)
        if raw_items is None:
            continue
        items = ensure_string_list(raw_items, key)
        sections.append(f"### {title}\n\n{format_bullets(items)}")
    return "\n\n".join(sections)


def format_resume_strategy(value: Any) -> str:
    mapping = ensure_mapping(value, "resume_strategy")
    order = [
        ("global_resume_file", "Global resume file"),
        ("task_topic_resume_file", "Task/topic resume file"),
        ("deliverable_inspection_path", "Deliverable inspection path"),
        ("if_state_missing", "If state missing"),
        ("never_assume", "Never assume"),
    ]
    lines = []
    for key, label in order:
        lines.append(f"- {label}: {ensure_string(mapping.get(key), f'resume_strategy.{key}')}")
    return "\n".join(lines)


def render_identity(spec: dict[str, Any]) -> str:
    return (
        "# IDENTITY.md\n\n"
        f"- Name: {ensure_string(spec.get('name'), 'name')}\n"
        f"- Role: {ensure_string(spec.get('role'), 'role')}\n\n"
        "## Public Identity\n\n"
        f"{ensure_string(spec.get('public_identity'), 'public_identity')}\n"
    )


def render_soul(spec: dict[str, Any]) -> str:
    parts = ["# SOUL.md\n"]

    lazy_default = spec.get("lazy_default_to_avoid")
    if isinstance(lazy_default, str) and lazy_default.strip():
        parts.append("## Lazy Default to Avoid\n\n" + lazy_default.strip() + "\n")
    else:
        parts.append("## Lazy Default to Avoid\n\n[REQUIRED] Define the lowest-quality version this agent must avoid.\n")

    parts.append("## Non-Negotiables\n\n" + format_bullets(ensure_string_list(spec.get("non_negotiables"), "non_negotiables")) + "\n")
    parts.append("## Enduring Style\n\n" + format_bullets(ensure_string_list(spec.get("enduring_style"), "enduring_style")) + "\n")
    return "\n".join(parts)


def render_agents(spec: dict[str, Any]) -> str:
    sections = [
        "# AGENTS.md\n",
        "## Workspace Positioning\n\n" + ensure_string(spec.get("workspace_positioning"), "workspace_positioning") + "\n",
        "## Session Startup\n\n" + format_bullets(ensure_string_list(spec.get("session_startup"), "session_startup")) + "\n",
    ]

    memory = render_memory_section(spec.get("memory_config"))
    if memory is not None:
        sections.append(memory)
    else:
        sections.append(MEMORY_BASELINE_SECTION)

    sections.extend([
        "## Red Lines\n\n" + format_bullets(ensure_string_list(spec.get("red_lines"), "red_lines")) + "\n",
        "## Default Behavior\n\n" + format_bullets(ensure_string_list(spec.get("default_behavior"), "default_behavior")) + "\n",
    ])

    heartbeat = render_heartbeat_section(spec.get("heartbeat_config"))
    if heartbeat is not None:
        sections.append(heartbeat)

    group_chat = render_group_chat_section(spec.get("group_chat_behavior"))
    if group_chat is not None:
        sections.append(group_chat)

    preferred = spec.get("preferred_control_pattern")
    if isinstance(preferred, str) and preferred.strip():
        sections.append("## Preferred Control Pattern\n\n- " + preferred.strip() + "\n")

    sections.extend(
        [
            "## Resume Strategy\n\n" + format_resume_strategy(spec.get("resume_strategy")) + "\n",
            "## Boundaries\n\n" + format_bullets(ensure_string_list(spec.get("boundaries"), "boundaries")) + "\n",
            "## Workspace Layout\n\n" + format_bullets(ensure_string_list(spec.get("workspace_layout"), "workspace_layout")) + "\n",
        ]
    )
    return "\n".join(sections)


def render_tools(spec: dict[str, Any]) -> str:
    capabilities = ensure_mapping(spec.get("capabilities"), "capabilities")
    skill_resources = ensure_mapping(spec.get("skill_resources"), "skill_resources")

    capability_sections = format_subsections(
        capabilities,
        {
            "native": "Native capability",
            "conditional": "Conditional capability",
            "unsupported": "Unsupported / non-capability",
        },
    )
    resource_sections = format_subsections(
        skill_resources,
        {
            "primary_skill_entrypoints": "Primary skill entrypoints",
            "high_priority_references": "High-priority references",
            "conditional_scripts": "Conditional scripts",
        },
    )

    if not capability_sections:
        raise ValueError("Field 'capabilities' must define at least one capability section.")
    if not resource_sections:
        raise ValueError("Field 'skill_resources' must define at least one resource section.")

    return (
        "# TOOLS.md\n\n"
        "## Output Roots\n\n"
        f"{format_bullets(ensure_string_list(spec.get('output_roots'), 'output_roots'))}\n\n"
        "## Local Conventions\n\n"
        f"{format_bullets(ensure_string_list(spec.get('local_conventions'), 'local_conventions'))}\n\n"
        "## Capabilities\n\n"
        f"{capability_sections}\n\n"
        "## Skill Resources\n\n"
        f"{resource_sections}\n"
    )


def render_bootstrap(spec: dict[str, Any]) -> str:
    topics = spec.get("bootstrap_config", {}).get("conversation_topics", ["identity", "user_profile", "soul_principles"])
    topic_lines = "\n".join(f"- {t}" for t in topics) if isinstance(topics, list) else "- identity"
    return (
        "# BOOTSTRAP.md\n\n"
        "This is your first run. Let's figure out who you are.\n\n"
        "## Step 1: Identity\n\n"
        "Ask your human about:\n"
        "- Your name\n"
        "- Your creature form (if any)\n"
        "- Your vibe / personality\n"
        "- Your emoji\n\n"
        "Then fill in `IDENTITY.md`.\n\n"
        "## Step 2: User Profile\n\n"
        "Learn about your human:\n"
        "- Name and pronouns\n"
        "- Timezone\n"
        "- What they need help with\n\n"
        "Then fill in `USER.md`.\n\n"
        "## Step 3: Soul\n\n"
        "Discuss with your human:\n"
        "- What kind of behavior they value\n"
        "- What boundaries to respect\n"
        "- Your communication style\n\n"
        "Then fill in `SOUL.md`.\n\n"
        "## Conversation Topics\n\n" + topic_lines + "\n\n"
        "## Step 4: Clean Up\n\n"
        "Delete this file when done. You won't need it again.\n"
    )


def render_user(spec: dict[str, Any]) -> str:
    profile = spec.get("user_profile", {})
    if not isinstance(profile, dict):
        profile = {}
    name = profile.get("name", "Your human's name")
    pronouns = profile.get("pronouns", "their pronouns")
    timezone = profile.get("timezone", "their timezone")
    return (
        "# USER.md\n\n"
        "- Name: " + str(name) + "\n"
        "- Pronouns: " + str(pronouns) + "\n"
        "- Timezone: " + str(timezone) + "\n"
    )


def render_heartbeat_file(spec: dict[str, Any]) -> str:
    tasks = spec.get("heartbeat_config", {}).get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []
    lines = ["# HEARTBEAT.md\n"]
    for task in tasks:
        lines.append(f"- [ ] {task}")
    return "\n".join(lines) + "\n"


def render_all(spec: dict[str, Any]) -> dict[str, str]:
    files = {
        "IDENTITY.md": render_identity(spec),
        "SOUL.md": render_soul(spec),
        "AGENTS.md": render_agents(spec),
        "TOOLS.md": render_tools(spec),
    }
    if spec.get("bootstrap_config", {}).get("enabled"):
        files["BOOTSTRAP.md"] = render_bootstrap(spec)
    if spec.get("user_profile"):
        files["USER.md"] = render_user(spec)
    if spec.get("heartbeat_config", {}).get("enabled"):
        files["HEARTBEAT.md"] = render_heartbeat_file(spec)
    return files
