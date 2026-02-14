### Introduction

Although reactive synthesis guarantees correct-by-construction implementations, its practical adoption is limited by a performance bottleneck in the iterative design-and-refinement cycle of formal specifications. GR(1) synthesizers perform redundant, from-scratch computations for each specification modification, severely slowing the development workflow. To address this inefficiency, we propose an incremental synthesis method that exploits the monotonicity of the underlying fixed-point computations. By reusing the system winning region from the preceding check, our method significantly accelerates realizability check.

We apply our incremental analysis method to the full GR(1) specification scope, encompassing both system guarantees and environment assumptions, and introduce two novel heuristics for early fixed-point detection. Evaluated on a large-scale benchmark of 8,282 specifications, our method exhibits a strong positive correlation between performance gain and specification complexity. For the most challenging specifications, which constitute the primary bottlenecks in development, our approach achieves speedups of several orders of magnitude, reducing computation times in some cases from nearly an hour to just seconds.

### Objective. 

This artifact aims to evaluate the following four research questions:

- **RQ1:** In iterative development scenarios, does the incremental method effectively reduce realizability checking time across all atomic modification types?
- **RQ2:** How effective is the incremental method when applied to specifications with different baseline running times?
- **RQ3:** How frequently does the winning region remain unchanged after a modification, and how effective are our heuristics at exploiting this invariance?
- **RQ4:** What are the performance trade-offs between our method and conflict-producing heuristics with respect to (a) *justice guarantee reordering* and (b) *early unrealizability detection*?

### Claims.

- **For RQ1:** In iterative development scenarios, our incremental synthesis method effectively reduces realizability checking time for majority, but not all, atomic modification cases. Its performance depends on both the modification type and the realizability status of the current specification.
- **For RQ2:** The performance gain of our incremental method is not uniform; it is strongly and positively correlated with specification complexity. For simple specifications, its benefits may be negated by fixed overheads. However, for the high-complexity, long-running specifications that form the main bottlenecks in the development process, the method's optimization effect is exponentially enhanced, delivering orders-of-magnitude speedups.
- **For RQ3:** In iterative development, it is common for a specification's winning region to remain unchanged after an incremental modification. When adding justice guarantees, our proposed heuristic is effective and provides a significant additional performance boost. However, in scenarios where the winning region can be expand, the heuristic's effect is negligible and unstable.
- **For RQ4:** For adding system justice guarantees scenario, our specialized reordering heuristic provides a superior performance gain than the conflicting heuristic from prior work. Disabling the *early unrealizability detection* heuristic to ensure correctness introduces a clear performance trade-off. While it does lead to performance degradation in some scenarios, it still brings significant performance improvements in other scenarios.

### Evaluation methodology.

We designed experimental runs under various configurations, systematically varying **(i)** the realizability status of the specification (*realizable/unrealizable*), **(ii)** the synthesis approach (*baseline/incremental*), **(iii)** the type of specification modification (*EnvJAdd, EnvJSub, EnvSAdd, EnvSSub, SysJAdd, SysJSub, SysSAdd, SysSSub*), **(iv)** whether our proposed heuristics were enabled, and **(v)** whether early unrealizability detection  heuristic was disabled. For each configuration, we recorded the running times for specifications in benchmark. We then computed the *geometric mean* of the runtime ratios between the incremental and baseline approaches across all specifications in  benchmark. Additionally, we computed the number and proportion of specifications for which the system’s winning region remained unchanged. These analyses yield **Tables 2–6** in the paper, thereby providing empirical support for the claims addressing **RQ1–RQ4**.

The remainder of this document first outlines the hardware dependencies, followed by an overview of the repository structure. It then demonstrates how to execute experiments under different configurations via a smoke test, and finally explains how to apply these configurations to the full experimental evaluation.

### Hardware Dependencies:

- Our experiments do not impose stringent requirements on memory or CPU resources; however, limited RAM or a less powerful CPU will significantly increase overall execution time.
- Experimental setup used in the paper: All experiments were conducted on a server instance equipped with an Intel Xeon Gold 6330 CPU and 90 GB of RAM, running Ubuntu 22.04. We used Java 21 and a modified version of the CUDD BDD library implemented in C. Each experimental task was executed on a single CPU core. To maintain reasonable computational costs, a timeout of 60 minutes was enforced for all runs. Reported execution times are averages (in milliseconds) over one or more repetitions per experiment.
- Although the algorithms are deterministic, runtime variability introduced by JVM garbage collection and CUDD’s dynamic variable reordering may cause fluctuations in individual runtimes. As noted in **Section 4.6** of the paper, these effects are negligible and do not compromise the validity of the overall statistical conclusions.

------

### Getting Started Guide

Pull and run the Docker container:

1. `docker pull paperae/oopsla-incre-final`
2. `docker run -itd --name oopsla-inc paperae/oopsla-incre-final`
3. `docker exec -it oopsla-inc /bin/bash`
4. `cp libcudd.so /usr/lib` (important and necessary) (in `/workspace`)

#### Repository Structure Overview

The repository includes the implementation of our incremental GR(1) synthesis approach within the Spectra synthesizer, a comprehensive benchmark suite of specification sequences for evaluation (See **Section 4.2.1** in the paper), all scripts required to reproduce the experiments, and the complete set of raw performance measurement data. We use **`SysJAdd`  folder** as a representative example; other directories correspond to different types of specification modifications but share an identical structural organization.

**`SysJAdd` folder**: This denotes the scenario where system justice guarantees are *added*. It contains two subdirectories: `r` and `u`, where `r` stands for *realizable* specifications and `u` for *unrealizable* specifications.

- **`r` directory**: Contains raw performance measurement data and the benchmark suite used for  evaluation.

  - **Benchmark suite `SYNTECH_filter_60_REAL_onefolder`**: This suite comprises specification sequences used in the evaluation. For instance, the folder `1669468393_Pre` in **`SYNTECH_filter_60_REAL_onefolder`** corresponds to the specification sequence derived from the base file `1669468393.spectra` (See **Section 4.2.1** in the paper). Each such folder contains one of the four subfolders—`envJ`, `envS`, `sysJ`, and `sysS`—representing different specification statement kind to be added or deleted. In the context of `SysJAdd`, the relevant subfolder is `sysJ`, which corresponds to the *realizable* setting (`r` directory) where system justice guarantees (`sysJ`) are *progressively removed* to generate the specification sequence.

    - The `sysJ` subfolder in  folder `1669468393_Pre` contains two types of files:
      - **Specification sequence files**, named numerically (e.g., `0.spectra`, `1.spectra`, …), where the number indicates the count of remaining system justice guarantees after successive deletions (analogously, in `envS`, the number reflects the remaining environment safety assumptions).
      - **Winning region files**, stored in folders labeled with suffixes indicating the synthesis method:
        - Folders with the suffix `Inc` (e.g., `1_winRegionInc`) store winning regions computed using the **incremental method**. If this folder is empty, it indicates that incremental computation is infeasible for this instance. This occurs because modifications involving certain high level constructs, as discussed in **Remark 2** of the paper, introduce changes to the underlying BDD variables, such as the addition or removal of variables, which render the previously computed winning region incompatible and lead to errors upon retrieval.
        - Folders without this suffix (e.g., `1_winRegion`) store winning regions computed using the **baseline method**.
    - **Examples**:
      - `1.spectra` represents the specification in the sequence where, starting from the full specification, system justice guarantees have been incrementally removed until only `1` remains.
      - `2_winRegion` is the system winning region obtained by applying the baseline method to `2.spectra`.
      - `3_winRegionInc` is the system winning region obtained via the incremental method on `3.spectra`. 

  - **Raw experimental data (`.csv` files). For name of data result files:**

    - The field `step` corresponds to the number of specification clauses added or removed in one iteration (i.e., **the (`\Delta`) in the paper**). For example, `step_1` means one clause was added or removed.

    - In filenames like `step2_1`, the trailing digit (`1`) denotes the repetition index (i.e., the first run of the experiment with (`\Delta = 2`)).

    - The flag `noE` indicates incremental synthesis ***without*** the performance heuristics proposed in the paper. Absence of this flag implies these heuristics were enabled.

    - The flag `nEDU` indicates that the *early unrealizability detection heuristic* was **disabled**. Its absence means the heuristic was active.

    - The `filtered` flag appears *only* in the `r` subdirectories of environment-assumption-related cases (`EnvSAdd`, `EnvSSub`, `EnvJAdd`, `EnvJSub`); we elaborate on this below.

    - **Filename examples**:

      - `SYNTECH_sysJAdd_step1_2.csv`: Realizable case (in  `r` folder of `SysJAdd` folder), system justice guarantees *added* (`sysJAdd` folder), `\Delta = 1` (`step1`), second run (`step1_2`) of the incremental method.
      - `SYNTECH_sysJAdd_step1_1_noE.csv`: Realizable case, system justice guarantees added, \Delta = 1, first run (`_1`) of incremental synthesis *without* the performance heuristics (`_noE`).
      - `SYNTECH_sysJStand_1.csv`: Realizable case, baseline method (indicated by `stand` instead of `add`/`sub` or `step`), first run (`_1`).
      - `Unreal_sysJAdd_nEDU_step1_1.csv`: Unrealizable case (in  `u` folder of `SysJAdd` folder), system justice guarantees added (`sysJAdd_nEDU`), early unrealizability detection *disabled* (`_nEDU`), `\Delta = 1`, first run.

    - **Data format for incremental method output (CSV)**:

      ```csv
      .../SYNTECH_filter_60_REAL_onefolder/1669468393_Pre/sysJ/4.spectra,3,258,13495,Corrent,Detect Early,Real
      ```

      1. Input `.spectra` file path: `../SYNTECH_filter_60_REAL_onefolder/1669468393_Pre/sysJ/4.spectra`

      2. `step` (`\Delta`): `3`.

      3. Number of innermost fixpoint iterations: `258`.

      4. Runtime (ms): `13495`.

      5. Correctness check result: `Corrent`. During batch runs of the incremental method, the winning region computed by the incremental approach is automatically compared against that of the baseline method immediately after its computation. The label `Corrent` indicates that the winning regions derived from both methods are identical, thereby verifying the correctness of our implementation.

         An `ERROR` may appear *only* when modifying environment assumptions within realizable settings (`r`), and it does ***not*** indicate a flaw in our method. In such cases, the specification sequence is constructed by deleting environment assumption clauses. Although the initial specification is realizable, removing these assumptions generates a significant number of intermediate unrealizable specifications.

         In realizable settings, we do not disable the *early unrealizability detection* heuristic. Consequently, for these intermediate unrealizable specifications, the computed system winning region is not the exact region but rather an over-approximation (upper bound), as the heuristic prematurely terminates the computation. This approximation causes a mismatch when compared to the precise winning region computed by the incremental method (disable *early unrealizability detection* heuristic) , resulting in a reported `ERROR`.

         This behavior is consistent with the analysis presented in **Remark 1** of our paper, which explains the conflict between incremental synthesis and exist *early unrealizability detection* heuristic. Far from indicating incorrectness, this observation actually validates the soundness of our method's implementation.

      6. `Detect Early`: Indicates our heuristic detected that the winning region remained unchanged. Used to calculate the proportion of invariant system winning regions.

      7. `Real`: Specification is realizable.

    - **Data format for baseline method output (CSV)**:

      ```
      .../syn/Unrealizable_nEDU/1670422119_Pre/envS/18.spectra,132,41418,Unreal
      ```

      1. File path: `.../syn/Unrealizable_nEDU/1670422119_Pre/envS/18.spectra`.
      2. Innermost fixpoint iterations: `132`.
      3. Runtime (ms): `41418`.
      4. `Unreal`: Specification is unrealizable.

- **`u` directory**:

  - Maintains the same structure as the `r` directory, containing the raw performance measurement data and the benchmark suite of specification sequences required for performance testing. We now highlight the differences between the `u` and `r` directories:

  - Under the unrealizable setting, two distinct baseline methods were executed:

    1. The first baseline method **includes** the *early unrealizability detection heuristic*. It corresponds to the `Unrealizable_base` folder and the experimental data file `Unreal_sysJStand_base_1.csv`, and is used to compare the performance of the incremental method (which disables this heuristic) against the baseline method (which includes it).
    2. The second baseline method **disables** the *early unrealizability detection heuristic*. It corresponds to the `Unrealizable_nEDU` folder and the experimental data file `Unreal_sysJStand_nEDU_1.csv`, and is used to verify the correctness of the incremental method.

    Apart from these distinctions, all other aspects are identical to the `r` directory, including the internal folder structure and the format of the experimental data files.

**`EnvJAdd`** folder: This denotes the scenario where environment justice assumptions are added. Within the `r` subdirectories of environment-assumption-related cases (`EnvSAdd`, `EnvSSub`, `EnvJAdd`, `EnvJSub`), there is one difference compared to directories related to system guarantees (e.g., `SysSAdd`, `SysSSub`, `SysJAdd`, `SysJSub`) in `r` subdirectories; the rest of the content remains consistent. We elaborate on this difference below.

- As previously discussed, during incremental experiments runs, specification sequences derived from environment assumptions often contain a large number of unrealizable specifications within the realizable setting (`r`). Combined with the *early unrealizability detection heuristic*, this leads to the `ERROR` mentioned earlier. Therefore, prior to comparison, the experimental results must be filtered to discard these unsuitable data and retain only valid data. The script `analysisFilter.py` is used for this purpose. It must reside in the same directory as the raw data file to be filtered. To use it, modify the last line `input_file = ""` to specify the filename of the target file （e.g., `SYNTECH_envSSub_Step1_1.csv`） in the same directory. The filtered output file will be saved in the same directory with the infix `filtered` (e.g., `SYNTECH_envSSub_filteredStep1_1.csv`) (Please note the required input file name format. See line `9` of `analysisFilter.py` for details.).

**`libcudd.so`**, **`run.jar`**, and **`runWithOutEUD.jar`**: These represent the underlying BDD library dependencies and the two executable Java JAR files implementing our method and the baseline method:

- **`run.jar`**: Contains both the baseline and our incremental method, with the *early unrealizability detection* heuristic **enabled**.
- **`runWithOutEUD.jar`**: Contains both the baseline and our incremental method, but with the *early unrealizability detection* heuristic **disabled**.





### How to Reproduce Our Experimental Results

#### Batch Command Overview

This section explains how to reproduce our experimental results using the batch execution scripts. We will first detail the command-line options of the batch script, followed by instructions on how to run a smoke test and reproduce the full results using our provided Docker image.

The batch script for running experiments is `runExperiment.py`. Accompanying this script in the same directory are the result analysis scripts: `analysisReal.py`, `analysisUnreal.py`, `analysisUnchange.py`, and `analysisUnrealUnchange.py`. These analysis scripts process the raw experimental data to generate the summary tables reported in the paper (**`table 2 to table 6`**).

The `runExperiment.py` script supports batch execution of both baseline and incremental synthesis experiments. Its usage is as follows:

```bash
usage: runExperiment.py [-h] [-s {shrink,nshrink}] [--asj] [--e] [--as-mode {add,sub}] [--step STEP] [--first-cmd-params FIRST_CMD_PARAMS] [--second-cmd-params SECOND_CMD_PARAMS] [--only-first] [--only-second] directory subfolder csv_path jar_path
```

- **`[-s {shrink,nshrink}]`**: Specifies whether the system’s winning region is expected to *shrink* (`-s shrink`) or *expand* (`-s nshrink`). For example, adding system guarantees causes the winning region to shrink. This aligns with **Theorems 3.2 and 3.3** in the paper.
- **`[--asj]`**: Must be used together with `--e`. Enables our *system justice reordering heuristic* when adding system justice guarantees (`AddSysJ`).
- **`[--e]`**: Enables our performance heuristics. When combined with `--asj`, it activates the reordering heuristic for `AddSysJ`; when used alone, it applies to scenarios where the winning region expands (`-s nshrink`).
- **`[--as-mode {add,sub}]`**: Indicates whether specification clauses are being **added** (`--as-mode add`) or **removed** (`--as-mode sub`).
- **`[--step STEP]`**: Corresponds to `\Delta` in the paper—the number of clauses added or removed per iteration (`--step 1`) —and matches the `step` field in raw data filenames (`_step1`). 
- **`[--only-first]`**: Runs only the **baseline** method (`--only-first`).
- **`[--only-second]`**: Runs only the **incremental** method (`--only-second`).
- **`directory`**: Path to the folder containing the specification sequences (e.g., `SYNTECH_filter_60_REAL_onefolder`).
- **`subfolder`**: One of `envJ`, `envS`, `sysJ`, or `sysS`, indicating the type of specification clause being added or removed. Combined with `--as-mode` (`add` or `sub`), it fully defines the modification type (e.g., `add sysJ`). This must be consistent with the top-level directory name (e.g., `SysJAdd`). Based on **Theorems 3.2 and 3.3**, one can then determine the appropriate `-s` argument (e.g., `shrink` for `add sysJ`).
- **`csv_path`**: Path to the output CSV file that records experimental results.
- **`jar_path`**: Path to the executable JAR file for realizability checking, which can be either `run.jar` (with *early unrealizability detection* enabled) or `runWithOutEUD.jar` (with it disabled).

#### Examples

1. **Running Incremental Experiments (Unrealizable Setting)**

   ```bash
   python runExperiment.py -s nshrink --as-mode sub --step 1 --only-second SysJSub/u/Unrealizable_nEDU sysJ Unreal_sysJSub_nEDU_step1_1_noE.csv runWithOutEUD.jar
   ```

   This command runs **batch incremental experiments** (`--only-second`) under the **unrealizable** setting (`/SysJSub/u/Unrealizable_nEDU`). **System justice guarantees** (`sysJ`) are being **removed** (`--as-mode sub`) with \Delta=1 (`--step 1`). The winning region is expanding (`-s nshrink`). The *early unrealizability detection heuristic* is **disabled** (indicated by the use of `runWithOutEUD.jar`), and no specific heuristic flag (no `--e`) is set.

2. **Running Incremental Experiments (Realizable Setting)**

   ```bash
   python runExperiment.py -s shrink --asj --e --as-mode add --step 1 --only-second SysJAdd/r/SYNTECH_filter_60_REAL_onefolder sysJ SYNTECH_sysJAdd_step1_1.csv run.jar
   ```

   This command runs **batch incremental experiments** (`--only-second`) under the **realizable** setting (`/SysJAdd/r/SYNTECH_filter_60_REAL_onefolder`). **System justice  guarantees** (`sysJ`) are being **added** (`--as-mode add`) with \Delta=1 (`--step 1`). The winning region is shrinking (`-s shrink`). Both the `reordering` heuristic (`--asj --e`) and *early unrealizability detection* (via `run.jar`) are **enabled**.

3. **Running Baseline Experiments**

   ```bash
   python runExperiment.py --only-first SysJAdd/r/SYNTECH_filter_60_REAL_onefolder sysJ SYNTECH_sysJStand_1.csv run.jar
   ```

   This command runs **batch baseline experiments** (`--only-first`) under the **realizable** setting (`SysJAdd/r/SYNTECH_filter_60_REAL_onefolder`), modifying system justice guarantees (`sysJ`) (both addition and removal).

------

- #### Experimental Data Analysis Scripts

  We now explain how to run the data analysis scripts on the obtained experimental results.

  The scripts `analysisReal.py`, `analysisUnreal.py`, `analysisUnchange.py`, and `analysisUnrealUnchange.py` process the raw data to generate the tables shown in the paper.

  - **`analysisReal.py`** and **`analysisUnreal.py`** are used for the **realizable** and **unrealizable** settings, respectively. To use them, modify the following lines (line `266-267` for `analysisReal.py`, line `259-260` for `analysisUnreal.py`) in the script and then execute the file:

  ```
    file1_path = ''
    file2_path = ''
  ```

  - **`file1_path`**: The CSV output path from the **incremental** batch experiment (serves as the numerator when calculating speedup ratios).
  - **`file2_path`**: The CSV output path from the **baseline** batch experiment (serves as the denominator).

  The script will automatically calculate metrics such as the geometric mean of the time ratios, including both the overall geometric mean and the geometric mean partitioned by the baseline method's execution time.

- **`analysisUnchange.py`** and **`analysisUnrealUnchange.py`** scripts are used to calculate the count and proportion of cases where the winning region remains unchanged. Modify the following line (bottom in the file):

  ```
    file1_path = ''
  ```

  Set `file1_path` to the CSV output of the **incremental** batch experiment. The script will then compute statistics regarding instances where the system winning region did not change during incremental synthesis (`Detect Early`).


### Update

To remove the need for manual modifications to the data analysis scripts when reproducing our experimental results, we have provided the latest versions of the files `analysisReal.py`, `analysisUnreal.py`, `analysisUnchange.py`, and `analysisUnrealUnchange.py` in the repository: [oopsla-incre/Supplementary at main · paperAE/oopsla-incre](https://github.com/paperAE/oopsla-incre/tree/main/Supplementary) (`/Supplementary` folder). These updates remove manual file modifications, allowing direct input via the command line. User can download these latest files from the link above to replace current version. For specific usage examples, please refer to the `Supplementary.md` file in at that link (`/Supplementary/Supplementary.md`).




# Smoke Test and Full Experimental Reproduction

- We provide a Docker image for you to reproduce the results.
- Pull and run the Docker container:
  1. `docker pull paperae/oopsla-incre-final`
  2. `docker run -itd --name oopsla-inc paperae/oopsla-incre-final`
  3. `docker exec -it oopsla-inc /bin/bash`
  4. `cp libcudd.so /usr/lib` (important and necessary) (in `/workspace`)

#### Kick-the-Tires (Smoke Test)

Execute a simple demonstration of our artifact( in `/workspace`) (Smoke Test)

1. First, run the baseline method:

   1. For the realizable setting, execute `touch smoke_real_stand_1.csv`. This creates the CSV file `smoke_real_stand_1.csv` to record baseline results. 

   2. Run the baseline method for the system justice sequence on specification `1669468393.spectra` in the `SmokeTest` directory under the realizable setting using the command: 

      ```bash
      python runExperiment.py --only-first /workspace/SmokeTest/Real sysJ smoke_real_stand_1.csv run.jar
      ```

      The full run takes several minutes to tens of minutes. After completion,  `smoke_real_stand_1.csv` should yield results similar to the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-1.png)

   3. For the unrealizable setting, execute `touch smoke_unreal_stand_base_1.csv` and `touch smoke_unreal_stand_nEDU_1.csv`.

   4. Run the first baseline test (without disabling the *early unrealizability detection* heuristic) for the system justice sequence on specification `1669643728.spectra` in the `SmokeTest` directory under the unrealizable setting using the command: 

      ```bash
      python runExperiment.py --only-first /workspace/SmokeTest/Unreal/Base sysJ smoke_unreal_stand_base_1.csv run.jar
      ```

      The full run takes several minutes to tens of minutes. Upon completion, the file `smoke_unreal_stand_base_1.csv` should contain results similar to the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-2.png)

   5. Run the second baseline test (disabling the *early unrealizability detection* heuristic) for the system justice sequence on specification `1669643728.spectra` in the `SmokeTest` directory under the unrealizable setting using the command: 

      ```bash
      python runExperiment.py --only-first /workspace/SmokeTest/Unreal/Incre sysJ smoke_unreal_stand_nEDU_1.csv runWithOutEUD.jar
      ```

      The full run takes several minutes to tens of minutes. Upon completion, the file `smoke_unreal_stand_nEDU_1.csv` should contain results similar to the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-3.png)

2. #### Running the Incremental Method

   1. **Realizable Setting**

      1. Create the CSV output file by running: `touch smoke_real_addSysJ_step1_1.csv`.

      2. Execute the incremental test for the system justice sequence on specification `1669468393.spectra` in the `SmokeTest` directory. This test involves adding system justice guarantees (`--as-mode add`), enables the heuristics proposed in the paper (`--asj --e`), and sets `\Delta=1` (`--step 1`). Run the command:

         ```bash
         python runExperiment.py -s shrink --asj --e --as-mode add --step 1 --only-second /workspace/SmokeTest/Real sysJ smoke_real_addSysJ_step1_1.csv run.jar
         ```

         You should obtain results similar to the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-4.png) We observe that the data of `1.spectra` is missing. The command line will report an error: `[Run Command Failed]`. This does **not** indicate a bug in the code, but rather signifies that incremental computation is infeasible for this instance. As discussed in **Remark 2** of the paper, this occurs because modifications involving certain high level constructs introduce changes to the underlying BDD variables, such as the addition or removal of variables, which render the previously computed winning region incompatible and lead to errors upon retrieval.

   2. **Unrealizable Setting**

      1. Create the CSV output file by running: `touch smoke_unreal_nEDU_addSysJ_step1_1.csv`.

      2. Execute the incremental test for the system justice sequence on specification `1669643728.spectra` in the `SmokeTest` directory. This test involves adding system justice guarantees (`--as-mode add`), disables the *early unrealizability detection heuristic* (`runWithOutEUD.jar`), and sets \Delta=1 (`--step 1`). Run the command:

         ```bash
         python runExperiment.py -s shrink --asj --e --as-mode add --step 1 --only-second /workspace/SmokeTest/Unreal/Incre sysJ smoke_unreal_nEDU_addSysJ_step1_1.csv runWithOutEUD.jar
         ```

         You should obtain results similar to the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-5.png)

   #### Analyzing Experimental Results

   1. **Realizable Setting**
      Analyze the results for the scenario where system justice guarantees are added under the realizable setting. In `analysisReal.py`, set the input file paths (lines `266–267`) as follows:

      ```python
      file1_path = '/workspace/smoke_real_addSysJ_step1_1.csv'
      file2_path = '/workspace/smoke_real_stand_1.csv'
      ```

      Then, run `python analysisReal.py`. The output should resemble the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-6.png) Here, `OVERALL GEOMETRIC MEAN (All Time Groups):& 0.16^{5}` indicates that the geometric mean of the time ratios (incremental vs. baseline) across `5` data points is `0.15` (variations may occur, as noted in the **Hardware Dependency section**). This generates the overall result shown in **Table 2** of the paper. `Processing file group` shows the matched result files based on the naming rules described earlier. Since we ran only one test, each group matches the file itself. The section below `Column labels` presents the geometric means for different baseline runtime partitions and the timeout ratios for our method and the baseline, which constitute the data in **Table 4** of the paper. `{---}` indicates no data is available (i.e., no baseline runs fall within that time interval).

   2. **Unrealizable Setting**
      Analyze the results for the scenario where system justice guarantees are added under the unrealizable setting. **Do not use** `smoke_unreal_stand_nEDU_1.csv`. The purpose of running this baseline type was to obtain the precise winning region for comparison, as the first baseline (with *early detection* enabled) would terminate prematurely, yielding an imprecise region.
      Before analysis, **manually modify** the file paths in `smoke_unreal_stand_base_1.csv` by replacing `Base` with `Incre`. This step is necessary because the baseline data was collected from two folders (`Incre` and `Base`), causing path inconsistencies. This modification ensures the analysis script can match the files correctly. Then, in `analysisUnreal.py`, set the file paths (lines `259–260`) as follows:

   ```python
      file1_path = '/workspace/smoke_unreal_nEDU_addSysJ_step1_1.csv'
      file2_path = '/workspace/smoke_unreal_stand_base_1.csv'
   ```

   Run `python analysisUnreal.py`. The output should resemble the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-7.png) The result `OVERALL GEOMETRIC MEAN (All Time Groups):& 0.09^{4}` indicates `4` data points with a geometric mean of `0.09` (minor variations may occur). This generates the overall result shown in **Table 3** of the paper. The section below `Column labels` provides the geometric means for different baseline runtime partitions and the timeout ratios, used to generate the data in **Table 5** of the paper. As noted earlier, although `smoke_unreal_stand_addSysJ_step_1.csv` contains `5` entries, one is realizable (`Real`) and is automatically filtered out by the analysis script.

3. **Analyzing Unchanged Winning Regions**
   Analyze the proportion of cases where the system winning region remains unchanged when system justice guarantees are added.

   - **Realizable Setting**: In `analysisUnchange.py`, modify the `file1_path` (line `116` at the bottom of the file) to:

     ```python
     file1_path = '/workspace/smoke_real_addSysJ_step1_1.csv'
     ```

     Run `python analysisUnchange.py`. The output should resemble the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-8.png) Here, `5/5(100.00\%)` indicates that the winning region did not change for all `5` cases, consistent with the `Detect Early` flag in the previous figures. This step generates the results shown in **Table 6** of the paper.

   - **Unrealizable Setting**: In `analysisUnrealUnchange.py`, modify the corresponding line (line `122` at the bottom of the file) to:

     ```python
     file1_path = '/workspace/smoke_unreal_nEDU_addSysJ_step1_1.csv'
     ```

     Run `python analysisUnrealUnchange.py`. The output should resemble the image below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/smoke-9.png) Here, `3/4(75.00\%)` indicates that the winning region did not change for `3` out of the `4` cases, consistent with the `Detect Early` flag in the previous figures.





### Running the Full Experiment Suite

We will now provide the command-line parameters required to reproduce the full experimental results for different scenarios (*realizable/unrealizable*) and various specification modification types (`EnvJAdd`, `EnvJSub`, `EnvSAdd`, `EnvSSub`, `SysJAdd`, `SysJSub`, `SysSAdd`, `SysSSub`).

In fact, as shown in the reproduction process below, the command format is consistent with that used in the smoke test. The only difference is that the `directory` input parameter for the `runExperiment.py` script changes from the `SmokeTest` specification directory (`/workspace/SmokeTest/Real`, `/workspace/SmokeTest/Unreal/Base`, `/workspace/SmokeTest/Unreal/Incre`) to the complete benchmark suite directory corresponding to the specific modification type. For example, for the `SysJAdd` folder (adding system justice guarantees), the directories for reproducing the full results are:

- `r/SYNTECH_filter_60_REAL_onefolder`  (realizable)
- `u/Unrealizable_base` and `u/Unrealizable_nEDU`  (unrealizable)

We will use the `SysJAdd` folder to demonstrate how to run the full experiment:

- Below are example command-line parameters:

  - **Realizable Setting (`SysJAdd`)**:

    - `touch SYNTECH_sysJStand_1.csv`

    - Run Baseline: 

      ```bash
      python runExperiment.py --only-first /workspace/SysJAdd/r/SYNTECH_filter_60_REAL_onefolder sysJ SYNTECH_sysJStand_1.csv run.jar
      ```

    - `touch SYNTECH_sysJAdd_step1_1.csv`

    - Run Incremental (adding system justice guarantees, \Delta=1 , with heuristics enabled): 

      ```bash
      python runExperiment.py -s shrink --asj --e --as-mode add --step 1 --only-second /workspace/SysJAdd/r/SYNTECH_filter_60_REAL_onefolder sysJ SYNTECH_sysJAdd_step1_1.csv run.jar
      ```

      *Note: Running the above commands takes more than 48-96 hours. If time is limited, you may terminate the process after obtaining a sufficient number of results.*

  - **Unrealizable Setting (`SysJAdd`)**:

    - `touch Unreal_sysJstand_base_1.csv`

    - First Baseline (*Early detection heuristic* **enabled**, consistent with the first test in the smoke test): 

      ```bash
      python runExperiment.py --only-first /workspace/SysJAdd/u/Unrealizable_base sysJ Unreal_sysJstand_base_1.csv run.jar
      ```

    - `touch Unreal_sysJstand_nEDU_1.csv`

    - Second Baseline (*Early detection heuristic* **disabled**, consistent with the second test in the smoke test): 

      ```bash
      python runExperiment.py --only-first /workspace/SysJAdd/u/Unrealizable_nEDU sysJ Unreal_sysJstand_nEDU_1.csv runWithOutEUD.jar
      ```

      Note the differences in the directory paths (`/workspace/SysJAdd/u/Unrealizable_base` vs. `/workspace/SysJAdd/u/Unrealizable_nEDU`) and the JAR files (`run.jar` vs. `runWithOutEUD.jar`).

    - `touch Unreal_sysJAdd_nEDU_step1_1.csv`

    - Run Incremental (adding system justice guarantees, \Delta=1 , with heuristics enabled): 

      ```bash
      python runExperiment.py -s shrink --asj --e --as-mode add --step 1 --only-second /workspace/SysJAdd/u/Unrealizable_nEDU sysJ Unreal_sysJAdd_nEDU_step1_1.csv runWithOutEUD.jar
      ```

      Note the differences in the directory paths (`/workspace/SysJAdd/u/Unrealizable_base` vs. `/workspace/SysJAdd/u/Unrealizable_nEDU`) and the JAR files (`run.jar` vs. `runWithOutEUD.jar`).

    - *Note: Running the above commands takes more than 48–96 hours. If time is limited, you may terminate the process after obtaining a sufficient number of results.*

As described above, the format of the command-line parameters for the full experiment is identical to that of the **Smoke Test**. The only change is the `directory` parameter, which is replaced with the full benchmark directories: `/workspace/SysJAdd/r/SYNTECH_filter_60_REAL_onefolder`, `/workspace/SysJAdd/u/Unrealizable_base`, and `/workspace/SysJAdd/u/Unrealizable_nEDU`.

The examples above correspond to the adding system justice guarantees scenario (`SysJAdd` folder). Other scenarios are located in their respective folders. For instance, adding system safety guarantees (both realizable and unrealizable cases) are located in the `/workspace/SysSAdd` folder. You can run them using the same command format as the examples above.

Below are additional example commands that you can run directly:

```bash
touch sysSSub_step1_1.csv

python runExperiment.py -s nshrink --e --as-mode sub --step 1 --only-second /workspace/SysSSub/r/SYNTECH_filter_60_REAL_onefolder sysS sysSSub_step1_1.csv run.jar

touch envJStand_1.csv

python runExperiment.py --only-first /workspace/EnvJSub/r/SYNTECH_filter_60_REAL_onefolder envJ envJStand_1.csv run.jar

touch sysSAdd_step1_1.csv

python runExperiment.py -s shrink --as-mode add --step 1 --only-second /workspace/SysSAdd/r/SYNTECH_filter_60_REAL_onefolder sysS sysSAdd_step1_1.csv run.jar 

touch Unreal_envSAdd_nEDU_step1_1.csv

python runExperiment.py -s nshrink --e --as-mode add --only-second /workspace/EnvSAdd/u/Unrealizable_nEDU envS Unreal_envSAdd_nEDU_step1_1.csv runWithOutEUD.jar 

touch sysSStand_base_1.csv

python runExperiment.py --only-first /workspace/SysSAdd/u/Unrealizable_base sysS sysSStand_base_1.csv run.jar


touch Unreal_envSSub_1.csv

python runExperiment.py -s shrink --as-mode sub --step 2 --only-second /workspace/EnvSSub/u/Unrealizable_nEDU envS Unreal_envSSub_1.csv runWithOutEUD.jar

touch Unreal_envSStand_nEDU_1.csv

python runExperiment.py --only-first /workspace/EnvSAdd/u/Unrealizable_nEDU envS Unreal_envSStand_nEDU_1.csv runWithOutEUD.jar
```

You can modify the parameters based on the examples above to run tests for the desired configurations. Since running the full experiment suite for all scenarios would take several months, you can choose to run only specific scenarios, terminate the batch process at any time, and use the analysis scripts to compare the existing results. Alternatively, you can directly use the provided data (as described in the following section) to obtain the experimental results for the paper's tables.





### Obtaining Paper Results from Provided Raw Data

Running the complete experiments for all scenarios would take several months. Therefore, we have included all the raw data required to reproduce the experimental results within the `r` and `u` folders of each scenario (e.g., `SysJAdd`, `SysSub`). Below, we demonstrate how to reproduce the `Add SysJ*` data from **Table 4** of the paper.

Modify lines `266–267` in the `analysisReal.py` file:

```python
file1_path = '/workspace/SysJAdd/r/SYNTECH_sysJAdd_step1_1.csv'
file2_path = '/workspace/SysJAdd/r/SYNTECH_sysJStand_1.csv'
```

After running the script with `python analysisReal.py` , you will obtain an output below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-1.png) The meaning of this output is the same as described in the smoke test section. Pay attention to the bottom data, which matches the first row (`\Delta=1`) of the `Add SysJ*` section in **Table 4** of the paper show below. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-2.png)

Similarly, change the value of `file1_path` to 

```python
file1_path = '/workspace/SysJAdd/r/SYNTECH_sysJAdd_step2_1.csv'
```

 to obtain the following result, which matches the second row (`\Delta=2`) in **Table 4** above. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-3.png)By continuing to modify the `file1_path`, you can obtain the remaining experimental results in the table.

Furthermore, the `OVERALL GEOMETRIC MEAN` (or the `All` column in `Column labels`) corresponds to the overall experimental results shown in **Table 2** of the paper. Essentially, each row in **Tables 4** and **5** represents a detailed breakdown of the individual overall results from **Tables 2** and **3**, partitioned by baseline runtime intervals. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-8.png)

We additionally discuss the case of environment assumptions, which involves filtering the experimental results. We demonstrate how to reproduce the `Sub EnvJ` data from **Table 4** of the paper.

Modify the following section in the `analysisReal.py` file (line `266-267`):

```python
file1_path = '/workspace/EnvJSub/r/SYNTECH_envJSub_filteredStep1_1.csv'
file2_path = '/workspace/EnvJSub/r/SYNTECH_envJStand_1.csv'
```

We can get following output: ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-4.png)Running the script yields the following result, which matches the first row of the `Sub EnvJ` section in Table 4 in following: ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-5.png)

We provide further examples of `file_path` modifications below:

```python
# For analysisReal.py

file1_path = '/workspace/EnvJAdd/r/SYNTECH_envJAdd_filteredStep1_1.csv'
file2_path = '/workspace/EnvJAdd/r/SYNTECH_envJStand_1.csv'

file1_path = '/workspace/EnvJSub/r/SYNTECH_envJSub_filteredStep1_1.csv'
file2_path = '/workspace/EnvJSub/r/SYNTECH_envJStand_1.csv'

file1_path = '/workspace/EnvSAdd/r/SYNTECH_envSAdd_filteredStep1_1.csv'
file2_path = '/workspace/EnvSAdd/r/SYNTECH_envSStand_1.csv'

file1_path = '/workspace/EnvSSub/r/SYNTECH_envSSub_filteredStep1_1.csv'
file2_path = '/workspace/EnvSSub/r/SYNTECH_envSStand_1.csv'


# For analysisUnreal.py

file1_path = '/workspace/SysJSub/u/Unreal_sysJSub_nEDU_step1_1.csv'
file2_path = '/workspace/SysJSub/u/Unreal_sysJStand_base_1.csv'

file1_path = '/workspace/SysSAdd/u/Unreal_sysSAdd_nEDU_step1_1.csv'
file2_path = '/workspace/SysSAdd/u/Unreal_sysSStand_base_1.csv'

file1_path = '/workspace/SysSSub/u/Unreal_sysSSub_nEDU_step1_1.csv'
file2_path = '/workspace/SysSSub/u/Unreal_sysSStand_base_1.csv'
```



For calculating the proportion of unchanged winning regions, we use `Add SysJ*` as an example:

Modify the path following `file1_path =` in `analysisUnchange.py` to (line `116`):

```python
file1_path = '/workspace/SysJAdd/r/SYNTECH_sysJAdd_step1_1.csv'
```

After running `python analysisUnchange.py`, you get: ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-6.png)

This matches the data for entry `\Delta=1` corresponding to `Add Sys J*` in **Table 6** of the paper. ![](https://github.com/paperAE/oopsla-incre/blob/main/Figures/full-7.png)

By referring to the cases above and the smoke test examples, you can reproduce all the experimental results from the tables in the paper by modifying the file paths in the scripts `analysisReal.py`, `analysisUnreal.py`, `analysisUnchange.py`, and `analysisUnrealUnchange.py`. Using the raw experimental data under the `r` and `u` folders of `EnvJAdd`, `EnvJSub`, `EnvSAdd`, `EnvSSub`, `SysJAdd`, `SysJSub`, `SysSAdd`, and `SysSSub`, the generated tables will be consistent with **Tables 2 to 6** in the paper, thereby substantiating our claims (refer to **Sections 4.3–4.5** of the paper for specific discussions).





*If any unexpected inconsistencies arise (e.g., inconsistent experimental results), you may use the backup Java executable files in `JavaRunBack`. The only difference between the backup files and the main directory files is that adjustments were made to the command-line output sections; no other content was modified. However, to prevent any unforeseen errors introduced by these modifications, we provide the more original versions in the alternative directory. To use them, simply delete the corresponding Java executable file in the main directory and replace it with the backup file. However, based on our smoke test and partial tests on the complete dataset, the modifications did not introduce any errors. Therefore, the backup executables should not be enabled; we provide them here solely as an alternative for unexpected scenarios.*


