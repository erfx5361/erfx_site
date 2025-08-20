import os, json, re
import sys
from os.path import dirname, abspath
from datetime import datetime
sys.path.append(dirname(dirname(abspath(__file__))))
from config import appdir

class Posts():
    json_path = os.path.join(os.path.dirname(__file__), 'posts.json')
    
    def __init__(self):
        self.sorted_posts = Posts.get_json_posts()
        self.posts_dict = {post.slug: post for post in self.sorted_posts}

    # note - json file is populated during render of quarto posts and used to populate Post metadata 
    def load_valid_json_posts():
        if os.path.exists(Posts.json_path):
            if os.path.getsize(Posts.json_path) == 0:
                current_posts = []
            else:
                with open(Posts.json_path, 'r') as f:
                    json_posts = json.load(f)
                    # remove posts that do not have a file in the posts directory
                current_posts = [post for post in json_posts if post.get('post_html_file') 
                        in os.listdir(os.path.join(appdir,'templates/posts'))]
        else:
            current_posts = []
        return current_posts
    

    def update_json_posts(posts):
        # create json
        with open(Posts.json_path, 'w') as f:
            json.dump(posts, f, default=str, indent=4)


    def get_json_posts():
        current_posts = Posts.load_valid_json_posts()
        Posts.update_json_posts(current_posts)
        sorted_posts = []    
        for post in current_posts:
            sorted_posts.append(Post(**post))
        return sorted_posts


class Post():
    # directory relative to appdir/templates/ for render_template()
    post_dir = 'posts/'

    def __init__(self, **kwargs):
        self.post_html_file = kwargs.get('post_html_file', '')
        self.title = kwargs.get('title', self.post_html_file.split('.')[0].replace('_', ' ').title())
        self.slug = self.generate_slug(self.title)
        self.source = kwargs.get('source', Post.post_dir + self.post_html_file)
        self.author = kwargs.get('author', 'Unknown')
        self.date = kwargs.get('date', '')
        self.dt_date = datetime.strptime(self.date, '%B %d, %Y')
        #self.dt_date = kwargs.get('dt_date', '')
        self.categories = kwargs.get('categories', [])

    @staticmethod
    def generate_slug(title):
        # Convert to lowercase
        slug = title.lower()
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove special characters
        slug = re.sub(r'[^\w\-]', '', slug)
        return slug

    