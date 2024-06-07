# IoT:Poker

IoT:Poker is a Python library which provides utilities to construct a Symbolic Information Flow Graph of a given IoT policy configuration.

## Requirements

The library requires the following packages:

- matplotlib (3.8.4),
- networkx (3.3),
- policyuniverse (1.5.1.20231109),
- z3_solver (4.13.0.0),

which can be installed by running the command:

```bash
pip install -r policytool/requirements.txt
```

## Demos

### Case study

A detailed demo of the tool on the case study discussed in the paper can be produced by executing the following:

```bash
python case_study_demo.py
```

This will load the configuration file provided in `case_study.config`, construct the corresponding Symbolic Information Flow Graph, and execute some reachability queries on the resulting graph.

### Scalability analysis

The code provided in `real_world_benchmark.py` will instead construct graphs of different sizes loading policies at random from a specified configuration folder.
A performance evaluation is detailed in the following sections.

## Performance

| Syntax    | Description |
| --------- | ----------- |
| Header    | Title       |
| Paragraph | Text        |
