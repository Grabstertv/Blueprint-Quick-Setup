import os
import re
import shutil
import urllib.parse

def validate_directory(path):
    return os.path.exists(path) and os.path.isdir(path)

def validate_version_number(version):
    return re.match(r"\d+\.\d+\.\d+", version)

def validate_url(url):
    return url.startswith("http://") or url.startswith("https://")

def get_input(prompt, validation_fn=None, error_message=None):
    while True:
        user_input = input(prompt).strip()
        if not validation_fn or validation_fn(user_input):
            return user_input
        print(error_message or "Invalid input. Please try again.")

def confirm_action(prompt):
    while True:
        user_input = input(prompt + " (Y/N): ").strip().lower()
        if user_input in ['y', 'n']:
            return user_input == 'y'
        print("Invalid input. Please enter 'Y' or 'N'.")

print("""
READ BEFORE CONTINUING
-------------
1. Be sure you're running this script on a new SAMPLE BRANCH of blueprint dashboard and not an existing one so you don't accidentally break a current project.
2. Be sure you have already created a new package before continuing (https://github.com/jahirfiquitiva/Blueprint/wiki/Create-a-Package). If not, do so and run the script.
3. This script only edits necessary files and values in one go to get your project up and running as quick as possible. Things such as about page, notifications and license checker code is not edited. You have to edit those manually. For advanced set up, refer to Blueprint wiki on GitHub and edit necessary values accordingly.
4. Finally, during the questionnaire, hit enter without typing anything to skip a step and leave it unchanged.
""")

# Step 1: Ask for working directory
working_directory = get_input(
    "Type your project directory to get started: ",
    validate_directory,
    "Invalid directory. Please provide a valid directory (e.g for MacOS: /Users/orange/Library/Reev Pro)"
)

# Step 2: Ask for Package name
package_name = get_input("Enter Package name (e.g com.reevpro.grabsterstudios): ")

# Update package name in specified files
file_paths = [
    os.path.join(working_directory, 'buildSrc/src/main/java/MyApp.kt'),
    os.path.join(working_directory, 'app/src/main/AndroidManifest.xml')
]

for file_path in file_paths:
    with open(file_path, 'r') as file:
        file_content = file.read()
        file_content = file_content.replace('dev.jahir.blueprint.app', package_name)

    with open(file_path, 'w') as file:
        file.write(file_content)

# Move files to new package directory
kotlin_dir = os.path.join(working_directory, 'app/src/main/kotlin')
old_package_dir = os.path.join(kotlin_dir, 'dev/jahir/blueprint/app')
new_package_dir = os.path.join(kotlin_dir, *package_name.split('.'))

if not os.path.exists(new_package_dir):
    os.makedirs(new_package_dir)

files_to_move = ['MainActivity.kt', 'MuzeiService.kt', 'MyApplication.kt', 'NotificationServiceExtension.kt']
for file_name in files_to_move:
    old_file_path = os.path.join(old_package_dir, file_name)
    new_file_path = os.path.join(new_package_dir, file_name)
    if os.path.exists(old_file_path):
        shutil.move(old_file_path, new_file_path)

if os.path.exists(old_package_dir):
    shutil.rmtree(old_package_dir)

# Step 3: Ask for version number
version_number = get_input(
    "What should the version number of your app be? (e.g., 1.1.1): ",
    validate_version_number,
    "Invalid version number format. Please provide a valid format (e.g., 1.1.1)."
)

version_parts = version_number.split(".")
version_code = int("".join(version_parts))

# Update version numbers in MyApp.kt
blueprint_kt_path = os.path.join(working_directory, 'buildSrc/src/main/java/MyApp.kt')
with open(blueprint_kt_path, 'r') as file:
    file_content = file.read()
    file_content = re.sub(r'const val version = \d+', f'const val version = {version_code}', file_content)
    file_content = re.sub(r'const val versionName = "[\d.]*"', f'const val versionName = "{version_number}"', file_content)

with open(blueprint_kt_path, 'w') as file:
    file.write(file_content)

# Step 4: Ask for icon pack name
icon_pack_name = get_input("What would you like to call your icon pack? ")

# Update icon pack name in strings.xml and blueprint_setup.xml
strings_path = os.path.join(working_directory, 'app/src/main/res/values/strings.xml')
blueprint_setup_path = os.path.join(working_directory, 'app/src/main/res/values/blueprint_setup.xml')

for file_path in [strings_path, blueprint_setup_path]:
    with open(file_path, 'r') as file:
        file_content = file.read()
        file_content = file_content.replace('Blueprint', icon_pack_name)

    with open(file_path, 'w') as file:
        file.write(file_content)

# Step 5: Set up wallpaper link
if confirm_action("Would you like to set up wallpaper link?"):
    wallpaper_link = get_input(
        "Type link to your JSON file: ",
        validate_url,
        "Invalid link format. Please provide a valid link."
    )

    # Update wallpaper link in frames_setup.xml
    frames_setup_path = os.path.join(working_directory, 'app/src/main/res/values/frames_setup.xml')
    with open(frames_setup_path, 'r') as file:
        file_content = file.read()
        file_content = file_content.replace('https://jahir.dev/frames/frames.json', wallpaper_link)

    with open(frames_setup_path, 'w') as file:
        file.write(file_content)

# Step 6: Enable immediate wallpaper downloads
allow_immediate_downloads = 'true' if confirm_action("Would you like to enable immediate wallpaper downloads?") else 'false'

# Update allow_immediate_downloads in frames_setup.xml
frames_setup_path = os.path.join(working_directory, 'app/src/main/res/values/frames_setup.xml')
with open(frames_setup_path, 'r') as file:
    file_content = file.read()
    file_content = re.sub(
        r'<bool name="allow_immediate_downloads">true</bool>|<bool name="allow_immediate_downloads">false</bool>',
        f'<bool name="allow_immediate_downloads">{allow_immediate_downloads}</bool>',
        file_content
    )

with open(frames_setup_path, 'w') as file:
    file.write(file_content)

# Step 7: Add privacy policy link
if confirm_action("Add a privacy policy link?"):
    privacy_policy_link = get_input("Paste your GitHub.io link here: ")

    # Update privacy_policy_link in dashboard_setup.xml
    dashboard_setup_path = os.path.join(working_directory, 'app/src/main/res/values/dashboard_setup.xml')
    with open(dashboard_setup_path, 'r') as file:
        file_content = file.read()
        file_content = re.sub(r'<string name="privacy_policy_link">""</string>', f'<string name="privacy_policy_link">{privacy_policy_link}</string>', file_content)

    with open(dashboard_setup_path, 'w') as file:
        file.write(file_content)

# Final check for dev.jahir.blueprint folder and delete if exists
blueprint_base_dir = os.path.join(kotlin_dir, 'dev/jahir/blueprint')
if os.path.exists(blueprint_base_dir):
    shutil.rmtree(blueprint_base_dir)

# Summary
print("\nSummary\n")
print(f"App name: {icon_pack_name}")
print(f"Package name: {package_name}")
print(f"Version: {version_number} (code: {version_code})")
if 'wallpaper_link' in locals():
    print(f"Wallpaper link: {wallpaper_link}")
print(f"Immediate wallpaper downloads: {'Enabled' if allow_immediate_downloads == 'true' else 'Disabled'}")
if 'privacy_policy_link' in locals():
    print(f"Privacy policy link: {privacy_policy_link}")

print("\nFiles changed:")
print("  - buildSrc/src/main/java/MyApp.kt")
print("  - app/src/main/AndroidManifest.xml")
print("  - app/src/main/res/values/strings.xml")
print("  - app/src/main/res/values/blueprint_setup.xml")
if 'wallpaper_link' in locals():
    print("  - app/src/main/res/values/frames_setup.xml")
print("  - app/src/main/res/values/dashboard_setup.xml")

print("\n✅ Your dashboard is now ready.. for the most part. Please visit the Blueprint Wiki for a more comprehensive guide on setting up the rest of the dashboard. /n — Created by @GrabsterTV (with the help of ChatGPT) \n")