from flask import request, render_template, jsonify, session as flask_session, current_app
from flask_login import login_required, current_user
from app.bot.models.betting_adviser import BettingAdviser
from app.extensions import db
from app.models import ChatSession, ChatMessage
from . import bot
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

@bot.route('/')
@login_required
def index():
    return render_template('index.html')




@bot.route('/select_sport', methods=['POST'])
@login_required
def select_sport():
    try:
        data = request.get_json(silent=True) or {}
        sport = (data.get('sport') or data.get('message') or '').strip().lower()
        if not sport:
            return jsonify({'error': "missing_param", 'where': 'validate', 'detail': "Falta 'sport'"}), 400
        if sport not in ['soccer', 'basketball']:
            return jsonify({'error': "invalid_sport", 'where': 'validate'}), 400

        # ------- Estado de sesión HTTP --------
        flask_session['sport'] = sport
        flask_session['facts'] = []
        flask_session['finished'] = False

        # ------- Adviser (posible fallo por imports/torch/etc.) --------
        try:
            adviser = BettingAdviser(sport)
            first_question = adviser.get_betting_advice([]) or {}
            initial_assistant_text = (first_question.get('message') or '').strip() or \
                                     "Hola. ¿Sobre qué quieres apostar hoy?"
            flask_session['next_fact'] = first_question.get('next_fact')
        except Exception as e:
            current_app.logger.exception("Adviser error")
            # No derribemos la request por el adviser; seguimos con un mensaje por defecto
            initial_assistant_text = "Hola. ¿Sobre qué quieres apostar hoy?"

        # ------- DB PRECHECK (¿hay conexión?) --------
        try:
            db.session.execute(db.text("SELECT 1"))
        except OperationalError as e:
            current_app.logger.exception("DB connection error")
            return jsonify({'error': 'db_error', 'where': 'precheck'}), 500

        # ------- Persistir ChatSession + mensajes --------
        try:
            
            chat_sess = ChatSession(
                user_id=current_user.id,
                sport=sport,
                title=f"{sport.capitalize()} • {getattr(current_user, 'username', 'usuario')}"
            )
            db.session.add(chat_sess)
            db.session.flush()  # obtiene id

            confirm_text = f'Has seleccionado {sport.capitalize()}.'
            db.session.add(ChatMessage(session_id=chat_sess.id, role='assistant', content=confirm_text))
            db.session.add(ChatMessage(session_id=chat_sess.id, role='assistant', content=initial_assistant_text))
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.exception("DB integrity error")
            return jsonify({'error': 'db_integrity', 'where': 'commit'}), 500
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("DB SQLAlchemy error")
            return jsonify({'error': 'db_sqlalchemy', 'where': 'commit'}), 500

        return jsonify({
            'message': f'Has seleccionado {sport.capitalize()}.',
            'next_message': initial_assistant_text,
            'session_id': chat_sess.id
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error en /bot/select_sport (unexpected)")
        return jsonify({'error': 'server_error', 'where': 'unexpected'}), 500


@bot.route('/get_response', methods=['POST'])
@login_required
def get_bot_response():
    try:
        payload = request.get_json(silent=True) or {}
        user_input = (payload.get('message') or '').strip()
        req_session_id = payload.get('session_id')

        if not user_input:
            return jsonify({'message': 'Por favor responde la pregunta para continuar.', 'finished': False}), 400

        # 1) Resolver la sesión primero (FUENTE DE LA VERDAD)
        chat_sess = None
        if req_session_id:
            chat_sess = ChatSession.query.filter_by(id=req_session_id, user_id=current_user.id).first()
            if not chat_sess:
                return jsonify({'message': 'Sesión no encontrada o no pertenece al usuario.', 'finished': False}), 404
        else:
            # Si no enviaron session_id, tomamos la última activa del usuario
            chat_sess = (ChatSession.query
                         .filter_by(user_id=current_user.id, is_active=True)
                         .order_by(ChatSession.updated_at.desc())
                         .first())
            if not chat_sess:
                return jsonify({'message': 'Primero selecciona un deporte.', 'finished': False}), 400

        # 2) Determinar el deporte desde la sesión (no depender de flask_session)
        sport = chat_sess.sport
        if not sport:
            return jsonify({'message': 'Sesión sin deporte asociado.', 'finished': True}), 400

        # Mantener compatibilidad con tu lógica de "facts"
        flask_session['sport'] = sport

        # 3) Si la sesión ya terminó, corta acá
        if not chat_sess.is_active:
            return jsonify({
                'message': 'La conversación ya terminó. Selecciona otro deporte para comenzar de nuevo.',
                'finished': True,
                'session_id': chat_sess.id
            }), 200

        # 4) Guardar mensaje del usuario
        db.session.add(ChatMessage(session_id=chat_sess.id, role='user', content=user_input))
        db.session.commit()

        # 5) Preparar facts
        facts = flask_session.get('facts', [])
        next_fact_key = flask_session.get('next_fact')
        if next_fact_key:
            facts.append({next_fact_key: user_input})

        # 6) Adviser robusto
        try:
            adviser = BettingAdviser(sport)
            response = adviser.get_betting_advice(facts) or {}
        except Exception:
            current_app.logger.exception("Adviser error")
            response = {}

        assistant_text = (response.get('message') or 'Estoy procesando tu información...')
        is_final = bool(response.get('is_final'))
        next_fact = response.get('next_fact')

        # Actualizar estado de sesión HTTP (opcional / legacy)
        flask_session['facts'] = facts
        flask_session['next_fact'] = next_fact
        flask_session['finished'] = is_final

        # 7) Guardar respuesta del asistente y cerrar si aplica
        db.session.add(ChatMessage(session_id=chat_sess.id, role='assistant', content=assistant_text))
        if is_final:
            chat_sess.is_active = False
            chat_sess.ended_at = db.func.now()
        db.session.commit()

        return jsonify({
            'message': assistant_text,
            'finished': is_final,
            'next_message': 'Puedes seleccionar otro deporte para una nueva recomendación.' if is_final else None,
            'session_id': chat_sess.id
        }), 200

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error en /bot/get_response (unexpected)")
        return jsonify({'error': 'server_error', 'where': 'unexpected'}), 500

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
