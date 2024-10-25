# IoT:Poker

IoT:Poker is a Python library which provides utilities to construct a Symbolic Information Flow Graph of a given IoT policy configuration.

## Requirements

The library requires the following packages:

- Python (3.10),
- matplotlib (3.8.4),
- networkx (3.3),
- policyuniverse (1.5.1.20231109),
- z3_solver (4.13.0.0),

which can be installed by running the command:

```bash
pip install -r policytool/requirements.txt
```

## Experiments of the paper

### RQ1: Does IoT:Poker effectively prove/disprove functional and security properties for a real-size IoT configuration?

To reproduce the experiment of the tool on the case study discussed in the paper use the following command:

```bash
python case_study_demo.py
```

This will load the configuration file provided in `case_study.config`, construct the corresponding Symbolic Information Flow Graph, and execute some reachability queries on the resulting graph.

#### Detailed queries

The following table corresponds to Table 1 of the paper.

| query           | parameter 1                    | parameter 2                                                                                                     | return | reason                                                                                       | time (ms) |
| --------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------- | --------: |
| reach           | `floor1_door_lock`             | `floor2_light`                                                                                                  | True   | `floor1_door_lock` &rarr; `presenceSensor1` &rarr; `floor2_light`                            |        <1 |
| reach           | `elevator`                     | `floor1_door_lock`                                                                                              | False  |                                                                                              |        <1 |
| reach_only      | `elevator`                     | `[]`                                                                                                            | True   |                                                                                              |        <1 |
| reach_only      | `floor1_door_lock`             | `[floor1_light, presenceSensor1, lambda_logger]`                                                                | False  | `floor1_light` &rarr; `presenceSensor1` &rarr; `floor2_light`                                |        <1 |
| reach_only      | `floor1_smoke_sensor`          | `[elevator, floor1_door_lock]`                                                                                  | False  | Found 11 violating paths.                                                                    |        <1 |
| reach_only      | `elevator`                     | `[floor2_water_pump]`                                                                                           | False  | Missing path.                                                                                |        <1 |
| only_reached_by | `elevator`                     | `[floor1_smoke_sensor, floor2_smoke_sensor, floor1_fire_alarm, floor2_fire_alarm, lambda_fire_alarm]`           | True   |                                                                                              |        <1 |
| only_reached_by | `floor1_fire_alarm`            | `[floor1_smoke_sensor, floor2_smoke_sensor, floor1_fire_alarm, floor2_fire_alarm, lambda_fire_alarm, elevator]` | False  | Missing path from `elevator`.                                                                |        <1 |
| only_reached_by | `floor1_light`                 | `[lambda_fire_alarm]`                                                                                           | False  | Found 10 violating paths.                                                                    |        <1 |
| isolated        | `[floor1_badge_reader]`        | `[floor1_water_pump, elevator]`                                                                                 | True   |                                                                                              |        <1 |
| isolated        | `[floor2_badge_reader]`        | `[lambda_fire_alarm, elevator, floor2_smoke_sensor]`                                                            | True   |                                                                                              |        <1 |
| isolated        | `[floor1_light, floor2_light]` | `[lambda_fire_alarm, elevator, floor2_smoke_sensor]`                                                            | False  | `lambda_fire_alarm` &rarr; `floor1_door_lock` &rarr; `presenceSensor1` &rarr; `floor1_light` |        <1 |

### RQ2: How does IoT:Poker scale when an IoT configuration's size (number of certificates) grows?

The code provided in `real_world_benchmark.py` will instead construct graphs of different sizes loading policies at random from a specified configuration folder.
The following command reproduce the experiments.

```bash
python real_world_benchmark.py tests/policies/policy_benchmark/FLAW1 -c 30 --seq 20 40 60 80 100
```

#### Average performance over 30 executions:

The following table corresponds to Table 2 of the paper.

| Size | Nodes  | Hard strategies | Graph time (s) | 1000 queries time (s) |
| ---- | ------ | --------------- | -------------- | --------------------- |
| 20   | 280.8  | 4.2             | 11.921         | 0.0063                |
| 40   | 995.4  | 11.4            | 38.693         | 0.0082                |
| 60   | 2213.2 | 22.0            | 68.082         | 0.0115                |
| 80   | 4014.8 | 36.3            | 128.33         | 0.0141                |
| 90   | 4962.0 | 49.5            | 181.66         | 0.0153                |
| 100  | 6344.3 | 49.4            | 179.26         | 0.0172                |

#### Fastest and slowest runs details:

|         | Size | Nodes | Hard strategies | Graph time (s) |
| ------- | ---- | ----- | --------------- | -------------- |
| Fastest | 20   | 396   | 0               | 0.65           |
|         | 40   | 852   | 0               | 3.47           |
|         | 60   | 1802  | 7               | 22.22          |
|         | 80   | 3527  | 11              | 46.18          |
|         | 90   | 4518  | 31              | 65.06          |
|         | 100  | 5803  | 19              | 57.78          |
|         |      |       |                 |
| Slowest | 20   | 205   | 13              | 63.54          |
|         | 40   | 983   | 28              | 150.48         |
|         | 60   | 2268  | 56              | 189.75         |
|         | 80   | 4612  | 69              | 249.5          |
|         | 90   | 4967  | 91              | 293.24         |
|         | 100  | 7082  | 90              | 261.55         |
