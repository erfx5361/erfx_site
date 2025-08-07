from flask import render_template, flash , redirect, request, abort
from app import app, calculate
from app.posts import Posts
from app.forms import PiPadForm, PiPadDissipationForm
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
import markdown
from markupsafe import Markup
from pathlib import Path
from config import appdir
import os

site_posts = Posts()
md = markdown.Markdown(
	extensions=[
		'tables'
	]
)

@app.route('/')
@app.route('/index')
def index():
	html = load_markdown('index')
	return render_template('index.html', body=Markup(html))

@app.route('/about')
def about():
	html = load_markdown('about')
	return render_template('about.html', body=Markup(html))


@app.route('/tools')
def tools():
	tools = [
		{
			'name': 'Pi-Pad Calculator',	
			'description': 'Fully-featured Pi Resistive Attenator Calculator',
			'endpoint': 'pi_pad_calculator'
		},
		{
			'name': 'Back Home',	
			'description': 'Not a very useful tool',
			'endpoint': 'index'
		}
	]
	return render_template('tools.html', title='Tools', tools=tools)


@app.route('/posts/<slug>')
def post(slug):
	post = site_posts.posts_dict[slug]
	return render_template(post.source, post=post)
    

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Posts', posts=site_posts.sorted_posts)


pi_atten = calculate.Pi_Atten()

@app.route('/pi_pad_calculator', methods=['GET', 'POST'])
def pi_pad_calculator():
	form_type = request.form.get('form_type')
	pipad_form = PiPadForm()
	pdiss_form = PiPadDissipationForm()
	
	if form_type == 'pipad_form':
		if pipad_form.validate_on_submit():
			pi_atten.define_from_form(pipad_form)
			return pipad_form.populate_pi_pad_form(pi_atten)
		else:
			print('validation failed')
			print(pipad_form.errors)

	elif form_type == 'pdiss_form':
		if pi_atten.defined == False:
			print('Pi attenuator not populated')
		elif pdiss_form.validate_on_submit():
			return pdiss_form.populate_pi_pad_dissipation(pi_atten)
		else:
			print('dissipation validation failed')
			print(pdiss_form.errors)
			#test
			flash('Error in form submission. Please check your inputs.', 'danger')
	
	return render_template('tools/pi_pad_calculator.html', form=pipad_form, pdiss_form=pdiss_form)


@app.route('/tee_pad_calculator', methods=['GET', 'POST'])
def tee_pad_calculator():
	return render_template('tools/tee_pad_calculator.html')


def load_markdown(slug: str) -> str:
	"""Return rendered HTML for `slug.md`; raise 404 if it’s missing."""
	md_file = Path(os.path.join(appdir, f'md_content/{slug}.md'))
	if not md_file.exists():
		abort(404)

	raw = md_file.read_text(encoding="utf-8")
	html = md.convert(raw)        # str containing <h1>, <p>…
	md.reset()                    # reset parser so TOC works on next run
	return html


