# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import jsonify, request, render_template, redirect

from datetime import datetime

from icecream import ic

from app.comment_parser import parse_comment
from app.db_funcs import (get_current_activity_comment, 
                          set_activity, 
                          add_log, 
                          get_logs_object,
                          get_activities_object,
                          get_log_tree_object,
                          get_log_dict,
                          edit_log as db_edit_log)
from app.util import get_time_span
from app import app, default_log_types



@app.route('/')
def index():
    date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', date=date)


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    comment = parse_comment(data['log-comment'])
    # state commands have no comment string, so they only change the state
    if comment.state_command:
        set_activity(comment.parent_id)
    else:
        add_log(comment, data.get('log-type'))
    return redirect('/')


@app.route('/get_logs', methods=['GET'])
def get_logs():
    time_span = get_time_span(request.args)
    ic(time_span)
    data = get_logs_object(time_span=time_span)
    return jsonify(data)


@app.route('/get_log_types', methods=['GET'])
def get_log_types():
    return jsonify(default_log_types)


@app.route('/current_activity', methods=['GET'])
def get_current_activity():
    comment = get_current_activity_comment()
    return jsonify(comment or 'no current task')


@app.route('/get_activity_history', methods=['GET'])
def get_state_history():
    time_span = get_time_span(request.args)

    data = get_activities_object(time_span=time_span)
    return jsonify(data)


@app.route('/get_log_tree', methods=['GET'])
def get_log_tree():
    time_span = get_time_span(request.args)
    tree = get_log_tree_object(time_span=time_span)
    return render_template('components/tree_view.html', log_tree=tree)


# @app.route('/get_logs_v2', methods=['GET'])
# def get_logs_v2():
#     return redirect('/get_logs')


@app.route('/log/<log_id>', methods=['GET'])
def get_log(log_id):
    log = get_log_dict(log_id)
    return jsonify(log)


@app.route('/edit_log/<log_id>', methods=['POST', 'GET'])
def edit_log(log_id):
    # if GET, return the edit log popup
    if request.method == 'GET':
        log = get_log_dict(log_id)
        log['log_types'] = [l_type['log_type'] for l_type in default_log_types]
        log['log_id'] = log_id
        return render_template('popups/edit_log.html', **log)
    # if POST, edit the log and return success or failure
    data = request.get_json(log_id)
    try:
        comment = parse_comment(data['comment'])
        log_id = data['log_id']
        default_log_type = data['log_type']
        parent_id = data['parent_id']
        db_edit_log(log_id, comment, default_log_type, parent_id)
        return jsonify('success')
    except Exception as e:
        ic(e)
        return jsonify(str(e))


@app.route('/test_route', methods=['GET'])
def test_route():  
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)
