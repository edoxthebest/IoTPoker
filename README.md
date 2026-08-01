# IoT:Poker

IoT:Poker is a Python library that provides utilities for constructing a Symbolic Information Flow Graph for a given IoT policy configuration, as presented in the corresponding paper "Checking Information Flow in Cloud-based IoT Access Control Policies" by Lorenzo Ceragioli, Letterio Galletta, and Edoardo Lunati.

We evaluate the tool’s effectiveness in detecting misconfigurations and unintended information flows using a case study designed to capture a typical Build Automation System. Although synthetic, the case study reflects the main structural constraints and operational patterns of real IoT systems.

In addition, we assess the tool’s performance by randomly synthesising a network of devices and associating them with real-world IoT policies available online [15, in the related paper]: we show that IoT:Poker scales well in practice as the network grows.
## Installation
A docker image is provided to run the tool without installing any dependencies. To build the docker image, run the following command:

```bash
docker build -t iotpoker .
```

## Manual installation

The library requires the following packages:

- Python (3.10),
- matplotlib (3.8.4),
- networkx (3.3),
- policyuniverse (1.5.1.20231109),
- z3_solver (4.13.0.0),
- cvc5 (1.3.0),

which can be installed by running the command:

```bash
pip install -r policytool/requirements.txt
```

## Experiments of the paper

### RQ1: Does IoT:Poker effectively prove/disprove functional and security properties for a real-size IoT configuration?

To reproduce the experiment of the tool on the case study discussed in the paper use the following command:

```bash
docker run --rm iotpoker case-study
```
or, alternatively, if you have installed the dependencies manually, run:
```bash
python case_study_demo.py
```

This will load the configuration file provided in `case_study.config`, construct the corresponding Symbolic Information Flow Graph, and execute some reachability queries on the resulting graph.

#### Detailed queries

The following table corresponds to Table 1 of the paper.

| query           | parameter 1             | parameter 2                                                                                           | result | reason & witness                                                   | time (ms) |
| --------------- | ----------------------- | ----------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------ | --------: |
| reach           | `presenceSensor1`       | `floor1_light`                                                                                        | True   | `presenceSensor1` &rarr; `light1`                                  |        <1 |
| reach           | `floor1_smoke_sensor`   | `elevator`                                                                                            | True   | `floor1_smoke_sensor` &rarr; `lambda_fire_alarm` &rarr; `elevator` |        <1 |
| isolated        | `[floor1_badge_reader]` | `[floor1_water_pump, elevator]`                                                                       | True   |                                                                    |        <1 |
| only_reached_by | `elevator`              | `[floor1_smoke_sensor, floor2_smoke_sensor, floor1_fire_alarm, floor2_fire_alarm, lambda_fire_alarm]` | True   |                                                                    |        <1 |
| reach_only      | `floor1_door_lock`      | `[floor1_light, presenceSensor1, lambda_logger]`                                                      | False  | `floor1_light` &rarr; `presenceSensor1` &rarr; `floor2_light`      |        <1 |

More queries are shown in the following table.

| query           | parameter 1                    | parameter 2                                                                                                     | return | reason                                                                                       | time (ms) |
| --------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------- | --------: |
| reach           | `floor1_door_lock`             | `floor2_light`                                                                                                  | True   | `floor1_door_lock` &rarr; `presenceSensor1` &rarr; `floor2_light`                            |        <1 |
| reach           | `elevator`                     | `floor1_door_lock`                                                                                              | False  |                                                                                              |        <1 |
| reach_only      | `elevator`                     | `[]`                                                                                                            | True   |                                                                                              |        <1 |
| reach_only      | `floor1_smoke_sensor`          | `[elevator, floor1_door_lock]`                                                                                  | False  | Found 10 violating paths.                                                                    |        <1 |
| reach_only      | `elevator`                     | `[floor2_water_pump]`                                                                                           | False  | Missing path.                                                                                |        <1 |
| only_reached_by | `floor1_fire_alarm`            | `[floor1_smoke_sensor, floor2_smoke_sensor, floor1_fire_alarm, floor2_fire_alarm, lambda_fire_alarm, elevator]` | False  | Missing path to `elevator`.                                                                  |        <1 |
| only_reached_by | `floor1_light`                 | `[lambda_fire_alarm]`                                                                                           | False  | Found 11 violating paths.                                                                    |        <1 |
| isolated        | `[floor2_badge_reader]`        | `[lambda_fire_alarm, elevator, floor2_smoke_sensor]`                                                            | True   |                                                                                              |        <1 |
| isolated        | `[floor1_light, floor2_light]` | `[lambda_fire_alarm, elevator, floor2_smoke_sensor]`                                                            | False  | `lambda_fire_alarm` &rarr; `floor1_door_lock` &rarr; `presenceSensor1` &rarr; `floor1_light` |        <1 |

### RQ2: How does IoT:Poker scale when an IoT configuration's size (number of certificates) grows?

The code provided in `real_world_benchmark.py` will instead construct graphs of different sizes loading policies at random from a specified configuration folder.
The following command reproduce the experiments using the generated sequence of certificates to use which can be found in `test.perms`.

```bash
docker run --rm -it iotpoker benchmark
```
or
```bash
python real_world_benchmark.py tests/policies/policy_benchmark/FLAW1 -c 30 --seq 20 40 60 80 100 120 140 160 180 200 220 240 258 -C
```

#### Average performance over 30 executions:

The following tables correspond to Table 3 of the paper, comparing the execution times of the two SMT solvers.

| Size | Nodes   | Hard strategies | Graph time min. \[cvc5\] (s) | Graph time min. \[z3\] (s) | Graph time avg. \[cvc5\] (s) | Graph time avg. \[z3\] (s) | Graph time max. \[cvc5\] (s) | Graph time max. \[z3\] (s) | 1000 queries time (s) |
| ---- | ------- | --------------- | ---------------------------- | -------------------------- | ---------------------------- | -------------------------- | ---------------------------- | -------------------------- | --------------------- |
| 20   | 264.6   | 1.8             | 0.42                         | 1.22                       | 2.87                         | 4.94                       | 12.00                        | 10.69                      | 0.0060                |
| 40   | 973.0   | 4.5             | 2.30                         | 6.17                       | 6.28                         | 12.64                      | 16.55                        | 20.28                      | 0.0086                |
| 60   | 2211.2  | 5.6             | 2.93                         | 7.04                       | 9.22                         | 18.22                      | 23.39                        | 30.00                      | 0.0108                |
| 80   | 3903.9  | 13.6            | 5.93                         | 18.67                      | 16.34                        | 30.72                      | 29.08                        | 47.88                      | 0.0136                |
| 100  | 6098.1  | 16.7            | 7.50                         | 18.89                      | 19.46                        | 39.82                      | 36.55                        | 58.76                      | 0.0167                |
| 120  | 8764.2  | 21.5            | 13.58                        | 35.17                      | 24.69                        | 52.35                      | 41.49                        | 87.98                      | 0.0198                |
| 140  | 12080.1 | 28.7            | 18.61                        | 42.75                      | 31.06                        | 64.81                      | 46.63                        | 100.06                     | 0.0244                |
| 160  | 15415.9 | 29.6            | 20.03                        | 51.89                      | 33.01                        | 72.11                      | 44.43                        | 90.16                      | 0.0280                |
| 180  | 19571.7 | 37.0            | 26.61                        | 69.91                      | 37.87                        | 86.89                      | 52.79                        | 109.81                     | 0.0318                |
| 200  | 24209.9 | 45.8            | 31.62                        | 78.76                      | 46.06                        | 103.63                     | 57.34                        | 125.65                     | 0.0349                |
| 220  | 29066.2 | 50.5            | 32.39                        | 95.42                      | 50.93                        | 117.21                     | 62.02                        | 129.81                     | 0.0393                |
| 240  | 34732.6 | 59.0            | 42.11                        | 114.48                     | 57.68                        | 130.17                     | 62.41                        | 141.43                     | 0.0430                |
| 258  | 40019.0 | 65.0            | 62.35                        | 141.24                     | 62.67                        | 144.20                     | 63.53                        | 152.19                     | 0.0473                |

#### Solver frequency and average time
To answer how frequently each solver is used and the average time spent on each solver, the following experiment can be run:

```bash
docker run --rm -it iotpoker benchmark-solvers
```
or, alternatively,
```bash
python real_world_benchmark_solvers.py tests/policies/policy_benchmark/FLAW1
``` 