#!/usr/bin/env python

import click
import json
from igor import igor
from request_utils import make_api_request
import types

def ipmi_print(data, indent=0):
    if isinstance(data, types.DictType):
        for key, value in data.iteritems():
            for i in xrange(indent):
                print '\t',

            print key + ':',
            if isinstance(value, types.DictType):
                print
                ipmi_print(value, indent+1)
            elif isinstance(value, types.ListType):
                print ', '.join(value)
            else:
                print value

# IPMI operation commands

## ipmitool chassis
## ipmitool chassis power

@igor.group()
@click.pass_obj
def ipmi(config):
    """IPMI operations"""

@ipmi.group()
@click.pass_obj
def chassis(config):
    """Chassis commands"""

@chassis.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.pass_obj
def info(config, hostname):
    """View chassis information.

    Example:

    \b
    $ igor ipmi chassis info --hostname osl01
    power_on: True
    misc_chassis_state: None
    power_restore_policy: always-on
    hostname: osl01
    power_fault: None
    main_power_fault: False
    power_control_fault: False
    power_interlock: inactive
    last_power_event: None
    power_overload: False
    """

    response = make_api_request('GET', config, '/machines/' + hostname +
                                               '/chassis')
    ipmi_print(response.json())

@chassis.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.option('--state', help='Desired power state.')
@click.pass_obj
def power(config, hostname, state):
    """View or set the chassis power.

    Example:

    \b
    $ igor ipmi chassis power --hostname osl01
    power_on: True
    hostname: osl01

    \b
    $ igor ipmi chassis power --hostname osl01 --state cycle
    power_on: True
    hostname: osl01
    """

    if not state:
        response = make_api_request('GET', config, '/machines/' + hostname +
                                                   '/chassis/power')
    else:
        data = json.dumps({'state': state})
        response = make_api_request('POST', config, '/machines/' + hostname +
                                                 '/chassis/power', data=data)
    ipmi_print(response.json())

@chassis.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.option('--state', help='Desired power policy.')
@click.pass_obj
def policy(config, hostname, state):
    """View or set the chassis power policy on the event of power failure.

    Example:

    \b
    $ igor ipmi chassis policy --hostname osl01
    policy: always-on
    hostname: osl01

    \b
    $ igor ipmi chassis power --hostname osl01 --state always-off
    policy: always-off
    hostname: osl01
    """

    if not state:
        response = make_api_request('GET', config, '/machines/' + hostname +
                                                   '/chassis/policy')
    else:
        data = json.dumps({'state': state})
        response = make_api_request('POST', config, '/machines/' + hostname +
                                                 '/chassis/policy', data=data)
    ipmi_print(response.json())

## ipmitool sensors list

@ipmi.group()
@click.pass_obj
def sensors(config):
    """Sensors commands"""

@sensors.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.pass_obj
def list(config, hostname):
    """Display sensor readings.

    Example:

    \b
    $ igor ipmi sensors list --hostname osl01
    Ambient Temp     | 18 degrees C      | ok
    Planar Temp      | disabled          | ns
    CMOS Battery     | 0x00              | ok
    """

    # TODO: Not implemented
    #response = make_api_request('GET', config, '/machines/' + hostname +
    #                                           '/sensors')
    #print response.json()
    pass

## ipmitool lan
## ipmitool lan set
## ipmitool lan alert
## ipmitool lan alert set

@ipmi.group()
@click.pass_obj
def lan(config):
    """LAN channel commands"""

@lan.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.option('--channel', type=click.INT,
                           help='The lan channel number')
@click.pass_obj
def info(config, hostname, channel):
    """Display lan channel information.

    Example:

    \b
    $ igor ipmi lan info --hostname osl01
    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    subnet_mask: 255.255.254.0
    ...
    
    \b
    $ igor ipmi lan info --hostname osl01 --channel 0
    Server response: Invalid channel: 0 (HTTP error 400)

    \b
    $ igor ipmi lan info --hostname osl01 --channel 1
    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    subnet_mask: 255.255.254.0
    ...
    """

    endpoint = '/machines/' + hostname + '/lan'
    if channel is not None:
        endpoint += '/' + str(channel)
    response = make_api_request('GET', config, endpoint)
    ipmi_print(response.json())

@lan.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.option('--channel', prompt=True, type=click.INT,
                           help='The lan channel number')
@click.option('--command', prompt=True,
                           help='The lan command to set')
@click.option('--param', prompt=True,
                         help='The lan command parameter')
@click.pass_obj
def set(config, hostname, channel, command, param):
    """Set lan channel information.

    For a list of valid commands, visit the ipmitool manpage.

    Example:

    \b
    $ igor ipmi lan set --hostname osl01
    Channel: 1
    Command: ipsrc
    Param: static

    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    ...

    \b
    $ igor ipmi lan set --hostname osl01 --channel 1 --command ipsrc \
                        --param static

    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    ...
    """

    data = json.dumps({'command': command, 'param': param})
    response = make_api_request('POST', config, '/machines/' + hostname
                                                + '/lan/' + str(channel),
                                                data=data)
    ipmi_print(response.json())

@lan.group()
@click.pass_obj
def alert(config):
    """LAN alert commands"""

@alert.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.option('--channel', type=click.INT,
                           help='The lan channel number')
@click.pass_obj
def info(config, hostname, channel):
    """Display lan alert information.

    Example:

    \b
    $ igor ipmi lan alert info --hostname osl01
    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    subnet_mask: 255.255.254.0
    ...

    \b
    $ igor ipmi lan alert info --hostname osl01 --channel 0
    Server response: Invalid channel: 0 (HTTP error 400)

    \b
    $ igor ipmi lan alert info --hostname osl01 --channel 1
    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    subnet_mask: 255.255.254.0
    ...
    """

    endpoint = '/machines/' + hostname + '/lan'
    if channel is not None:
        endpoint += '/' + str(channel)
    endpoint += '/alert'
    response = make_api_request('GET', config, endpoint)
    ipmi_print(response.json())

@alert.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.option('--channel', prompt=True, type=click.INT,
                           help='The lan channel number')
@click.option('--command', prompt=True,
                           help='The lan command to set')
@click.option('--param', prompt=True,
                         help='The lan command parameter')
@click.pass_obj
def set(config, hostname, channel, command, param):
    """Set lan alert channel information.

    For a list of valid commands, visit the ipmitool manpage.

    Example:

    \b
    $ igor ipmi lan alert set --hostname osl01
    Channel: 1
    Command: ipsrc
    Param: static

    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    ...

    \b
    $ igor ipmi lan alert set --hostname osl01 --channel 1 --command ipsrc \
                              --param static

    auth_type_support: NONE, MD2, MD5, PASSWORD
    snmp_community_string: 4h519bu64
    n_802_1q_vlan_priority: 0
    cipher_suite_priv_max: aaaaaaaaaaaaaaa
    ip_address_source: Static Address
    ...
    """

    data = json.dumps({'command': command, 'param': param})
    response = make_api_request('POST', config, '/machines/' + hostname
                                                + '/lan/' + str(channel)
                                                + '/alert',
                                                data=data)
    ipmi_print(response.json())

@ipmi.group()
@click.pass_obj
def sel(config):
    """System event log commands"""

@sel.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.pass_obj
def info(config, hostname):
    """Display system event log information.

    Example:

    \b
    $ igor ipmi sel info --hostname osl01
    hostname: osl01
    supported_cmds: Reserve
    last_add_time: 1970-01-01 00:00:59
    free_space: 8144
    version:
        compliant: v1.5, v2
        number: 1.5
    entries: 3
    overflow: False
    last_del_time: 2013-05-10 20:14:10
    """

    endpoint = '/machines/' + hostname + '/sel'
    response = make_api_request('GET', config, endpoint)
    ipmi_print(response.json())

@sel.command()
@click.option('--hostname', prompt=True,
                            help='The short hostname for this machine.')
@click.option('--time', help='(YYYY-MM-DD hh:mm:ss) Desired SEL clock time.')
@click.pass_obj
def time(config, hostname, time):
    """Display or set the SEL clock time.

    Example:

    \b
    $ igor ipmi sel time --hostname osl01
    hostname: osl01
    time: 2014-07-31 03:38:01

    \b
    $ igor ipmi sel time --time '1990-05-22 23:15:50' --hostname osl01
    hostname: osl01
    time: 1990-05-22 23:15:50
    """

    if not time:
        response = make_api_request('GET', config, '/machines/' + hostname +
                                                   '/sel/time')
    else:
        data = json.dumps({'time': time})
        response = make_api_request('POST', config, '/machines/' + hostname +
                                                 '/sel/time', data=data)
    ipmi_print(response.json())
