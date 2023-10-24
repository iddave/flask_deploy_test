import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db
from .db import update_record
from .similarity import get_similar


bp = Blueprint('test_form', __name__, url_prefix='/test')


@bp.route('/qaform', methods = ('GET', 'POST'))
def get_question():
    result = []
    if request.method == 'GET':
        user_question = request.args.get('user_question')
        n_results = int(request.args.get('n_results', 5))
        percentage = request.args.get('percentage')
        error = None
        # print(f"error: {error}\n")
        if not user_question:
            error = 'Нужно вписать вопрос.'
        if error is None:
            print(f"inside if result: {error}\n")
            try:
                print(f"n = {n_results}")
                result = get_similar(user_question, percentage, n_results).to_dict(orient='records')
                print("\n", type(result), "\n")
            except Exception as e:
                print(f"что-то не так с запросом. Ошибка - {e}")
    session['result'] = result
    session['n_results'] = n_results
    session['user_question'] = user_question
    print(result, "\n")
    return render_template('test_form/qaform.html',
                           result=result,
                           input_question=user_question,
                           input_question_db=user_question,
                           n_result_value=n_results)


@bp.route('/add_question', methods = ('GET', 'POST'))
def add_question():
    result = session.get('result', [])
    n_results = session.get('n_results', 5)
    user_question = session.get('user_question', '')
    user_question_db = ''
    if request.method == 'POST':
        ans = request.form['answer_db']
        ans_link = request.form['answer_link_db']
        user_question_db = request.form['user_question_db']
        user_question_db = user_question_db if user_question_db != '' else user_question
        print(f"first qu from session: {session.get('user_question')}, userQ = {user_question}")
        db.insert_into_db(user_question_db, ans,  ans_link)
    return render_template('test_form/qaform.html',
                           result=result,
                           input_question=user_question,
                           input_question_db=user_question_db,
                           n_result_value=n_results)


@bp.route('/update_data', methods=['POST'])
def update_data():
    data = request.get_json()
    db.update_record(data)
    return jsonify({'message': 'Data updated successfully'})

@bp.route('/delete_record', methods=['DELETE'])
def delete_data():
    data = request.get_json()
    db.delete_data('QTable', 'QEmbeddings', data)
    db.delete_data('QTable_temp', 'QEmbeddings_temp', data)
    return jsonify({'message': 'Data updated successfully'})