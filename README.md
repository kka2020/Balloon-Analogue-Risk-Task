# Balloon Analogue Risk Task (BART) for Nottingham Trent University

## Overview
BART is a simple task conducted on a computer used to investigate how financial risk affects behaviour.

* The game consists of 0 to 240 rounds (decided by the investigator before the game starts). In each round, the player inflates a balloon by pressing the right arrow key. Each inflate adds £1 to their bank account.  
* However, there is a random chance of the balloon popping and the player losing all the money earned that round.  
* The bigger the balloon gets, the greater the chance the balloon pops (the relevant probabilities of popping at each balloon size is decided by the investigator).
* The player can choose to bank the money earned that round by pressing the left arrow key. The round ends when the balloon pops or the player banks.

## BART basic
This is the basic version of BART with only one type of balloon

## BART risk
This version involves multiple types of balloons, each with an associated risk level.

1. **Low risk**
  * This is the green balloon
  * Can be inflated a max number of 10 times
2. **Medium risk**
  * This is the yellow balloon
  * Can be inflated a max number of 7 times
3. **High risk**
  * This is the red balloon
  * Can be inflated a max number of 3 times

An equal number of each balloon type appears across the game where possible.  
Where it isn't, there are more medium balloons and an equal number of high and low balloons.

## Files
* 'BART basic.py' is the version of the experiment with only one type of balloon
* 'BART risk.py' is the version with 3 types of balloon
* 'Util.py': contains utility functions
* probabilities_basic.txt: probability of popping at each balloon size; can be edited by investigator
* probabilities_risk.txt: probability of popping at each balloon size for each balloon type; can be edited by investigator

## How to run
If running in a terminal, navigate into the folder containing the scripts before running.

Libraries to install before use:  
Pygame (run 'pip install pygame')  
CSV (run 'pip install csv')

Any images can be changed by replacing the ones found in the 'images' folder, however make sure to keep the same names
