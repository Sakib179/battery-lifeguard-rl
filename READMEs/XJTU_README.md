# README

This dataset consists of 55 18650 nickel-cobalt-manganese (NCM) Li-ion batteries manufactured by LISHEN. The chemical composition is LiNi0.5Co0.2Mn0.3O2. The nominal capacity is 2000 mAh, the nominal voltage is 3.6 V, and the charging and discharging cut-off voltages are 4.2 V and 2.5 V, respectively. All batteries were cycled to failure at room temperature under 6 charge/discharge protocols. Batch 1 to batch 6 represent the 6 protocols: 2 C CC-CV charge and 1 C discharge to 2.5 V, 3 C CC-CV charge and 1 C discharge to 2.5 V, 2 C CC-CV charge and discharge to 2.5 V with a current value of x C where x is in {0.5, 1, 2, 3, 5}, 2 C CC-CV charge and discharge to 3.0 V with the same current values as batch 3, 1 C CC-CV charge to 4.2 V followed by random-walk discharge to 3.0 V with a random integer current in [2, 8] A for [2, 6] minutes, and a geosynchronous-earth-orbit satellite cycling strategy. All batches contain 8 batteries except batch 2, which contains 15 batteries.



If you use this dataset, please cite the original papers:

- **Physics-informed neural network for lithium-ion battery degradation stable modeling and prognosis** *2024 Nature Communications*



| Battery Number | Format | Chemical System | Operation Temperature | Protocol | Data Source | Battery Type | Year |
| -------------- | ------ | --------------- | --------------------- | -------- | ----------- | ------------ | ---- |
| 55             | 1      | 1               | 1                     | 6        | Lab test    | Li-ion       | 2024 |



The original datasets are available at:

- [Project - Physics-informed neural network for lithium-ion battery degradation stable modeling and prognosis (zenodo.org)](https://zenodo.org/records/10963339)
