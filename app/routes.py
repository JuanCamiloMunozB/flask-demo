from flask import Blueprint, request, render_template, jsonify, session
from app.models.betting_adviser import BettingAdviser

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/select_sport', methods=['POST'])
def select_sport():
    data = request.get_json()
    sport = data.get('sport', '').lower()

    if sport not in ['soccer', 'basketball']:
        return jsonify({'error': 'Invalid sport selected'}), 400

    # Guardar el deporte en sesión y reiniciar variables
    session['sport'] = sport
    session['facts'] = []
    session['finished'] = False

    # Inicializa el asesor de apuestas
    adviser = BettingAdviser(sport)
    first_question = adviser.get_betting_advice([])

    session['next_fact'] = first_question.get('next_fact', None)

    return jsonify({
        'message': f'Has seleccionado {sport.capitalize()}.',
        'next_message': first_question['message'],
    })

@main.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.get_json().get('message', '').strip()

    if 'sport' not in session:
        return jsonify({'message': 'Primero selecciona un deporte.', 'finished': False})

    if not user_input:
        return jsonify({'message': 'Por favor responde la pregunta para continuar.', 'finished': False})

    if session.get('finished'):
        return jsonify({'message': 'La conversación ya terminó. Selecciona otro deporte para comenzar de nuevo.', 'finished': True})

    sport = session['sport']
    adviser = BettingAdviser(sport)

    # Añadir la respuesta del usuario como un nuevo hecho
    facts = session.get('facts', [])
    next_fact_key = session.get('next_fact')

    if next_fact_key:
        facts.append({next_fact_key: user_input})

    # Obtener siguiente pregunta o diagnóstico
    response = adviser.get_betting_advice(facts)

    session['facts'] = facts
    session['next_fact'] = response.get('next_fact')
    session['finished'] = response['is_final']

    return jsonify({
        'message': response['message'],
        'finished': response['is_final'],
        'next_message': 'Puedes seleccionar otro deporte para una nueva recomendación.' if response['is_final'] else None
    })
