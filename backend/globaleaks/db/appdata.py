# -*- coding: UTF-8
# datainit.py: database initialization
#   ******************
import copy
import json
import os

from storm.expr import And, Not, In

from globaleaks import models
from globaleaks.orm import transact
from globaleaks.handlers.admin.field import db_create_field, db_update_field, db_import_fields
from globaleaks.rest import errors
from globaleaks.settings import GLSettings


def load_appdata():
    with file(GLSettings.appdata_file, 'r') as f:
        json_string = f.read()
        appdata_dict = json.loads(json_string)
        return appdata_dict


def load_default_questionnaires(store):
    appdata = store.find(models.ApplicationData).one()
    steps = appdata.default_questionnaire['steps']
    del appdata.default_questionnaire['steps']

    questionnaire = store.find(models.Questionnaire, models.Questionnaire.key == u'default').one()
    if questionnaire is None:
        questionnaire = models.db_forge_obj(store, models.Questionnaire, appdata.default_questionnaire)
    else:
        for step in questionnaire.steps:
            store.remove(step)

    for step in steps:
        f_children = step['children']
        del step['children']
        s = models.db_forge_obj(store, models.Step, step)
        db_import_fields(store, s, None, f_children)
        s.questionnaire_id = questionnaire.id


def load_default_fields(store):
    for fname in os.listdir(GLSettings.fields_path):
        fpath = os.path.join(GLSettings.fields_path, fname)
        with file(fpath, 'r') as f:
            json_string = f.read()
            field_dict = json.loads(json_string)
            old_field = store.find(models.Field, models.Field.key == field_dict['key']).one()

            if old_field is not None:
                field_dict['id'] = old_field.id
                store.remove(old_field)

            db_create_field(store, field_dict, None)


def db_update_appdata(store):
    # Load new appdata
    appdata_dict = load_appdata()

    # Drop old appdata
    store.find(models.ApplicationData).remove()

    # Load and setup new appdata
    store.add(models.ApplicationData(appdata_dict))

    load_default_questionnaires(store)
    load_default_fields(store)

    return appdata_dict


@transact
def update_appdata(store):
    return db_update_appdata(store)


def db_fix_fields_attrs(store):
    # Load the field attributes descriptors
    field_attrs = {}
    with file(GLSettings.field_attrs_file, 'r') as f:
        json_string = f.read()
        field_attrs = json.loads(json_string)

    # Get the list of keys
    uptodate_keys = []
    for k1 in field_attrs.keys():
        for k2 in field_attrs[k1].keys():
            field_attrs[k1][k2]['name'] = k2
            uptodate_keys.append(k2)

    # Remove keys that have been removed
    store.find(models.FieldAttr,
               Not(In(models.FieldAttr.name, uptodate_keys))).remove()

    # Add keys that have been added
    for field in store.find(models.Field):
        attrs = field_attrs.get(field.type, {})
        for attr_name in attrs.keys():
            if not store.find(models.FieldAttr,
                              And(models.FieldAttr.field_id == field.id,
                                  models.FieldAttr.name == attr_name)).one():

                field.attrs.add(models.db_forge_obj(store, models.FieldAttr,
                                                    attrs[attr_name]))
