# -*- coding: utf-8 -*-
# API handling upload/delete of users/contexts picture
import base64

from globaleaks import models
from globaleaks.handlers.base import BaseHandler
from globaleaks.orm import transact

model_map = {
  'users': models.UserImg,
  'contexts': models.ContextImg
}


def db_get_model_img(session, tid, obj_key, obj_id):
    model = model_map[obj_key]
    img =  session.query(model).filter(model.id == obj_id).one_or_none()
    if img is None:
        return ''
    else:
        return img.data


@transact
def get_model_img(session, tid, obj_key, obj_id):
    return db_get_model_img(session, tid, obj_key, obj_id)


@transact
def add_model_img(session, tid, obj_key, obj_id, data):
    model = model_map[obj_key]
    data = base64.b64encode(data)
    img = session.query(model).filter(model.id == obj_id).one_or_none()
    if img is None:
        session.add(model({'id': obj_id, 'data': data}))
    else:
        img.data = data


@transact
def del_model_img(session, tid, obj_key, obj_id):
    model = model_map[obj_key]
    session.query(model).filter(model.id == obj_id).delete(synchronize_session='fetch')


class ModelImgInstance(BaseHandler):
    check_roles = 'admin'
    invalidate_cache = True
    upload_handler = True

    def post(self, obj_key, obj_id):
        sf = self.state.get_tmp_file_by_path(self.uploaded_file['path'])
        with sf.open('r') as encrypted_file:
            data = encrypted_file.read()

        return add_model_img(self.request.tid, obj_key, obj_id, data)

    def delete(self, obj_key, obj_id):
        return del_model_img(self.request.tid, obj_key, obj_id)
