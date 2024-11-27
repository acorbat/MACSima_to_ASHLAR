# MACSima_to_ASHLAR
A short notebook and utils functions to generate ASHLAR commands for MACSima files.

# Installation

If you don't have Python and something to handle Python packages and environments, I suggest you install from [Miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#download).

You can clone this repository to any local folder via git.

```
cd /folder/of/choice
git clone git@github.com:acorbat/MACSima_to_ASHLAR.git
```

Once the folder is cloned to your local system, you can change directory into it and create the required environment.

```
cd MACSima_to_ASHLAR
conda env create -f .\environment.yml
```

Activate the environment and install ASHLAR

```
conda activate macs_to_ashlar
pip install ashlar
```

# Usage

After installing the environment and ASHLAR in it, you can open the notebook called `preprocess_files.ipynb` from jupyter lab.

```
conda activate macs_to_ashlar
jupyter lab
```

Jupyter Lab should open from your default internet explorer and you can double click on `preprocess_files.ipynb`. Follow the instructions in the notebook.

*Note: If your channel selected for alignment has a different index after each cycle, you can try out [my fork of ASHLAR](https://github.com/acorbat/ashlar). It is NOT maintained but it saved me from trouble when the DAPI channel was assigned different indexes in each cycle due to alphabetical sort.*