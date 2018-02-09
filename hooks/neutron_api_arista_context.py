from charmhelpers.core.hookenv import (
    config,
)

from charmhelpers.contrib.openstack import context

VLAN = 'vlan'
VXLAN = 'vxlan'
GRE = 'gre'
OVERLAY_NET_TYPES = [VLAN]


def get_overlay_network_type():
    overlay_networks = config('overlay-network-type').split()
    for overlay_net in overlay_networks:
        if overlay_net not in OVERLAY_NET_TYPES:
            raise ValueError('Unsupported overlay-network-type %s'
                             % overlay_net)
    return ','.join(overlay_networks)


class AristaMl2Context(context.OSContextGenerator):
    def _arista_context(self):
        ctxt = {'eapi_host': config('eapi-host'),
                'eapi_username': config('eapi-username'),
                'eapi_password': config('eapi-password'),
                'region_name': config('region-name'),
                'arista_version': config('arista-version')}
        return ctxt

    def __call__(self):
        ctxt = self._arista_context()
        if not ctxt:
            return {}
        ctxt['overlay_network_type'] = get_overlay_network_type()
        ctxt['security_groups'] = config('security-groups')
        ctxt['network_vlan_ranges'] = config('vlan-ranges')
        return ctxt
