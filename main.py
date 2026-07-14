from flask import Flask, render_template
from models import get_notes
app = Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html", notes=get_notes(1))

if __name__ == "__main__":
    app.run(debug=True)