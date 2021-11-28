# airport_signals

A script to generate appropriate signals for the Factorio [Airport Display by SuicideJunkie](https://forums.factorio.com/viewtopic.php?p=553689#p553689).

# Usage

Create a message file (e.g. `message.txt`) with at most 16 characters per rwo and at most two rows. Feel free to use ANSI color codes for color, as below:

```
\033[36mO2\033[0m Tigress
\033[31mH\033[0m\033[32me\033[0m\033[33ml\033[0m\033[34ml\033[0m\033[35mo\033[0m\033[36m \033[0m\033[31mW\033[0m\033[32mo\033[0m\033[33mr\033[0m\033[34ml\033[0m\033[35md\033[0m
```

which produces

![An airport display showing the text "O2 TIGRESS HELLO WORLD", with the O2 in cyan and the HELLO WORLD in rainbow](https://github.com/agmlego/airport_signals/blob/trunk/sample.png?raw=true)

To generate the blueprint string, run the script as follows:

`python airport.py message.txt`