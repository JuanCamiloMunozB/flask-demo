from flask import request, render_template, jsonify, session as flask_session
from flask_login import login_required, current_user
from . import bot
from app.services.betting_service import BettingService
from app.services.chat_service import ChatService
from app.core.extensions import db
from app.core.exceptions import ValidationError


@bot.route('/')
@login_required
def index():
    """Main bot interface."""
    return render_template('index.html')


@bot.route('/select_sport', methods=['POST'])
@login_required
def select_sport():
    """Select a sport and start a new betting session."""
    data = request.get_json(silent=True) or {}
    sport = (data.get('sport') or data.get('message') or '').strip().lower()
    
    if not sport:
        raise ValidationError("Falta 'sport'")
    
    # Validate sport using service
    betting_service = BettingService()
    if not betting_service.validate_sport(sport):
        raise ValidationError("Deporte no válido")

    # Set session state
    flask_session['sport'] = sport
    flask_session['facts'] = []
    flask_session['finished'] = False

    # Get initial advice
    first_question = betting_service.get_betting_advice(sport, [])
    initial_assistant_text = first_question.get('message', 'Hola. ¿Sobre qué quieres apostar hoy?')
    flask_session['next_fact'] = first_question.get('next_fact')

    # Database precheck
    db.session.execute(db.text("SELECT 1"))

    # Create chat session
    chat_session = ChatService.create_session(
        user_id=current_user.id,
        sport=sport,
        title=f"{sport.capitalize()} • {getattr(current_user, 'username', 'usuario')}"
    )
    
    confirm_text = f'Has seleccionado {sport.capitalize()}.'
    ChatService.add_message(chat_session.id, 'assistant', confirm_text)
    ChatService.add_message(chat_session.id, 'assistant', initial_assistant_text)

    return jsonify({
        'message': f'Has seleccionado {sport.capitalize()}.',
        'next_message': initial_assistant_text,
        'session_id': chat_session.id
    }), 200


@bot.route('/get_response', methods=['POST'])
@login_required
def get_bot_response():
    """Get bot response to user input."""
    payload = request.get_json(silent=True) or {}
    user_input = (payload.get('message') or '').strip()
    req_session_id = payload.get('session_id')

    if not user_input:
        return jsonify({'message': 'Por favor responde la pregunta para continuar.', 'finished': False}), 400

    # Get or validate session
    if req_session_id:
        chat_session = ChatService.get_session_by_id(req_session_id, current_user.id)
        if not chat_session:
            return jsonify({'message': 'Sesión no encontrada o no pertenece al usuario.', 'finished': False}), 404
    else:
        chat_session = ChatService.get_latest_active_session(current_user.id)
        if not chat_session:
            return jsonify({'message': 'Primero selecciona un deporte.', 'finished': False}), 400

    # Check if session is still active
    if not chat_session.is_active:
        return jsonify({
            'message': 'La conversación ya terminó. Selecciona otro deporte para comenzar de nuevo.',
            'finished': True,
            'session_id': chat_session.id
        }), 200

    # Save user message
    ChatService.add_message(chat_session.id, 'user', user_input)

    # Get sport from session
    sport = chat_session.sport
    flask_session['sport'] = sport

    # Prepare facts
    facts = flask_session.get('facts', [])
    next_fact_key = flask_session.get('next_fact')
    if next_fact_key:
        updated = False
        for fact in facts:
            if next_fact_key in fact:
                fact[next_fact_key] = user_input
                updated = True
                break
        if not updated:
            facts.append({next_fact_key: user_input})

    # Get betting advice
    betting_service = BettingService()
    response = betting_service.get_betting_advice(sport, facts)

    assistant_text = response.get('message', 'Estoy procesando tu información...')
    is_final = bool(response.get('is_final'))
    next_fact = response.get('next_fact')

    # Update session state
    flask_session['facts'] = facts
    flask_session['next_fact'] = next_fact
    flask_session['finished'] = is_final

    # Save assistant response and end session if final
    ChatService.add_message(chat_session.id, 'assistant', assistant_text)
    if is_final:
        ChatService.end_session(chat_session.id, current_user.id)

    return jsonify({
        'message': assistant_text,
        'finished': is_final,
        'next_message': 'Puedes seleccionar otro deporte para una nueva recomendación.' if is_final else None,
        'session_id': chat_session.id
    }), 200


@bot.route('/history', methods=['GET'])
@login_required
def history():
    """Get user's chat history."""
    sessions = ChatService.get_user_sessions(current_user.id)
    payload = [{
        'id': s.id,
        'title': s.title,
        'sport': s.sport,
        'is_active': s.is_active,
        'created_at': s.created_at.isoformat() if s.created_at else None,
        'updated_at': s.updated_at.isoformat() if s.updated_at else None,
        'ended_at': s.ended_at.isoformat() if s.ended_at else None
    } for s in sessions]
    return jsonify(payload)


@bot.route('/history/<int:session_id>', methods=['GET'])
@login_required
def history_session(session_id):
    """Get specific session history."""
    session = ChatService.get_session_by_id(session_id, current_user.id)
    if not session:
        return jsonify({'error': 'Sesión no encontrada'}), 404

    messages = ChatService.get_session_messages(session_id)
    payload = [{
        'role': m.role,
        'content': m.content,
        'created_at': m.created_at.isoformat() if m.created_at else None
    } for m in messages]

    return jsonify({
        'session': {
            'id': session.id,
            'title': session.title,
            'sport': session.sport,
            'is_active': session.is_active
        },
        'messages': payload
    })
