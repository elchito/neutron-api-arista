#!/usr/bin/env python

from charmhelpers.core.hookenv import (
    Hooks,
    UnregisteredHookError,
    log as juju_log,
    log,
    config,
    relation_set,
    relation_get,
    relation_ids,
    related_units,
    status_set,

)
import json
import sys
import uuid
import os

from charmhelpers.fetch import (
    apt_install,
    apt_update,
)

from neutron_api_arista_utils import (
    register_configs,
    determine_packages,
    install_networking_arista,
    restart_service,
    ensure_pkg,
)

hooks = Hooks()
CONFIGS = register_configs()


@hooks.hook('config-changed')
def config_changed():
    charm_config = config()
    if (charm_config.changed('vlan-ranges') or
        charm_config.changed('overlay-network-type') or
        charm_config.changed('security-groups') or
        charm_config.changed('eapi-host') or
        charm_config.changed('eapi-username') or
        charm_config.changed('eapi-password')):
        status_set('maintenance', 'Applying changes to configuration')
    if (charm_config.changed('arista-version') or charm_config.changed('pip-proxy')):
        status_set('maintenance', 'Upgrading pip packages')
        install_networking_arista()
        restart_service()
        status_set('active', 'Unit is ready')
    CONFIGS.write_all()


@hooks.hook('neutron-plugin-api-subordinate-relation-joined')
def neutron_api_joined(rid=None):
    principle_config = {
        'neutron-api': {
            '/etc/neutron/neutron.conf': {
                'sections': {
                    'DEFAULT': [
                    ],
                }
            }
        }
    }
    relation_info = {
        'neutron-plugin': 'arista',
        'core-plugin': 'ml2',
        'service-plugins': ' ',
        'subordinate_configuration': json.dumps(principle_config),
    }
    relation_set(relation_settings=relation_info)


@hooks.hook('install')
def install():
    status_set('maintenance', 'Executing pre-install')
    ensure_pkg()
    apt_update()
    pkgs = determine_packages()
    for pkg in pkgs:
        apt_install(pkg, options=['--force-yes'], fatal=True)
    status_set('maintenance', 'Installing pip packages')
    install_networking_arista()
    restart_service()

def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        juju_log('Unknown hook {} - skipping.'.format(e))

if __name__ == '__main__':
    main()
