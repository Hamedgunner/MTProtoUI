import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Login Management ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
ADMIN_PASSWORD = os.environ.get('MTPROXY_PASSWORD', 'default_password')

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# --- Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            user = User(1)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    status = get_services_status()
    return render_template('index.html', status=status)

@app.route('/execute', methods=['POST'])
@login_required
def execute():
    script = request.form.get('script')
    args_str = request.form.get('args')
    
    if not script:
        return "Error: No script specified.", 400

    command = f"bash {script} {args_str}"
    
    # Using subprocess to run the command
    # NOTE: Running shell commands from a web app is a security risk.
    # This is simplified for this specific use case.
    try:
        # We use a pipe to capture output in a blocking way for simplicity
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=300) # 5-minute timeout
        
        output = f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}"
        
        # Re-fetch status after execution
        status = get_services_status()
        
        return render_template('index.html', output=output, status=status)

    except subprocess.TimeoutExpired:
        return render_template('index.html', output="Error: The command took too long to execute and was terminated.", status=get_services_status())
    except Exception as e:
        return render_template('index.html', output=f"An error occurred: {str(e)}", status=get_services_status())


def get_services_status():
    """Checks the status of all known proxy services."""
    services = {
        'Official': 'MTProxy',
        'Python': 'mtprotoproxy',
        'Golang (MTG)': 'mtg'
    }
    status = {}
    for name, service_file in services.items():
        try:
            # Check if the service file exists first
            if not os.path.exists(f"/etc/systemd/system/{service_file}.service"):
                 status[name] = "Not Installed"
                 continue
            
            # Check if the service is active
            result = subprocess.run(['systemctl', 'is-active', service_file], capture_output=True, text=True)
            if result.returncode == 0:
                status[name] = "Active"
            else:
                status[name] = "Inactive"
        except Exception:
            status[name] = "Error Checking"
            
    return status

if __name__ == '__main__':
    # This is for development only. Use Waitress in production.
    app.run(host='0.0.0.0', port=5001, debug=True)
