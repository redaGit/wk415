# Containerlab Basics

This workshop section introduces you to containerlab basics - topology file, image management workflows and lab lifecycle. It is loosely based on the official [Containerlab quickstart](https://containerlab.dev/quickstart/).

## Repository

Clone this repository to your workshop VM:

```bash
cd ~ && git clone https://github.com/redaGit/wk415.git \
&& cd wk415/10-basics
``` 

The repo should be cloned and you should be in the `wk415` directory as per the output below:

```
nokiauser@2: cd ~/wk415/10-basics$ 
```

## Topology

The topology file `basic.clab.yml` defines the lab we are going to use in this basics exercise. It consists of the two nodes:

* Nokia SR Linux
* Arista cEOS

The nodes are interconnected with a single link over their respective first Ethernet interfaces.

```yaml
name: basic
topology:
  nodes:
    srl:
      kind: nokia_srlinux
      image: ghcr.io/nokia/srlinux
    ceos:
      kind: arista_ceos
      image: ceos:4.33.0F

  links:
    - endpoints: [srl:e1-1, ceos:eth1]
```

## Image management

Check what images are available on the system:

```bash
sudo docker images
```

Pull SR Linux container image available for free:

```bash
sudo docker pull ghcr.io/nokia/srlinux
```

Import cEOS image located stored on your VM and pay attention to the 2nd argument for the `docker import` command where you have to specify the image:

```bash
sudo docker import ~/images/cEOS64-lab-4.33.0F.tar ceos:4.33.0F
```

Expected output:

```bash
sha256:f4c604a5da646b0b1fa5a895086465472aa1f25c386ebc8aa2e6e72de277e618
```

Check the local image store again:

```bash
sudo docker images
```

Expected output:

```bash
REPOSITORY              TAG       IMAGE ID       CREATED          SIZE
ceos                    4.33.0F   927c8cd41224   34 seconds ago   2.46GB
ghcr.io/nokia/srlinux   latest    eb2a823cd8ce   8 days ago       2.35GB
hello-world             latest    d2c94e258dcb   18 months ago    13.3kB
```

## Deploy the lab

Now that the images are available, try to deploy the lab:

```bash
sudo clab dep -t basic.clab.yml
```

The deployment should succeed and a table will be displayed with the list of nodes and their management IPs.

```bash
╭─────────────────┬───────────────────────┬─────────┬───────────────────╮
│       Name      │       Kind/Image      │  State  │   IPv4/6 Address  │
├─────────────────┼───────────────────────┼─────────┼───────────────────┤
│ clab-basic-ceos │ arista_ceos           │ running │ 172.20.20.2       │
│                 │ ceos:4.33.0F          │         │ 3fff:172:20:20::2 │
├─────────────────┼───────────────────────┼─────────┼───────────────────┤
│ clab-basic-srl  │ nokia_srlinux         │ running │ 172.20.20.3       │
│                 │ ghcr.io/nokia/srlinux │         │ 3fff:172:20:20::3 │
╰─────────────────┴───────────────────────┴─────────┴───────────────────╯
```

## Connecting to the nodes

Connect to the Nokia SR Linux node using the container name:

```bash
ssh clab-basic-srl
```

Connect to cEOS node using its hostname or IP address. Refer to the card for password.

```bash
ssh admin@172.20.20.2
```

## Containerlab hosts automation

Containerlab creates `/etc/hosts` entries for each deployed lab so that you can access the nodes using their names. Check the entries:

```bash
cat /etc/hosts
```

## Checking network connectivity

SR Linux and cEOS are started with their first Ethernet interfaces connected. Check the connectivity between the nodes:

The nodes also come up with LLDP enabled, our goal is to verify that the basic network connectivity is working by inspecting

```bash
ssh clab-basic-srl
```

and checking the LLDP neighbors on ethernet-1/1 interface

```
show /system lldp neighbor interface ethernet-1/1
```

The expected output should be:

```
--{ running }--[  ]--
A:srl# show /system lldp neighbor interface ethernet-1/1
  +----------+----------+---------+---------+---------+---------+---------+
  |   Name   | Neighbor | Neighbo | Neighbo | Neighbo | Neighbo | Neighbo |
  |          |          |    r    |    r    | r First | r Last  | r Port  |
  |          |          | System  | Chassis | Message | Update  |         |
  |          |          |  Name   |   ID    |         |         |         |
  +==========+==========+=========+=========+=========+=========+=========+
  | ethernet | 00:1C:73 | ceos    | 00:1C:7 | 20      | 16      | Etherne |
  | -1/1     | :46:95:5 |         | 3:46:95 | hours   | seconds | t1      |
  |          | C        |         | :5C     | ago     | ago     |         |
  +----------+----------+---------+---------+---------+---------+---------+
```

## Listing running labs

When you are in the directory that contains the lab file, you can list the nodes of that lab simply by running:

```bash
sudo clab inspect
```

Expected output:

```bash
12:15:59 INFO Parsing & checking topology file=basic.clab.yml
╭─────────────────┬───────────────────────┬─────────┬───────────────────╮
│       Name      │       Kind/Image      │  State  │   IPv4/6 Address  │
├─────────────────┼───────────────────────┼─────────┼───────────────────┤
│ clab-basic-ceos │ arista_ceos           │ running │ 172.20.20.2       │
│                 │ ceos:4.33.0F          │         │ 3fff:172:20:20::2 │
├─────────────────┼───────────────────────┼─────────┼───────────────────┤
│ clab-basic-srl  │ nokia_srlinux         │ running │ 172.20.20.3       │
│                 │ ghcr.io/nokia/srlinux │         │ 3fff:172:20:20::3 │
╰─────────────────┴───────────────────────┴─────────┴───────────────────╯
```

If the topology file is located in a different directory, you can specify the path to the topology file:

```bash
sudo clab inspect -t ~/wk415/10-basics/
12:15:59 INFO Parsing & checking topology file=basic.clab.yml
╭─────────────────┬───────────────────────┬─────────┬───────────────────╮
│       Name      │       Kind/Image      │  State  │   IPv4/6 Address  │
├─────────────────┼───────────────────────┼─────────┼───────────────────┤
│ clab-basic-ceos │ arista_ceos           │ running │ 172.20.20.2       │
│                 │ ceos:4.33.0F          │         │ 3fff:172:20:20::2 │
├─────────────────┼───────────────────────┼─────────┼───────────────────┤
│ clab-basic-srl  │ nokia_srlinux         │ running │ 172.20.20.3       │
│                 │ ghcr.io/nokia/srlinux │         │ 3fff:172:20:20::3 │
╰─────────────────┴───────────────────────┴─────────┴───────────────────╯
```

You can also list all running labs regardless of where their topology files are located:

```bash
sudo clab inspect --all
╭────────────────┬──────────┬─────────────────┬───────────────────────┬─────────┬───────────────────╮
│    Topology    │ Lab Name │       Name      │       Kind/Image      │  State  │   IPv4/6 Address  │
├────────────────┼──────────┼─────────────────┼───────────────────────┼─────────┼───────────────────┤
│ basic.clab.yml │ basic    │ clab-basic-ceos │ arista_ceos           │ running │ 172.20.20.2       │
│                │          │                 │ ceos:4.33.0F          │         │ 3fff:172:20:20::2 │
│                │          ├─────────────────┼───────────────────────┼─────────┼───────────────────┤
│                │          │ clab-basic-srl  │ nokia_srlinux         │ running │ 172.20.20.3       │
│                │          │                 │ ghcr.io/nokia/srlinux │         │ 3fff:172:20:20::3 │
╰────────────────┴──────────┴─────────────────┴───────────────────────┴─────────┴───────────────────╯
```

The output will contain all labs and their nodes.

Shortcuts:

* `sudo clab ins` == `sudo containerlab inspect`
* `sudo clab ins -a` == `sudo containerlab inspect --all`

## Lab directory

Lab directory stores the artifacts generated by containerlab that are related to the lab:

* tls certificates
* startup configurations
* inventory files
* topology export json file
* bind bounted directories

To list the contents of the lab directory, run:

```bash
tree -L 3 clab-basic/
```

## Destroying the lab

When you are done with the lab, you can destroy it:

```bash
sudo clab destroy -t basic.clab.yml
```

You have now finished the basics lab exercise!
