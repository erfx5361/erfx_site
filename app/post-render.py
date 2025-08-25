import os, shutil, re

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
    file_name = os.path.splitext(file)[0]
    file_name_files_dir = file_name + '_files'

    # Construct the source and destination paths
    source_path = os.path.join(output_dir, file_name_files_dir)
    destination_path = posts_static_dir

    cut_paste_dir(source_path, destination_path)


def fix_file_for_flask(file, output_dir, posts_static_dir):
    file_name = os.path.splitext(file)[0]
    file_name_files_dir = file_name + '_files/'
    file_path = os.path.join(output_dir, file)

    with open(file_path, 'r') as f:
        content = f.read()

    # replace quarto static file location with flask location
    updated_content = content.replace(f'{file_name_files_dir}', f'{posts_static_dir}')
    # apply flask site styling override
    updated_content = apply_flask_styling(updated_content)
    # replace quarto image links with flask image links
    updated_content = update_image_links(updated_content)

    with open(file_path, 'w') as f:
        f.write(updated_content)


def apply_flask_styling(content):

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
    
    updated_content = '\n'.join(updated_content)
    return updated_content


def update_image_links(content):
    image_link_template = "{{ url_for('static', filename='') }}"
    updated_content = content.splitlines()
    # match image links from quarto posts
    for index, line, in enumerate(content.splitlines()):
        if line.startswith('<img'):
            print(f'image line found: {line}')
            # regex requires no spaces or double quotes in filenames
            match = re.search(r'src="(images/.*)" ', line)
            if match:
                src = match.group(1)
                print(f'match found: {src}')
                updated_src = image_link_template.replace("''", "'"+'posts/'+src+"'")
                updated_line = line.replace(src, updated_src)
                print(f'updated image line: {updated_line}')
                updated_content[index] = updated_line
    updated_content = '\n'.join(updated_content)
    return updated_content


def main():
    print('Running post-render.py')
    # list of files rendered
    output_files = os.getenv('QUARTO_PROJECT_OUTPUT_FILES').split('\n')
    # directory of rendered files
    output_dir = os.getenv('QUARTO_PROJECT_OUTPUT_DIR')
    # new directory for rendered files to integrate into flask site
    posts_static_dir = '../static/posts/'
    posts_images_dir = '../static/posts/images/'
    os.makedirs(posts_static_dir, exist_ok=True)

    for f in output_files:
        f = f.split('/')[-1]
        fix_file_for_flask(f, output_dir, posts_static_dir)
        move_post_files(f, output_dir, posts_static_dir)
    # move image files to flask location
    cut_paste_dir(os.path.join(output_dir, 'images'), posts_images_dir)
        

if __name__ == "__main__":
    main()

