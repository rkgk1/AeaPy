import os
import shutil
import sys

CONFIG_FILE = "last_used_dirs.txt"

def save_directories(main_dir, temp_dir):
    with open(CONFIG_FILE, "w") as file:
        file.write(f"{main_dir}\n{temp_dir}")

def load_directories():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()
            if len(lines) == 2:
                main_dir = lines[0].strip()
                temp_dir = lines[1].strip()
                return main_dir, temp_dir
    return None, None

def divide_files(file_list):
    mid_index = len(file_list) // 2
    return file_list[:mid_index], file_list[mid_index:]

def move_files(files, destination):
    for file in files:
        try:
            shutil.move(file, destination)
            print(f"Moved {os.path.basename(file)} to {destination}")
        except Exception as e:
            print(f"Error moving {file}: {e}")

def restore_files(files, main_dir):
    for file in files:
        try:
            restored_path = os.path.join(main_dir, os.path.basename(file))
            shutil.move(file, restored_path)
            print(f"Restored {os.path.basename(file)} to {main_dir}")
        except Exception as e:
            print(f"Error restoring {file}: {e}")

def prompt_for_test_result(group_name):
    while True:
        result = input(f"Did {group_name} cause an error? (yes/no): ").lower()
        if result in ['yes', 'no']:
            return result == 'yes'
        else:
            print("Please respond with 'yes' or 'no'.")

def binary_search_debug(file_list, main_dir, temp_dir):
    groups = [(file_list, "Initial Group")]

    while groups:
        current_group, group_name = groups.pop()

        if len(current_group) == 1:
            print(f"The problematic file is: {current_group[0]}")
            return

        first_half, second_half = divide_files(current_group)

        restore_files(first_half, main_dir)
        if prompt_for_test_result(f"{group_name} (First Half)"):
            move_files(second_half, temp_dir)
            groups.append((first_half, f"{group_name} (First Half)"))
        else:
            move_files(first_half, temp_dir)
            restore_files(second_half, main_dir)
            groups.append((second_half, f"{group_name} (Second Half)"))

def get_files_in_directory(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]

def set_directories():
    main_dir = input("Enter the main directory path where files should be restored for testing: ")
    temp_dir = input("Enter the temporary directory path for storing excluded files: ")

    os.makedirs(main_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    save_directories(main_dir, temp_dir)
    return main_dir, temp_dir

def main_menu():
    while True:
        print("\n--- Binary File Debugger Menu ---")
        print("1. Set new directories")
        print("2. Use recent directories")
        print("3. Quit")

        main_dir, temp_dir = load_directories()

        choice = input("Choose an option (1, 2, or 3): ")

        if choice == "1":
            return set_directories()
        elif choice == "2":
            if main_dir and temp_dir:
                print(f"Using last saved directories:\nMain Directory: {main_dir}\nTemporary Directory: {temp_dir}")
                return main_dir, temp_dir
            else:
                print("No recent directories found. Please set new directories.")
        elif choice == "3":
            print("Exiting program.")
            sys.exit()
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def retry_or_quit():
    while True:
        print("\nThe process has completed.")
        print("1. Restart the program")
        print("2. Quit")
        choice = input("Choose an option (1 or 2): ")

        if choice == "1":
            main()  # Restart the program
        elif choice == "2":
            print("Exiting program.")
            sys.exit()
        else:
            print("Invalid choice. Please enter 1 or 2.")

def main():
    main_dir, temp_dir = main_menu()

    file_list = get_files_in_directory(temp_dir)

    if not file_list:
        print("No files found in the temporary directory.")
        retry_or_quit()
    else:
        print(f"Found {len(file_list)} files in the temporary directory.")
        binary_search_debug(file_list, main_dir, temp_dir)
        retry_or_quit()

if __name__ == "__main__":
    main()
