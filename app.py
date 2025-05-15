from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

SAVE_DIR = 'saved_designs'
UPLOAD_DIR = 'uploads'
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

sizes = ["Small", "Medium", "Large"]
fabrics = ["Air Cool", "Dry Fit", "Cotton"]
cuts = ["NBA", "V-Neck", "Sleeveless"]

fabric_paths = {
    "Air Cool": "static/air_cool.jpg",
    "Dry Fit": "static/dry_fit.jpg",
    "Cotton": "static/cotton.jpg"
}

trace_paths = {
    "NBA": "static/jersey_trace.png",
    "V-Neck": "static/jersey_vcut.png",
    "Sleeveless": "static/jersey_sleeveless.png"
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        if username:
            session['username'] = username
            return redirect(url_for('design'))
        flash('Please enter a valid username.')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/design', methods=['GET', 'POST'])
def design():
    if 'username' not in session:
        return redirect(url_for('login'))

    saved_filename = None
    fabric_image = None

    if request.method == 'POST':
        username = session['username']
        size = request.form['size']
        fabric = request.form['fabric']
        cut = request.form['cut']
        file = request.files['design']

        fabric_image = fabric_paths.get(fabric)

        if file:
            design_path = os.path.join(UPLOAD_DIR, file.filename)
            file.save(design_path)

            design = Image.open(design_path).convert("RGBA").resize((300, 400))
            trace = Image.open(trace_paths[cut]).convert("RGBA").resize((300, 400))
            final = Image.alpha_composite(design, trace)

            saved_filename = f"{username}_{cut}_{fabric}_{size}.png"
            output_path = os.path.join(SAVE_DIR, saved_filename)
            final.save(output_path)

            flash(f'Design saved as {saved_filename}')
        else:
            flash('No design file uploaded.')
    else:
        fabric_image = fabric_paths.get(fabrics[0])

    return render_template('design.html',
                           username=session['username'],
                           sizes=sizes,
                           fabrics=fabrics,
                           cuts=cuts,
                           saved_filename=saved_filename,
                           fabric_image=fabric_image)

@app.route('/saved/<filename>')
def saved_file(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)