import os
import subprocess
import shlex
from flask import Flask, render_template, request, redirect, url_for, flash
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
    # Pass an empty output so the template doesn't break on first load
    return render_template('index.html', status=status, output=None, selected_script=None)

@app.route('/execute', methods=['POST'])
@login_required
def execute():
    script_name = request.form.get('script')
    if not script_name:
        flash("Error: No script selected.", "error")
        return redirect(url_for('index'))

    # Base command
    command_list = ['bash', script_name]

    # --- Build arguments based on the selected script ---
    # Official Proxy
    if script_name == 'MTProtoProxyOfficialInstall.sh':
        port = request.form.get('official_port')
        secret = request.form.get('official_secret')
        tag = request.form.get('official_tag')
        workers = request.form.get('official_workers')

        if port: command_list.extend(['--port', port])
        if secret: command_list.extend(['--secret', secret])
        if tag: command_list.extend(['--tag', tag])
        if workers: command_list.extend(['--workers', workers])

    # Python Proxy
    elif script_name == 'MTProtoProxyInstall.sh':
        action = request.form.get('python_action')
        username = request.form.get('python_username')
        secret = request.form.get('python_secret')
        
        if action and action in ['4', '5']: # Add or Revoke User
            command_list.append(action)
            if username:
                command_list.append(username)
                if action == '4' and secret: # Only add secret for 'add' action
                    command_list.append(secret)
        elif action:
             command_list.append(action)


    # Golang (MTG) Proxy
    elif script_name == 'MTGInstall.sh':
        action = request.form.get('mtg_action')
        if action:
            command_list.append(action)

    # For manual commands or other scripts
    else:
        manual_args = request.form.get('manual_args')
        if manual_args:
            command_list.extend(shlex.split(manual_args))
    
    # --- Execute the command ---
    output = ""
    try:
        process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd())
        stdout, stderr = process.communicate(timeout=300)
        
        output = f"--- STDOUT ---\n{stdout}\n\n--- STDERR ---\n{stderr}"
        if process.returncode != 0:
            flash(f"Command finished with an error (Code: {process.returncode}). Check the output.", "error")
        else:
            flash("Command executed successfully!", "success")

    except subprocess.TimeoutExpired:
        output = "Error: The command took too long to execute and was terminated."
        flash(output, "error")
    except Exception as e:
        output = f"An error occurred while trying to run the command: {str(e)}"
        flash(output, "error")

    status = get_services_status()
    return render_template('index.html', status=status, output=output, selected_script=script_name)


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
            if not os.path.exists(f"/etc/systemd/system/{service_file}.service"):
                status[name] = "Not Installed"
                continue
            
            result = subprocess.run(['systemctl', 'is-active', service_file], capture_output=True, text=True, check=False)
            status[name] = "Active" if result.returncode == 0 else "Inactive"
        except Exception:
            status[name] = "Error Checking"
    return status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
