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

As you can see, this topo file is not a joke, and once the deployment finishes, you might want to understand what exactly was deployed and how the topology is structured. Enter graphs.

## Containerlab and graphing options

When your topology has 3-5 nodes and a few links, you can easily visualize the topology in your head, but once your lab grows bigger, with more nodes involved and more links created, it becomes harder to remember what is what and where.

To help you with visualizing the topology, containerlab provides a few graphing options (<https://containerlab.dev/cmd/graph/>) that we will explore briefly.

### Web graph

After you deployed the lab, run the `graph` command:

```
cd ~/srl-telemetry-lab
sudo clab graph
```

The local web server provided by containerlab will be welcoming you at `http://<ID>.wrkshpz.net:50080` where `<ID>` is your ID. The web server will render the deployed topology in an interactive graph that you can sort vertically or horizontally.

The `group` options on the node level help you to order the lab nodes in the graph.

### Drawio export

The web graph is great, but has a number of limitations:

- Not editable
- Opinionated
- Only one ”pane” - physical

To combat these limitations, another project has been created in the containerlab ecosystem - [clab-io-draw](https://github.com/srl-labs/clab-io-draw).

It allows to generate a drawio topology from a containerlab topology and does so with style!

```bash
sudo clab graph --drawio --drawio-args "--theme grafana_dark"
```

It has many neat options, so please go checkout the readme file at the projects' repo.
