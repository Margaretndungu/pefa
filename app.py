from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# --------- Helper Functions ---------
def load_fellowships():
    """Load fellowships from JSON file"""
    try:
        with open('data/fellowships.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"name": "", "location": ""} for _ in range(30)]

def load_prayer_requests():
    """Load prayer requests from JSON file"""
    try:
        with open('data/prayer_requests.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_prayer_request(request_data):
    """Save a new prayer request to JSON"""
    requests = load_prayer_requests()
    requests.append(request_data)
    with open('data/prayer_requests.json', 'w') as f:
        json.dump(requests, f, indent=4)

def save_prayer_requests(all_requests):
    """Save all prayer requests to JSON"""
    with open('data/prayer_requests.json', 'w') as f:
        json.dump(all_requests, f, indent=4)

# --------- Routes ---------
@app.route('/')
def home():
    return render_template('splash.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/first-time')
def first_time():
    return render_template('first-time.html')

@app.route('/prayer-request', methods=['GET', 'POST'])
def prayer_request():
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')
        email = request.form.get('email', '')
        prayer_text = request.form.get('prayer_request', '')
        
        if prayer_text:
            prayer_data = {'name': name, 'email': email, 'request': prayer_text}
            save_prayer_request(prayer_data)
            return redirect(url_for('prayer_request'))
    
    requests = load_prayer_requests()
    return render_template('prayer-request.html', prayer_requests=requests)

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/fellowships')
def fellowships():
    fellowship_data = load_fellowships()
    return render_template('fellowships.html', fellowships=fellowship_data)

# --------- Admin Fellowships ---------
@app.route('/admin/fellowships', methods=['GET', 'POST'])
def admin_fellowships():
    fellowship_data = load_fellowships()

    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        save_row_index = request.form.get('save_row')

        # If a specific row was saved
        if save_row_index is not None:
            idx = int(save_row_index)
            fellowship_data[idx]['name'] = data['name'][idx]
            fellowship_data[idx]['location'] = data['location'][idx]
        else:
            # Save all rows
            fellowships = []
            for name, loc in zip(data['name'], data['location']):
                fellowships.append({"name": name, "location": loc})
            fellowship_data = fellowships

        # Save updated data to JSON
        with open('data/fellowships.json', 'w') as f:
            json.dump(fellowship_data, f, indent=4)

        return redirect(url_for('admin_fellowships'))

    return render_template('admin-fellowships.html', fellowships=fellowship_data)

# --------- Admin Prayer Requests ---------
@app.route('/admin/prayer-request', methods=['GET', 'POST'])
def admin_prayer_request():
    prayer_requests = load_prayer_requests()

    if request.method == 'POST':
        delete_index = request.form.get('delete_index')
        if delete_index is not None:
            delete_index = int(delete_index)
            if 0 <= delete_index < len(prayer_requests):
                prayer_requests.pop(delete_index)
                save_prayer_requests(prayer_requests)
            return redirect(url_for('admin_prayer_request'))

    return render_template('admin-prayer-request.html', prayer_requests=prayer_requests)

# --------- Run App ---------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

