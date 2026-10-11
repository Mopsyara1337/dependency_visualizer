import gzip
from urllib.request import urlopen
from urllib.parse import urljoin

REQUEST_TIMEOUT_SECONDS = 15
PACKAGES_INDEX_PATH = "dists/noble/main/binary-amd64/Packages.gz"

def fetch_packages(repository_url):
    url = urljoin(repository_url, PACKAGES_INDEX_PATH)
    with urlopen(url, timeout = REQUEST_TIMEOUT_SECONDS) as response:
        file = response.read()
        packages_data = gzip.decompress(file).decode("utf-8")
        return packages_data

def find_package(packages_data, package_name):
    packages = packages_data.split("\n\n")
    for package in packages:
        lines = package.splitlines()
        for line in lines:
            if line == f"Package: {package_name}":
                return package
    raise ValueError(f"Пакет {package_name} не найден в репозитории")

def get_dependencies(package_data, field_name):
    parts = []
    found = False
    for line in package_data.splitlines():
        if line.startswith(f"{field_name}: "):
            parts.append(line.removeprefix(f"{field_name}: "))
            found = True
            continue

        if found and line.startswith((" ", "\t")):
            parts.append(line.strip())
            continue

        if found:
            break

    return " ".join(parts)

def parse_dependencies(dependencies):
    if not dependencies.strip():
        return []
    dependencies_list = []
    for dep in dependencies.split(","):
        dep_list = [extract_package_name(x) for x in dep.split("|")]
        dependencies_list.append(dep_list)

    return dependencies_list

def extract_package_name(dependency):
    result = dependency.split("(", 1)[0].strip()
    result = result.split(":", 1)[0].strip()
    return result