from collections import deque
import packages as pak

def build_dependency_graph(package_index, package_name):
    if not package_name in package_index:
        raise ValueError(f"Выбранный пакет {package_name}"
                         f" не найден в индексе репозитория")
    graph = {}
    visited = {package_name}
    queue = deque([package_name])
    missing_packages = set()

    while queue:
        current_name = queue.popleft()
        current = package_index.get(current_name)
        if current is None:
            missing_packages.add(current_name)
            continue

        dependencies = {}
        depends = pak.parse_dependencies(
            pak.get_dependencies(current, "Depends")
        )
        pre_depends = pak.parse_dependencies(
            pak.get_dependencies(current, "Pre-Depends")
        )

        for groups in (depends, pre_depends):
            for dependency in groups:
                for package in dependency:
                    if package not in visited:
                        queue.append(package)
                        visited.add(package)

        dependencies["Depends"] = depends
        dependencies["Pre-Depends"] = pre_depends
        graph[current_name] = dependencies
    return graph, missing_packages


