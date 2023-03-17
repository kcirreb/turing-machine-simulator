#!/usr/bin/python
import sys

# exit status
ACCEPT = 0
REJECT = 1
INPUT_ERROR = 2
FILE_ERROR = 3

# class for tape
class Tape:
  def __init__(self, tape_desc_file, tm):
    self.contents = []    # list of symbols
    self.size = 0         # size of tape until and including first '_' at the infinite end

    # tape desc file is given
    if (tape_desc_file != None):
      try:
        with open(tape_desc_file) as file:
          for line in file:
            for symbol in line:
              if (symbol in tm.alphabet):
                self.contents.append(symbol)
              elif (symbol != '\n' and symbol != ' '):    # symbol not in tm's alphabet
                tm.halt(INPUT_ERROR, None)
      # error in opening file
      except OSError:
        tm.halt(FILE_ERROR, None)

    # append '_' to infinite end of tape
    self.contents.append('_')

    self.size = len(self.contents)

# class for turing machine
class TuringMachine:
  def __init__(self, tm_desc_file):
    self.alphabet = set()
    self.states = set()
    self.transition_functions = {}    # {(state1, tape_input): (state2, tape_output, move)}
    self.current_state = None
    self.accept_state = None
    self.reject_state = None
    self.head_location = 0
    self.steps = 0

    try:
      with open(tm_desc_file) as file:
        # states
        # check if line has the form "states <n>"
        line = next(file, "").split()
        if (len(line) != 2):
          self.halt(INPUT_ERROR, None)
        if (line[0] != "states"):
          self.halt(INPUT_ERROR, None)
        try:
          n = int(line[1])
        except ValueError:
          self.halt(INPUT_ERROR, None)
        if (n < 1):
          self.halt(INPUT_ERROR, None)
        # set states
        for _ in range(n):
          line = next(file, "").split()
          if (line == []):    # missing line
            self.halt(INPUT_ERROR, None)
          state_name = line[0]
          if (state_name == "+" or state_name == "-" or state_name == "alphabet"):    # forbidden state names
            self.halt(INPUT_ERROR, None)
          self.states.add(state_name)
          if (self.current_state == None):    # set first state as start state
            self.current_state = state_name
          if (len(line) > 1):
            if (line[1] == '+' and self.accept_state == None):
              self.accept_state = state_name
            elif (line[1] == '-' and self.reject_state == None):
                self.reject_state = state_name
            else:   # incorrect symbol, or multiple accept/reject states
              self.halt(INPUT_ERROR, None)
            
        # alphabet
        # check if line has the form "alphabet <n> <a1> <a2> ..."
        line = next(file, "").split()
        if (len(line) < 3):
          self.halt(INPUT_ERROR, None)
        if (line[0] != "alphabet"):
          self.halt(INPUT_ERROR, None)
        try:
          n = int(line[1])
        except ValueError:
          self.halt(INPUT_ERROR, None)
        if (n < 1):
          self.halt(INPUT_ERROR, None)
        # set alphabet starting at index 2
        self.alphabet = set(line[2:])
        if (len(self.alphabet) != n):    # incorrect n
          self.halt(INPUT_ERROR, None)
        # add '_' to alphabet
        self.alphabet.add('_')

        # set transition functions
        # check if line has the form "<state1> <tapeinput> <state2> <tapeoutput> <move>"
        line = next(file, "")
        while (line != "" and line != "\n"):
          line = line.split()
          if (len(line) != 5):
            self.halt(INPUT_ERROR, None)
          state1, tape_input, state2, tape_output, move = line
          if (state1 not in self.states or state2 not in self.states):    # state1/state2 not in states
            self.halt(INPUT_ERROR, None)
          if (state1 == self.accept_state or state1 == self.reject_state):    # state1 is an accept/reject state
            self.halt(INPUT_ERROR, None)
          if (tape_input not in self.alphabet or tape_output not in self.alphabet):    # tapeinput/tapeoutput not in alphabet
            self.halt(INPUT_ERROR, None)
          if (move not in ['L', 'R', 'N']):    # invalid move
            self.halt(INPUT_ERROR, None)
          if ((state1, tape_input) in self.transition_functions):    # duplicate transition function
            self.halt(INPUT_ERROR, None)
          self.transition_functions[(state1, tape_input)] = (state2, tape_output, move)
          line = next(file, "")
    # open file error
    except OSError:
      self.halt(FILE_ERROR, None)
  
  # function for running turing machine on tape
  def compute(self, tape):
    while(True):
      # states[(state1, tape_input)] = (state2, tape_output, move)
      # if not found, go to reject state and move left
      next_state, tape_output, move = self.transition_functions.get((self.current_state, tape.contents[self.head_location]), (self.reject_state, tape.contents[self.head_location], 'L'))
      # update current state and tape contents
      self.current_state = next_state
      tape.contents[self.head_location] = tape_output
      # check if accept or reject
      if (self.current_state == self.accept_state):
        self.halt(ACCEPT, tape)
      elif (self.current_state == self.reject_state):
        self.halt(REJECT, tape)
      # update head location according to move
      if (move == 'L' and self.head_location > 0):    # not moving the head if it is at finite end
        self.head_location -= 1
      elif (move == 'R'):
        self.head_location += 1
        if (self.head_location == tape.size):    # append '_' to tape if needed
          tape.contents.append('_')
          tape.size += 1
      self.steps += 1

  # function for halting turing machine
  def halt(self, exit_status, tape):
    if (exit_status == ACCEPT or exit_status == REJECT):
      # remove '_' at infinite end of tape
      while(tape.size > 0 and tape.contents[-1] == '_'):
        tape.contents.pop()
        tape.size -= 1
      # append '_' to tape if it is empty
      if (tape.size == 0):
        tape.contents.append('_')
      if (exit_status == ACCEPT):
        print("accepted")
      elif (exit_status == REJECT):
        print("not accepted")
      print(self.steps)
      print(('').join(tape.contents))
    elif(exit_status == INPUT_ERROR):
      print("input error")
    sys.exit(exit_status)

# main function
if __name__ == "__main__":
  argv = sys.argv

  # initialise turing machine and tape objects with given files
  tm = TuringMachine(argv[1])
  tape = Tape(argv[2] if (len(argv) == 3) else None, tm)

  # run tm on tape
  tm.compute(tape)