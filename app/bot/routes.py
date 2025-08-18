from flask import request, render_template, jsonify, session as flask_session, current_app
from flask_login import login_required, current_user
from app.bot.models.betting_adviser import BettingAdviser
from app.extensions import db
from app.models import ChatSession, ChatMessage
from . import bot

@bot.route('/')
@login_required
def index():
    return render_template('index.html')


@bot.route('/select_sport', methods=['POST'])
@login_required
def select_sport():
    try:
        data = request.get_json() or {}
        sport = (data.get('sport') or '').lower()

        if sport not in ['soccer', 'basketball']:
            return jsonify({'error': 'Invalid sport selected'}), 400

        # Estado en sesión (Flask)
        flask_session['sport'] = sport
        flask_session['facts'] = []
        flask_session['finished'] = False

        # Primera pregunta del asesor
        adviser = BettingAdviser(sport)
        first_question = adviser.get_betting_advice([])
        flask_session['next_fact'] = first_question.get('next_fact')

        # Crear sesión de chat persistente
        chat_sess = ChatSession(
            user_id=current_user.id,
            sport=sport,
            title=f"{sport.capitalize()} • {getattr(current_user, 'username', 'usuario')}"
        )
        db.session.add(chat_sess)
        db.session.flush()  # obtenemos id sin cerrar la transacción

        # Mensajes iniciales del asistente
        confirm_text = f'Has seleccionado {sport.capitalize()}.'
        initial_assistant_text = first_question['message']

        db.session.add(ChatMessage(session_id=chat_sess.id, role='assistant', content=confirm_text))
        db.session.add(ChatMessage(session_id=chat_sess.id, role='assistant', content=initial_assistant_text))
        db.session.commit()

        return jsonify({
            'message': confirm_text,
            'next_message': initial_assistant_text,
            'session_id': chat_sess.id
        }), 200

    except Exception as e:
        db.session.rollback()
        # Esto imprime el traceback completo en los logs de Render
        current_app.logger.exception("Error en /bot/select_sport")
        # Devolvemos JSON (para que el frontend no intente parsear HTML)
        return jsonify({'error': 'server_error'}), 500

@bot.route('/get_response', methods=['POST'])
@login_required
def get_bot_response():
    payload = request.get_json() or {}
    user_input = (payload.get('message') or '').strip()
    req_session_id = payload.get('session_id')

    if 'sport' not in flask_session:
        return jsonify({'message': 'Primero selecciona un deporte.', 'finished': False})

    if not user_input:
        return jsonify({'message': 'Por favor responde la pregunta para continuar.', 'finished': False})

    if flask_session.get('finished'):
        return jsonify({'message': 'La conversación ya terminó. Selecciona otro deporte para comenzar de nuevo.', 'finished': True})

    sport = flask_session['sport']
    adviser =  BettingAdviser(sport)

    # === NUEVO: resolver/crear la sesión de chat persistente ===
    chat_sess = None
    if req_session_id:
        chat_sess = ChatSession.query.filter_by(id=req_session_id, user_id=current_user.id).first()
        if not chat_sess:
            return jsonify({'message': 'Sesión no encontrada o no pertenece al usuario.', 'finished': False}), 404
    else:
        # Si el front aún no envía session_id, recupera la última sesión activa del usuario y deporte actual
        chat_sess = (ChatSession.query
                     .filter_by(user_id=current_user.id, sport=sport, is_active=True)
                     .order_by(ChatSession.updated_at.desc())
                     .first())
        if not chat_sess:
            # Crea una nueva para no romper flujo
            chat_sess = ChatSession(
                user_id=current_user.id,
                sport=sport,
                title=f"{sport.capitalize()} • {getattr(current_user, 'username', 'usuario')}"
            )
            db.session.add(chat_sess)
            db.session.commit()

    # === Guardar mensaje del usuario ===
    db.session.add(ChatMessage(session_id=chat_sess.id, role='user', content=user_input))
    db.session.commit()

    # === Tu lógica original con facts/next_fact ===
    facts = flask_session.get('facts', [])
    next_fact_key = flask_session.get('next_fact')

    if next_fact_key:
        facts.append({next_fact_key: user_input})

    response = adviser.get_betting_advice(facts)

    flask_session['facts'] = facts
    flask_session['next_fact'] = response.get('next_fact')
    flask_session['finished'] = response['is_final']

    assistant_text = response['message']

    # === Guardar respuesta del asistente ===
    db.session.add(ChatMessage(session_id=chat_sess.id, role='assistant', content=assistant_text))
    db.session.commit()

    # Si terminó, marca la sesión como no activa y con ended_at
    if response['is_final']:
        chat_sess.is_active = False
        from sqlalchemy import func
        chat_sess.ended_at = db.func.now()
        db.session.commit()

    # Mantener estructura original; si el front quiere, puede usar session_id
    return jsonify({
        'message': assistant_text,
        'finished': response['is_final'],
        'next_message': 'Puedes seleccionar otro deporte para una nueva recomendación.' if response['is_final'] else None,
        'session_id': chat_sess.id
    })

# === NUEVOS ENDPOINTS DE HISTORIAL ===

@bot.route('/history', methods=['GET'])
@login_required
def history():
    sessions = (ChatSession.query
                .filter_by(user_id=current_user.id)
                .order_by(ChatSession.updated_at.desc())
                .limit(50)
                .all())
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
    s = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not s:
        return jsonify({'error': 'Sesión no encontrada'}), 404

    msgs = (ChatMessage.query
            .filter_by(session_id=s.id)
            .order_by(ChatMessage.created_at.asc())
            .all())

    payload = [{
        'role': m.role,
        'content': m.content,
        'created_at': m.created_at.isoformat() if m.created_at else None
    } for m in msgs]

    return jsonify({
        'session': {
            'id': s.id,
            'title': s.title,
            'sport': s.sport,
            'is_active': s.is_active
        },
        'messages': payload
    })
