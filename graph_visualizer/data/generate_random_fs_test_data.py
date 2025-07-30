import os
import random


def create_random_test_fs_structure(base_path, min_files=200, max_depth=5, max_files_in_folder=10):
    file_counter = [0]

    def create_folder(path, current_depth):
        if current_depth > max_depth:
            return

        os.makedirs(path, exist_ok=True)
        file_counter[0] += 1

        num_files = random.randint(1, max_files_in_folder)
        for i in range(num_files):
            if file_counter[0] >= min_files:
                return
            filename = f"file_{file_counter[0]}.{'txt' if random.random() < 0.5 else 'log'}"
            file_path = os.path.join(path, filename)
            with open(file_path, "w") as f:
                f.write(f"Test file {file_counter[0]}")
            file_counter[0] += 1

        num_subfolders = random.randint(1, 5)
        for i in range(num_subfolders):
            if file_counter[0] >= min_files:
                return
            subfolder_name = f"folder_{current_depth}_{file_counter[0]}"
            subfolder_path = os.path.join(path, subfolder_name)
            create_folder(subfolder_path, current_depth+1)

    create_folder(base_path, current_depth=0)
    print(f"Random file system structure created at: {base_path}")


if __name__ == "__main__":
    target_path = os.path.join("data", "fs_test_folder")
    create_random_test_fs_structure(target_path)
