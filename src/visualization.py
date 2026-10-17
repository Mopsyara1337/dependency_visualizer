import subprocess
from pathlib import Path

MISSING_NODE_STYLE = "fill:#ffcccc,stroke:#ff0000"
PROJECT_DIR = Path(__file__).resolve().parent.parent
RENDER_TIMEOUT_SECONDS = 120
RENDER_SCALE = 3

def generate_mermaid(graph, missing_packages):
    lines = ["flowchart TD"]
    all_packages = set(graph) | missing_packages
    node_ids = {}
    for i, package in enumerate(sorted(all_packages)):
        node_ids[package] = f"p{i}"

    for package in sorted(all_packages):
        lines.append(f"    {node_ids[package]}[\"{package}\"]")

    append_dependency_edges(lines, graph, node_ids)

    for package in sorted(missing_packages):
        lines.append(f"    style {node_ids[package]} "
                     f"{MISSING_NODE_STYLE}")

    mermaid = "\n".join(lines)
    return mermaid

def append_dependency_edges(lines, graph, node_ids):
    dependency_types = (
        ("Depends", "-->"),
        ("Pre-Depends", "-.->")
    )
    or_count = 0
    for field_name, arrow in dependency_types:
        for package_name, dependencies in graph.items():
            for group in dependencies[field_name]:
                current_node = node_ids[package_name]
                current_arrow = arrow
                if len(group) > 1:
                    or_id = f"or{or_count}"
                    or_count += 1
                    lines.append(f"    {or_id}{{\"ИЛИ\"}}")
                    lines.append(f"    {node_ids[package_name]} "
                                 f"{arrow} {or_id}")
                    current_node = or_id
                    current_arrow = "-->"
                for dep in group:
                    lines.append(f"    {current_node} {current_arrow} "
                                 f"{node_ids[dep]}")

def save_graph_png(mermaid_code, output_file):
    mermaid_cli = PROJECT_DIR / "node_modules" / ".bin" / "mmdc.cmd"
    mermaid_path = PROJECT_DIR / "graph.mmd"
    output_path = PROJECT_DIR / output_file

    mermaid_path.write_text(mermaid_code, encoding="utf-8")

    command = [
        str(mermaid_cli),
        "-i",
        str(mermaid_path),
        "-o",
        str(output_path),
        "-s",
        str(RENDER_SCALE)
    ]

    subprocess.run(command, check = True,
                   timeout=RENDER_TIMEOUT_SECONDS,
                   stdout=subprocess.DEVNULL)
