import sys

def increment_version(version_type="patch"):
    print(f"Received version type: {version_type}")  # Debug print

    with open("version.txt", "r") as file:
        version = file.read().strip()
    
    major, minor, patch = map(int, version.split('.'))
    print(f"Current version: {major}.{minor}.{patch}")  # Debug print
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        print(f"Unknown version type: {version_type}")  # Debug print for unknown type
    
    new_version = f"{major}.{minor}.{patch}"
    
    with open("version.txt", "w") as file:
        file.write(new_version)
    
    print(f"Version incremented to {new_version}")

if __name__ == "__main__":
    version_type = "patch"
    if len(sys.argv) > 1:
        version_type = sys.argv[1]
    increment_version(version_type)
