# -*- coding: utf-8
#
# Handlers implementing platform signup
import copy
from datetime import timedelta

from globaleaks import models
from globaleaks.handlers.admin.node import db_admin_serialize_node
from globaleaks.handlers.admin.notification import db_get_notification
from globaleaks.handlers.admin.tenant import db_create as db_create_tenant
from globaleaks.handlers.base import BaseHandler, new_session
from globaleaks.handlers.wizard import db_wizard
from globaleaks.models import config
from globaleaks.orm import transact
from globaleaks.rest import requests, errors, apicache
from globaleaks.utils.utility import datetime_to_ISO8601
from globaleaks.utils.security import generateRandomKey


def serialize_signup(signup):
    return {
        'name': signup.name,
        'surname': signup.surname,
        'email': signup.email,
        'subdomain': signup.subdomain,
        'activation_token': signup.activation_token,
        'registration_date': datetime_to_ISO8601(signup.registration_date)
    }


@transact
def signup(session, state, tid, request, language):
    node = config.ConfigFactory(session, 1, 'node')

    if not node.get_val(u'enable_signup'):
        raise errors.ForbiddenOperation

    request['activation_token'] = generateRandomKey(32)
    request['language'] = language

    signup = models.Signup(request)

    session.add(signup)

    session.flush()

    ret = {
        'signup': serialize_signup(signup),
        'activation_url': 'https://%s/#/activation?token=%s' % (node.get_val(u'rootdomain'), signup.activation_token),
        'expiration_date': datetime_to_ISO8601(signup.registration_date + timedelta(days=7))
    }

    template_vars = copy.deepcopy(ret)
    template_vars.update({
        'type': 'signup',
        'node': db_admin_serialize_node(session, 1, language),
        'notification': db_get_notification(session, 1, language),
    })

    state.format_and_send_mail(session, 1, {'mail_address': signup.email}, template_vars)

    return ret


@transact
def signup_activation(session, state, tid, token, language):
    node = config.ConfigFactory(session, 1, 'node')

    if not node.get_val(u'enable_signup'):
        raise errors.ForbiddenOperation

    signup = session.query(models.Signup).filter(models.Signup.activation_token == token).one_or_none()
    if signup is None:
        return {}

    if signup.tid is None:
        signup.tid = db_create_tenant(session, {'label': signup.subdomain,
                                                'subdomain': signup.subdomain}).id

        wizard = {
            'node_name': signup.subdomain,
            'admin_name': signup.name + ' ' + signup.surname,
            'admin_password': '',
            'admin_mail_address': signup.email,
            'receiver_name': signup.name + ' ' + signup.surname,
            'receiver_mail_address': signup.email,
            'profile': 'default',
            'enable_developers_exception_notification': True
        }

        db_wizard(session, state, signup.tid, wizard, False, language)

        template_vars = {
            'type': 'activation',
            'node': db_admin_serialize_node(session, 1, language),
            'notification': db_get_notification(session, 1, language),
            'signup': serialize_signup(signup),
            'activation_url': '',
            'expiration_date': datetime_to_ISO8601(signup.registration_date + timedelta(days=7))
        }

        state.format_and_send_mail(session, 1, {'mail_address': signup.email}, template_vars)

    if session.query(models.Tenant).filter(models.Tenant.id == signup.tid).one_or_none() is not None:
        admin = session.query(models.User).filter(models.User.tid == signup.tid, models.User.role == u'admin').one()
        admin.password_change_needed = False

        recipient = session.query(models.User).filter(models.User.tid == signup.tid, models.User.role == u'receiver').one()
        recipient.password_change_needed = False

        return {
            'platform_url': 'https://%s.%s' % (signup.subdomain, node.get_val(u'rootdomain')),
            'login_url': 'https://%s.%s/#/login' % (signup.subdomain, node.get_val(u'rootdomain')),
            'admin_login_url': 'https://%s.%s/#/login?token=%s' % (signup.subdomain, node.get_val(u'rootdomain'), admin.auth_token),
            'recipient_login_url': 'https://%s.%s/#/login?token=%s' % (signup.subdomain, node.get_val(u'rootdomain'), recipient.auth_token),
            'expiration_date': datetime_to_ISO8601(signup.registration_date + timedelta(days=7))
        }
    else:
        return {}


class Signup(BaseHandler):
    """
    Signup handler
    """
    check_roles = 'unauthenticated'
    invalidate_cache = True

    def post(self):
        request = self.validate_message(self.request.content.read(),
                                        requests.SignupDesc)

        return signup(self.state, self.request.tid, request, self.request.language)


class SignupActivation(BaseHandler):
  """
  Signup handler
  """
  check_roles = 'unauthenticated'
  invalidate_cache = True

  def get(self, token):
      ret = signup_activation(self.state, self.request.tid, token, self.request.language)

      # invalidate also cache of tenant 1
      apicache.ApiCache.invalidate(1)

      return ret
