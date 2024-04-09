from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required,current_user
from .models import *
from datetime import datetime
views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home(): 
    if request.method == 'POST':
        # Check if the delete button was clicked
        if 'delete_appointment' in request.form:
            appointment_id = int(request.form['delete_appointment'])
            # Get the appointment to delete
            appointment = Appointment.query.get(appointment_id)
            # Check if the appointment exists and belongs to the current user
            if appointment and appointment.user_id == current_user.id:
                # Delete the appointment
                db.session.delete(appointment)
                db.session.commit()
                flash('Appointment deleted successfully', 'success')
            else:
                flash('You are not authorized to delete this appointment', 'error')
            # Redirect back to the home page
            return redirect(url_for('views.home'))

    # If it's a GET request or after deleting, retrieve and render appointments
    appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", user=current_user, appointments=appointments)

@views.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment(): 
    if request.method == 'POST':
        doctor = request.form.get('doctor')
        # Combine date and time input fields into a single datetime object
        appointment_datetime_str = request.form.get('date') + ' ' + request.form.get('time')
        appointment_datetime = datetime.strptime(appointment_datetime_str, '%Y-%m-%d %H:%M')
        
        # Check if the appointment datetime is in the past
        if appointment_datetime < datetime.now():
            flash('You cannot book appointments for past dates and times', 'error')
            return redirect(url_for('views.book_appointment'))

        user_id = current_user.id 
        
        # Check if there are any existing appointments at the same time
        existing_appointment = Appointment.query.filter_by(appointment_datetime=appointment_datetime).first()
        if existing_appointment:
            flash('Appointment at the same time already exists', 'error')
            return redirect(url_for('views.book_appointment'))

        # If no existing appointment and not in the past, proceed to create the new appointment
        new_appointment = Appointment(doctor_name=doctor, appointment_datetime=appointment_datetime, user_id=user_id)
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('views.home'))
    
    return render_template('book_appointment.html', user=current_user)