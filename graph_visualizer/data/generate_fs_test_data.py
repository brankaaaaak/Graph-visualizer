import os


def create_test_fs_structure(base_path, num_files=200):
    os.makedirs(base_path, exist_ok=True)

    for i in range(num_files):
        subfolder = os.path.join(base_path, f"subfolder_{i // 10}")
        os.makedirs(subfolder, exist_ok=True)
        with open(os.path.join(subfolder, f"file_{i}.txt"), "w") as f:
            f.write(f"This is test file number {i}")

    print(f"Generated {num_files} test files in {base_path}")


if __name__ == "__main__":
    target_path = os.path.join("data", "fs_test_folder")
    create_test_fs_structure(target_path)
