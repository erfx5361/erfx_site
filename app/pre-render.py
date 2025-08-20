import os, json
from datetime import datetime
if __name__ == "__main__" and __package__ is None:
    import sys
    from os.path import dirname, abspath
    sys.path.append(dirname(dirname(abspath(__file__))))
    from posts import Post, Posts

# wishlist
# allow option to regenerate json file, default=false

def date_post(file):
    with open(file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated = False

    for i, line in enumerate(lines[1:], start=1):  # Skip the first line
        if 'date:' in line:
            date = line.split(': ')[1]
            if 'date' in date or date == '':
                today = datetime.today().strftime('%B %d, %Y')
                lines[i] = f'date: "{today}"'
                updated = True
            break
        if '---' in line.strip():
            today = datetime.today().strftime('%B %d, %Y')
            lines.insert(i, f'date: "{today}"')
            updated = True
            break

    if updated:
        with open(file, 'w') as f:
            f.write('\n'.join(lines))


def extract_metadata(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    metadata = {}
    if lines[0].strip() == '---':
        in_categories = False
        categories = []
        for line in lines[1:]:
            if line.strip() == '---':
                break
            if in_categories:
                # Check if the line is part of the categories list
                if line.strip().startswith('-'):
                    categories.append(line.strip().lstrip('-').strip())
                    continue
                else:
                    in_categories = False
                
            if line.startswith('categories:'):
                in_categories = True
                continue
            # Handle other metadata fields
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"')
    try:
        print(metadata.get('date'))
        metadata['dt_date'] = datetime.strptime(metadata.get('date', ''), '%B %d, %Y')
    except ValueError:
        raise ValueError(f"Date format is incorrect in file: {file_path} - got: {metadata.get('date')}")
    metadata['post_html_file'] = file_path.replace(file_path.split('.')[-1], 'html')
    metadata['categories'] = categories
    print(metadata['post_html_file'])
    print(metadata['dt_date'])
    print(f"type-dt: {type(metadata['dt_date'])}")
    return metadata


def write_posts_to_json(posts, json_path):
    posts_sorted = sorted(posts, key=lambda x: x.dt_date, reverse=True)
    with open(json_path, 'w') as f:
        json.dump([post.__dict__ for post in posts_sorted], f, default=str, indent=4)


def main():
    print('Running pre-render.py...')

    input_files = os.getenv('QUARTO_PROJECT_INPUT_FILES').split('\n')

    json_path = '../posts.json'

    existing_posts = Posts.get_json_posts()

    for f in input_files:
        date_post(f)
        metadata = extract_metadata(f)
        post_to_render = Post(**metadata)
        # Replace existing post with the same title
        existing_posts = [p for p in existing_posts if p.title != post_to_render.title]
        existing_posts.append(post_to_render)
        for p in existing_posts:
            print(f'post: {p.title}')
            print(f'dt: {p.dt_date}')
            print(f'type-dt: {type(p.dt_date)}')

    # write all rendered posts to json
    write_posts_to_json([p for p in existing_posts], json_path)


if __name__ == "__main__":
    main()


