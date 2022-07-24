import os
import shutil

def get_resource_path(name: str) -> str:
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, name)


PLACEHOLDER_JS = get_resource_path("placeholder-plugin.js")


def copy_asset_if_target_file_does_not_exist(output_dir: str, target_path_in_output_folder: str, asset_name: str):
    if not target_path_in_output_folder:
        raise ValueError("Empty value for 'target_path_in_output_folder' given")

    target_path = os.path.join(output_dir, target_path_in_output_folder)
    if os.path.exists(target_path):
        # The file exists. This probably means, that the user wanted to override the default file
        # So we just do nothing
        pass
    else:
        # Make sure that the folder exists
        parent_dir = os.path.dirname(target_path)
        os.makedirs(parent_dir, exist_ok=True)
        # Copy the file
        asset_path = get_resource_path(asset_name)
        shutil.copyfile(asset_path, target_path)

def replace_text_in_file(file_path: str, old_text: str, new_text: str) -> None:
    # read file contents
    with open(file_path, "r") as f:
        text = f.read()

    # do the replacing
    text = text.replace(old_text, new_text)

    # write back the results
    with open(file_path, "w") as f:
        f.write(text)
