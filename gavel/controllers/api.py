from gavel import app
import gavel.utils as utils
from gavel.models import *
from gavel.constants import *
import json
from flask import (
    request,
    session,
    jsonify,
    Response
)

@app.route('/api/test', methods=['GET'])
@utils.requires_auth
def api_test():
    return jsonify(
        test='Auth success'
    )

# Submit a project and create an annotator for that project
@app.route('/api/submit-project', methods=['POST'])
@utils.requires_auth
def api_submit_project():

        # Create item
        _item = Item(
            request.form['project_name'],
            request.form['project_location'],
            request.form['project_description'],
        )
        db.session.add(_item)

        # Flush item to generate a database id for it
        db.session.flush()

        # Create annotator
        _annotator = Annotator(
            'Project ' + str(_item.id) + ' annotator 1' ,
            request.form['team_email'],
            'Auto-generated annotator for project id: ' + str(_item.id)
        )
        # Add created project to ignore list
        _annotator.ignore.append(_item)
        db.session.add(_annotator)

        # Commit item and annotator to DB
        db.session.commit()

        return jsonify(
            status='success',
            message='Created project and annotator',
            data={
                'project_id': _item.id,
                'annotator_secret': _annotator.secret,
                'annotator_link': '/login/' + _annotator.secret,
            }
        )
# Submit a project and create an annotator for that project
@app.route('/api/edit-project', methods=['POST'])
@utils.requires_auth
def api_edit_project():
    item = Item.by_id(request.form['item_id'])
    if not item:
        return utils.user_error('Item %s not found ' % request.form['item_id'])
    if 'location' in request.form:
        item.location = request.form['location']
    if 'name' in request.form:
        item.name = request.form['name']
    if 'description' in request.form:
        item.description = request.form['description']
    db.session.commit()
    return jsonify(
        status='success',
        message='Edited item',
        data={
            'project_id': _item.id
        }
    )


def judging_open():
    return Setting.value_of(SETTING_CLOSED) == SETTING_TRUE

@app.route('/api/items.csv')
@utils.requires_auth
def item_dump():
    items = Item.query.order_by(desc(Item.mu)).all()
    data = [['Mu', 'Sigma Squared', 'Name', 'Location', 'Description', 'Active']]
    data += [[
        str(item.mu),
        str(item.sigma_sq),
        item.name,
        item.location,
        item.description,
        item.active
    ] for item in items]
    return Response(utils.data_to_csv_string(data), mimetype='text/csv')

@app.route('/api/annotators.csv')
@utils.requires_auth
def annotator_dump():
    annotators = Annotator.query.all()
    data = [['Name', 'Email', 'Description', 'Secret']]
    data += [[
        str(a.name),
        a.email,
        a.description,
        a.secret
    ] for a in annotators]
    return Response(utils.data_to_csv_string(data), mimetype='text/csv')

@app.route('/api/decisions.csv')
@utils.requires_auth
def decisions_dump():
    decisions = Decision.query.all()
    data = [['Annotator ID', 'Winner ID', 'Loser ID', 'Time']]
    data += [[
        str(d.annotator.id),
        str(d.winner.id),
        str(d.loser.id),
        str(d.time)
    ] for d in decisions]
    return Response(utils.data_to_csv_string(data), mimetype='text/csv')
