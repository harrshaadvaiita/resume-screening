from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename  # Add this import
from models import db, Candidate
from utils import evaluate_resume  # Make sure this is imported
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YourStrongRandomSecretKeyHere123!@#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_screening.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Keep the first initialization at the top
db.init_app(app)

# Configure upload folder
# Update the UPLOAD_FOLDER path and create if not exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'resumes')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

@app.route('/submit', methods=['POST'])
def submit_candidate():
    try:
        if 'resume' not in request.files:
            flash('No resume file uploaded', 'error')
            return redirect(url_for('index'))
            
        resume = request.files['resume']
        if resume.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('index'))

        if resume and allowed_file(resume.filename):
            filename = secure_filename(f"{request.form['name']}_{resume.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(filepath)

            new_candidate = Candidate(
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                age=int(request.form['age']),
                gender=request.form['gender'],
                role=request.form['role'],
                resume_filename=filename
            )
            
            try:
                db.session.add(new_candidate)
                db.session.commit()
                return render_template('success.html')
            except Exception as e:
                db.session.rollback()
                if 'UNIQUE constraint' in str(e):
                    flash('This email is already registered', 'error')
                else:
                    flash('Database error occurred', 'error')
                return redirect(url_for('index'))
                
    except Exception as e:
        flash('Error submitting application. Please try again.', 'error')
        print(f"Error: {str(e)}")  # For debugging
        return redirect(url_for('index'))

# Add this helper function
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Remove this duplicate initialization
# Initialize database
# db.init_app(app)  # <- Remove this line

# Selector credentials (move to secure storage in production)
selectors = {'admin': 'pass'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply')
def apply():
    return render_template('candidate_form.html')

@app.route('/selector', methods=['GET', 'POST'])
def selector_login():
    if request.method == 'POST':
        selector_id = request.form['selector_id']
        password = request.form['password']
        if selectors.get(selector_id) == password:
            session['selector'] = selector_id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('selector_login.html')

@app.route('/dashboard')
def dashboard():
    if 'selector' not in session:
        return redirect(url_for('selector_login'))
    candidates = Candidate.query.all()
    return render_template('selector_dashboard.html', candidates=candidates)

@app.route('/evaluate/<int:id>')
def evaluate(id):
    if 'selector' not in session:
        return redirect(url_for('selector_login'))

    try:
        candidate = Candidate.query.get_or_404(id)
        path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.resume_filename)
        
        if not os.path.exists(path):
            flash('Resume file not found', 'error')
            return redirect(url_for('dashboard'))
            
        score = evaluate_resume(path, candidate.role)
        candidate.score = score
        db.session.commit()
        flash(f'Resume evaluated successfully. Score: {score}', 'success')
        
    except Exception as e:
        flash(f'Error evaluating resume: {str(e)}', 'error')
        
    return redirect(url_for('dashboard'))

@app.route('/evaluate_all')
def evaluate_all():
    if 'selector' not in session:
        return redirect(url_for('selector_login'))
    candidates = Candidate.query.filter_by(score=None).all()
    for candidate in candidates:
        try:
            path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.resume_filename)
            score = evaluate_resume(path, candidate.role)
            candidate.score = score
        except Exception as e:
            flash(f'Error evaluating {candidate.name}: {str(e)}', 'error')
    db.session.commit()
    flash('All resumes evaluated', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('selector', None)
    return redirect(url_for('selector_login'))

@app.route('/score_view')
@app.route('/score_view/<role>')
def score_view(role='all'):
    if 'selector' not in session:
        return redirect(url_for('selector_login'))
    
    if role == 'all':
        candidates = Candidate.query.all()
    else:
        candidates = Candidate.query.filter_by(role=role).all()
    
    return render_template('score_view.html', candidates=candidates, selected_role=role)

@app.route('/top_scores')
@app.route('/top_scores/<role>')
def top_scores(role='all'):  # Set default value to 'all'
    if role == 'clear':
        return redirect(url_for('top_scores', role='all'))
    if 'selector' not in session:
        return redirect(url_for('selector_login'))
    
    query = Candidate.query.filter(Candidate.score.isnot(None))
    
    if role != 'all':
        query = query.filter_by(role=role)
    
    candidates = query.order_by(Candidate.score.desc()).limit(10).all()
    return render_template('top_scores.html', top=candidates, selected_role=role)

@app.route('/delete_candidate/<int:id>')
def delete_candidate(id):
    if 'selector' not in session:
        return redirect(url_for('selector_login'))
    try:
        candidate = Candidate.query.get_or_404(id)
        # Delete the resume file
        if candidate.resume_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.resume_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        # Delete from database
        db.session.delete(candidate)
        db.session.commit()
        flash('Candidate deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting candidate: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    if request.method == 'POST':
        email = request.form.get('email')
        candidate = Candidate.query.filter_by(email=email).first()
        
        if candidate is None:
            flash('No application found with this email', 'error')
            return redirect(url_for('check_status'))
        
        # Don't set score to 0.0, let the template handle None values
        return render_template('status.html', candidate=candidate)
    
    return render_template('check_status.html')


@app.route('/clear_all')
def clear_all():
    if 'selector' not in session:
        return redirect(url_for('selector_login'))
    try:
        # Delete all resume files
        candidates = Candidate.query.all()
        for candidate in candidates:
            if candidate.resume_filename:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.resume_filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # Delete all records from database
        Candidate.query.delete()
        db.session.commit()
        flash('All candidates and resumes cleared successfully', 'success')
    except Exception as e:
        flash(f'Error clearing candidates: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_all')
def delete_all():
    try:
        db.session.query(Candidate).delete()
        db.session.commit()
        flash('All resumes have been deleted successfully', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while deleting resumes', 'error')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
