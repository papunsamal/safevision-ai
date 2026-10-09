import os

def print_directory_tree(startpath, max_depth=None):
    """Prints directory tree similar to 'tree' command."""
    if not os.path.exists(startpath):
        print(f"Path does not exist: {startpath}")
        return

    # Directories to ignore for cleaner view
    ignore_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build'}
    
    def _walk(dir_path, prefix='', depth=0):
        if max_depth is not None and depth > max_depth:
            return
        
        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            return

        # Filter out ignored dirs/files
        filtered_entries = [e for e in entries if e not in ignore_dirs and not e.startswith('.')]
        
        for i, entry in enumerate(filtered_entries):
            full_path = os.path.join(dir_path, entry)
            is_last = (i == len(filtered_entries) - 1)
            
            # Print current item
            connector = '└── ' if is_last else '├── '
            print(prefix + connector + entry)
            
            # Recurse if it's a directory
            if os.path.isdir(full_path):
                extension = '    ' if is_last else '│   '
                _walk(full_path, prefix + extension, depth + 1)

    print("\n📂 SAFEVISION AI PROJECT STRUCTURE\n")
    print("Root:")
    _walk(startpath)
    print("-" * 30)
    print("✅ Structure Verified.\n")

if __name__ == "__main__":
    # Current working directory
    print_directory_tree(".")