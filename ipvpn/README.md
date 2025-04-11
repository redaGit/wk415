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

To display all deployed labs on your VM at any time, use:

```bash
sudo clab inspect --all
```

## Connecting to the devices

Find the nodename or IP address of the device from the above output and then use SSH.

```bash
ssh pe1
```

To login to the client, identify the client hostname using the `sudo clab inspect --all` command above and then:

```bash
sudo docker exec –it client3 bash
```

## Physical link connectivity

We will be using [Openconfig](https://www.openconfig.net/) to configure the following:

- Configure interfaces between PE and P nodes
- Configure interface between PE and CE nodes
- Configure system loopback on PE
- Configure default Network Instance (VRF) and add system loopback and Leaf/Spine interfaces to this VRF

We will use [gRPC gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/) to push the configuration to the devices.

[gNMIc](https://gnmic.openconfig.net/) is the most widely used client for gNMI and we will use that for this purpose.

The Openconfig configuration files are located at [configs/oc/](./configs/oc).

Before we start, verify the current configured interfaces on PE1 or PE2.

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

## Using gNMI to push Openconfig

Exit from SR Linux and on your VM, run the following commands to push the configuration in the files to the devices. There is no native configuration for spine as all required configs are covered in Openconfig.

```
gnmic -a 
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

Now that the interfaces are configured, check reachability between PE and P devices using ping.

Example on PE1 to P1:

```srl
ping -c 3 10.0.0.1 network-instance default
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
| Exit from the node | `quit` or `CTRL+d` |


