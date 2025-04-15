## Lab Topology

Each workshop participant will be provided with the below topology consisting of 2 leaf and 1 spine nodes along with 4 clients.

![image](../images/lab-topology.jpg)

## NOS (Network Operating System)

Both leafs and Spine nodes will be running the latest Nokia [SR Linux](https://www.nokia.com/networks/ip-networks/service-router-linux-NOS/) release.

## Deploying the lab

To deploy the lab, run the following:

```bash
cd ~/wk415/evpn
sudo clab deploy -t srl-evpn.clab.yml
```

Containerlab will deploy the lab and display a table with the list of nodes and their IPs.

```bash
╭─────────┬───────────────────────────────┬─────────┬────────────────────╮
│   Name  │           Kind/Image          │  State  │   IPv4/6 Address   │
├─────────┼───────────────────────────────┼─────────┼────────────────────┤
│ client1 │ linux                         │ running │ 172.20.20.10       │
│         │ ghcr.io/srl-labs/alpine       │         │ 2001:172:20:20::10 │
├─────────┼───────────────────────────────┼─────────┼────────────────────┤
│ client2 │ linux                         │ running │ 172.20.20.11       │
│         │ ghcr.io/srl-labs/alpine       │         │ 2001:172:20:20::11 │
├─────────┼───────────────────────────────┼─────────┼────────────────────┤
│ client3 │ linux                         │ running │ 172.20.20.12       │
│         │ ghcr.io/srl-labs/alpine       │         │ 2001:172:20:20::12 │
├─────────┼───────────────────────────────┼─────────┼────────────────────┤
│ client4 │ linux                         │ running │ 172.20.20.13       │
│         │ ghcr.io/srl-labs/alpine       │         │ 2001:172:20:20::13 │
├─────────┼───────────────────────────────┼─────────┼────────────────────┤
│ leaf1   │ nokia_srlinux                 │ running │ 172.20.20.2        │
│         │ ghcr.io/nokia/srlinux:24.10.1 │         │ 2001:172:20:20::2  │
├─────────┼───────────────────────────────┼─────────┼────────────────────┤
│ leaf2   │ nokia_srlinux                 │ running │ 172.20.20.4        │
│         │ ghcr.io/nokia/srlinux:24.10.1 │         │ 2001:172:20:20::4  │
├─────────┼───────────────────────────────┼─────────┼────────────────────┤
│ spine   │ nokia_srlinux                 │ running │ 172.20.20.3        │
│         │ ghcr.io/nokia/srlinux:24.10.1 │         │ 2001:172:20:20::3  │
╰─────────┴───────────────────────────────┴─────────┴────────────────────╯
```

To display all deployed labs on your VM at any time, use:

```bash
sudo clab inspect --all
```

## Connecting to the devices

Find the nodename or IP address of the device from the above output and then use SSH.

```bash
ssh leaf1
```

To login to the client, identify the client hostname using the `sudo clab inspect --all` command above and then:

```bash
sudo docker exec –it client3 bash
```

## Physical link connectivity

We will be using [Openconfig](https://www.openconfig.net/) to configure the following:

- Configure interfaces between Leaf & Spine
- Configure interface between Leaf & Client
- Configure system loopback
- Configure route policy to advertise system loopback (this policy will be later applied under BGP)
- Configure default Network Instance (VRF) and add system loopback and Leaf/Spine interfaces to this VRF

We will use [gRPC gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/) to push the configuration to the devices.

[gNMIc](https://gnmic.openconfig.net/) is the most widely used client for gNMI and we will use that for this purpose.

The Openconfig configuration files are located at [configs/oc/](./configs/oc). Any config that is missing in OC will be implemented using SR Linux models. For our use case, we will use SRL models to configure the client facing interfaces on the leafs as a `bridged` interface.

Before we start, verify the current configured interfaces.

To view Interface status on SR Linux use:

```srl
show interface
```

Only the management interface is configured.

Change to the `OC Running` mode and view the interface configuration in OC.

```
enter oc
```

```
info flat interfaces
```

The management interface configuration can be seen in OC format. The other interfaces are enabled with no IP configuration.

### IPv4 Link Addressing

![image](../images/lab-ipv4-2.jpg)

### IPv6 Link Addressing

![image](../images/lab-ipv6.jpg)

### Using gNMI to push Openconfig

Exit from SR Linux and on your VM, run the following commands to push the configuration in the files to the devices. There is no native configuration for spine as all required configs are covered in Openconfig.

```
gnmic -a leaf1:57401 -u admin -p NokiaSrl1! --insecure set --update-path openconfig:/ --update-file configs/oc/leaf1-oc.json --update-path srl_nokia:/ --update-file configs/srl/leaf1-native.json --encoding=JSON_IETF

gnmic -a leaf2:57401 -u admin -p NokiaSrl1! --insecure set --update-path openconfig:/ --update-file configs/oc/leaf2-oc.json --update-path srl_nokia:/ --update-file configs/srl/leaf2-native.json --encoding=JSON_IETF

gnmic -a spine:57401 -u admin -p NokiaSrl1! --insecure set --update-path openconfig:/ --update-file configs/oc/spine-oc.json --encoding=JSON_IETF
```

Expected response from each device:

```
{
  "source": "leaf1:57401",
  "timestamp": 1740857162969095065,
  "time": "2025-03-01T21:26:02.969095065+02:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "openconfig:"
    },
    {
      "operation": "UPDATE",
      "path": "srl_nokia:"
    }
  ]
}
```

### Viewing configuration in OC or native

The configuration that we pushed using OC can be viewed in both OC or native format.

To view in OC format, enter `OC Running` mode and run `info flat interfaces`.

To view in SRL format, enter `SRL Running` mode (if not already there) and run `info flat interface *`.

### Verify reachability between devices

Now that the interfaces are configured, check reachability between leaf and spine devices using ping.

Example on spine to Leaf1 using IPv4:

```srl
ping -c 3 192.168.10.2 network-instance default
```

Example on spine to Leaf1 using IPv6:

```srl
ping6 -c 3 192:168:10::2 network-instance default
```

## SR Linux Configuration Mode

To enter candidate configuration edit mode in SR Linux, use:

```srl
enter candidate
```

To commit the configuration in SR Linux, use:

```srl
commit stay
```

Here's a reference table with some commonly used commands.

| Action | Command |
| --- | --- |
| Enter Candidate mode | `enter candidate {private}` |
| Commit configuration changes | `commit {now\|stay}` |
| | `now` – commits and exits from candidate mode |
| | `stay` – commits and stays in candidate mode |
| Delete configuration elements | `delete` |
| | Eg: `delete interface ethernet-1/5` |
| Discard configuration changes | `discard {now\|stay}` |
| Compare candidate to running | `diff running /` |
| View configuration in current mode & context | `info {flat}` |
| View configuration in another mode & context | `info {flat} from state /interface ethernet-1/1` |
| Output modifiers | `<command> \| as {table\|json\|yaml}` |
| Access Linux shell | `bash` |
| Find a command | `tree flat detail \| grep <keyword>` |


## Configure BGP Underlay

We are now ready to start configuring the fabric for EVPN.

The first step is to configure BGP for underlay.

Underlay refers to the physical connectivity between Leaf and Spine that are directly connected. This forms the basis for reachability of a node from all other nodes.

BGP is commonly used for this purpose in a Data Center network. Other options are OSPF or IS-IS.

Each Leaf is in a separate Autonomous System (AS) and Spine is in it's own AS. This is typical in a Clos network.

We will use the IPv4 and IPv6 interface address to form BGP sessions between Leaf and Spine nodes.

We will export the system loopback IP over BGP to other nodes. This is required to create our overlay sessions in the next step.

The export policies are already created as part of the startup config. The routing policy config can be seen using the `info /routing-policy` command. In this step, we will apply them to BGP.

![image](../images/bgp-underlay.jpg)

### BGP Underlay Configuration

BGP underlay configuration on Leaf1:

```srl
set / network-instance default protocols bgp autonomous-system 64501
set / network-instance default protocols bgp router-id 1.1.1.1
set / network-instance default protocols bgp ebgp-default-policy import-reject-all false
set / network-instance default protocols bgp ebgp-default-policy export-reject-all false
set / network-instance default protocols bgp afi-safi ipv4-unicast admin-state enable
set / network-instance default protocols bgp group ebgp peer-as 64500
set / network-instance default protocols bgp group ebgp afi-safi ipv6-unicast admin-state enable
set / network-instance default protocols bgp neighbor 192.168.10.3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.10.3 export-policy [ export-underlay-v4 ]
set / network-instance default protocols bgp neighbor 192.168.10.3 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:10::3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:10::3 export-policy [ export-underlay-v6 ]
set / network-instance default protocols bgp neighbor 192:168:10::3 afi-safi ipv4-unicast admin-state disable
```

BGP underlay configuration on Leaf2:

```srl
set / network-instance default protocols bgp autonomous-system 64502
set / network-instance default protocols bgp router-id 2.2.2.2
set / network-instance default protocols bgp ebgp-default-policy import-reject-all false
set / network-instance default protocols bgp ebgp-default-policy export-reject-all false
set / network-instance default protocols bgp afi-safi ipv4-unicast admin-state enable
set / network-instance default protocols bgp group ebgp peer-as 64500
set / network-instance default protocols bgp group ebgp afi-safi ipv6-unicast admin-state enable
set / network-instance default protocols bgp neighbor 192.168.20.3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.20.3 export-policy [ export-underlay-v4 ]
set / network-instance default protocols bgp neighbor 192.168.20.3 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:20::3 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:20::3 export-policy [ export-underlay-v6 ]
set / network-instance default protocols bgp neighbor 192:168:20::3 afi-safi ipv4-unicast admin-state disable
```

BGP underlay configuration on Spine:

```srl
set / network-instance default protocols bgp autonomous-system 64500
set / network-instance default protocols bgp router-id 3.3.3.3
set / network-instance default protocols bgp ebgp-default-policy import-reject-all false
set / network-instance default protocols bgp ebgp-default-policy export-reject-all false
set / network-instance default protocols bgp afi-safi ipv4-unicast admin-state enable
set / network-instance default protocols bgp group ebgp afi-safi ipv6-unicast admin-state enable
set / network-instance default protocols bgp neighbor 192.168.10.2 peer-as 64501
set / network-instance default protocols bgp neighbor 192.168.10.2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.10.2 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192.168.20.2 peer-as 64502
set / network-instance default protocols bgp neighbor 192.168.20.2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192.168.20.2 afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:10::2 peer-as 64501
set / network-instance default protocols bgp neighbor 192:168:10::2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:10::2 afi-safi ipv4-unicast admin-state disable
set / network-instance default protocols bgp neighbor 192:168:20::2 peer-as 64502
set / network-instance default protocols bgp neighbor 192:168:20::2 peer-group ebgp
set / network-instance default protocols bgp neighbor 192:168:20::2 afi-safi ipv4-unicast admin-state disable
```

### BGP Underlay Verification

The BGP underlay sessions should be UP now. Check using the following command on the Spine.

```srl
show network-instance default protocols bgp neighbor
```

The output below confirms that both IPv4 and IPv6 BGP neighbor sessions are established between Spine and the 2 Leaf nodes.

The last column in the output shows the number of routes Received/Active/Transmitted by BGP. The count is 1 as we are exporting the system loopback IP.

```srl
A:spine# show network-instance default protocols bgp neighbor
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP neighbor summary for network-instance "default"
Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+-------------------+---------------------------+-------------------+-------+----------+---------------+---------------+--------------+---------------------------+
|     Net-Inst      |           Peer            |       Group       | Flags | Peer-AS  |     State     |    Uptime     |   AFI/SAFI   |      [Rx/Active/Tx]       |
+===================+===========================+===================+=======+==========+===============+===============+==============+===========================+
| default           | 192.168.10.2              | ebgp              | S     | 64501    | established   | 0d:0h:27m:40s | ipv4-unicast | [1/1/1]                   |
| default           | 192.168.20.2              | ebgp              | S     | 64502    | established   | 0d:0h:27m:40s | ipv4-unicast | [1/1/1]                   |
| default           | 192:168:10::2             | ebgp              | S     | 64501    | established   | 0d:0h:27m:45s | ipv6-unicast | [1/1/1]                   |
| default           | 192:168:20::2             | ebgp              | S     | 64502    | established   | 0d:0h:27m:45s | ipv6-unicast | [1/1/1]                   |
+-------------------+---------------------------+-------------------+-------+----------+---------------+---------------+--------------+---------------------------+
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Summary:
4 configured neighbors, 4 configured sessions are established, 0 disabled peers
0 dynamic peers
```

The route table for the default network instance (VRF) should now show the system loopback IP of other nodes.

```srl
show network-instance default route-table all
```

Output on Leaf1:

```srl
A:leaf1# show network-instance default route-table all
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance default
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+--------------------------+-------+------------+----------------------+----------+----------+---------+------------+----------------+----------------+----------------+---------------------+
|          Prefix          |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    |    Next-hop    |    Next-hop    |  Backup Next-  |   Backup Next-hop   |
|                          |       |            |                      |          | Network  |         |            |     (Type)     |   Interface    |   hop (Type)   |      Interface      |
|                          |       |            |                      |          | Instance |         |            |                |                |                |                     |
+==========================+=======+============+======================+==========+==========+=========+============+================+================+================+=====================+
| 1.1.1.1/32               | 5     | host       | net_inst_mgr         | True     | default  | 0       | 0          | None (extract) | None           |                |                     |
| 2.2.2.2/32               | 0     | bgp        | bgp_mgr              | True     | default  | 0       | 170        | 192.168.10.2/3 | ethernet-1/1.0 |                |                     |
|                          |       |            |                      |          |          |         |            | 1 (indirect/lo |                |                |                     |
|                          |       |            |                      |          |          |         |            | cal)           |                |                |                     |
| 192.168.10.2/31          | 1     | local      | net_inst_mgr         | True     | default  | 0       | 0          | 192.168.10.2   | ethernet-1/1.0 |                |                     |
|                          |       |            |                      |          |          |         |            | (direct)       |                |                |                     |
| 192.168.10.2/32          | 1     | host       | net_inst_mgr         | True     | default  | 0       | 0          | None (extract) | None           |                |                     |
+--------------------------+-------+------------+----------------------+----------+----------+---------+------------+----------------+----------------+----------------+---------------------+
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 routes total                    : 4
IPv4 prefixes with active routes     : 4
IPv4 prefixes with active ECMP routes: 0
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv6 unicast route table of network instance default
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+--------------------------+-------+------------+----------------------+----------+----------+---------+------------+----------------+----------------+----------------+---------------------+
|          Prefix          |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    |    Next-hop    |    Next-hop    |  Backup Next-  |   Backup Next-hop   |
|                          |       |            |                      |          | Network  |         |            |     (Type)     |   Interface    |   hop (Type)   |      Interface      |
|                          |       |            |                      |          | Instance |         |            |                |                |                |                     |
+==========================+=======+============+======================+==========+==========+=========+============+================+================+================+=====================+
| 192:168:10::2/127        | 1     | local      | net_inst_mgr         | True     | default  | 0       | 0          | 192:168:10::2  | ethernet-1/1.0 |                |                     |
|                          |       |            |                      |          |          |         |            | (direct)       |                |                |                     |
| 192:168:10::2/128        | 1     | host       | net_inst_mgr         | True     | default  | 0       | 0          | None (extract) | None           |                |                     |
| 2001::1/128              | 5     | host       | net_inst_mgr         | True     | default  | 0       | 0          | None (extract) | None           |                |                     |
| 2001::2/128              | 0     | bgp        | bgp_mgr              | True     | default  | 0       | 170        | 192:168:10::2/ | ethernet-1/1.0 |                |                     |
|                          |       |            |                      |          |          |         |            | 127 (indirect/ |                |                |                     |
|                          |       |            |                      |          |          |         |            | local)         |                |                |                     |
+--------------------------+-------+------------+----------------------+----------+----------+---------+------------+----------------+----------------+----------------+---------------------+
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv6 routes total                    : 4
IPv6 prefixes with active routes     : 4
IPv6 prefixes with active ECMP routes: 0
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

Now we are ready to configure the overlay.

## Configure BGP for Overlay

Overlay refers to the connectivity between nodes that are not necessarily directly connected.

Our end goal is to have an EVPN service between Leaf1 and Leaf2. BGP is required to advertise EVPN routes between the leaf devices.

For establishing overlay BGP session between Leaf1 and Leaf2, we will use the system loopback IP of the Leaf nodes. These IPs are pre-configured as part of initial lab deployment and can be verified using `show interface system0` command.

BGP overlay configuration is not required on the Spine as Spine is not aware of EVPN routes.

![image](../images/bgp-overlay.jpg)

### BGP Overlay Configuration

BGP Overlay configuration on Leaf1:

```srl
set / network-instance default protocols bgp group evpn peer-as 65500
set / network-instance default protocols bgp group evpn multihop admin-state enable
set / network-instance default protocols bgp group evpn afi-safi evpn admin-state enable
set / network-instance default protocols bgp group evpn afi-safi ipv4-unicast admin-state disable
set / network-instance default protocols bgp group evpn afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp group evpn local-as as-number 65500
set / network-instance default protocols bgp neighbor 2.2.2.2 peer-group evpn
set / network-instance default protocols bgp neighbor 2.2.2.2 transport local-address 1.1.1.1
set / network-instance default protocols bgp neighbor 2001::2 peer-group evpn
set / network-instance default protocols bgp neighbor 2001::2 transport local-address 2001::1
```

BGP Overlay configuration on Leaf2:

```srl
set / network-instance default protocols bgp group evpn peer-as 65500
set / network-instance default protocols bgp group evpn multihop admin-state enable
set / network-instance default protocols bgp group evpn afi-safi evpn admin-state enable
set / network-instance default protocols bgp group evpn afi-safi ipv4-unicast admin-state disable
set / network-instance default protocols bgp group evpn afi-safi ipv6-unicast admin-state disable
set / network-instance default protocols bgp group evpn local-as as-number 65500
set / network-instance default protocols bgp neighbor 1.1.1.1 peer-group evpn
set / network-instance default protocols bgp neighbor 1.1.1.1 transport local-address 2.2.2.2
set / network-instance default protocols bgp neighbor 2001::1 peer-group evpn
set / network-instance default protocols bgp neighbor 2001::1 transport local-address 2001::2
```

### BGP Overlay Verification

The BGP overlay sessions should be UP now. Check using the following commands on Leaf1 or Leaf2.

```srl
show network-instance default protocols bgp neighbor
```

The output confirms that EVPN neigbor sessions are established to both the IPv4 and IPv6 loopback IPs.

The output also displays the underlay IPv4 and IPv6 sessions.

The devices are not currently advertising any EVPN routes which is the last column is all 0s.

```srl
A:leaf1# show network-instance default protocols bgp neighbor
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP neighbor summary for network-instance "default"
Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+-------------------+---------------------------+-------------------+-------+----------+---------------+---------------+--------------+---------------------------+
|     Net-Inst      |           Peer            |       Group       | Flags | Peer-AS  |     State     |    Uptime     |   AFI/SAFI   |      [Rx/Active/Tx]       |
+===================+===========================+===================+=======+==========+===============+===============+==============+===========================+
| default           | 2.2.2.2                   | evpn              | S     | 65500    | established   | 0d:0h:26m:26s | evpn         | [0/0/0]                   |
| default           | 192.168.10.3              | ebgp              | S     | 64500    | established   | 0d:0h:26m:36s | ipv4-unicast | [1/1/1]                   |
| default           | 192:168:10::3             | ebgp              | S     | 64500    | established   | 0d:0h:26m:41s | ipv6-unicast | [1/1/1]                   |
| default           | 2001::2                   | evpn              | S     | 65500    | established   | 0d:0h:26m:27s | evpn         | [0/0/0]                   |
+-------------------+---------------------------+-------------------+-------+----------+---------------+---------------+--------------+---------------------------+
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Summary:
4 configured neighbors, 4 configured sessions are established, 0 disabled peers
0 dynamic peers
```

## Configure L2 EVPN-VXLAN

> <p style="color:red">!!! If you would like to skip configuring BGP and directly start with this section, 
> point the startup config file location in your topology file (srl-evpn.clab.yml) to `configs/fabric/startup-with-bgp/leaf1-startup-bgp.cfg (for Leaf1)`</p>

Now that we have established our underlay and overlay connectivity, our next step is to configure the Layer 2 EVPN-VXLAN instance.

The objective is to establish a connection between Client 1 (connected to Leaf1) and Client 3 (connected to Leaf2).

Both the clients are in the same subnet (172.16.10.0/24) and therefore, this will be a Layer 2 connection. From a client perspective, it is just like they are connected to a Layer 2 switch.

![image](../images/l2-evpn.jpg)

### Configure Client Interface

For Layer 2 client interfaces, it is not required to configure IPs on the Leaf interfaces facing the client.

Client facing Layer 2 interface configuration on Leaf1:

```srl
set / interface ethernet-1/10 description To-Client1
set / interface ethernet-1/10 subinterface 0 type bridged
```

Client facing Layer 2 interface configuration on Leaf2:

```srl
set / interface ethernet-1/10 description To-Client3
set / interface ethernet-1/10 subinterface 0 type bridged
```

IP addresses on the client side are pre-configured (on interface eth1) during deployment. This can be verified by logging in to the Client shell and running `ip a`.

To login to Client1, use:
```bash
sudo docker exec -it client1 bash
```

Output on Client1:

```bash
/ # ip a
<--truncated-->
20: eth1@if19: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 9500 qdisc noqueue state UP
    link/ether aa:c1:ab:81:49:35 brd ff:ff:ff:ff:ff:ff
    inet 172.16.10.50/24 scope global eth1
       valid_lft forever preferred_lft forever
    inet6 fe80::a8c1:abff:fe81:4935/64 scope link
       valid_lft forever preferred_lft forever
```

### Configuring VXLAN

VXLAN is the transport protocol for this EVPN instance.

All data packets will be encapsulated in VXLAN and transported to the destination.

On each Leaf, a VXLAN tunnel interface should be created with a unique VNI.

Configuring VXLAN on Leaf1:

```srl
set / tunnel-interface vxlan13 vxlan-interface 100 type bridged
set / tunnel-interface vxlan13 vxlan-interface 100 ingress vni 100
```

Configuring VXLAN on Leaf2:

```srl
set / tunnel-interface vxlan13 vxlan-interface 100 type bridged
set / tunnel-interface vxlan13 vxlan-interface 100 ingress vni 100
```

### Configuring Layer 2 EVPN-VXLAN

Layer 2 instance on SR Linux is called MAC-VRF. To learn more about SR Linux Network Instances, visit [SR Linux Documentation](https://documentation.nokia.com/srlinux/24-7/books/config-basics/network-instances.html).

In this step, we will configure a mac-vrf on each Leaf and add the client facing interface along with the VXLAN tunnel interface to the mac-vrf instance.

Each EVPN instance is uniquely identified by an EVI across the entire network.

When advertising an EVPN route over BGP (Multi-Protocol BGP), each route should include a Route Distinguisher (RD) and Route Target (RT).

RD is used to identify the source of the route. In our case, we will use the system-IP:EVI.

RT is used as an identifier (or condition) to import the route on the far end device.

EVPN-VXLAN configuration on Leaf1:

```srl
set / network-instance mac-vrf-1 type mac-vrf
set / network-instance mac-vrf-1 interface ethernet-1/10.0
set / network-instance mac-vrf-1 vxlan-interface vxlan13.100
set / network-instance mac-vrf-1 protocols bgp-evpn bgp-instance 1 encapsulation-type vxlan
set / network-instance mac-vrf-1 protocols bgp-evpn bgp-instance 1 vxlan-interface vxlan13.100
set / network-instance mac-vrf-1 protocols bgp-evpn bgp-instance 1 evi 100
set / network-instance mac-vrf-1 protocols bgp-vpn bgp-instance 1 route-distinguisher rd 1.1.1.1:100
set / network-instance mac-vrf-1 protocols bgp-vpn bgp-instance 1 route-target export-rt target:65500:100
set / network-instance mac-vrf-1 protocols bgp-vpn bgp-instance 1 route-target import-rt target:65500:100
```

EVPN-VXLAN configuration on Leaf2:

```srl
set / network-instance mac-vrf-1 type mac-vrf
set / network-instance mac-vrf-1 interface ethernet-1/10.0
set / network-instance mac-vrf-1 vxlan-interface vxlan13.100
set / network-instance mac-vrf-1 protocols bgp-evpn bgp-instance 1 encapsulation-type vxlan
set / network-instance mac-vrf-1 protocols bgp-evpn bgp-instance 1 vxlan-interface vxlan13.100
set / network-instance mac-vrf-1 protocols bgp-evpn bgp-instance 1 evi 100
set / network-instance mac-vrf-1 protocols bgp-vpn bgp-instance 1 route-distinguisher rd 2.2.2.2:100
set / network-instance mac-vrf-1 protocols bgp-vpn bgp-instance 1 route-target export-rt target:65500:100
set / network-instance mac-vrf-1 protocols bgp-vpn bgp-instance 1 route-target import-rt target:65500:100
```

### Layer 2 EVPN verification

EVPN will advertise Route Type 3 Inclusive Multicast Ethernet Tag (IMET) to discover PE devices and setup tree for BUM (Broadcast, Unknown, Multicast) traffic.

This route advertisement can be seen in the BGP show output using the below command.

```srl
show network-instance default protocols bgp routes evpn route-type summary
```

Output on Leaf1:

```srl
A:leaf1# show network-instance default protocols bgp routes evpn route-type summary
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Show report for the BGP route table of network-instance "default"
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Status codes: u=used, *=valid, >=best, x=stale
Origin codes: i=IGP, e=EGP, ?=incomplete
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP Router ID: 1.1.1.1      AS: 64501      Local AS: 64501
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Type 3 Inclusive Multicast Ethernet Tag Routes
+--------+--------------------------------------+------------+---------------------+--------------------------------------+--------------------------------------+
| Status |         Route-distinguisher          |   Tag-ID   |    Originator-IP    |               neighbor               |               Next-Hop               |
+========+======================================+============+=====================+======================================+======================================+
| u*>    | 2.2.2.2:100                          | 0          | 2.2.2.2             | 2.2.2.2                              | 2.2.2.2                              |
| *      | 2.2.2.2:100                          | 0          | 2.2.2.2             | 2001::2                              | 2.2.2.2                              |
+--------+--------------------------------------+------------+---------------------+--------------------------------------+--------------------------------------+
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
0 Ethernet Auto-Discovery routes 0 used, 0 valid
0 MAC-IP Advertisement routes 0 used, 0 valid
2 Inclusive Multicast Ethernet Tag routes 1 used, 2 valid
0 Ethernet Segment routes 0 used, 0 valid
0 IP Prefix routes 0 used, 0 valid
0 Selective Multicast Ethernet Tag routes 0 used, 0 valid
0 Selective Multicast Membership Report Sync routes 0 used, 0 valid
0 Selective Multicast Leave Sync routes 0 used, 0 valid
```

### Ping between Client 1 & 3

Verify if Client 3 is able to ping Client 1

Login to Client3 using:

```bash
sudo docker exec -it client3 bash
```

Run `ip a` and note down the MAC address of eth1 interface (facing Leaf2).

```bash
# sudo docker exec -it client3 bash
/ # ip a
26: eth1@if25: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 9500 qdisc noqueue state UP
    link/ether aa:c1:ab:67:32:61 brd ff:ff:ff:ff:ff:ff
    inet 172.16.10.60/24 scope global eth1
       valid_lft forever preferred_lft forever
    inet6 fe80::a8c1:abff:fe3f:aed8/64 scope link
       valid_lft forever preferred_lft forever
/ #
```

The MAC address of Client3 eth1 interface is aa:c1:ab:67:32:61. This could be different in your setup.

Ping Client1 IP from Client3:

```bash
ping -c 1 172.16.10.50
```

Output on Client1:

```bash
/ # ping -c 1 172.16.10.50
PING 172.16.10.50 (172.16.10.50): 56 data bytes
64 bytes from 172.16.10.50: seq=0 ttl=64 time=0.886 ms

--- 172.16.10.50 ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss
round-trip min/avg/max = 0.886/0.886/0.886 ms
```

Ping is successful. We have now established a Layer2 EVPN connection between Client1 & Client3.

Let's understand how this ping worked.

When we initiated the ping from Client3, with the first ping packet an ARP was sent by Client 3 for the destination IP of Client1. Unlike a traditional VPLS, the ARP is not flooded to all devices but only sent to the PE devices discovered using EVPN Route Type 3 (RT3).

At the same time, Leaf2 connected to Client3 learns the MAC of Client3 from the source MAC address field of the ICMP ping packet. Leaf2 sends an EVPN MAC-IP Route Type 2 advertisement to Leaf1 advertising Client3 MAC with Leaf2 as next-hop.

Now let's verify the MAC-IP advertisement using EVPN Route Type 2.

Run the below command on Leaf1 to see this route advertisement. Verify if the MAC address in the table below is the same MAC address we noted above for Client3.

```srl
show network-instance default protocols bgp routes evpn route-type summary
```

Output on Leaf1:

```srl
A:leaf1# show network-instance default protocols bgp routes evpn route-type summary
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Show report for the BGP route table of network-instance "default"
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Status codes: u=used, *=valid, >=best, x=stale
Origin codes: i=IGP, e=EGP, ?=incomplete
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP Router ID: 1.1.1.1      AS: 64501      Local AS: 64501
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Type 2 MAC-IP Advertisement Routes
+--------+------------------+------------+-------------------+------------------+------------------+------------------+------------------+--------------------------------+------------------+
| Status |      Route-      |   Tag-ID   |    MAC-address    |    IP-address    |     neighbor     |     Next-Hop     |      Label       |              ESI               |   MAC Mobility   |
|        |  distinguisher   |            |                   |                  |                  |                  |                  |                                |                  |
+========+==================+============+===================+==================+==================+==================+==================+================================+==================+
| u*>    | 2.2.2.2:100      | 0          | AA:C1:AB:67:32:61 | 0.0.0.0          | 2.2.2.2          | 2.2.2.2          | 100              | 00:00:00:00:00:00:00:00:00:00  | -                |
| *      | 2.2.2.2:100      | 0          | AA:C1:AB:67:32:61 | 0.0.0.0          | 2001::2          | 2.2.2.2          | 100              | 00:00:00:00:00:00:00:00:00:00  | -                |
+--------+------------------+------------+-------------------+------------------+------------------+------------------+------------------+--------------------------------+------------------+
```

When Leaf1 receives the ARP from Leaf2 for Client1 IP, Leaf1 will broadcast that ARP to it's connected Client. Client1 responds to the ARP which is encapsulated by Leaf1 and sent to Leaf2.

Now Leaf1 will send EVPN Route Type2 to Leaf2 advertising Client1 MAC address with Leaf1 system IP as next-hop. Verify this using the same command above on Leaf2.

At this time, both Leaf nodes have learned the remote Client MAC address.

Verify the MAC Address table on the Leaf using the below command.

```srl
show network-instance mac-vrf-1 bridge-table mac-table all
```

Output on Leaf1:

The table shows that Client1 (locally connected to Leaf1) MAC was learned directly over the interface facing the client.

Client3 MAC address was learned over the VXLAN tunnel. The ICMP ping packet will be encapsulated in VXLAN and sent to the destination 2.2.2.2 (Leaf2).

On Leaf2, the VXLAN encapsulation will be removed and the packet will be forwarded to Client3.


```srl
A:leaf1# show network-instance mac-vrf-1 bridge-table mac-table all
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Mac-table of network instance mac-vrf-1
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+--------------------+------------------------------------------------------+------------+----------------+---------+--------+------------------------------------------------------+
|      Address       |                     Destination                      | Dest Index |      Type      | Active  | Aging  |                     Last Update                      |
+====================+======================================================+============+================+=========+========+======================================================+
| AA:C1:AB:67:32:61  | vxlan-interface:vxlan13.100 vtep:2.2.2.2 vni:100     | 2736993    | evpn           | true    | N/A    | 2024-10-17T04:46:04.000Z                             |
| AA:C1:AB:81:49:35  | ethernet-1/10.0                                      | 2          | learnt         | true    | 76     | 2024-10-17T04:46:00.000Z                             |
+--------------------+------------------------------------------------------+------------+----------------+---------+--------+------------------------------------------------------+
```

### Debug and Packet Capture in SR Linux

SR Linux provides tools in CLI to capture packets for debug purposes.

Run the below command on Spine while a ping test is in progress between Client1 and Client3.

The output shows VXLAN encapsulated ICMP packets being sent between the 2 clients.

```srl
tools system traffic-monitor verbose protocol udp destination-port 4789
```

In this command, port 4789 is standard port for VXLAN.

Also, try the commands in the [packet capture section](../40-packet-capture#remote-capture) of this workshop to see VxLAN packet dumps in wireshark.

## Configure Layer 3 EVPN-VXLAN

Our final step is to configure a Layer 3 EVPN-VXLAN.

The objective is to connect Client 2 and Client 4 over a Layer 3 EVPN.

![image](../images/l3-evpn.jpg)

### Configure Client Interface

Client2 & 4 are Layer 3 clients with IPs in different subnets.

Client Layer 3 interface configuration on Leaf1:

```srl
set / interface ethernet-1/11 description To-Client2
set / interface ethernet-1/11 admin-state enable
set / interface ethernet-1/11 subinterface 0 ipv4 admin-state enable
set / interface ethernet-1/11 subinterface 0 ipv4 address 10.80.1.2/24
set / interface ethernet-1/11 subinterface 0 ipv6 admin-state enable
set / interface ethernet-1/11 subinterface 0 ipv6 address 10:80:1::2/64
```

Client Layer 3 interface configuration on Leaf2:

```srl
set / interface ethernet-1/11 description To-Client4
set / interface ethernet-1/11 admin-state enable
set / interface ethernet-1/11 subinterface 0 ipv4 admin-state enable
set / interface ethernet-1/11 subinterface 0 ipv4 address 10.90.1.2/24
set / interface ethernet-1/11 subinterface 0 ipv6 admin-state enable
set / interface ethernet-1/11 subinterface 0 ipv6 address 10:90:1::2/64
```

IP addresses on the client side are pre-configured during deployment. This can be verified by logging in to the Client shell and running `ip a`.

### Configuring VXLAN

We will create a Layer 3 VXLAN tunnel between Leaf1 and Leaf2 with a unique VNI.

Configuring VXLAN on Leaf1:

```srl
set / tunnel-interface vxlan24 vxlan-interface 200 type routed
set / tunnel-interface vxlan24 vxlan-interface 200 ingress vni 200
```

Configuring VXLAN on Leaf2:

```srl
set / tunnel-interface vxlan24 vxlan-interface 200 type routed
set / tunnel-interface vxlan24 vxlan-interface 200 ingress vni 200
```

### Configuring Layer 3 EVPN-VXLAN

Layer 3 instance on SR Linux is called IP-VRF. To learn more about SR Linux Network Instances, visit [SR Linux Documentation](https://documentation.nokia.com/srlinux/24-7/books/config-basics/network-instances.html)

We will create an ip-vrf and include the client facing interface and the vxlan tunnel in this instance.

RD & RT will be separate from the Layer2 instance.

EVPN-VXLAN configuration on Leaf1:

```srl
set / network-instance ip-vrf-1 type ip-vrf
set / network-instance ip-vrf-1 admin-state enable
set / network-instance ip-vrf-1 interface ethernet-1/11.0
set / network-instance ip-vrf-1 vxlan-interface vxlan24.200
set / network-instance ip-vrf-1 protocols bgp-evpn bgp-instance 1 encapsulation-type vxlan
set / network-instance ip-vrf-1 protocols bgp-evpn bgp-instance 1 vxlan-interface vxlan24.200
set / network-instance ip-vrf-1 protocols bgp-evpn bgp-instance 1 evi 200
set / network-instance ip-vrf-1 protocols bgp-vpn bgp-instance 1 route-distinguisher rd 1.1.1.1:200
set / network-instance ip-vrf-1 protocols bgp-vpn bgp-instance 1 route-target export-rt target:65500:200
set / network-instance ip-vrf-1 protocols bgp-vpn bgp-instance 1 route-target import-rt target:65500:200
```

EVPN-VXLAN configuration on Leaf2:

```srl
set / network-instance ip-vrf-1 type ip-vrf
set / network-instance ip-vrf-1 admin-state enable
set / network-instance ip-vrf-1 interface ethernet-1/11.0
set / network-instance ip-vrf-1 vxlan-interface vxlan24.200
set / network-instance ip-vrf-1 protocols bgp-evpn bgp-instance 1 encapsulation-type vxlan
set / network-instance ip-vrf-1 protocols bgp-evpn bgp-instance 1 vxlan-interface vxlan24.200
set / network-instance ip-vrf-1 protocols bgp-evpn bgp-instance 1 evi 200
set / network-instance ip-vrf-1 protocols bgp-vpn bgp-instance 1 route-distinguisher rd 2.2.2.2:200
set / network-instance ip-vrf-1 protocols bgp-vpn bgp-instance 1 route-target export-rt target:65500:200
set / network-instance ip-vrf-1 protocols bgp-vpn bgp-instance 1 route-target import-rt target:65500:200
```

### Layer 3 EVPN Route Verification

When Layer 3 EVPN is enabled, the Leaf nodes will start advertising the client facing interface IPs to each other using EVPN IP-prefix Route Type 5.

This can verified using the below command.

```srl
show network-instance default protocols bgp routes evpn route-type summary
```

Output on Leaf1:

```srl
A:leaf1# show network-instance default protocols bgp routes evpn route-type summary
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Show report for the BGP route table of network-instance "default"
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Status codes: u=used, *=valid, >=best, x=stale
Origin codes: i=IGP, e=EGP, ?=incomplete
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Type 5 IP Prefix Routes
+--------+----------------------------+------------+---------------------+----------------------------+----------------------------+----------------------------+----------------------------+
| Status |    Route-distinguisher     |   Tag-ID   |     IP-address      |          neighbor          |          Next-Hop          |           Label            |          Gateway           |
+========+============================+============+=====================+============================+============================+============================+============================+
| u*>    | 2.2.2.2:200                | 0          | 10.90.1.0/24        | 2.2.2.2                    | 2.2.2.2                    | 200                        | 0.0.0.0                    |
| *      | 2.2.2.2:200                | 0          | 10.90.1.0/24        | 2001::2                    | 2.2.2.2                    | 200                        | 0.0.0.0                    |
| u*>    | 2.2.2.2:200                | 0          | 10:90:1::/64        | 2.2.2.2                    | 2.2.2.2                    | 200                        | ::                         |
| *      | 2.2.2.2:200                | 0          | 10:90:1::/64        | 2001::2                    | 2.2.2.2                    | 200                        | ::                         |
+--------+----------------------------+------------+---------------------+----------------------------+----------------------------+----------------------------+----------------------------+
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

The remote routes will also be installed on the Leaf's route table.

Verify the VRF route table on Leaf1 using the below command:

```srl
show network-instance ip-vrf-1 route-table ipv4-unicast summary
```

Output on Leaf1:

```srl
A:leaf1# show network-instance ip-vrf-1 route-table ipv4-unicast summary
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance ip-vrf-1
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+--------------------------+-------+------------+----------------------+----------+----------+---------+------------+----------------+----------------+----------------+---------------------+
|          Prefix          |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    |    Next-hop    |    Next-hop    |  Backup Next-  |   Backup Next-hop   |
|                          |       |            |                      |          | Network  |         |            |     (Type)     |   Interface    |   hop (Type)   |      Interface      |
|                          |       |            |                      |          | Instance |         |            |                |                |                |                     |
+==========================+=======+============+======================+==========+==========+=========+============+================+================+================+=====================+
| 10.80.1.0/24             | 3     | local      | net_inst_mgr         | True     | ip-vrf-1 | 0       | 0          | 10.80.1.2      | ethernet-      |                |                     |
|                          |       |            |                      |          |          |         |            | (direct)       | 1/11.0         |                |                     |
| 10.80.1.2/32             | 3     | host       | net_inst_mgr         | True     | ip-vrf-1 | 0       | 0          | None (extract) | None           |                |                     |
| 10.80.1.255/32           | 3     | host       | net_inst_mgr         | True     | ip-vrf-1 | 0       | 0          | None           |                |                |                     |
|                          |       |            |                      |          |          |         |            | (broadcast)    |                |                |                     |
| 10.90.1.0/24             | 0     | bgp-evpn   | bgp_evpn_mgr         | True     | ip-vrf-1 | 0       | 170        | 2.2.2.2/32 (in |                |                |                     |
|                          |       |            |                      |          |          |         |            | direct/vxlan)  |                |                |                     |
+--------------------------+-------+------------+----------------------+----------+----------+---------+------------+----------------+----------------+----------------+---------------------+
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

### Ping between Client 2 & 4

Login to client2 using:

```bash
sudo docker exec -it client2 bash
```

Ping Client4 IP from Client2:

```bash
ping -c 1 10.90.1.1
```

Output:
```bash
PING 10.90.1.1 (10.90.1.1): 56 data bytes
64 bytes from 10.90.1.1: seq=0 ttl=253 time=2.208 ms

--- 10.90.1.1 ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss
round-trip min/avg/max = 2.208/2.208/2.208 ms
```

Let's understand how this ping worked.

On Client2, there is a static route defined for destination 10.90.1.0/24 with Leaf1 as next-hop. This can be verified using `ip r` command on the Client.

```bash
/ # ip r
default via 172.20.20.1 dev eth0
10.80.1.0/24 dev eth1 scope link  src 10.80.1.1
10.90.1.0/24 via 10.80.1.2 dev eth1
172.20.20.0/24 dev eth0 scope link  src 172.20.20.4
```

When the ICMP ping packet reaches Leaf1, it checks the destination IP (10.90.1.1) against it's route-table. As seen in the above route-table output, the next-hop for this destination is a VXLAN tunnel to 2.2.2.2 (Leaf2) with VNI 200.

The ICMP packet is encapsulated in VXLAN and sent to 2.2.2.2 (Leaf2). On Leaf2, the VXLAN encapsulation is removed and the ICMP packet is forwarded to the Client. The ping reponse follows similar path back to Leaf1.

## Bonus - Interconnecting Layer 2 and Layer 3 using IRB

In this section, our objective is to connect the MAC-VRF to IP-VRF so that Client1 (using IP 172.16.10.50) is able to ping Client4 (10.90.1.1).

Typical use case is when there is a mix of Layer 2 and Layer 3 devices within the same client network.

We will use an IRB (Integrated Routing and Bridging) to inter-connect Layer 2 ( mac-vrf) and Layer 3 (ip-vrf).

![image](../images/bonus-irb.jpg)

### IRB Configuration

The IP address on the IRB will act as a gateway for Layer 2 devices.

IRB configuration on Leaf1:

```srl
set / interface irb1 admin-state enable
set / interface irb1 subinterface 100 ipv4 admin-state enable
set / interface irb1 subinterface 100 ipv4 address 172.16.10.254/24
set / interface irb1 subinterface 100 ipv4 arp evpn advertise dynamic
```

IRB configuration on Leaf2:

```srl
set / interface irb1 admin-state enable
set / interface irb1 subinterface 100 ipv4 admin-state enable
set / interface irb1 subinterface 100 ipv4 address 172.16.10.253/24
set / interface irb1 subinterface 100 ipv4 arp evpn advertise dynamic
```

### Attaching IRB to MAC-VRF and IP-VRF

The same IRB interface is now attached to both network instances.

On Leaf1:

```srl
set / network-instance mac-vrf-1 interface irb1.100
set / network-instance ip-vrf-1 interface irb1.100
```

On Leaf2:

```srl
set / network-instance mac-vrf-1 interface irb1.100
set / network-instance ip-vrf-1 interface irb1.100
```

### Ping between Client 1 & 4

Login to Client 1 using `sudo docker exec –it client1 bash`.

Ping Client4 IP from Client1:

```bash
/ # ping 10.90.1.1
PING 10.90.1.1 (10.90.1.1): 56 data bytes
64 bytes from 10.90.1.1: seq=1 ttl=63 time=755.807 ms
64 bytes from 10.90.1.1: seq=2 ttl=63 time=0.905 ms
64 bytes from 10.90.1.1: seq=3 ttl=63 time=0.707 ms
64 bytes from 10.90.1.1: seq=4 ttl=63 time=0.871 ms
64 bytes from 10.90.1.1: seq=5 ttl=63 time=0.783 ms
^C
--- 10.90.1.1 ping statistics ---
6 packets transmitted, 5 packets received, 16% packet loss
round-trip min/avg/max = 0.707/151.814/755.807 ms
```

By now, you should have an understanding of how this ping worked. If you have questions, please raise your hand and a Nokia team member will be happy to help.

## Explore this lab with everything pre-configured

If you would like to explore all of the above without doing any manual configurations, we got you covered !

Go to [Complete startup config](configs/startup-complete) to see the full configuration for each device.

In your topology file (srl-evpn.clab.yml), point the startup config file location to `configs/startup-complete/leaf1-startup-complete.cfg` (for Leaf1).

Destroy any existing lab using the command `sudo clab destroy -t srl-evpn.clab.yml --cleanup`.

Then deploy the lab using `sudo clab deploy -t srl-evpn.clab.yml`.

## Useful links

* [containerlab](https://containerlab.dev/)
* [gNMIc](https://gnmic.openconfig.net/)

### SR Linux
* [SR Linux documentation](https://documentation.nokia.com/srlinux/)
* [Learn SR Linux](https://learn.srlinux.dev/)
* [YANG Browser](https://yang.srlinux.dev/)
* [gNxI Browser](https://gnxi.srlinux.dev/)
* [Ansible Collection](https://learn.srlinux.dev/ansible/collection/)
