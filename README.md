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

## Experiments of the paper

### RQ1: Does IoT:Poker effectively prove/disprove functional and security properties for a real-size IoT configuration?

To reproduce the experiment of the tool on the case study discussed in the paper use the following command:

```bash
python case_study_demo.py
```

This will load the configuration file provided in `case_study.config`, construct the corresponding Symbolic Information Flow Graph, and execute some reachability queries on the resulting graph.

### RQ2: How does IoT:Poker scale when an IoT configuration's size (number of certificates) grows?

The code provided in `real_world_benchmark.py` will instead construct graphs of different sizes loading policies at random from a specified configuration folder.
A performance evaluation is detailed in the following sections.

#### Average performance over 10 executions:

| Policy Pool     | Size | Nodes  | Graph time (s) | 1000 queries time (s) |
| --------------- | ---- | ------ | -------------- | --------------------- |
| case-study      | 1    | 0      | 0.0444863      | 0.00660214            |
| case-study      | 2    | 1.2    | 0.1547626      | 0.00600495            |
| case-study      | 4    | 2.1    | 0.4027572      | 0.00605094            |
| case-study      | 8    | 8.2    | 1.4861627      | 0.00773758            |
| case-study      | 16   | 24.9   | 6.9089985      | 0.00842836            |
| case-study      | 32   | 116.6  | 22.412111      | 0.01036623            |
| case-study      | 64   | 386.8  | 91.154251      | 0.01745937            |
| case-study      | 128  | 1473.8 | 361.96051      | 0.03149600            |
| secure          | 1    | 0      | 0.0151731      | 0.00332294            |
| secure          | 2    | 0      | 0.0606074      | 0.02976060            |
| secure          | 4    | 0      | 0.2370243      | 0.02777078            |
| secure          | 8    | 0      | 0.9311338      | 0.02638292            |
| secure          | 16   | 0      | 3.7048442      | 0.02628827            |
| secure          | 32   | 0      | 14.729268      | 0.02929783            |
| secure          | 64   | 0      | 58.951998      | 0.00278075            |
| secure          | 128  | 0      | 234.11445      | 0.00297205            |
| flawed + secure | 1    | 0.4    | 0.0738048      | 0.00307925            |
| flawed + secure | 2    | 0.4    | 0.6222871      | 0.00272455            |
| flawed + secure | 4    | 3.8    | 1.7949341      | 0.00293033            |
| flawed + secure | 8    | 11.4   | 3.2338835      | 0.00337193            |
| flawed + secure | 16   | 37.2   | 12.904390      | 0.00386884            |
| flawed + secure | 32   | 137.1  | 47.877657      | 0.00416610            |
| flawed + secure | 64   | 471.9  | 182.77990      | 0.00486009            |
| flawed + secure | 128  | 2027.6 | 966.47158      | 0.00744104            |
