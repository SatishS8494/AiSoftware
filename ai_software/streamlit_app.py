""" Build Project With Ai.

Run from repo root:
    streamlit run ai_software/streamlit_app.py
"""

import shutil
import time
import uuid
from pathlib import Path

import streamlit as st

from config import settings
from graph import graph
from state import ProjectState


# ─── Constants ────────────────────────────────────────────────────────────────

WORKSPACE = Path(settings.workspace_path).resolve()

AGENT_ORDER = ["planner", "architect", "coder", "runner", "tester", "reviewer"]
AGENT_LABELS = {
    "planner": "Planner", "architect": "Architect", "coder": "Coder",
    "runner": "Runner", "tester": "Tester", "reviewer": "Reviewer",
    "fixer": "Fixer", "writer": "Writer", "queue": "Queue",
}
AGENT_ICONS = {
    "planner": "📋", "architect": "🏗️", "coder": "💻",
    "runner": "🏃", "tester": "🧪", "reviewer": "👀",
    "fixer": "🔧", "writer": "📝", "queue": "📥",
}
STATUS = {
    "pending": ("⏸", "#6B7280"),
    "running": ("🟡", "#F59E0B"),
    "done":    ("✅", "#10B981"),
    "error":   ("❌", "#EF4444"),
}
EXT_LANG = {
    ".py": "python", ".js": "javascript", ".jsx": "jsx", ".ts": "typescript",
    ".tsx": "tsx", ".java": "java", ".json": "json", ".html": "html",
    ".css": "css", ".xml": "xml", ".md": "markdown", ".yml": "yaml",
    ".yaml": "yaml", ".toml": "toml", ".sh": "bash", ".sql": "sql",
}
FILE_ICONS = {
    ".py": "🐍", ".js": "📜", ".jsx": "⚛️", ".ts": "📘", ".tsx": "⚛️",
    ".java": "☕", ".json": "📋", ".html": "🌐", ".css": "🎨", ".xml": "📄",
    ".md": "📝", ".yml": "⚙️", ".yaml": "⚙️", ".toml": "⚙️",
}
IGNORE_DIRS = {"node_modules", ".git", "target", "__pycache__", ".venv", "venv", "dist", "build"}

EXAMPLES = {
    "Flask API":  "Create a Flask REST API with GET and POST endpoints for a simple todo list, stored in memory.",
    "React App":  "Create a React counter app with increment and decrement buttons.",
    "CLI Tool":   "Create a Python CLI that reads a CSV file and prints summary statistics.",
    "Java App":   "Create a Java calculator app that supports +, -, *, / from command-line arguments.",
}


# ─── Page config + CSS ────────────────────────────────────────────────────────

st.set_page_config(page_title="NumZone Software", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
  section[data-testid="stSidebar"] { background: #0B0F19; border-right: 1px solid #1F2937; }
  section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

  /* Hero landing */
  .hero-wrap { padding-top: 4vh; }
  .hero-title { font-size: 2.4rem; font-weight: 800; text-align: center; margin-bottom: 6px;
                background: linear-gradient(90deg, #A78BFA, #60A5FA); -webkit-background-clip: text;
                -webkit-text-fill-color: transparent; }
  .hero-sub { text-align: center; color: #9CA3AF; font-size: 1rem; margin-bottom: 28px; }
  .hero-eyebrow { text-align: center; color: #7C3AED; font-weight: 600; letter-spacing: .12em;
                  text-transform: uppercase; font-size: .72rem; margin-bottom: 6px; }

  /* Metric cards */
  .metric { background: #141A2A; border: 1px solid #1F2937; border-radius: 10px; padding: 10px 14px; }
  .metric .lbl { color: #9CA3AF; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .06em; }
  .metric .val { color: #E5E7EB; font-size: 1.2rem; font-weight: 600; margin-top: 2px; }

  /* Agent row */
  .agent-row { display: flex; align-items: center; gap: 8px; padding: 6px 8px; margin: 2px 0; border-radius: 8px; }
  .agent-row.running { background: rgba(245, 158, 11, 0.08); }
  .agent-row.done { background: rgba(16, 185, 129, 0.05); }
  .agent-row .name { flex: 1; color: #E5E7EB; font-weight: 500; }
  .agent-row .status { font-size: 0.8rem; }

  /* File tree */
  .tree-header { color: #9CA3AF; text-transform: uppercase; letter-spacing: .08em;
                 font-size: .72rem; margin: 4px 0 6px 0; }
  .tree-folder { color: #93C5FD; font-weight: 600; padding: 2px 6px; }

  /* Badges */
  .badge { display: inline-block; padding: 2px 8px; border-radius: 999px;
           font-size: 0.72rem; font-weight: 600; margin-left: 6px; }
  .badge.ok  { background: rgba(16, 185, 129, 0.15); color: #10B981; }
  .badge.err { background: rgba(239, 68, 68, 0.15); color: #EF4444; }
  .badge.warn{ background: rgba(245, 158, 11, 0.15); color: #F59E0B; }

  .h-brand { font-size: 1.15rem; font-weight: 700; color: #E5E7EB; }
  .h-tag   { color: #9CA3AF; font-size: 0.8rem; margin-top: -2px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)


# ─── Session state defaults ───────────────────────────────────────────────────

def _init_state():
    defaults = {
        "thread_id": None,
        "status_map": {a: "pending" for a in AGENT_ORDER + ["fixer"]},
        "accumulated": {},
        "run_started_at": None,
        "run_finished_at": None,
        "run_error": None,
        "selected_file": None,
        "activity_log": [],
        "example_prompt": "",
        "force_hero": False,
        "pending_run": None,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


_init_state()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def scan_workspace(root: Path) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        parts = p.relative_to(root).parts
        if any(part in IGNORE_DIRS for part in parts):
            continue
        out.append(p)
    return sorted(out, key=lambda x: str(x.relative_to(root)).lower())


def file_icon(path: Path) -> str:
    return FILE_ICONS.get(path.suffix.lower(), "📄")


def lang_for(path: Path) -> str:
    return EXT_LANG.get(path.suffix.lower(), "text")


def _merge(accum: dict, update: dict) -> dict:
    for k, v in update.items():
        if v is not None:
            accum[k] = v
    return accum


def _mark_next_running(status_map: dict, just_finished: str) -> None:
    if just_finished not in AGENT_ORDER:
        return
    idx = AGENT_ORDER.index(just_finished)
    for a in AGENT_ORDER[idx + 1:]:
        if status_map[a] == "pending":
            status_map[a] = "running"
            return


def _reset_run_state():
    st.session_state.status_map = {a: "pending" for a in AGENT_ORDER + ["fixer"]}
    st.session_state.accumulated = {}
    st.session_state.run_started_at = time.time()
    st.session_state.run_finished_at = None
    st.session_state.run_error = None
    st.session_state.activity_log = []
    st.session_state.selected_file = None
    st.session_state.force_hero = False


def _clear_for_new_project():
    _reset_run_state()
    st.session_state.thread_id = None
    st.session_state.run_started_at = None
    st.session_state.example_prompt = ""
    st.session_state.force_hero = True


def _run_pipeline(requirement: str, thread_id: str, resume: bool, status_ph):
    _reset_run_state()
    st.session_state.thread_id = thread_id
    st.session_state.status_map["planner"] = "running"

    config = {"configurable": {"thread_id": thread_id}}
    initial_state = None if resume else ProjectState(requirement=requirement)

    try:
        for chunk in graph.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_update in chunk.items():
                if node_name in st.session_state.status_map:
                    st.session_state.status_map[node_name] = "done"
                    _mark_next_running(st.session_state.status_map, node_name)

                ts = time.strftime("%H:%M:%S")
                msg = "finished"
                if isinstance(node_update, dict):
                    if node_update.get("generated_files"):
                        latest = node_update["generated_files"][-1]
                        path = latest.path if hasattr(latest, "path") else latest.get("path", "?")
                        msg = f"wrote `{path}`"
                    elif node_update.get("current_file"):
                        msg = f"working on `{node_update['current_file']}`"
                    elif node_update.get("execution_result"):
                        er = node_update["execution_result"]
                        rc = er.return_code if hasattr(er, "return_code") else "?"
                        msg = f"exit code {rc}"
                st.session_state.activity_log.append({"ts": ts, "node": node_name, "msg": msg})

                if isinstance(node_update, dict):
                    _merge(st.session_state.accumulated, node_update)

                status_ph.info(f"🟡 {AGENT_ICONS.get(node_name,'•')} **{AGENT_LABELS.get(node_name, node_name)}**: {msg}")
    except Exception as e:
        st.session_state.run_error = str(e)
        st.session_state.run_finished_at = time.time()
        status_ph.error(f"❌ Run failed: {e}")
        time.sleep(0.5)
        st.rerun()
        return

    for a in st.session_state.status_map:
        if st.session_state.status_map[a] == "running":
            st.session_state.status_map[a] = "done"

    st.session_state.run_finished_at = time.time()
    status_ph.success(f"✅ Done in {st.session_state.run_finished_at - st.session_state.run_started_at:.1f}s")
    time.sleep(0.5)
    st.rerun()


def _group_files(files: list[Path], root: Path):
    groups: dict[str, list[Path]] = {}
    root_files: list[Path] = []
    for f in files:
        rel = f.relative_to(root)
        if len(rel.parts) == 1:
            root_files.append(f)
        else:
            groups.setdefault(rel.parts[0], []).append(f)
    return groups, root_files


def _render_live_tree(placeholder, files: list[Path], latest: str | None):
    with placeholder.container():
        st.markdown('<div class="tree-header">📁 Project Files</div>', unsafe_allow_html=True)
        if not files:
            st.info("Files will appear here as they are generated...")
            return
        groups, root_files = _group_files(files, WORKSPACE)
        lines: list[str] = []
        for f in root_files:
            rel = str(f.relative_to(WORKSPACE)).replace("\\", "/")
            new = "🟢 " if rel == latest else ""
            lines.append(f"{new}{file_icon(f)}&nbsp;&nbsp;{f.name}")
        for folder in sorted(groups):
            lines.append(f"📂&nbsp;&nbsp;<b>{folder}/</b>")
            for f in groups[folder]:
                rel_p = f.relative_to(WORKSPACE)
                rel = str(rel_p).replace("\\", "/")
                depth = "&nbsp;&nbsp;&nbsp;&nbsp;" * (len(rel_p.parts) - 1)
                new = "🟢 " if rel == latest else ""
                lines.append(f"{depth}{new}{file_icon(f)}&nbsp;&nbsp;{rel_p.parts[-1]}")
        st.markdown("<br>".join(lines), unsafe_allow_html=True)
        st.caption(f"{len(files)} file{'s' if len(files) != 1 else ''}")


def _render_interactive_tree(files: list[Path]):
    st.markdown('<div class="tree-header">📁 Project Files</div>', unsafe_allow_html=True)
    if not files:
        st.info("Files will appear here as they are generated.")
        return
    groups, root_files = _group_files(files, WORKSPACE)
    display_labels: list[str] = []
    actual_paths: list[str | None] = []
    for f in root_files:
        display_labels.append(f"{file_icon(f)}  {f.name}")
        actual_paths.append(str(f.relative_to(WORKSPACE)).replace("\\", "/"))
    for folder in sorted(groups):
        display_labels.append(f"📂  {folder}/")
        actual_paths.append(None)
        for f in groups[folder]:
            rel = f.relative_to(WORKSPACE)
            depth = "    " * (len(rel.parts) - 1)
            display_labels.append(f"{depth}{file_icon(f)}  {rel.parts[-1]}")
            actual_paths.append(str(rel).replace("\\", "/"))
    valid_indices = [i for i, p in enumerate(actual_paths) if p is not None]
    default_idx = 0
    if st.session_state.selected_file:
        for j, i in enumerate(valid_indices):
            if actual_paths[i] == st.session_state.selected_file:
                default_idx = j
                break
    picked = st.radio(
        "Files",
        options=valid_indices,
        index=default_idx,
        format_func=lambda i: display_labels[i],
        label_visibility="collapsed",
        key="file_tree_radio",
    )
    st.session_state.selected_file = actual_paths[picked]
    st.caption(f"{len(valid_indices)} files · `{WORKSPACE.name}/`")


def _run_pipeline_live(requirement, thread_id, resume, status_ph, tree_ph):
    st.session_state.status_map["planner"] = "running"
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = None if resume else ProjectState(requirement=requirement)
    latest_path: str | None = None
    try:
        for chunk in graph.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_update in chunk.items():
                if node_name in st.session_state.status_map:
                    st.session_state.status_map[node_name] = "done"
                    _mark_next_running(st.session_state.status_map, node_name)

                ts = time.strftime("%H:%M:%S")
                msg = "finished"
                if isinstance(node_update, dict):
                    if node_update.get("generated_files"):
                        latest = node_update["generated_files"][-1]
                        path = latest.path if hasattr(latest, "path") else latest.get("path", "?")
                        msg = f"wrote `{path}`"
                        latest_path = path
                    elif node_update.get("current_file"):
                        msg = f"working on `{node_update['current_file']}`"
                    elif node_update.get("execution_result"):
                        er = node_update["execution_result"]
                        rc = er.return_code if hasattr(er, "return_code") else "?"
                        msg = f"exit code {rc}"

                st.session_state.activity_log.append({"ts": ts, "node": node_name, "msg": msg})
                if isinstance(node_update, dict):
                    _merge(st.session_state.accumulated, node_update)

                status_ph.info(
                    f"🟡 {AGENT_ICONS.get(node_name,'•')} **{AGENT_LABELS.get(node_name, node_name)}**: {msg}"
                )
                _render_live_tree(tree_ph, scan_workspace(WORKSPACE), latest=latest_path)
    except Exception as e:
        st.session_state.run_error = str(e)
        st.session_state.run_finished_at = time.time()
        status_ph.error(f"❌ Run failed: {e}")
        time.sleep(0.6)
        st.rerun()
        return

    for a in st.session_state.status_map:
        if st.session_state.status_map[a] == "running":
            st.session_state.status_map[a] = "done"
    st.session_state.run_finished_at = time.time()
    status_ph.success(f"✅ Done in {st.session_state.run_finished_at - st.session_state.run_started_at:.1f}s")
    time.sleep(0.5)
    st.rerun()


# ─── Decide view: hero landing vs. workspace ──────────────────────────────────

workspace_files = scan_workspace(WORKSPACE)
show_workspace = (
    (len(workspace_files) > 0
     or st.session_state.run_started_at is not None
     or st.session_state.pending_run is not None)
    and not st.session_state.force_hero
)


# ═════════════════════════════════════════════════════════════════════════════
# HERO LANDING
# ═════════════════════════════════════════════════════════════════════════════

if not show_workspace:
    with st.sidebar:
        st.markdown(
            '<div class="h-brand">NumZone</div>'
            '<div class="h-tag">Multi-agent code generation</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border-color:#1F2937;'>", unsafe_allow_html=True)
        

    # Centered hero form
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="hero-eyebrow">NumZone Software</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">What do you want to build?</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Describe your project and my agents will plan, code, run, and review it.</div>', unsafe_allow_html=True)

        # Example chips
        example_cols = st.columns(4)
        for i, (name, prompt) in enumerate(EXAMPLES.items()):
            if example_cols[i].button(name, use_container_width=True, key=f"ex_{name}"):
                st.session_state.example_prompt = prompt
                st.rerun()

        requirement = st.text_area(
            "Requirement",
            value=st.session_state.example_prompt,
            height=140,
            placeholder="e.g. Create a Flask REST API with a /health endpoint...",
            label_visibility="collapsed",
            key="hero_requirement",
        )

        button_ph = st.empty()
        with button_ph.container():
            col_gen, col_resume = st.columns([2, 3])
            with col_gen:
                start = st.button("🚀 Generate", type="primary", use_container_width=True)
            with col_resume:
                resume_thread = st.text_input(
                    "Resume thread (optional)",
                    placeholder="paste a thread id to resume",
                    label_visibility="collapsed",
                )

        status_ph = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)

    if start:
        req = (requirement or "").strip()
        thr = (resume_thread or "").strip()
        if not req and not thr:
            st.warning("Please enter a requirement (or a thread ID to resume).")
        else:
            thread_id = thr or str(uuid.uuid4())
            _reset_run_state()
            st.session_state.thread_id = thread_id
            st.session_state.pending_run = {
                "requirement": req,
                "thread_id": thread_id,
                "resume": bool(thr),
            }
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# WORKSPACE VIEW (file tree left, preview right)
# ═════════════════════════════════════════════════════════════════════════════

else:
    is_running = st.session_state.pending_run is not None

    # ─── Sidebar: header + New Project + live/interactive file tree ─────
    with st.sidebar:
        st.markdown(
            '<div class="h-brand">🤖NumZOne Software</div>'
            '<div class="h-tag">Multi-agent code generation</div>',
            unsafe_allow_html=True,
        )

        col_new, col_clear = st.columns(2)
        if col_new.button("🆕 New Project", use_container_width=True, disabled=is_running):
            _clear_for_new_project()
            st.rerun()
        if col_clear.button("🗑️ Clear Files", use_container_width=True, disabled=is_running, help="Delete generated files on disk"):
            if WORKSPACE.exists():
                shutil.rmtree(WORKSPACE, ignore_errors=True)
            _clear_for_new_project()
            st.rerun()

        st.markdown("<hr style='border-color:#1F2937;'>", unsafe_allow_html=True)

        tree_ph = st.empty()
        if is_running:
            _render_live_tree(tree_ph, workspace_files, latest=None)
        else:
            with tree_ph.container():
                _render_interactive_tree(workspace_files)

        if st.session_state.thread_id:
            st.markdown("<hr style='border-color:#1F2937;'>", unsafe_allow_html=True)
            st.caption("Thread ID (paste in Resume to continue)")
            st.code(st.session_state.thread_id, language="text")

    # ─── Main area: metrics + tabs ──────────────────────────────────────────
    acc = st.session_state.accumulated
    plan = acc.get("plan")
    execution = acc.get("execution_result")
    files_generated = len(workspace_files)

    if st.session_state.run_error:
        status_label, badge_class = "Failed", "err"
    elif st.session_state.run_finished_at:
        if execution and getattr(execution, "success", False):
            status_label, badge_class = "Success", "ok"
        elif execution:
            status_label, badge_class = "Completed w/ Issues", "warn"
        else:
            status_label, badge_class = "Completed", "ok"
    elif st.session_state.run_started_at:
        status_label, badge_class = "Running", "warn"
    else:
        status_label, badge_class = "Ready", "ok"

    lang_val = plan.language if plan and hasattr(plan, "language") else "—"
    elapsed = "—"
    if st.session_state.run_started_at:
        end = st.session_state.run_finished_at or time.time()
        elapsed = f"{end - st.session_state.run_started_at:.1f}s"

    st.write("")

    live_status_ph = st.empty()
    if is_running:
        live_status_ph.info("🟡 Starting pipeline… files will stream into the sidebar as they are written.")

    tab_preview, tab_console, tab_reports, tab_activity = st.tabs(
        ["📄 Preview", "🖥️ Console", "📊 Reports", "📈 Activity"]
    )

    with tab_preview:
        if st.session_state.selected_file:
            file_path = WORKSPACE / st.session_state.selected_file
            if file_path.exists():
                size = file_path.stat().st_size
                st.markdown(
                    f"**{file_icon(file_path)} `{st.session_state.selected_file}`** &nbsp;·&nbsp; {size} bytes",
                    unsafe_allow_html=True,
                )
                try:
                    content = file_path.read_text(encoding="utf-8")
                    st.code(content, language=lang_for(file_path), line_numbers=True)
                except UnicodeDecodeError:
                    st.warning("Binary or non-UTF8 file — cannot preview.")
            else:
                st.info("File no longer exists on disk.")
        else:
            st.info("Select a file in the sidebar to preview it here.")

    with tab_console:
        if execution:
            exec_dict = execution.model_dump() if hasattr(execution, "model_dump") else execution
            rc = exec_dict.get("return_code", "?")
            ok = exec_dict.get("success", False)
            badge = f'<span class="badge {"ok" if ok else "err"}">exit {rc}</span>'
            st.markdown(f"**Execution result** {badge}", unsafe_allow_html=True)
            if exec_dict.get("stdout"):
                st.caption("STDOUT")
                st.code(exec_dict["stdout"], language="text")
            if exec_dict.get("stderr"):
                st.caption("STDERR")
                st.code(exec_dict["stderr"], language="text")
            if not exec_dict.get("stdout") and not exec_dict.get("stderr"):
                st.caption("No output.")
        else:
            st.info("No execution has run yet.")

    with tab_reports:
        plan_ = acc.get("plan")
        manifest_ = acc.get("manifest")
        bug_ = acc.get("bug_report")
        review_ = acc.get("review_report")
        errors_ = acc.get("errors") or []

        if plan_:
            with st.expander("📋 Project Plan", expanded=True):
                st.json(plan_.model_dump() if hasattr(plan_, "model_dump") else plan_)

        if manifest_:
            with st.expander("🏗️ Architecture Manifest", expanded=False):
                st.json(manifest_.model_dump() if hasattr(manifest_, "model_dump") else manifest_)

        if bug_:
            bd = bug_.model_dump() if hasattr(bug_, "model_dump") else bug_
            ok = bd.get("success", False)
            badge = f'<span class="badge {"ok" if ok else "err"}">{"passed" if ok else "issues"}</span>'
            with st.expander(f"🐛 QA Report {'✅' if ok else '⚠️'}", expanded=not ok):
                st.markdown(f"**Summary:** {bd.get('summary','—')} {badge}", unsafe_allow_html=True)
                st.markdown(f"**Cause:** {bd.get('probable_cause','—')}")
                st.markdown(f"**Recommendation:** {bd.get('recommendation','—')}")

        if review_:
            rd = review_.model_dump() if hasattr(review_, "model_dump") else review_
            approved = rd.get("approved", False)
            badge = f'<span class="badge {"ok" if approved else "warn"}">{"approved" if approved else "needs work"}</span>'
            with st.expander(f"👀 Code Review (score {rd.get('score','?')}/10) {'✅' if approved else '⚠️'}", expanded=True):
                st.markdown(f"**Summary:** {rd.get('summary','—')} {badge}", unsafe_allow_html=True)
                if rd.get("strengths"):
                    st.markdown("**Strengths:**")
                    for s in rd["strengths"]:
                        st.markdown(f"- {s}")
                if rd.get("improvements"):
                    st.markdown("**Improvements:**")
                    for i in rd["improvements"]:
                        st.markdown(f"- {i}")

        if errors_:
            with st.expander(f"⚠️ Warnings ({len(errors_)})", expanded=False):
                for err in errors_:
                    st.markdown(f"- {err}")

        if not any([plan_, manifest_, bug_, review_, errors_]):
            st.info("Reports appear here after a run finishes.")

    with tab_activity:
        if st.session_state.activity_log:
            for entry in reversed(st.session_state.activity_log):
                ts = entry["ts"]
                icon = AGENT_ICONS.get(entry["node"], "•")
                label = AGENT_LABELS.get(entry["node"], entry["node"])
                st.markdown(f"`{ts}` &nbsp; {icon} **{label}** — {entry['msg']}", unsafe_allow_html=True)
        else:
            st.info("Agent activity appears here as the pipeline runs.")

    # ─── Kick off the live pipeline run (after the whole UI is drawn) ───────
    if is_running:
        pending = st.session_state.pending_run
        # Clear immediately so a browser reload / rerender does not re-trigger it
        st.session_state.pending_run = None
        _run_pipeline_live(
            requirement=pending["requirement"],
            thread_id=pending["thread_id"],
            resume=pending["resume"],
            status_ph=live_status_ph,
            tree_ph=tree_ph,
        )
