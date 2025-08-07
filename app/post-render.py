import os
import shutil

def cut_paste_dir(source_dir, destination_dir):
    """
    Recursively moves all contents from source_dir to destination_dir.
    Keeps existing content in destination_dir and overwrites files with the same name.
    If destination_dir does not exist, it is created.
    """

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)  # Create the destination directory if it doesn't exist

    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)
        if os.path.isfile(source_item):
            if os.path.isfile(destination_item):
                os.remove(destination_item)  # Overwrite files with the same name
            shutil.move(source_item, destination_item)  # Move the item
        elif os.path.isdir(source_item):
            cut_paste_dir(source_item, destination_item)  # Remove existing directory with the same name
    os.rmdir(source_dir)  # Remove the source directory if it's empty


def move_post_files(file, output_dir, posts_static_dir):
    file_name = file.split('.')[0]
    file_name_files_dir = file_name + '_files'

    # Construct the source and destination paths
    source_path = os.path.join(output_dir, file_name_files_dir)
    destination_path = posts_static_dir

    cut_paste_dir(source_path, destination_path)


def update_paths(file, output_dir, posts_static_dir):
    file_name = file.split('.')[0]
    file_name_files_dir = file_name + '_files/'
    fpath_name = os.path.join(output_dir, file)

    with open(fpath_name, 'r') as f:
        content = f.read()

    updated_content = content.replace(f'{file_name_files_dir}', f'{posts_static_dir}')

    with open(fpath_name, 'w') as f:
        f.write(updated_content)


def apply_jinja_template(file, output_dir):
    # Construct the full file path
    file_path = os.path.join(output_dir, file)

    # Read the existing content of the file
    with open(file_path, 'r') as f:
        content = f.read()

    # define Jinja template lines
    include_navbar = '{% include "_navbar.html" %}'
    include_style_overrides = '{% include "_post_styling.html" %}'

    updated_content = content.splitlines()
    # insert Jinja template lines
    for index, line, in enumerate(content.splitlines()):
        # assume styling appears first, insert style edits before existing quarto styling
        if line.startswith('<style'):
            updated_content.insert(index, include_style_overrides)
            styling_inserted = True
        # insert navbar after body, with one offset for added style line
        if line.startswith('<body') and styling_inserted:
            updated_content.insert(index + 2 , include_navbar)
            navbar_inserted = True
            break
    if not styling_inserted:
        raise ValueError("No <style> tag found in the file.")
    if not navbar_inserted:
        raise ValueError("No <body> tag found in the file.")
    
    # join the updated content back into a single string
    updated_content = '\n'.join(updated_content)

    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(updated_content)




def main():
    print('Running post-render.py')

    output_files = os.getenv('QUARTO_PROJECT_OUTPUT_FILES').split('\n')
    output_dir = os.getenv('QUARTO_PROJECT_OUTPUT_DIR')
    posts_static_dir = '../static/posts/'
    os.makedirs(posts_static_dir, exist_ok=True)

    for f in output_files:
        f = f.split('/')[-1]
        update_paths(f, output_dir, posts_static_dir)
        apply_jinja_template(f, output_dir)
        move_post_files(f, output_dir, posts_static_dir)
        

if __name__ == "__main__":
    main()

