import os
import subprocess
import json

from collections import OrderedDict
from charmhelpers.contrib.openstack.utils import os_release
from charmhelpers.contrib.openstack import templating
from charmhelpers.core.hookenv import (
    config,
    relation_ids,
    relation_get,
    related_units,
)

from charmhelpers.contrib.python.packages import pip_install

import neutron_api_arista_context
import charmhelpers.core.hookenv as hookenv

TEMPLATES = 'templates/'
CHARM_LIB_DIR = os.environ.get('CHARM_DIR', '') + "/lib/"
ARISTA_VERSION = "2017.2.2"

ML2_CONFIG = '/etc/neutron/plugins/ml2/ml2_conf.ini'
ML2_CONFIG_ARISTA = '/etc/neutron/plugins/ml2/ml2_conf_arista.ini'

PACKAGES = ['python-pip']

def determine_packages():
    return PACKAGES

def register_configs(release=None):
    resources = OrderedDict([
        (ML2_CONFIG, {
            'services': ['neutron-server'],
            'contexts': [neutron_api_arista_context.AristaMl2Context(), ]
        }),
        (ML2_CONFIG_ARISTA, {
            'services': ['neutron-server'],
            'contexts': [neutron_api_arista_context.AristaMl2Context(), ]
        }),
    ])
    release = os_release('neutron-common')
    configs = templating.OSConfigRenderer(templates_dir=TEMPLATES,
                                          openstack_release=release)
    for cfg, rscs in resources.iteritems():
        configs.register(cfg, rscs['contexts'])
    return configs


def api_ready(relation, key):
    ready = 'no'
    for rid in relation_ids(relation):
        for unit in related_units(rid):
            ready = relation_get(attribute=key, unit=unit, rid=rid)
    return ready == 'yes'


def is_neutron_api_ready():
    return api_ready('neutron-plugin-api-subordinate', 'neutron-api-ready')

def install_networking_arista():
    if config('arista-version') is None:
        package_version = ARISTA_VERSION
    else:
        package_version = config('arista-version')
    package_name = 'networking-arista==%s' % package_version
    if config('pip-proxy') != "None":
        pip_install(package_name, fatal=True, proxy=config('pip-proxy'))
    else:
        pip_install(package_name, fatal=True)

def restart_service():
    cmd = ['service', 'neutron-server', 'restart']
    subprocess.check_call(cmd)

def ensure_pkg():
    cmd = ['apt', 'install', '-y', 'python-apt']
    subprocess.check_call(cmd)

