#!/usr/bin/env python3

import time

# prompt: Message for user
# high: the max number input can't go over
def input_int(prompt):
    while True:
        # asks user for input
        int_input = input(prompt)
        
        if int_input == "ex":
            return int_input
        
        # checks to make sure user input is only a number
        # if not then it restarts loop
        if not int_input.isdigit():
            print('Invalid input: ' + str(int_input) + '\n')
            continue
        else:
            return int_input

def clear():
    print("\n"*20)