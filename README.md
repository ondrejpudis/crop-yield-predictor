# Crop yield predictor

A tool which is capable of making predictions of cereal and potato yields for districts of the Slovak Republic.

It was developed as a part of the owner's Bachelor's Thesis at Faculty of Information Technology of CTU at Prague.

## Installation guide

This tool supports two types of installation. The first, simplier and advised possibility is using **Docker**. The second one is a local development environment.

### Dockerisation

This approach requires a working installation of Docker programme on your local machine.

- enter the source directory
- `docker build -t yield-predictor .`
- `docker run -i -t -p 8888:8888 --name predictor yield-predictor bash`

If you don't desire to use `jupyter` from within the container you don't have to specify the `-p 8888:8888` option.

Once you enter the container, you need to authenticate yourself to the Google Earth Engine service:

- `earthengine authenticate`

Now you are ready to use the tool.

After exiting the container, it is terminated, but still exists on your machine. To avoid duplicate authentisations, you can start and enter the existing container.

- `docker start -i predictor`

This will start the container, enter it's bash and stop the container upon exit.

### Local development environment

Before starting this approach, make sure the following requirements are met:

- Python **3.7**
- `openssl` library (in some cases `libssl-dev` as well)
- `gcc` compiler

Start by create a new local environment in the project's root directory:
- `python3 -m venv env --symlinks`

Enter this environment:
- `source env/bin/activate`

Install all the requirements: 
- `pip install -r requirements.txt`

After the installation, you have to authenticate yourself to the Google Earth Engine service:
- `earthengine authenticate`

To install the project's commands to your terminal:
- `pip install -e .`

## Command-line interface

The commands can be run from the root project's directory (`/app` in Docker container).

### `test-predict`

Test the models and get Mean Absolute or Root Mean Squared Errors.

- `-c` feature extraction algorithm (`kmeans` or `lvq`)
- `-p` prediction algorithm (`lr` or `svm`)
- `--start` a year to start the test in (`>= 1999`) [1999]
- `--end` a year to end the test in (`<= 2017`) [2017]
- `--crop` a crop to run the computation for (`cereals` or `potatoes`) [cereals]
- `--split` use a Lowland-Highland split [no]
- `--rmse` display RMSE [no]
- `--force-server` request a computation on a server [no]

### `predict`

Predict a yield for a specified year for either a district or the whole republic.

- `-c` feature extraction algorithm (`kmeans` or `lvq`)
- `-p` prediction algorithm (`lr` or `svm`)
- `--year` a year to make a prediction for (`>= 1999` and `<= 2019`) [2019]
- `--district` a district to make a prediction for [None]
- `--crop` a crop to run the computation for (`cereals` or `potatoes`) [cereals]
- `--split` use a Lowland-Highland split [no]
- `--force-server` request a computation on a server [no]

## Directories

This section describes the directories in the project.

- `datasets` information sources of the project (past crop yields and geographical data)
- `javascript` code for Earth Engine web-based IDE (visualisations for the thesis text, see `text/thesis.pdf`)
- `json` saved responses from the Earth Engine servers (so that we don't need to repeat the calls)
- `jupyter` source code for the graphs used for analysis throughout the text
- `src` project's source code itself
- `text` thesis text

## Jupyter

The project ships with code used for creating the graphs used in the text.

If you desire to inspect them, you have to install `sklearn-lvq` package:
- `pip install sklearn-lvq`

If you use a local environment, just enter the `jupyter` directory and run:
- `jupyter notebook`

For running `jupyter` from within the Docker container and access it using browser you need to map `8888` port by creating a new container (see Installation). Then, enter the `jupyter` directory and run:
- `jupyter notebook --ip=0.0.0.0 --no-browser --allow-root`

Afterwards, you can load `localhost:8888` and log in with the token specified in the terminal.

## Data sources

The past crop yields data were obtained from the Statistical Office of the Slovak Republic (<http://datacube.statistics.sk/>) and converted from `.xlsx` to `.csv`.

The geographic information about district and region borders were acquired from the Geodetic and Cartographic Institute of the Slovak Republic (<https://www.geoportal.sk/sk/zbgis_smd/na-stiahnutie/>) and converted from the original `.gdb` to `.csv` (<https://zbgis.skgeodesy.sk/rts/sk/Convert>).

## Troubleshooting

Sometimes, it can happen that the server returns `EEEException` with the information that the computation was rejected because of too many requests. 

The calls are automatically retried for **three** times, but it is still possible that the error will be propagated and cause a termination of one of the threads. In case of such a program, wait a few minutes are rerun the command.
