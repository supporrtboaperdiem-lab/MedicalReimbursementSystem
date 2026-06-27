from pathlib import Path

# ==========================================
# Medical Reimbursement System Setup Script
# ==========================================

PROJECT_NAME = "MedicalReimbursementSystem"

folders = [
    "app",
    "app/models",
    "app/routes",
    "app/services",
    "app/services/ocr",
    "app/repositories",
    "app/utils",
    "app/templates",
    "app/static",

    "migrations",
    "uploads",
    "exports",
    "logs",
    "tests",
    "instance"
]

init_files = [
    "app/__init__.py",
    "app/models/__init__.py",
    "app/routes/__init__.py",
    "app/services/__init__.py",
    "app/services/ocr/__init__.py",
    "app/repositories/__init__.py",
    "app/utils/__init__.py"
]

other_files = [
    "requirements.txt",
    "README.md",
    ".env",
    ".env.example",
    ".gitignore",
    "run.py"
]

gitkeep_dirs = [
    "uploads",
    "exports",
    "logs"
]


def create_structure():
    root = Path(PROJECT_NAME)

    print(f"\nCreating project: {PROJECT_NAME}\n")

    root.mkdir(exist_ok=True)

    # Create folders
    for folder in folders:
        path = root / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {path}")

    # Create __init__.py files
    for file in init_files:
        path = root / file
        path.touch(exist_ok=True)
        print(f"Created file: {path}")

    # Create other files
    for file in other_files:
        path = root / file
        path.touch(exist_ok=True)
        print(f"Created file: {path}")

    # Create .gitkeep files
    for folder in gitkeep_dirs:
        gitkeep = root / folder / ".gitkeep"
        gitkeep.touch(exist_ok=True)

    print("\nProject structure created successfully.")


if __name__ == "__main__":
    create_structure()