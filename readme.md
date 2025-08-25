Simple flask site I am building for a personal website. The [site](https://erfx5361.xyz) has some additional "user content" that is not featured on this repository.

This repository contains the structure of the site and tools, while the content for posts, about, and home page are stored in a private repository. Anyone who likes the structure or some of the tools can freely replicate. The site includes the following basic sections so far:
- Home Page
- About Page
- Posts Page
    - Individual Posts (rendered from quarto .qmd files)
- Tools Page
    - Pi Pad Calculator

## Pi Pad Calculator

As if the internet didn't already have enough of these, I made another one. Most of us use standard resistor values, so it makes sense to have this option integrated into the calculator. Power dissipation is seemlessly built into the same calculator as well.

Maybe eventually output calculations will include worst case or monte carlo tolerance analysis.

Tee pad tool coming soon, but who uses those anyway?

## Quarto Integration

I like the powerful integrations that [Quarto](https://quarto.org/) offers and I wanted to to be able to leverage some of the features including: python snippits, python plots, mathematical equations, and basic markdown formatting. I have opted to integrate quarto posts into my custom flask site. 

Quarto pre-render and post-render scripts are run to integrate the quarto posts into the flask site. Some tweaks are performed to maintain consistent styling between the posts and the rest of the site. 

Quarto posts (`.qmd` files) should be stored in `app/quarto_posts`, the quarto root directory. The `_quarto.yml` configuration file defines the correct output directory for the posts within the flask site. However, the post-render script is needed to move the generated static files to the appropriate locations in the flask app as well as support files stored in the quarto root directory (currently just `/images` directory). The scripts also extract the proper hooks to integrate the posts into the logic of the flask site.

There are some additional guidelines for how the quarto directory can be used in practice.

### Quarto Guidelines

The current site makes the following assumptions in order for things to work.
1. All quarto posts are stored within a `.qmd` file in the quarto project root directory `app/quarto_posts`
2. Currently, the only supported local content to load for `.qmd` posts are `.jpg` and `.png` files stored in `quarto_post/images`
3. These image files cannot have double quote `"` or space ` ` characters within the filename since there is a regex used in post-render.py to replace image links from `.qmd` files to links that work within the rendered `.html` files in the flask site.




## Acknowledgements
 Started building this site using Miguel Grinberg's [flask tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world). This resource was super helpful for someone like me with no web experience.

## License
This software is public domain.
