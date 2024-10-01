import os
import sys

def create_structure(structure, base_path):
    """Recursively create the directory structure and files."""
    for item in structure:
        path = os.path.join(base_path, item.lstrip('/'))
        if item.endswith('/'):
            os.makedirs(path, exist_ok=True)
        else:
            dir_path = os.path.dirname(path)
            os.makedirs(dir_path, exist_ok=True)
            open(path, 'a').close()  # Create an empty file

def load_structure(file_path):
    """Load the structure from a text file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def main():
    file_path = r'C:\Users\jefft\PycharmProjects\bet-project\Atelier\project-structure.txt'
    base_dir = r'C:\Users\jefft\PycharmProjects\bet-project\Atelier'

    try:
        structure = load_structure(file_path)
    except Exception as e:
        print(f"Error loading structure file: {e}")
        sys.exit(1)

    try:
        create_structure(structure, base_dir)
        print(f"Project structure created successfully in {base_dir}")
    except Exception as e:
        print(f"Error creating project structure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()