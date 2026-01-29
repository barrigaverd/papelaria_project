from run import app

@app.route('/dashboard')
    @login_required # Isso garante que só logados entrem
    def dashboard():
        return render_template('dashboard.html')