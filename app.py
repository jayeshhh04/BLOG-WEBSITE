from flask import Flask, request, render_template, redirect, url_for, flash
from transformers import pipeline
from models import db, BlogPost
import logging

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # For flash messages

# Initialize DB
db.init_app(app)

# Initialize Models
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

# Setting up logging for error tracking
logging.basicConfig(level=logging.INFO)

# Predefined tags for categorization
candidate_labels = [
    "spiritual", "comedy", "incident", "love story", "moment", "technology", 
    "news", "fashion", "lifestyle", "wellness", "health", "fitness", 
    "travel", "home decor", "DIY", "motivation", "creativity", "gratitude", 
    "reflection", "autumn", "winter", "spring", "summer", "events", 
    "innovation", "beauty", "skincare", "cooking", "photography"
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form.get('content', '')

        # Validation check for empty content
        if not content.strip():
            flash('Please provide some content to generate a summary and tags!', 'error')
            return redirect(url_for('index'))

        try:
            # Generate summary
            summary = summarizer(content, max_length=50, min_length=25, do_sample=False)[0]['summary_text']
            
            # Generate tags using classifier
            tags = classifier(content, candidate_labels=candidate_labels)

            # Log the output for debugging
            logging.info(f"Generated summary: {summary}")
            logging.info(f"Generated tags: {tags['labels'][:2]}")

            # Create a new blog post object
            new_post = BlogPost(
                content=content, 
                summary=summary, 
                tags=", ".join(tags['labels'][:3])  # Use top 3 labels for more specific categorization
            )
            
            # Save to the database
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('result', post_id=new_post.id))

        except Exception as e:
            # Handle and log errors
            logging.error(f"An error occurred: {str(e)}")
            flash(f"An error occurred: {str(e)}", 'error')
            return redirect(url_for('index'))

    # Retrieve all blog posts from the database for display on main screen
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    return render_template('index.html', posts=posts)

# Route to show a single blog post
@app.route('/result/<int:post_id>')
def result(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('result.html', post=post)

# Route to display all blog posts
@app.route('/blogs')
def all_blogs():
    # Retrieve all blog posts from the database
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    return render_template('all_blogs.html', posts=posts)

# Route to delete a blog post
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('all_blogs'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True)

