# Lab Topology

![image](ip-vpn-topology.jpg)

# Deploying the lab

To deploy the lab, run the following:

```bash
cd ~/cwrk/ipvpn
sudo clab deploy -t vm.clab.yml
```

Containerlab will deploy the lab and display a table with the list of nodes and their IPs.

```bash
╭──────┬──────────────────────────────┬─────────┬───────────────────╮
│ Name │          Kind/Image          │  State  │   IPv4/6 Address  │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ cea1 │ nokia_srlinux                │ running │ 172.20.20.6       │
│      │ ghcr.io/nokia/srlinux:25.3.1 │         │ 3fff:172:20:20::6 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ cea2 │ nokia_srlinux                │ running │ 172.20.20.7       │
│      │ ghcr.io/nokia/srlinux:25.3.1 │         │ 3fff:172:20:20::7 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ cez1 │ nokia_srlinux                │ running │ 172.20.20.3       │
│      │ ghcr.io/nokia/srlinux:25.3.1 │         │ 3fff:172:20:20::3 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ cez2 │ nokia_srlinux                │ running │ 172.20.20.5       │
│      │ ghcr.io/nokia/srlinux:25.3.1 │         │ 3fff:172:20:20::5 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ p1   │ nokia_sros                   │ running │ 172.20.20.2       │
│      │ vrnetlab/nokia_sros:25.3.R1  │         │ 3fff:172:20:20::2 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ p2   │ nokia_sros                   │ running │ 172.20.20.4       │
│      │ vrnetlab/nokia_sros:25.3.R1  │         │ 3fff:172:20:20::4 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ p3   │ nokia_sros                   │ running │ 172.20.20.8       │
│      │ vrnetlab/nokia_sros:25.3.R1  │         │ 3fff:172:20:20::8 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ p4   │ nokia_sros                   │ running │ 172.20.20.9       │
│      │ vrnetlab/nokia_sros:25.3.R1  │         │ 3fff:172:20:20::9 │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ pe1  │ nokia_srlinux                │ running │ 172.20.20.11      │
│      │ ghcr.io/nokia/srlinux:25.3.1 │         │ 3fff:172:20:20::b │
├──────┼──────────────────────────────┼─────────┼───────────────────┤
│ pe2  │ nokia_srlinux                │ running │ 172.20.20.10      │
│      │ ghcr.io/nokia/srlinux:25.3.1 │         │ 3fff:172:20:20::a │
╰──────┴──────────────────────────────┴─────────┴───────────────────╯
```


