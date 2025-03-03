from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import math
import requests
from sqlalchemy import func
from sqlalchemy.orm import aliased

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logistics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # For flash messages
db = SQLAlchemy(app)



class Admin(db.Model):
    __tablename__ = 'admin'
    keyID = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), nullable=True, unique=True)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

class COORUser(db.Model):
    __tablename__ = 'coor_user'
    keyID = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(100))  # Optional
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(100), nullable=False, unique=True)
    telegram_chat_id = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    

class Container(db.Model):
    __tablename__ = 'container'
    containerID = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    coor_user_id = db.Column(db.Integer, db.ForeignKey('coor_user.keyID'), nullable=False)
    dimensions = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Stores tags as a comma-separated string
    description = db.Column(db.Text)
    origin_location = db.Column(db.String(100))
    destination_location = db.Column(db.String(100))
    date_of_departure = db.Column(db.DateTime, nullable=True)
    date_of_arrival = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.String(20), nullable=False, default="Unmatched")  # Changed to String
    flexidate_tolerance = db.Column(db.Integer, nullable=True)  # Tolerance in days
    constituent_cargo = db.relationship('Cargo', backref='container', lazy=True)

class Cargo(db.Model):
    __tablename__ = 'cargo'
    cargoID = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    coor_user_id = db.Column(db.Integer, db.ForeignKey('coor_user.keyID'), nullable=False)
    dimensions = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Stores tags as a comma-separated string
    description = db.Column(db.Text)
    origin_location = db.Column(db.String(100))
    destination_location = db.Column(db.String(100))
    date_of_departure = db.Column(db.DateTime, nullable=True)
    date_of_arrival = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.String(20), nullable=False, default="Unmatched")  # Changed to String
    flexidate_tolerance = db.Column(db.Integer, nullable=True)  # Tolerance in days
    container_id = db.Column(db.Integer, db.ForeignKey('container.containerID'), nullable=True)  # Nullable to allow for unmatched cargo

class Dispute(db.Model):
    __tablename__ = 'dispute'
    disputeID = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-increment primary key
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    dispute_plaintiff = db.Column(db.Integer, db.ForeignKey('coor_user.keyID'), nullable=False)
    involved_users = db.Column(db.String(200))  # Comma-separated COOR user IDs
    description = db.Column(db.Text, nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey('container.containerID'), nullable=True)  # Optional
    cargoID = db.Column(db.Integer, nullable=True)  # Optional
    coor_user_id = db.Column(db.Integer, db.ForeignKey('coor_user.keyID'), nullable=False)




# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for Cargo Dashboard
@app.route('/User login page')
def User_login_page():
    return render_template('User login page.html')

# Route for Cargo Dashboard
@app.route('/PSA login page')
def PSA_login_page():
    return render_template('PSA login page.html')
# Route for Cargo Dashboard

@app.route('/Registration page')
def Registration_page():
    return render_template('Registration page.html')

@app.route('/PSA Dash Board')
def PSA_Dash_Board():
    return render_template('PSA Dash Board.html')

@app.route('/PSA_active_container')
def PSA_active_container():
    return render_template('PSA Active Container.html')

@app.route('/PSA_Unmatched_container')
def PSA_Unmatched_container():
    return render_template('PSA Unmatched Container.html')

@app.route('/PSA_History_container')
def PSA_History_container():
    return render_template('PSA History Container.html')

@app.route('/PSA_active_cargo')
def PSA_active_cargo():
    return render_template('PSA Active Cargo.html')

@app.route('/PSA_Unmatched_cargo')
def PSA_Unmatched_cargo():
    return render_template('PSA Unmatched Cargo.html')

@app.route('/PSA_Histroy_cargo')
def PSA_History_cargo():
    return render_template('PSA History Cargo.html')

@app.route('/Cargo_DashBoard')
def Cargo_DashBoard():
    return render_template('Cargo DashBoard.html')

@app.route('/Cargo_Booking')
def Cargo_Booking():
    return render_template('Cargo Booking.html')

@app.route('/Cargo Info')
def Cargo_Info():
    return render_template('Cargo Info.html')

@app.route('/Cargo Disputes')
def Cargo_Disputes():
    return render_template('Cargo Disputes.html')

@app.route('/Container_DashBoard')
def Container_DashBoard():
    return render_template('Container DashBoard.html')

@app.route('/Container_Booking')
def Container_Booking():
    return render_template('Container Booking .html')

@app.route('/Container Info')
def Container_Info():
    return render_template('Container Info .html')

@app.route('/Container Disputes')
def Container_Disputes():
    return render_template('Container Disputes.html')


@app.route('/login', methods=['POST'])
def User_login():
    username = request.form['username']
    password = request.form['password']
    print(username, password)
    user_type = 'Container' if request.form.get('user_type') else 'Cargo'
    print(user_type)

    # Find the user in the Admin database
    admin = Admin.query.filter_by(username=username, password=password).first()

    if admin:
        # Store session details
        session['user_id'] = admin.keyID  # Corrected to use the instance's actual value
        session['username'] = admin.username  # Corrected to use the instance's actual value
        session['user_type'] = user_type

        # Redirect based on user type
        if user_type == 'Cargo':
            return redirect(url_for('Cargo_DashBoard'))
        elif user_type == 'Container':
            return redirect(url_for('Container_DashBoard'))
    else:
        flash('Invalid username or password!', 'danger')
        print('Invalid username or password!', 'danger')
        return redirect(url_for('User_login_page'))
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_type', None)
    flash('You have been logged out.')
    return redirect(url_for('User_login_page'))  # Redirect to login page

@app.route('/PSAlogin', methods=['POST'])
def PSA_login():
    # Retrieve form data
    employee_id = request.form['employee_id']
    username = request.form['username']
    password = request.form['password']

    # Debug print statements to verify inputs
    print(f"Username: {username}, Password: {password}, Employee ID: {employee_id}")

    # Query the Admin table to find the user by employee_id, username, and password
    admin = Admin.query.filter_by(employee_id=employee_id, username=username, password=password).first()

    # Check if the user exists
    if admin:
        # Check if the user type is 'PSA'
        if admin.user_type == 'PSA':
            flash('Login successful!', 'success')
            return redirect(url_for('PSA_Dash_Board'))  # Redirect to PSA dashboard
        else:
            # If user exists but not of type 'PSA', show error
            flash('You are not authorized to access this page!', 'danger')
            return redirect(url_for('User_login_page'))
    else:
        # If no matching user found, show error
        flash('Invalid username, password, or employee ID!', 'danger')
        print('Invalid username, password, or employee ID!', 'danger')
        return redirect(url_for('User_login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = 'Container' if request.form.get('user_type') else 'Cargo'
        gender = request.form['gender']

        # Password validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Create a new Admin object
        new_admin = Admin(
            name=full_name,
            username=username,
            password=password,
            user_type=user_type,
            gender=gender,
            email=email
        )

        try:
            # Add the new admin to the database
            db.session.add(new_admin)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('User_login_page'))  # Redirect to a home page or login page
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/get-all-containers', methods=['GET'])
def get_all_containers():
    # Filter containers that are in transit
    containers = Container.query.filter_by(status="In Transit").all()
    container_list = []

    for container in containers:
        container_list.append({
            'containerID': container.containerID,
            'name': container.name,
            'quantity': 'N/A',  # Adjust according to your model logic
            'date_created': container.date_created.strftime('%Y-%m-%d'),
            'date_completed': container.date_completed.strftime('%Y-%m-%d') if container.date_completed else None,
            'date_of_departure': container.date_of_departure.strftime('%Y-%m-%d') if container.date_of_departure else None,
            'date_of_arrival': container.date_of_arrival.strftime('%Y-%m-%d') if container.date_of_arrival else None,
            'status': container.status,
            'origin_location': container.origin_location,
            'destination_location': container.destination_location,
            'description': container.description,
        })

    return jsonify({'containers': container_list})

@app.route('/get-all-containers-Delivered', methods=['GET'])
def get_all_containers_Delivered():
    # Filter containers that are in transit
    containers = Container.query.filter_by(status="Delivered").all()
    container_list = []

    for container in containers:
        container_list.append({
            'containerID': container.containerID,
            'name': container.name,
            'quantity': 'N/A',  # Adjust according to your model logic
            'date_created': container.date_created.strftime('%Y-%m-%d'),
            'date_completed': container.date_completed.strftime('%Y-%m-%d') if container.date_completed else None,
            'date_of_departure': container.date_of_departure.strftime('%Y-%m-%d') if container.date_of_departure else None,
            'date_of_arrival': container.date_of_arrival.strftime('%Y-%m-%d') if container.date_of_arrival else None,
            'status': container.status,
            'origin_location': container.origin_location,
            'destination_location': container.destination_location,
            'description': container.description,
        })

    return jsonify({'containers': container_list})

@app.route('/get-all-containers-Pending', methods=['GET'])
def get_all_containers_Pending():
    # Filter containers that are in transit
    containers = Container.query.filter_by(status="Pending").all()
    container_list = []

    for container in containers:
        container_list.append({
            'containerID': container.containerID,
            'name': container.name,
            'quantity': 'N/A',  # Adjust according to your model logic
            'date_created': container.date_created.strftime('%Y-%m-%d'),
            'date_completed': container.date_completed.strftime('%Y-%m-%d') if container.date_completed else None,
            'date_of_departure': container.date_of_departure.strftime('%Y-%m-%d') if container.date_of_departure else None,
            'date_of_arrival': container.date_of_arrival.strftime('%Y-%m-%d') if container.date_of_arrival else None,
            'status': container.status,
            'origin_location': container.origin_location,
            'destination_location': container.destination_location,
            'description': container.description,
        })

    return jsonify({'containers': container_list})


@app.route('/get-cargo-details/<int:container_id>', methods=['GET'])
def get_cargo_details(container_id):
    # Fetch cargo related to the specific container ID
    cargo_items = Cargo.query.filter_by(container_id=container_id).all()
    print(cargo_items)

    # Prepare the cargo data for response
    cargo_list = []
    
    for cargo in cargo_items:
        cargo_list.append({
            'product_name': cargo.name,
            'product_id': cargo.cargoID,
            'quantity': f"{random.randint(500, 1000)} kg",  # Adjust if actual quantity data exists
            'dimension': cargo.dimensions,
            'tags': cargo.tags,
            'flexidate_tolerance': cargo.flexidate_tolerance
        })
    print(cargo_list)

    # Return the cargo data as JSON
    return jsonify({'cargo': cargo_list})


@app.route('/get-complaints-details/<int:container_id>', methods=['GET'])
def get_complaints_details(container_id):
    # Fetch complaints related to the specific container ID
    complaints_items = Dispute.query.filter_by(container_id=container_id).all()

    # Prepare the complaints data for response
    complaints_list = []
    
    for complaint in complaints_items:
        complaints_list.append({
            'complaint_id': complaint.disputeID,
            'description': complaint.description,
            'date': complaint.date_created.strftime('%Y-%m-%d')  # Assuming date_created field exists
        })

    # Return the complaints data as JSON
    return jsonify({'complaints': complaints_list})

@app.route('/get-all-cargo', methods=['GET'])
def get_all_cargo():
    # Fetch only the cargo items that are 'In Progress'
    cargo_items = Cargo.query.filter_by(status='In Progress').all()

    # Prepare the cargo data for response
    cargo_list = []
    for cargo in cargo_items:
        cargo_list.append({
            'cargoID': cargo.cargoID,
            'date_created': cargo.date_created.strftime('%Y-%m-%d'),
            'date_completed': cargo.date_completed.strftime('%Y-%m-%d') if cargo.date_completed else None,
            'status': cargo.status,
            'name': cargo.name,
            'dimensions': cargo.dimensions,
            'tags': cargo.tags,
            'additional_description': cargo.description,
            'origin_location': cargo.origin_location,
            'destination_location': cargo.destination_location,
            'date_of_departure': cargo.date_of_departure.strftime('%Y-%m-%d') if cargo.date_of_departure else None,
            'date_of_arrival': cargo.date_of_arrival.strftime('%Y-%m-%d') if cargo.date_of_arrival else None,
            'completed': 'Yes' if cargo.completed else 'No',
            'flexidate_tolerance': cargo.flexidate_tolerance,
            'assigned_container': cargo.container_id  # Assuming container_id is a foreign key
        })

    # Return the filtered cargo data as JSON
    return jsonify({'cargo': cargo_list})


@app.route('/get-all-cargo-Delivered', methods=['GET'])
def get_all_cargo_Delivered():
    # Fetch only the cargo items that are 'In Progress'
    cargo_items = Cargo.query.filter_by(status='Completed').all()
    # Prepare the cargo data for response
    cargo_list = []
    for cargo in cargo_items:
        cargo_list.append({
            'cargoID': cargo.cargoID,
            'date_created': cargo.date_created.strftime('%Y-%m-%d'),
            'date_completed': cargo.date_completed.strftime('%Y-%m-%d') if cargo.date_completed else None,
            'status': cargo.status,
            'name': cargo.name,
            'dimensions': cargo.dimensions,
            'tags': cargo.tags,
            'additional_description': cargo.description,
            'origin_location': cargo.origin_location,
            'destination_location': cargo.destination_location,
            'date_of_departure': cargo.date_of_departure.strftime('%Y-%m-%d') if cargo.date_of_departure else None,
            'date_of_arrival': cargo.date_of_arrival.strftime('%Y-%m-%d') if cargo.date_of_arrival else None,
            'completed': 'Yes' if cargo.completed else 'No',
            'flexidate_tolerance': cargo.flexidate_tolerance,
            'assigned_container': cargo.container_id  # Assuming container_id is a foreign key
        })

    # Return the filtered cargo data as JSON
    return jsonify({'cargo': cargo_list})

@app.route('/get-all-cargo-pending', methods=['GET'])
def get_all_cargo_pending():
    # Fetch only the cargo items that are 'In Progress'
    cargo_items = Cargo.query.filter_by(status='Pending').all()
    # Prepare the cargo data for response
    cargo_list = []
    for cargo in cargo_items:
        cargo_list.append({
            'cargoID': cargo.cargoID,
            'date_created': cargo.date_created.strftime('%Y-%m-%d'),
            'date_completed': cargo.date_completed.strftime('%Y-%m-%d') if cargo.date_completed else None,
            'status': cargo.status,
            'name': cargo.name,
            'dimensions': cargo.dimensions,
            'tags': cargo.tags,
            'additional_description': cargo.description,
            'origin_location': cargo.origin_location,
            'destination_location': cargo.destination_location,
            'date_of_departure': cargo.date_of_departure.strftime('%Y-%m-%d') if cargo.date_of_departure else None,
            'date_of_arrival': cargo.date_of_arrival.strftime('%Y-%m-%d') if cargo.date_of_arrival else None,
            'completed': 'Yes' if cargo.completed else 'No',
            'flexidate_tolerance': cargo.flexidate_tolerance,
            'assigned_container': cargo.container_id  # Assuming container_id is a foreign key
        })

    # Return the filtered cargo data as JSON
    return jsonify({'cargo': cargo_list})

@app.route('/submit-cargo', methods=['POST'])
def submit_cargo():
    # Ensure that the user is logged in
    if 'user_id' not in session:
        return jsonify({'message': 'User is not logged in.'}), 403  # Unauthorized access

    data = request.json

    try:
        # Get the user_id from the session
        user_id = session['user_id']
        
        # Retrieve the Admin user based on user_id
        admin_user = Admin.query.filter_by(keyID=user_id).first()
        
        if not admin_user:
            return jsonify({'message': 'Admin user not found.'}), 404
        
        # Check if user exists in COORUser based on the provided email or admin's keyID
        existing_user = COORUser.query.filter_by(email=data.get('business_email')).first()

        if existing_user:
            # User already exists, use their keyID
            coor_user_id = existing_user.keyID
        else:
            # User doesn't exist, create a new COORUser and assign the same keyID from Admin user
            new_user = COORUser(
                keyID=admin_user.keyID,  # Assign the same keyID from Admin user
                date_created=datetime.utcnow(),
                name=admin_user.name,  # Autofill from Admin database
                business_name=data.get('business_name', ''),
                contact_number=data.get('phone_number'),
                email=data.get('business_email'),
                telegram_chat_id=data.get('chat_id'),  # If applicable
                is_active=True  # Assuming all newly created users are active
            )
            db.session.add(new_user)
            db.session.commit()

            # After committing, the new user's keyID will be the same as Admin's
            coor_user_id = new_user.keyID

        # Create new cargo instance with received data and coor_user_id
        new_cargo = Cargo(
            date_created=datetime.utcnow(),
            status='Pending',  # Assuming all newly created cargo starts as 'In Progress'
            name=data.get('name'),
            coor_user_id=coor_user_id,  # Assign the user ID from COORUser
            dimensions=f"{data['dimensions']['length']}x{data['dimensions']['width']}x{data['dimensions']['height']}",
            weight=data.get('weight'),
            tags=', '.join(data.get('tags', [])),  # Join tags array into a comma-separated string
            description=data.get('additional_comments', ''),
            origin_location=data.get('origin'),
            destination_location=data.get('destination'),
            date_of_departure=datetime.strptime(data.get('send_off_date'), '%Y-%m-%d') if data.get('send_off_date') else None,
            date_of_arrival=datetime.strptime(data.get('arrival_date'), '%Y-%m-%d') if data.get('arrival_date') else None,
            completed='Unmatched',  # Default to 'No'
            flexidate_tolerance=data.get('flexidate_tolerance', 0)  # Default tolerance to 0
        )

        # Save the new cargo to the database
        db.session.add(new_cargo)
        db.session.commit()

        return jsonify({'message': 'Cargo and user data saved successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error saving cargo data: {e}")
        return jsonify({'message': 'Failed to save cargo and user data.'}), 500

@app.route('/get-user-cargo', methods=['GET'])
def get_user_cargo():
    if 'user_id' not in session:
        return jsonify({'message': 'User is not logged in.'}), 403  # Unauthorized access

    user_id = session['user_id']

    try:
        # Fetching all cargo entries that match the logged-in user's keyID in the COORUser table
        cargo_entries = Cargo.query.join(COORUser, COORUser.keyID == Cargo.coor_user_id).filter(COORUser.keyID == user_id).all()
        cargo_list = [{
            'cargoID': cargo.cargoID,
            'date_created': cargo.date_created.strftime('%Y-%m-%d'),
            'date_completed': cargo.date_completed.strftime('%Y-%m-%d') if cargo.date_completed else 'N/A',
            'status': cargo.status,
            'dimensions': cargo.dimensions,
            'weight': cargo.weight,
            'tags': cargo.tags,
            'description': cargo.description,
            'origin_location': cargo.origin_location,
            'destination_location': cargo.destination_location,
            'date_of_departure': cargo.date_of_departure.strftime('%Y-%m-%d') if cargo.date_of_departure else 'N/A',
            'date_of_arrival': cargo.date_of_arrival.strftime('%Y-%m-%d') if cargo.date_of_arrival else 'N/A',
            'flexidate_tolerance': cargo.flexidate_tolerance
        } for cargo in cargo_entries]

        return jsonify(cargo_list), 200

    except Exception as e:
        print(f"Error fetching cargo data: {e}")
        return jsonify({'message': 'Failed to fetch cargo data.'}), 500
    
@app.route('/delete-cargo', methods=['POST'])
def delete_cargo():
    data = request.get_json()
    cargo_ids = data.get('cargoIDs', [])
    print("Received cargo IDs for deletion:", cargo_ids)  # Print received cargo IDs

    response = {'status': 'success'}
    if not cargo_ids:
        print("No cargo IDs provided for deletion.")
        response['status'] = 'error'
        response['message'] = 'No cargo IDs provided'
        return jsonify(response)

    try:
        query = Cargo.query.filter(Cargo.cargoID.in_(cargo_ids))
        print(f"Prepared to execute delete query: {str(query)}")  # Print the query
        deleted_count = query.delete(synchronize_session=False)
        db.session.commit()
        print(f"Number of cargo entries deleted: {deleted_count}")  # Print number of deletions
        if deleted_count == 0:
            response['status'] = 'warning'
            response['message'] = 'No entries found with provided IDs'
    except Exception as e:
        db.session.rollback()
        response['status'] = 'error'
        response['message'] = str(e)
        print(f"Failed to delete cargo: {e}")  # Print error message
    finally:
        db.session.close()

    return jsonify(response)

@app.route('/emission-savings')
def emission_savings():
    containers = db.session.query(Container).all()
    total_baseline_emissions = 0.0
    total_optimized_emissions = 0.0
    for container in containers:
    
        results = calculate_emission_savings(container.origin_location, container.destination_location)
        total_baseline_emissions += results['baseline_emissions']
        total_optimized_emissions += results['optimized_emissions']
    
    emissions_saved = total_baseline_emissions - total_optimized_emissions
    savings_percentage = (emissions_saved / total_baseline_emissions) * 100 if total_baseline_emissions > 0 else 0


    # Return the results as a JSON response
    return jsonify({
        'emissions_saved': emissions_saved,
        'savings_percentage': savings_percentage
    })

@app.route('/sustainability-comparison')
def sustainability_comparison():
    try:
        # Get the time interval from query parameters (e.g., daily, weekly, monthly)
        time_interval = request.args.get('interval', 'daily')
        print(f"Requested Time Interval: {time_interval}")

        # Query to get all data from Container along with origin, destination, and date/time
        results = db.session.query(
            Container.date_created.label('date'),  # Raw date from the database
            Container.origin_location,
            Container.destination_location
        ).join(Cargo).all()  # Removed group_by clause

        # Log the raw results for debugging
        print("Raw Results from Database:")
        for result in results:
            print(result)

        # Initialize empty lists for x and y coordinates
        x_coords = []  # For dates
        y_coords = []  # For emissions saved

        # Process results individually
        for date, origin, destination in results:
            # Calculate emission savings for each container
            emission_results = calculate_emission_savings(origin, destination)

            # Append the x and y coordinates to their respective lists
            x_coords.append(date)  # Append the date for x-axis
            y_coords.append(emission_results['emissions_saved'])  # Append emissions saved for y-axis

            print(f"Date: {date}, Origin: {origin}, Destination: {destination}, Emissions Saved: {emission_results['emissions_saved']}")

        # Prepare data for response in the format expected for a chart
        response_data = {
            'x': x_coords,  # X coordinates (dates)
            'y': y_coords,  # Y coordinates (emissions saved)
        }

        print("Processed Data for Response:")
        print(response_data)

        return jsonify(response_data)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500



@app.route('/get-filed-by-me', methods=['GET'])
def get_filed_by_me():
    # Check if the user is logged in
    keyID = session.get('user_id')  # Extract 'user_id' from session
    if not keyID:
        return jsonify({'error': 'User not logged in'}), 401

    # Retrieve disputes filed by the logged-in user
    disputes = Dispute.query.filter_by(dispute_plaintiff=keyID).all()

    # Format the disputes into a list of dictionaries
    dispute_list = [{
        'date_created': d.date_created.strftime('%Y-%m-%d'),
        'status': d.status,
        'dispute_plaintiff': d.dispute_plaintiff,
        'involved_users': d.involved_users,
        'description': d.description,
        'container_id': d.container_id or 'N/A'
    } for d in disputes]

    return jsonify({'filed_by_me': dispute_list}), 200

@app.route('/get-filed-against-me', methods=['GET'])
def get_filed_against_me():
    # Check if the user is logged in
    keyID = session.get('user_id')  # Extract 'user_id' from session
    if not keyID:
        return jsonify({'error': 'User not logged in'}), 401

    # Use an alias for the Cargo table to join it with the Dispute table
    cargo_alias = aliased(Cargo)

    # Query to join Dispute with Cargo and filter by cargoID and coor_user_id
    disputes = (
        db.session.query(Dispute)
        .join(cargo_alias, Dispute.cargoID == cargo_alias.cargoID)
        .filter(cargo_alias.coor_user_id == keyID)  # Ensure it's filed against this user
        .all()
    )

    # Format the disputes into a list of dictionaries
    dispute_list = [{
        'date_created': d.date_created.strftime('%Y-%m-%d'),
        'status': d.status,
        'dispute_plaintiff': d.dispute_plaintiff,
        'involved_users': d.involved_users,
        'description': d.description,
        'cargoID': d.cargoID
    } for d in disputes]

    return jsonify({'filed_against_me': dispute_list}), 200

@app.route('/file-dispute', methods=['POST'])
def file_dispute():
    try:
        # Ensure the user is logged in by checking the session
        if 'user_id' not in session:
            return jsonify({'error': 'User not logged in'}), 401

        # Extract the logged-in user's keyID from the session
        coor_user_id = session['user_id']

        # Extract form data from the request
        data = request.get_json()
        dispute = Dispute(
            dispute_plaintiff=coor_user_id,  # Use the logged-in user's keyID
            involved_users=data['involved_user'],  # Comma-separated COOR user IDs
            description=data['description'],
            container_id=data.get('container_id'),  # Optional field
            status='Filed',  # Default status for new disputes
            coor_user_id=coor_user_id  # Use the same user as coor_user_id
        )

        # Save the new dispute to the database
        db.session.add(dispute)
        db.session.commit()

        return jsonify({'message': 'Dispute filed successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/submit-container', methods=['POST'])
def submit_container():
    if 'user_id' not in session:
        return jsonify({'message': 'User is not logged in.'}), 403

    data = request.json

    try:
        # Extract date strings from the request
        send_off_date_str = data.get('send_off_date')
        arrival_date_str = data.get('arrival_date')

        # Safely parse the dates
        send_off_date = (
            datetime.fromisoformat(send_off_date_str)
            if isinstance(send_off_date_str, str) else None
        )
        arrival_date = (
            datetime.fromisoformat(arrival_date_str)
            if isinstance(arrival_date_str, str) else None
        )

        # Retrieve the user from session
        user_id = session['user_id']
        admin_user = Admin.query.filter_by(keyID=user_id).first()

        # Check if the COORUser exists or create a new one
        coor_user = COORUser.query.filter_by(keyID=admin_user.keyID).first()
        if not coor_user:
            coor_user = COORUser(
                keyID=admin_user.keyID,
                date_created=datetime.utcnow(),
                name=admin_user.name,
                business_name=data.get('business_name', ''),
                contact_number=data.get('phone_number'),
                email=data.get('business_email'),
                is_active=True
            )
            db.session.add(coor_user)
            db.session.commit()

        # Handle tags as a comma-separated string
        tags = ', '.join(data.get('tags', []))

        # Create new container booking
        new_container = Container(
            date_created=datetime.utcnow(),
            status='In Progress',
            name=data.get('name'),
            coor_user_id=coor_user.keyID,
            dimensions=f"{data['length']}x{data['width']}x{data['height']}",
            tags=tags,
            description=data.get('comments', ''),
            origin_location=data.get('origin'),
            destination_location=data.get('destination'),
            date_of_departure=send_off_date,
            date_of_arrival=arrival_date,
            completed='Unmatched',
            flexidate_tolerance=data.get('flexidate', 0)
        )

        # Save the container booking
        db.session.add(new_container)
        db.session.commit()

        return jsonify({'message': 'Container booking saved successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error saving container data: {e}")
        return jsonify({'message': 'Failed to save container booking.'}), 500

@app.route('/delete-container', methods=['POST'])
def delete_container():
    data = request.get_json()
    container_ids = data.get('containerIDs', [])
    print("Received container IDs for deletion:", container_ids)

    response = {'status': 'success'}
    if not container_ids:
        response['status'] = 'error'
        response['message'] = 'No container IDs provided'
        return jsonify(response)

    try:
        query = Container.query.filter(Container.containerID.in_(container_ids))
        deleted_count = query.delete(synchronize_session=False)
        db.session.commit()
        print(f"Number of containers deleted: {deleted_count}")
        if deleted_count == 0:
            response['status'] = 'warning'
            response['message'] = 'No entries found with provided IDs'
    except Exception as e:
        db.session.rollback()
        response['status'] = 'error'
        response['message'] = str(e)
        print(f"Failed to delete containers: {e}")
    finally:
        db.session.close()

    return jsonify(response)

@app.route('/get-user-containers', methods=['GET'])
def get_user_containers():
    if 'user_id' not in session:
        return jsonify({'message': 'User is not logged in.'}), 403

    user_id = session['user_id']

    try:
        # Fetch containers that belong to the logged-in user
        containers = Container.query.filter_by(coor_user_id=user_id).all()
        container_list = [{
            'containerID': container.containerID,
            'date_created': container.date_created.strftime('%Y-%m-%d'),
            'date_completed': container.date_completed.strftime('%Y-%m-%d') if container.date_completed else 'N/A',
            'status': container.status,
            'dimensions': container.dimensions,
            'tags': container.tags,
            'description': container.description,
            'origin_location': container.origin_location,
            'destination_location': container.destination_location,
            'date_of_departure': container.date_of_departure.strftime('%Y-%m-%d') if container.date_of_departure else 'N/A',
            'date_of_arrival': container.date_of_arrival.strftime('%Y-%m-%d') if container.date_of_arrival else 'N/A',
            'flexidate_tolerance': container.flexidate_tolerance
        } for container in containers]

        return jsonify(container_list), 200

    except Exception as e:
        print(f"Error fetching container data: {e}")
        return jsonify({'message': 'Failed to fetch container data.'}), 500


@app.route('/file-container-dispute', methods=['POST'])
def file_container_dispute():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging print

        # Ensure the user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in.'}), 401

        # Ensure CargoID is provided
        cargo_id = data.get('cargoID')
        if not cargo_id:
            return jsonify({'error': 'CargoID is required.'}), 400

        # Verify if the provided CargoID exists
        cargo = Cargo.query.filter_by(cargoID=cargo_id).first()
        if not cargo:
            return jsonify({'error': 'Invalid CargoID.'}), 400

        # Create a new dispute entry
        new_dispute = Dispute(
            dispute_plaintiff=user_id,  # Use logged-in user ID
            involved_users=data['involved_user'],
            description=data['description'],
            cargoID=cargo_id,  # Assign CargoID
            container_id=None,  # Leave Container ID empty
            coor_user_id=user_id,  # Assign the same user ID as coor_user_id
            status='Pending'
        )
        db.session.add(new_dispute)
        db.session.commit()

        print("Dispute filed successfully.")  # Debugging print
        return jsonify({'message': 'Container dispute filed successfully!'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error filing dispute: {e}")  # Print the exact error
        return jsonify({'error': str(e)}), 500

    
@app.route('/get-container-disputes-by-me', methods=['GET'])
def get_container_disputes_by_me():
    # Ensure the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Query for disputes with CargoID and no ContainerID, filed by the logged-in user
    disputes = Dispute.query.filter(
        Dispute.dispute_plaintiff == user_id,
        Dispute.container_id == None,  # No ContainerID
        Dispute.cargoID != None,        # Must have CargoID
        Dispute.coor_user_id == user_id  # coor_user_id matches session user ID
    ).all()

    # Prepare the data to be returned as JSON
    dispute_list = [{
        'date_created': d.date_created.strftime('%Y-%m-%d'),
        'status': d.status,
        'dispute_plaintiff': d.dispute_plaintiff,
        'involved_users': d.involved_users,
        'description': d.description,
        'cargo_id': d.cargoID  # Include CargoID
    } for d in disputes]

    return jsonify({'filed_by_me': dispute_list}), 200


@app.route('/get-container-disputes-against-me', methods=['GET'])
def get_container_disputes_against_me():
    user_id = session.get('user_id')  # Get the logged-in user's ID from the session
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Join Dispute, Container, and Cargo to find relevant disputes
    disputes = (
        db.session.query(Dispute)
        .join(Container, Dispute.container_id == Container.containerID, isouter=True)  # Optional join on Container
        .join(Cargo, Cargo.container_id == Container.containerID)  # Join with Cargo based on ContainerID
        .filter(Cargo.coor_user_id == user_id)  # Match with logged-in user's ID
        .all()
    )

    # Format the disputes into a list of dictionaries for response
    dispute_list = [{
        'date_created': d.date_created.strftime('%Y-%m-%d'),
        'status': d.status,
        'dispute_plaintiff': d.dispute_plaintiff,
        'involved_users': d.involved_users,
        'description': d.description,
        'cargo_id': d.cargoID  # Include CargoID for reference
    } for d in disputes]

    return jsonify({'filed_against_me': dispute_list}), 200

def parse_date(date_str):
    """Helper function to safely parse ISO date strings."""
    try:
        if date_str and isinstance(date_str, str):
            return datetime.fromisoformat(date_str)
    except ValueError as e:
        print(f"Invalid date format: {e}")
    return None  # Return None if the date is invalid or missing
    
def calculate_emission_savings(origin, destination):
    # Constants
    EMISSION_RATE_PER_KM = 0.1  # kg CO₂ per km per container
    BASELINE_UTILIZATION = 0.5   # Assume containers are only 50% utilized without optimization

    # Step 1: Retrieve data from the database
    total_baseline_emissions = 0
    total_optimized_emissions = 0

    # Step 2: Calculate emissions for each container
    distance = calculate_distance(origin, destination)
    cargos_in_container = 10  # Number of cargos packed

    # Assume max capacity is 10 cargos per container for this example
    max_capacity = 10

     # Baseline emissions (assuming 50% utilization)
    baseline_emissions = (distance * EMISSION_RATE_PER_KM) / BASELINE_UTILIZATION
    total_baseline_emissions += baseline_emissions

    # Optimized emissions based on actual utilization
    utilization_ratio = cargos_in_container / max_capacity
    optimized_emissions = distance * EMISSION_RATE_PER_KM * utilization_ratio
    total_optimized_emissions += optimized_emissions

    # Step 3: Calculate savings and percentage
    emissions_saved = total_baseline_emissions - total_optimized_emissions
    savings_percentage = (emissions_saved / total_baseline_emissions) * 100

    # Step 4: Return results
    return {
        'baseline_emissions': total_baseline_emissions,
        'optimized_emissions': total_optimized_emissions,
        'emissions_saved': emissions_saved,
        'savings_percentage': savings_percentage
    }

def get_lat_long(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': location,
        'key': 'AIzaSyDFlQy2yBwug1vMuffg7cG-RfsBqSTwXDA'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        # Extracting the latitude and longitude
        lat_long = data['results'][0]['geometry']['location']
        return lat_long['lat'], lat_long['lng']
    else:
        raise Exception("Error in API response: {}".format(data.get('error_message', 'No error message provided')))

def haversine(lat1, lon1, lat2, lon2):
    r = 6371  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)

    c = 2 * math.asin(math.sqrt(a))
    distance = r * c  # Distance in kilometers
    return distance

def calculate_distance(origin, destination):
    # Get latitude and longitude for both locations
    lat1, lon1 = get_lat_long(origin)
    lat2, lon2 = get_lat_long(destination)

    # Calculate the distance using Haversine formula
    distance = haversine(lat1, lon1, lat2, lon2)
    return distance









@app.route('/get-dispute-stats', methods=['GET'])
def get_dispute_stats():
    user_id = session.get('user_id')  # Get user ID from session
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Query all disputes related to the user
    disputes = Dispute.query.filter(Dispute.coor_user_id == user_id).all()

    # Initialize counters for each status
    total_disputes = len(disputes)
    active_count = sum(1 for d in disputes if d.status.lower() == 'active')
    solved_count = sum(1 for d in disputes if d.status.lower() == 'solved')
    filed_count = sum(1 for d in disputes if d.status.lower() == 'filed')

    # Calculate percentages
    active_percentage = (active_count / total_disputes) * 100 if total_disputes else 0
    solved_percentage = (solved_count / total_disputes) * 100 if total_disputes else 0
    filed_percentage = (filed_count / total_disputes) * 100 if total_disputes else 0

    # Return the stats as JSON
    return jsonify({
        'total_disputes': total_disputes,
        'active_count': active_count,
        'solved_count': solved_count,
        'filed_count': filed_count,
        'active_percentage': active_percentage,
        'solved_percentage': solved_percentage,
        'filed_percentage': filed_percentage
    }), 200


@app.route('/get-cargo-stats', methods=['GET'])
def get_cargo_stats():
    user_id = session.get('user_id')  # Get the logged-in user's ID from session
    if not user_id:
        return jsonify({'error': 'User not logged in.'}), 401

    # Query cargo entries related to the logged-in user
    cargo_entries = Cargo.query.filter_by(coor_user_id=user_id).all()

    # Initialize counters for each status
    total_cargo = len(cargo_entries)
    active_cargo = sum(1 for c in cargo_entries if c.status.lower() == 'in progress')
    unmatched_cargo = sum(1 for c in cargo_entries if c.status.lower() == 'pending')
    successful_cargo = sum(1 for c in cargo_entries if c.status.lower() == 'delieverd')

    # Calculate percentages
    active_percentage = (active_cargo / total_cargo) * 100 if total_cargo else 0
    unmatched_percentage = (unmatched_cargo / total_cargo) * 100 if total_cargo else 0
    successful_percentage = (successful_cargo / total_cargo) * 100 if total_cargo else 0

    # Return the stats as JSON
    return jsonify({
        'total_cargo': total_cargo,
        'active_cargo': active_cargo,
        'unmatched_cargo': unmatched_cargo,
        'successful_cargo': successful_cargo,
        'active_percentage': active_percentage,
        'unmatched_percentage': unmatched_percentage,
        'successful_percentage': successful_percentage
    }), 200

@app.route('/get-container-dispute-stats', methods=['GET'])
def get_container_dispute_stats():
    user_id = session.get('user_id')  # Get user ID from session
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    # Query all container-related disputes for the logged-in user
    disputes = (
        Dispute.query
        .join(Container, Dispute.container_id == Container.containerID)
        .filter(Container.coor_user_id == user_id)
        .all()
    )

    # Initialize counters for each status
    total_disputes = len(disputes)
    active_count = sum(1 for d in disputes if d.status.lower() == 'active')
    solved_count = sum(1 for d in disputes if d.status.lower() == 'solved')
    filed_count = sum(1 for d in disputes if d.status.lower() == 'filed')

    # Calculate percentages
    active_percentage = (active_count / total_disputes) * 100 if total_disputes else 0
    solved_percentage = (solved_count / total_disputes) * 100 if total_disputes else 0
    filed_percentage = (filed_count / total_disputes) * 100 if total_disputes else 0

    # Return the stats as JSON
    return jsonify({
        'total_disputes': total_disputes,
        'active_count': active_count,
        'solved_count': solved_count,
        'filed_count': filed_count,
        'active_percentage': active_percentage,
        'solved_percentage': solved_percentage,
        'filed_percentage': filed_percentage
    }), 200


if __name__ == "__main__":
    # with app.app_context():
    #     # Delete all records from the container table
    #     db.session.query(Container).delete()
    #     db.session.commit()
    # with app.app_context():
    #     generate_dummy_data()

    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    # with app.app_context():
    #     populate_database()
    app.run(debug=True)
    
    
    