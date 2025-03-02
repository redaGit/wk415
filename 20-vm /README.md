# VM-based nodes in containerlab

VM nodes integration in containerlab is based on the [hellt/vrnetlab](https://github.com/hellt/vrnetlab) project which is a fork of `vrnetlab/vrnetlab` where things were added to make it work with the container networking.

Start with cloning the project:

```bash
cd ~ && git clone https://github.com/hellt/vrnetlab.git && \
cd ~/vrnetlab
```

## Building SR OS container image

SR OS VM image is located at `~/images/sros-vm-24.7.R1.qcow2` on your VM and should be copied to the `~/vrnetlab/sros/` directory before building the container image.

```bash
cp ~/images/sros-vm-24.7.R1.qcow2 ~/vrnetlab/sros/
```

Once copied, we can enter in the `~/vrnetlab/sros` image and build the container image:

```bash
cd ~/vrnetlab/sros && make
```

The resulting image will be tagged as `vrnetlab/nokia_sros:24.7.R1`. This can be verified using `docker images` command.

```bash
REPOSITORY                    TAG       IMAGE ID       CREATED         SIZE
vrnetlab/nokia_sros           24.7.R1   553e94475c12   7 seconds ago   889MB
```

## JUNOS OS container image

Junos VM docker image is already prepared and is located at `~/images/vr-vmx.tar.gz` on your VM.

Import this image into docker.

```
docker load -i ~/images/vr-vmx.tar.gz
```

Check local docker image repo and verify that the vmx image is present.

```
docker images
```

Expected output:

```
REPOSITORY                                       TAG         IMAGE ID       CREATED         SIZE
registry.srlinux.dev/pub/vr-vmx                  bb          877650904adc   2 years ago     10.6GB
```

## Deploying the VM-based nodes lab

With the sros and junos image built, we can proceed with the lab deployment. We will deploy a lab with sros, junos and SR Linux to show that Containerlab can have a VM based docker node and a native docker node in the same lab.

First, let's switch back to the lab directory:

```bash
cd ~/cwrk/20-vm
```

Now lets deploy the lab:

```bash
sudo clab dep -c
```

At the end of the deployment, the following table will be displayed. Wait for the sonic boot to be completed (see next section), before trying to login to sonic.

```bash
+---+---------------+--------------+--------------------------------+---------------+---------+----------------+----------------------+
| # |     Name      | Container ID |             Image              |     Kind      |  State  |  IPv4 Address  |     IPv6 Address     |
+---+---------------+--------------+--------------------------------+---------------+---------+----------------+----------------------+
| 1 | clab-vm-sonic | c865295f6b4e | vrnetlab/sonic_sonic-vs:202405 | sonic-vm      | running | 172.20.20.3/24 | 3fff:172:20:20::3/64 |
| 2 | clab-vm-srl   | 51b41a280f84 | ghcr.io/nokia/srlinux          | nokia_srlinux | running | 172.20.20.2/24 | 3fff:172:20:20::2/64 |
+---+---------------+--------------+--------------------------------+---------------+---------+----------------+----------------------+
```



### Monitoring the boot process

To monitor the boot process of SR OS nodes or Cisco XRd node, you can open a new terminal and run the following command:

```bash
sudo docker logs -f pe1-sr1
```

## Connecting to the nodes

To connect to SR OS node:

```bash
ssh admin@pe1-sr1
```

To connect to SR Linux node:

```bash
ssh pe2-srL
```

To connect to Junos node:

```bash
ssh ????
```

Refer to the passwords in your card.

## Configuring the nodes

Login to SR Linux node and run `enter candidate` to get into configuration edit mode and paste the below lines to configure the interface:

```srl
set / interface ethernet-1/1 admin-state enable
set / interface ethernet-1/1 subinterface 0 ipv4 admin-state enable
set / interface ethernet-1/1 subinterface 0 ipv4 address 10.0.0.1/31
set / network-instance default type default
set / network-instance default interface ethernet-1/1.0
```
Once configured issue the `commit now` command to make sure the candidate config is merged into running.

Now we configured the two systems to be able to communicate with each other. Perform a ping from SONiC to SR Linux:

```bash
admin@sonic:~$ ping 10.0.0.1 -c 3
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=2.00 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=1.97 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=3.17 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 1.965/2.378/3.168/0.558 ms
```

We have now completed the section on bring VM based nodes into Containerlab.
