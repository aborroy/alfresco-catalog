import os
import re
import yaml

# Define the folder containing Markdown entries
ENTRIES_DIR = "entries"

# Mapping from old compatibility patterns to allowed labels
COMPAT_MAP = {
    "4": "ACS 4.x",
    "5": "ACS 5.x",
    "5.2": "ACS 5.x",
    "6": "ACS 6.x",
    "7": "ACS 7.x",
    "23.1": "ACS 23.1",
    "23.2": "ACS 23.2",
    "23.3": "ACS 23.3",
    "23.4": "ACS 23.4",
    "23": "ACS 23.x",
    "25.1": "ACS 25.1",
    "25.2": "ACS 25.2",
    "25": "ACS 25.x",
}

def normalize_version(value: str) -> str:
    """Return mapped ACS label if found, else None."""
    value = value.strip().replace('"', '').replace("'", "")
    value = re.sub(r"[vV]", "", value)  # remove leading 'v' if present
    value = value.replace(".x", "")
    for key, label in COMPAT_MAP.items():
        if value.startswith(key):
            return label
    return None

def update_front_matter(content: str) -> str:
    """Update compatibility field in YAML front matter."""
    parts = content.split("---")
    if len(parts) < 3:
        return content  # no YAML front matter

    yaml_block = parts[1]
    data = yaml.safe_load(yaml_block)
    if not isinstance(data, dict) or "compatibility" not in data:
        return content

    old_values = data["compatibility"]
    if not isinstance(old_values, list):
        return content

    new_values = sorted(set(
        label for v in old_values if (label := normalize_version(str(v)))
    ))

    if not new_values:
        return content

    data["compatibility"] = new_values
    updated_yaml = yaml.dump(data, sort_keys=False, allow_unicode=True)
    parts[1] = "\n" + updated_yaml + "---\n"
    return "---".join(parts)

def main():
    for root, _, files in os.walk(ENTRIES_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            updated = update_front_matter(content)
            if updated != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(updated)
                print(f"✅ Updated {path}")
            else:
                print(f"➡️  No change: {path}")

if __name__ == "__main__":
    main()

