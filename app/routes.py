# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import jsonify, request, redirect

from datetime import datetime

from icecream import ic

from .lib.comment_parser import parse_comment
from .lib.db_funcs import (set_activity, 
                          add_log, 
                          get_logs_object,
                          get_activities_object,
                          get_log_tree_object,
                          get_log_dict,
                          edit_log as db_edit_log,
                          get_current_tree_data,
                          get_current_activity_log_dict,
                          get_promoted_logs_object)
from .lib.util import get_time_span
from .lib.rendering import (render_log_tree,
                            render_log_table,
                            render_center_tile,
                            render_index,
                            render_edit_log)
from . import app, default_log_types

# enable/disable ic here
#ic.disable()

@app.route('/')
def index():
    date = datetime.now().strftime('%Y-%m-%d')
    time_span = get_time_span({'target_date': date})
    tree_data = get_log_tree_object(time_span)
    table_data = get_logs_object(time_span)
    current_tree_data = get_current_tree_data()
    active_log = get_current_activity_log_dict()

    return render_index(tree_data, table_data, current_tree_data, active_log)


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
    current_tree_data = get_current_tree_data()
    current_tree = render_log_tree(current_tree_data)
    current_activity_log = get_current_activity_log_dict()
    return render_center_tile(current_tree, current_activity_log)


@app.route('/promoted_activity', methods=['GET'])
def get_promoted_activity():
    promoted_tree_data = get_promoted_logs_object()
    promoted_tree = render_log_tree(promoted_tree_data)
    current_activity_log = get_current_activity_log_dict()
    return render_center_tile(promoted_tree, current_activity_log)


@app.route('/get_activity_history', methods=['GET'])
def get_state_history():
    time_span = get_time_span(request.args)

    data = get_activities_object(time_span=time_span)
    return jsonify(data)


@app.route('/log_tree', methods=['GET'])
def get_log_tree():
    time_span = get_time_span(request.args)
    tree = get_log_tree_object(time_span=time_span)
    return render_log_tree(tree)


@app.route('/log_table', methods=['GET'])
def get_log_table():
    time_span = get_time_span(request.args)
    logs = get_logs_object(time_span=time_span)
    return render_log_table(logs)


@app.route('/log/<log_id>', methods=['GET'])
def get_log(log_id):
    log = get_log_dict(log_id)
    return jsonify(log)


@app.route('/edit_log/<log_id>', methods=['POST', 'GET'])
def edit_log(log_id):
    # if GET, return the edit log popup
    if request.method == 'GET':
        log = get_log_dict(log_id)

        return render_edit_log(log)
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


if __name__ == '__main__':
    app.run(debug=True)
