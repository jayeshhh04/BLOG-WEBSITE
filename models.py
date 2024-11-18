from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500), nullable=False)
    tags = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<BlogPost {self.id}: {self.summary}>'
