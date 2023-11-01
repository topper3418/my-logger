# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import jsonify, request, render_template, redirect


from app.comment_parser import parse_comment
from app.db_funcs import (get_current_activity_comment, 
                          set_activity, 
                          add_log, 
                          get_logs_object,
                          get_activities_object,
                          get_log_tree_object)
from app.util import get_time_span
from app import app, default_log_types



@app.route('/')
def index():
    return render_template('index.html')


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
    return jsonify(tree)


@app.route('/get_logs_v2', methods=['GET'])
def get_logs_v2():
    time_span = get_time_span(request.args)

    data = get_logs_object(time_span=time_span)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
