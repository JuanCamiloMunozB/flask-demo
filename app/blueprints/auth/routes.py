from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from .forms import RegisterForm, LoginForm
from app.services.auth_service import AuthService


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = AuthService.register_user(form.username.data, form.password.data)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        # Form validation errors
        return render_template('register.html', form=form), 400

    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = AuthService.authenticate_user(form.username.data, form.password.data)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('bot.index'))
        # Form validation errors
        return render_template('login.html', form=form), 400

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
