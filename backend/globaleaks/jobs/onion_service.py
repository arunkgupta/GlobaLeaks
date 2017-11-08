# -*- coding: utf-8 -*-
# Implements configuration of Tor hidden service

import os
from txtorcon import build_local_tor_connection

from twisted.internet import reactor, defer

from globaleaks import models
from globaleaks.jobs.base import BaseJob
from globaleaks.models.config import NodeFactory, PrivateFactory
from globaleaks.orm import transact
from globaleaks.utils.utility import log
from globaleaks.state import State


try:
    from txtorcon.torconfig import EphemeralHiddenService
except ImportError:
    from globaleaks.mocks.txtorcon_mocks import EphemeralHiddenService


__all__ = ['OnionService']


@transact
def list_onion_service_info(store):
    return [db_get_onion_service_info(store, tid)
        for tid in store.find(models.Tenant.id, models.Tenant.active == True)]


@transact
def get_onion_service_info(store, tid):
    return db_get_onion_service_info(store, tid)


def db_get_onion_service_info(store, tid):
    node_fact = NodeFactory(store, tid)
    hostname = node_fact.get_val(u'onionservice')

    key = PrivateFactory(store, tid).get_val(u'tor_onion_key')

    return hostname, key, tid


@transact
def set_onion_service_info(store, tid, hostname, key):
    NodeFactory(store, tid).set_val(u'onionservice', hostname)
    PrivateFactory(store, tid).set_val(u'tor_onion_key', key)

    # Update external application state
    State.tenant_cache[tid].onionservice = hostname
    State.tenant_hostname_id_map[hostname] = tid


class OnionService(BaseJob):
    name = "OnionService"
    threaded = False
    print_startup_error = True
    tor_conn = None
    hs_map = {}

    def service(self, restart_deferred):
        control_socket = '/var/run/tor/control'

        def startup_callback(tor_conn):
            self.print_startup_error = True
            self.tor_conn = tor_conn
            self.tor_conn.protocol.on_disconnect = restart_deferred

            log.debug('Successfully connected to Tor control port')

            return self.add_all_hidden_services()

        def startup_errback(err):
            if self.print_startup_error:
                # Print error only on first run or failure or on a failure subsequent to a success condition
                self.print_startup_error = False
                log.err('Failed to initialize Tor connection; error: %s', err)

            restart_deferred.callback(None)

        if not os.path.exists(control_socket):
            startup_errback(Exception('Tor control port not open on /var/run/tor/control; waiting for Tor to become available'))
            return

        if not os.access(control_socket, os.R_OK):
            startup_errback(Exception('Unable to access /var/run/tor/control; manual permission recheck needed'))
            return

        d = build_local_tor_connection(reactor)
        d.addCallback(startup_callback)
        d.addErrback(startup_errback)

    def operation(self):
        deferred = defer.Deferred()

        self.service(deferred)

        return deferred

    def stop(self):
        super(OnionService, self).stop()

        if self.tor_conn is not None:
            tor_conn = self.tor_conn
            self.tor_conn = None
            return tor_conn.protocol.quit()
        else:
            return defer.succeed(None)

    @defer.inlineCallbacks
    def add_all_hidden_services(self):
        hostname_key_list = yield list_onion_service_info()

        hs_add = []

        if self.tor_conn is not None:
            for hostname, key, tid in hostname_key_list:
                if hostname not in self.hs_map:
                    hs_add.append(self.add_hidden_service(hostname, key, tid))

        yield defer.DeferredList(hs_add)

    def add_hidden_service(self, hostname, key, tid):
        hs_loc = ('80 localhost:8083')
        if not hostname and not key:
            log.info('Creating new onion service')
            ephs = EphemeralHiddenService(hs_loc)
        else:
            log.info('Setting up existing onion service %s', hostname)
            ephs = EphemeralHiddenService(hs_loc, key)
            self.hs_map[hostname] = ephs

        @defer.inlineCallbacks
        def initialization_callback(ret):
            log.info('Initialization of hidden-service %s completed.', ephs.hostname)
            if not hostname and not key:
                yield set_onion_service_info(tid, ephs.hostname, ephs.private_key)
                self.hs_map[ephs.hostname] = ephs

        d = ephs.add_to_tor(self.tor_conn.protocol)
        return d.addCallback(initialization_callback) # pylint: disable=no-member

    @defer.inlineCallbacks
    def remove_unwanted_hidden_services(self):
        # Collect the list of all hidden services listed by tor then remove all of them
        # that are not present in the tenant cache ensuring that the OnionService.hs_map
        # is kept up to date.
        running_services = yield self.get_all_hidden_services()
        tenant_services = {tc.onionservice for tc in State.tenant_cache.values()}

        for onion_addr in running_services:
            if onion_addr not in tenant_services and onion_addr in self.hs_map:
                ephs = self.hs_map.pop(onion_addr)
            elif onion_addr not in self.hs_map:
                log.err('Hit unexpected condition: %s not in tenant_services', onion_addr)
                ephs = object.__new__(EphemeralHiddenService)
                ephs.hostname = onion_addr
            else:
                ephs = None

            if ephs is not None:
                log.info('Removing onion address: %s' % ephs.hostname)
                yield ephs.remove_from_tor(self.tor_conn.protocol)

    @defer.inlineCallbacks
    def get_all_hidden_services(self):
        if self.tor_conn is None:
            defer.returnValue([])

        ret = yield self.tor_conn.protocol.get_info('onions/current')

        running_services = ret.get('onions/current', '').strip().split('\n')
        if ret == '':
            running_services = []
        running_services = [r+'.onion' for r in running_services]

        defer.returnValue(running_services)
