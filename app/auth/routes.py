from flask import request, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import RegisterForm, LoginForm
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from app.models import User


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User(username=form.username.data)
			user.set_password(form.password.data)
			db.session.add(user)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()
				form.username.errors.append('El nombre de usuario ya existe')
				return render_template('register.html', form=form), 400
			# Registro exitoso: redirigir al login
			return redirect(url_for('auth.login'))
		# En caso de errores de validación, renderizar la plantilla con el formulario
		return render_template('register.html', form=form), 400

	# GET: return form or template placeholder
	return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(username=form.username.data).first()
			if user and user.check_password(form.password.data):
				login_user(user)
				# Login exitoso: redirigir al index de main
				return redirect(url_for('bot.index'))
			# Credenciales inválidas: añadir error al campo password y re-renderizar
			form.password.errors.append('Credenciales inválidas')
			return render_template('login.html', form=form), 401
		# Errores de validación del formulario
		return render_template('login.html', form=form), 400

	return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('auth.login'))
