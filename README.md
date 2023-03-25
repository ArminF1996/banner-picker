# Banner Picker
Just a simple project about picking banners based on their revenue performance.

## Current scenario

    I assumed two assumptions:
        1.If we receive a click and don't have its related impression in our DB, create its impression and add both of theminto DB
        2.If we receive a conversion and don't have its related click in our DB, add it into DB, but never affects the final result even if the related click is received after a while

The current scenario is "doing all the process for
data when we received them" but I want to change it to "update all the performance info at the first of each quarter" in this scenario we can ignore the above assumptions and calculate performance information based on our current dataset, although we will have less consistency in this scenario.

# Projects Diagram + Database Schema

![diagram](https://raw.githubusercontent.com/ArminF1996/banner-picker/main/diagram.jpg)

## Run Backend

1. Clone the repository.
2. Go to backend directory.
2. Run `pip3 install -r requirements.txt`.
3. Change related `config.ini` constants as you want. 
4. Run `python3 run.py config.ini`

Or you can use provided Dockerfile

## Run ETL

1. Clone the repository.
2. Go to etl directory.
2. Run `pip3 install .`.
3. Change related `config.ini` constants as you want. 
4. Run `python3 run.py config.ini`

Or you can use provided Dockerfile