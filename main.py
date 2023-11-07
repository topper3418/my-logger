# FILEPATH: /c:/Users/travi/OneDrive/Desktop/my-logger/main.py

from flask import jsonify, request, render_template, redirect

from datetime import datetime

from icecream import ic

from app.comment_parser import parse_comment
from app.db_funcs import (set_activity, 
                          add_log, 
                          get_logs_object,
                          get_activities_object,
                          get_log_tree_object,
                          get_log_dict,
                          edit_log as db_edit_log,
                          get_current_tree_data,
                          get_current_activity_comment)
from app.util import get_time_span
from app import app, default_log_types

# enable/disable ic here
#ic.disable()

@app.route('/')
def index():
    date = datetime.now().strftime('%Y-%m-%d')
    time_span = get_time_span({'target_date': date})

    tree_data = get_log_tree_object(time_span)
    table_data = get_logs_object(time_span)
    log_tree = render_template('components/tree_view.html', log_tree=tree_data)
    log_table = render_template('components/table_view.html', log_table=table_data)
    legend = render_template('components/type_legend.html', log_types=default_log_types)
    type_dropdown = render_template('components/type_dropdown.html', 
                                    log_types=default_log_types, 
                                    dropdown_id='log-type-dropdown',
                                    default_log_type=default_log_types[0])
    current_tree_data = get_current_tree_data()
    parent_id = current_tree_data[0]['parent_id']
    current_activity_comment = get_current_activity_comment()
    current_activity_type = current_tree_data[0]['log_type']
    current_tree = render_template('components/tree_view.html', log_tree=current_tree_data)
    current_activity = render_template('components/current_activity.html', 
                                       current_tree=current_tree,
                                       parent_id=parent_id,
                                       current_activity=current_activity_comment,
                                       current_activity_type=current_activity_type)
    return render_template('index.html', 
                           date=date, 
                           log_tree=log_tree, 
                           log_table=log_table, 
                           type_legend=legend,
                           type_dropdown=type_dropdown,
                           current_activity=current_activity)


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
    current_activity_comment = get_current_activity_comment()
    current_tree = render_template('components/tree_view.html', log_tree=current_tree_data)
    parent_id = current_tree_data[0]['parent_id']
    return render_template('components/current_activity.html', 
                           current_tree=current_tree,
                           parent_id=parent_id,
                           current_activity=current_activity_comment)


@app.route('/get_activity_history', methods=['GET'])
def get_state_history():
    time_span = get_time_span(request.args)

    data = get_activities_object(time_span=time_span)
    return jsonify(data)


@app.route('/log_tree', methods=['GET'])
def get_log_tree():
    time_span = get_time_span(request.args)
    tree = get_log_tree_object(time_span=time_span)
    return render_template('components/tree_view.html', log_tree=tree)


@app.route('/log_table', methods=['GET'])
def get_log_table():
    time_span = get_time_span(request.args)
    logs = get_logs_object(time_span=time_span)
    return render_template('components/table_view.html', log_table=logs)


@app.route('/log/<log_id>', methods=['GET'])
def get_log(log_id):
    log = get_log_dict(log_id)
    return jsonify(log)


@app.route('/edit_log/<log_id>', methods=['POST', 'GET'])
def edit_log(log_id):
    # if GET, return the edit log popup
    if request.method == 'GET':
        log = get_log_dict(log_id)
        log['log_types'] = default_log_types
        log['log_id'] = log_id
        type_dropdown = render_template('components/type_dropdown.html', 
                                        log_types=default_log_types,
                                        dropdown_id='edit-log-type-dropdown',
                                        default_log_type=log['log_type'])

        return render_template('popups/edit_log.html', 
                               log_id=log['log_id'],
                               parent_id=log['parent_id'],
                               log_types=default_log_types,
                               comment=log['comment'],
                               type_dropdown=type_dropdown)
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
