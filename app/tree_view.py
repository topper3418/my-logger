from app.models import Log, Activity, Comment, TimeSpan
from typing import List

from flask import render_template




def assemble_tree_view(logs: List[dict]) -> dict:
    """returns an html element representing the given log and its children"""
    # this is an array of nested dicts
    # loop through the top level dicts
    # the actual function for assembling the tree is recursive
    # I need templates for each element as well as the 