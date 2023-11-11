from flask import render_template

from .. import default_log_types

from typing import List

def render_log_tree(log_tree):
    return render_template('components/tree_view.html', log_tree=log_tree)


def render_log_table(logs):
    return render_template('components/table_view.html', log_table=logs)


def render_legend():
    return render_template('components/type_legend.html', log_types=default_log_types)


def render_type_dropdown(dropdown_id):
    return render_template('components/type_dropdown.html', 
                           dropdown_id=dropdown_id, 
                           log_types=default_log_types,
                           default_log_type=default_log_types[0])


def render_center_tile(display_html: str, active_log: dict) -> str:

    return render_template('components/current_activity.html', 
                           current_tree=display_html,
                           current_activity=active_log.get('comment', ''),
                           current_activity_type=active_log.get('log_type', 'None'))


def render_index(tree_data: List[dict], table_data: List[dict], current_tree_data: List[dict], active_log: dict) -> str: 
    log_tree = render_log_tree(tree_data)
    log_table = render_log_table(table_data)
    legend = render_legend()
    type_dropdown = render_type_dropdown('log-type-dropdown')
    current_tree = render_log_tree(current_tree_data)
    current_activity = render_center_tile(current_tree, active_log)
    return render_template('index.html', 
                           log_tree=log_tree, 
                           log_table=log_table, 
                           type_legend=legend,
                           type_dropdown=type_dropdown,
                           current_activity=current_activity)


def render_edit_log(log_data: dict) -> str:
    type_dropdown = render_type_dropdown('edit-log-type-dropdown')
    return render_template('popups/edit_log.html', 
                           log_id=log_data.get('id'),
                           parent_id=log_data.get('parent_id'),
                           log_types=default_log_types,
                           comment=log_data.get('comment'),
                           type_dropdown=type_dropdown)