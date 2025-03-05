# Streaming Telemetry Lab

When pulling together what we have learned so far, we can build a lab that embodies a lot of what containerlab has to offer. One of the labs that we've built to demonstrate the power of containerlab is the [Streaming Telemetry Lab](https://github.com/srl-labs/srl-telemetry-lab).

To deploy this lab we will use another neat containerlab feature - the ability to deploy a lab by specifying lab's remote URL. For the labs stored as a repo on GitHub we could even use the shorthand syntax:

```bash
cd ~
sudo containerlab deploy -t srl-labs/srl-telemetry-lab
```

This will pull down the repository and deploy the lab right away.

## Exploring the topology file

The streaming telemetry lab' [topology file](https://github.com/srl-labs/srl-telemetry-lab/blob/main/st.clab.yml) is worth a closer look. It features:

- customization of the management network
- use of `defaults` and `kinds` sections to simplify the topology file
- static management IPs for consistency
- combination of network OSes and "regular" containerized workloads like iperf clients, streaming telemetry and logging stack
- use of the bind mounts to load the configuration files
- use of env vars to parametrize the started containers
- `exec` command to run commands in the started containers
- port exposure to the host to make the lab services accessible from the outside
- using of `group` parameter to influence lab nodes ordering in the graph products

## Start Grafana 

Using your laptop browser
- http://<id>.wrkshpz.net:3000
- Dashboards
- Network Telemetry

## Start traffic 

```bash
cd srl-telemetry-lab
```

```bash
./traffic.sh start all
```



