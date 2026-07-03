import logging
import os

logger = logging.getLogger(__name__)


def main() -> None:
    root_dir = os.environ.get("SEARCH_CREDS_ROOT_DIR")
    if not root_dir:
        raise RuntimeError("SEARCH_CREDS_ROOT_DIR env var is required")

    keywords = os.environ.get(
        "SEARCH_CREDS_KEYWORDS",
        "postgres,password,db_password,database,5432",
    ).split(",")

    keywords = [k.strip().lower() for k in keywords if k.strip()]

    for root, _, files in os.walk(root_dir):
        # Exclude virtual environments and node modules
        if any(exclude in root.lower() for exclude in ["venv", "node_modules", ".git", "dist"]):
            continue

        for file in files:
            if file.endswith((".py", ".env", ".ts", ".tsx", ".json", ".txt")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        content_lower = content.lower()

                    for keyword in keywords:
                        if keyword in content_lower:
                            print(f"Keyword '{keyword}' found in file: {filepath}")
                            # Print matching lines
                            for i, line in enumerate(content.split("\n")):
                                if keyword in line.lower() and len(line) < 200:
                                    print(f"  Line {i+1}: {line.strip()}")
                except Exception:
                    logger.exception("Failed scanning file: %s", filepath)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
