#!/usr/bin/python
# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ibm_svc_info
short_description: This module gathers various information from the
                   IBM Spectrum Virtualize storage systems.
version_added: "2.10"
description:
- Gathers the list of specified IBM Spectrum Virtualize storage system
  entities. These include the list of nodes, pools, volumes, hosts,
  host clusters, FC ports, iSCSI ports, target port FC, FC consistgrp,
  vdiskcopy, I/O groups, FC map, FC connectivity, NVMe fabric,
  array, and system.
author:
- Peng Wang (@wangpww)
options:
  name:
    description:
    - Collects storage information
    required: true
    type: str
  state:
    type: str
    required: False
    description:
    - Returns "info"
    default: "info"
    choices: ['info']
  clustername:
    description:
    - The hostname or management IP of the
      Spectrum Virtualize storage system
    type: str
    required: true
  domain:
    description:
    - Domain for the IBM Spectrum Virtualize storage system
    type: str
  username:
    description:
    - REST API username for the IBM Spectrum Virtualize storage system
    required: true
    type: str
  password:
    description:
    - REST API password for the IBM Spectrum Virtualize storage system
    required: true
    type: str
  log_path:
    description:
    - Debugs log for this file
    type: str
  validate_certs:
    description:
    - Validate certification
    type: bool
  gather_subset:
    type: list
    required: False
    description:
    - List of string variables to specify the IBM Spectrum Virtualize entities
      for which information is required.
    - all - list of all IBM Spectrum Virtualize entities
            supported by the module
    - vol - lists information for VDisks
    - pool - lists information for mdiskgrps
    - node - lists information for nodes
    - iog - lists information for I/O groups
    - host - lists information for hosts
    - hc - lists information for host clusters
    - fc - lists information for FC connectivity
    - fcport - lists information for FC ports
    - targetportfc - lists information for WWPN which is required to set up
                     FC zoning and to display the current failover status
                     of host I/O ports
    - fcmap - lists information for FC maps
    - fcconsistgrp - displays a concise list or a detailed
                     view of FlashCopy consistency groups
    - iscsiport - lists information for iSCSI ports
    - vdiskcopy - lists information for volume copy
    - array - lists information for array MDisks
    - system - displays the storage system information
    choices: [vol, pool, node, iog, host, hc, fcport
              , iscsiport, fcmap, fc, fcconsistgrp
              , vdiskcopy, 'targetportfc', array, system, all]
    default: "all"
'''

EXAMPLES = '''
- name: Using the IBM Spectrum Virtualize collection to gather storage information
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Get volume info
      ibm_svc_info:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/ansible.log
        state: info
        gather_subset: vol

- name: Using the IBM Spectrum Virtualize collection to gather storage information
  hosts: localhost
  collections:
    - ibm.spectrum_virtualize
  gather_facts: no
  connection: local
  tasks:
    - name: Get pool info
      ibm_svc_info:
        clustername: "{{clustername}}"
        domain: "{{domain}}"
        username: "{{username}}"
        password: "{{password}}"
        log_path: /tmp/ansible.log
        state: info
        gather_subset: pool

'''

RETURN = '''
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.spectrum_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCGatherInfo(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', default='info', choices=['info']),
                gather_subset=dict(type='list', required=False,
                                   default=['all'],
                                   choices=['vol',
                                            'pool',
                                            'node',
                                            'iog',
                                            'host',
                                            'hc',
                                            'fc',
                                            'fcport',
                                            'targetportfc',
                                            'iscsiport',
                                            'fcmap',
                                            'fcconsistgrp',
                                            'vdiskcopy',
                                            'array',
                                            'system',
                                            'all'
                                            ]),
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        self.log = get_logger(self.__class__.__name__, log_path)
        self.name = self.module.params['name']

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path
        )

    def get_volumes_list(self):
        try:
            vols = self.restapi.svc_obj_info(cmd='lsvdisk', cmdopts=None,
                                             cmdargs=None)
            self.log.info("Successfully listed %d volumes from array %s",
                          len(vols), self.module.params['clustername'])
            return vols
        except Exception as e:
            msg = ('Get Volumes from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_pools_list(self):
        try:
            pools = self.restapi.svc_obj_info(cmd='lsmdiskgrp', cmdopts=None,
                                              cmdargs=None)
            self.log.info('Successfully listed %d pools from array '
                          '%s', len(pools), self.module.params['clustername'])
            return pools
        except Exception as e:
            msg = ('Get Pools from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_nodes_list(self):
        try:
            nodes = self.restapi.svc_obj_info(cmd='lsnode', cmdopts=None,
                                              cmdargs=None)
            self.log.info('Successfully listed %d pools from array %s',
                          len(nodes), self.module.params['clustername'])
            return nodes
        except Exception as e:
            msg = ('Get Nodes from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_hosts_list(self):
        try:
            hosts = self.restapi.svc_obj_info(cmd='lshost', cmdopts=None,
                                              cmdargs=None)
            self.log.info('Successfully listed %d hosts from array '
                          '%s', len(hosts), self.module.params['clustername'])
            return hosts
        except Exception as e:
            msg = ('Get Hosts from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_iogroups_list(self):
        try:
            iogrps = self.restapi.svc_obj_info(cmd='lsiogrp', cmdopts=None,
                                               cmdargs=None)
            self.log.info('Successfully listed %d hosts from array '
                          '%s', len(iogrps), self.module.params['clustername'])
            return iogrps
        except Exception as e:
            msg = ('Get IO Groups from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_host_clusters_list(self):
        try:
            hcs = self.restapi.svc_obj_info(cmd='lshostcluster', cmdopts=None,
                                            cmdargs=None)
            self.log.info('Successfully listed %d host clusters from array '
                          '%s', len(hcs), self.module.params['clustername'])
            return hcs
        except Exception as e:
            msg = ('Get Host Cluster from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fc_connectivity_list(self):
        try:
            fc = self.restapi.svc_obj_info(cmd='lsfabric', cmdopts=None,
                                           cmdargs=None)
            self.log.info('Successfully listed %d fc connectivity from array '
                          '%s', len(fc), self.module.params['clustername'])
            return fc
        except Exception as e:
            msg = ('Get FC Connectivity from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fc_ports_list(self):
        try:
            fcports = self.restapi.svc_obj_info(cmd='lsportfc', cmdopts=None,
                                                cmdargs=None)
            self.log.info('Successfully listed %d fc ports from array %s',
                          len(fcports), self.module.params['clustername'])
            return fcports
        except Exception as e:
            msg = ('Get fc ports from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_target_port_fc_list(self):
        try:
            targetportfc = self.restapi.svc_obj_info(cmd='lstargetportfc',
                                                     cmdopts=None,
                                                     cmdargs=None)
            self.log.info('Successfully listed %d target port fc '
                          'from array %s', len(targetportfc),
                          self.module.params['clustername'])
            return targetportfc
        except Exception as e:
            msg = ('Get target port fc from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_iscsi_ports_list(self):
        try:
            ipports = self.restapi.svc_obj_info(cmd='lsportip', cmdopts=None,
                                                cmdargs=None)
            self.log.info('Successfully listed %d iscsi ports from array %s',
                          len(ipports), self.module.params['clustername'])
            return ipports
        except Exception as e:
            msg = ('Get iscsi ports from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fc_map_list(self):
        try:
            fcmaps = self.restapi.svc_obj_info(cmd='lsfcmap', cmdopts=None,
                                               cmdargs=None)
            self.log.info('Successfully listed %d fc maps from array %s',
                          len(fcmaps), self.module.params['clustername'])
            return fcmaps
        except Exception as e:
            msg = ('Get fc maps from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_array_list(self):
        try:
            array = self.restapi.svc_obj_info(cmd='lsarray', cmdopts=None,
                                              cmdargs=None)
            self.log.info('Successfully listed %d array info from array %s',
                          len(array), self.module.params['clustername'])
            return array
        except Exception as e:
            msg = ('Get Array info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_system_list(self):
        try:
            system = self.restapi.svc_obj_info(cmd='lssystem', cmdopts=None,
                                               cmdargs=None)
            self.log.info('Successfully listed %d system info from array %s',
                          len(system), self.module.params['clustername'])
            return system
        except Exception as e:
            msg = ('Get System info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_fcconsistgrp_list(self):
        try:
            fcconsistgrp = self.restapi.svc_obj_info(cmd='lsfcconsistgrp',
                                                     cmdopts=None,
                                                     cmdargs=None)
            self.log.info('Successfully listed %d fcconsistgrp info '
                          'from array %s', len(fcconsistgrp),
                          self.module.params['clustername'])
            return fcconsistgrp
        except Exception as e:
            msg = ('Get fcconsistgrp info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def get_vdiskcopy_list(self):
        try:
            vdiskcopy = self.restapi.svc_obj_info(cmd='lsvdiskcopy',
                                                  cmdopts=None,
                                                  cmdargs=None)
            self.log.info('Successfully listed %d vdiskcopy info '
                          'from array %s', len(vdiskcopy),
                          self.module.params['clustername'])
            return vdiskcopy
        except Exception as e:
            msg = ('Get vdiskcopy info from array %s failed with error %s ',
                   self.module.params['clustername'], str(e))
            self.log.error(msg)
            self.module.fail_json(msg=msg)

    def apply(self):

        subset = self.module.params['gather_subset']
        if len(subset) == 0 or 'all' in subset:
            self.log.info("The default value for gather_subset is all")
            subset = ['vol', 'pool', 'node', 'iog', 'host', 'hc', 'fc',
                      'fcport', 'iscsiport', 'fcmap', 'fcconsistgrp',
                      'vdiskcopy', 'targetportfc', 'array', 'system']

        vol = []
        pool = []
        node = []
        iog = []
        host = []
        hc = []
        fc = []
        fcport = []
        targetportfc = []
        iscsiport = []
        fcmap = []
        fcconsistgrp = []
        vdiskcopy = []
        array = []
        system = []

        if 'vol' in subset:
            vol = self.get_volumes_list()
        if 'pool' in subset:
            pool = self.get_pools_list()
        if 'node' in subset:
            node = self.get_nodes_list()
        if 'iog' in subset:
            iog = self.get_iogroups_list()
        if 'host' in subset:
            host = self.get_hosts_list()
        if 'hc' in subset:
            hc = self.get_host_clusters_list()
        if 'fc' in subset:
            fc = self.get_fc_connectivity_list()
        if 'targetportfc' in subset:
            targetportfc = self.get_target_port_fc_list()
        if 'fcport' in subset:
            fcport = self.get_fc_ports_list()
        if 'iscsiport' in subset:
            iscsiport = self.get_iscsi_ports_list()
        if 'fcmap' in subset:
            fcmap = self.get_fc_map_list()
        if 'fcconsistgrp' in subset:
            fcconsistgrp = self.get_fcconsistgrp_list()
        if 'vdiskcopy' in subset:
            vdiskcopy = self.get_vdiskcopy_list()
        if 'array' in subset:
            array = self.get_array_list()
        if 'system' in subset:
            system = self.get_system_list()

        self.module.exit_json(
            Volumes=vol,
            Pools=pool,
            Nodes=node,
            IOGroup=iog,
            Hosts=host,
            HostClusters=hc,
            FCConnectivity=fc,
            FCConsistgrp=fcconsistgrp,
            VdiskCopy=vdiskcopy,
            FCPorts=fcport,
            TargetPortFC=targetportfc,
            iSCSIPorts=iscsiport,
            FCMaps=fcmap,
            Array=array,
            System=system)


def main():
    v = IBMSVCGatherInfo()
    try:
        v.apply()
    except Exception as e:
        v.log.debug("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
