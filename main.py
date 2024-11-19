import random
from prettytable import PrettyTable
import pandas as pd


# Class used to store information for a wire
class Node(object):

  def __init__(self, name, value, gatetype, innames, c0, c1):
    self.name = name  # string
    self.value = value  # char: '0', '1', 'U' for unknown
    self.gatetype = gatetype  # string such as "AND", "OR" etc
    self.interms = [
    ]  # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
    self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them
    self.c0 = c0  # scoap (c0,c1)
    self.c1 = c1
    self.is_input = False  # boolean: true if this wire is a primary input of the circuit
    self.is_output = False  # boolean: true if this wire is a primary output of the circuit

  def set_value(self, v):
    self.value = v

  def display(self):  # print out the node nicely on one line

    if self.is_input:
      # nodeinfo = f"input:\t{str(self.name[4:]):5} = {self.value:^4}"
      nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}"
      print(nodeinfo)
      return
    elif self.is_output:
      nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
    else:  # internal nodes
      nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"

    interm_str = " "
    interm_val_str = " "
    for i in self.interms:
      interm_str += str(i.name) + " "
      interm_val_str += str(i.value) + " "

    nodeinfo += f"as {self.gatetype:>5}"
    nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"

    print(nodeinfo)
    return

# calculates the value of a node based on its gate type and values at interms

  def calculate_value(self):

    for i in self.interms:  # skip calculating unless all interms have specific values 1 or 0
      if i.value != "0" and i.value != "1":
        return "U"
    if self.gatetype == "AND":
      val = "1"
      for i in self.interms:
        if i.value == "0":
          val = "0"
      self.value = val
      return val
    elif self.gatetype == "OR":
      val = "0"
      for i in self.interms:
        if i.value == '1':
          val = "1"
      self.value = val
      return val
    elif self.gatetype == "NAND":
      flag = "1"
      for i in self.interms:
        if i.value == "0":
          flag = "0"
      val = str(1 - int(flag))
      self.value = val
      return val
    elif self.gatetype == "NOT":
      val = self.interms[0].value
      self.value = str(1 - int(val))
      return val
    elif self.gatetype == "XOR":
      num_of_1 = 0
      for i in self.interms:
        if i.value == "1":
          num_of_1 = num_of_1 + 1
      val = num_of_1 % 2
      val = str(val)
      self.value = val
      return val
    elif self.gatetype == "XNOR":
      num_of_1 = 0
      for i in self.interms:
        if i.value == "1":
          num_of_1 = num_of_1 + 1
      val = num_of_1 % 2
      self.value = str(1 - val)
      return val
    elif self.gatetype == "NOR":
      flag = "0"
      for i in self.interms:
        if i.value == "1":
          flag = "1"
      val = str(1 - int(flag))
      self.value = val
      return val
    elif self.gatetype == "BUFF":
      val = self.interms[0].value
      self.value = val
      return val

  def calculate_cvalue(self):
    c0list = []
    c1list = []
    if n.is_input:
      self.c0 = 1
      self.c1 = 1
    for i in self.interms:  # skip calculating unless all interms have specific values 1 or 0
      if (i.c0 != 0 and i.c1 != 0):
        c0list.append(i.c0)
        c1list.append(i.c1)

        if self.gatetype == "AND":
          self.c0 = min(c0list) + 1
          self.c1 = sum(c1list) + 1

        elif self.gatetype == "OR":
          self.c0 = sum(c0list) + 1
          self.c1 = min(c1list) + 1

        elif self.gatetype == "NOR":
          self.c0 = min(c1list) + 1
          self.c1 = sum(c0list) + 1

        elif self.gatetype == "NAND":
          self.c0 = sum(c1list) + 1
          self.c1 = min(c0list) + 1

        elif self.gatetype == "NOT":
          self.c0 = c1list[0] + 1
          self.c1 = c0list[0] + 1

        elif self.gatetype == "BUFF":
          self.c0 = c0list[0] + 1
          self.c1 = c1list[0] + 1



def parse_gate(rawline):
  # example rawline is: a' = NAND(b', 256, c')

  # should return: node_name = a',  node_gatetype = NAND,  node_innames = [b', 256, c']

  # get rid of all spaces
  line = rawline.replace(" ", "")
  # now line = a'=NAND(b',256,c')
  name_end_idx = line.find("=")
  node_name = line[0:name_end_idx]
  # now node_name = a'

  gt_start_idx = line.find("=") + 1
  gt_end_idx = line.find("(")
  node_gatetype = line[gt_start_idx:gt_end_idx]
  # now node_gatetype = NAND

  # get the string of interms between ( ) to build tp_list
  interm_start_idx = line.find("(") + 1
  end_position = line.find(")")
  temp_str = line[interm_start_idx:end_position]
  tp_list = temp_str.split(",")
  # now tp_list = [b', 256, c]
  node_innames = [i for i in tp_list]
  # now node_innames = [b', 256, c]
  return node_name, node_gatetype, node_innames



def construct_nodelist(inputs_list, outputs_list, gates_list):
  o_name_list = []

  for line in input_file_values:
    if line == "\n":
      continue

    if line.startswith("#"):
      continue

   
    if line.startswith("INPUT"):
      index = line.find(")")
      # intValue = str(line[6:index])
      name = str(line[6:index])
      n = Node(name, "U", "PI", [], 1, 1)
      n.is_input = True
      node_list.append(n)
      inputs_list.append(n)

    elif line.startswith("OUTPUT"):
      index = line.find(")")
      name = line[7:index]
      o_name_list.append(name)
      n = Node(name, "U", "PI", [], 1, 1)
      outputs_list.append(n)

    else:  # majority of internal gates processed here
      node_name, node_gatetype, node_innames = parse_gate(line)
      n = Node(node_name, "U", node_gatetype, node_innames, 0, 0)
      node_list.append(n)
      gates_list.append(n)

  # now mark all the gates that are output as is_output
  for n in node_list:
    if n.name in o_name_list:
      n.is_output = True

  # link the interm nodes from parsing the list of node names (string)
  # example: a = AND (b, c, d)
  # thus a.innames = [b, c, d]
  # node = a, want to search the entire node_list for b, c, d
  for node in node_list:
    for cur_name in node.innames:
      for target_node in node_list:
        if target_node.name == cur_name:
          node.interms.append(target_node)

  return


wantToInputCircuitFile = str(
    input(
    "Provide a benchfile name: (a for p2.bench, b for c432.bench):\n"
  ))

if len(wantToInputCircuitFile) != 0:
  circuitFile = wantToInputCircuitFile
  if wantToInputCircuitFile == "a":
    circuitFile = "p2.bench"
  elif wantToInputCircuitFile == "b":
    circuitFile = "c432.bench"
  try:
    f = open(circuitFile)
    f.close()
  except FileNotFoundError:
    print('File does not exist, setting circuit file to default')
    circuitFile = "circuit.bench"
else:
  circuitFile = "circuit.bench"

# Constructing the circuit netlist
file1 = open(circuitFile, "r")
input_file_values = file1.readlines()
file1.close()
node_list = []

outputs_list = []
inputs_list = []
gates_list = []

construct_nodelist(inputs_list, outputs_list, gates_list)
inputCount = outputCount = 0
for n in node_list:
  if n.is_input:
    inputCount += 1
  if n.is_output:
    outputCount += 1

print("---------------")
print(f'Number of inputs for this circuit: {inputCount}')
print(f'Number of outputs for this circuit: {outputCount}\n')

print(
  "-------------------------------------------------------------------------")
print("Controllability calculation for " + circuitFile)

c_table = PrettyTable(['NODE', 'GATE', 'C0','C1'])

for n in node_list:
  n.calculate_cvalue()  
  c_table.add_row([n.name, n.gatetype, n.c0, n.c1])
print(c_table)
print(
  "-------------------------------------------------------------------------")
while True:
  line_of_val = input("Press Enter for Monte Carlo Simulation:")
  if len(line_of_val) == 0:
    break
  # Clear all nodes values to U in between simulation runs
  for node in node_list:
    node.set_value("U")

  strindex = 0
  # Set value of input node
  for node in node_list:
    if node.is_input:
      if strindex > len(line_of_val) - 1:
        break
      node.set_value(line_of_val[strindex])
      strindex = strindex + 1

  
  # simulation by trying calculating each node's value in the list
  updated_count = 1  #initialize to 1 to enter while loop at least once
  iteration = 0
  while updated_count > 0:
    updated_count = 0
    iteration += 1
    for n in node_list:
      if n.value == "U":
        n.calculate_value()
        if n.value == "0" or n.value == "1":
          updated_count += 1
      

  

  input_list = [i.name for i in node_list if i.is_input]
  input_val = [i.value for i in node_list if i.is_input]

  

  output_list = [i.name for i in node_list if i.gatetype]
  output_val = [i.value for i in node_list if i.gatetype]


  print(
    "-------------------------------------------------------------------------"
  )


def montesim():
  ## Generate 10 random inputs vecter
  out_list = []
  inputSize = len(inputs_list)
  
  for x in range(1000):
    curr_tv = ""
    for y in range(inputSize):
      new_bit = random.randint(0, 1)
      curr_tv = curr_tv + str(new_bit)
    

    for node in node_list:
      node.set_value("U")

    strindex = 0
    line_of_val = curr_tv
    for node in node_list:
      if node.is_input:
        if strindex > len(line_of_val) - 1:
          break
        node.set_value(line_of_val[strindex])
        strindex = strindex + 1

    # simulation by trying calculating each node's value in the list
    updated_count = 1  #initialize to 1 to enter while loop at least once
    iteration = 0
    while updated_count > 0:
      updated_count = 0
      iteration += 1
      for n in node_list:
        if n.value == "U":
          n.calculate_value()
          if n.value == "0" or n.value == "1":
            updated_count += 1

  

    output_list = [i.name for i in node_list if i.gatetype]
    output_val = [i.value for i in node_list if i.gatetype]

    out_str = ''
    for a in output_val:
      out_str = out_str + str(a)

    

    out_list.append(out_str)

  return out_list, output_list


### Monte-Carlo Simulation ####

dict_list = []
output_list = []
for j in range(10):
  o_list, output_list = montesim()
  out_dict = []
  for s in range(len(output_list)):
    n0 = n1 = 0
    for k in o_list:
      if k[s] == '0':
        n0 += 1
      else:
        n1 += 1
    out_dict.append([n0, n1])
  dict_list.append(out_dict)

avg_list = []
for j in range(len(dict_list[0])):
  tot_0 = tot_1 = 0
  for i in range(len(dict_list)):
    tot_0 += dict_list[i][j][0]
    tot_1 += dict_list[i][j][1]
  avg_0 = tot_0 / 10
  avg_1 = tot_1 / 10
  avg_list.append([output_list[j], avg_0, avg_1])

our_table = PrettyTable(['NODE', 'n0', 'n1'])

print("\n-----------------------------------------\n")
print("Monte Carlo Simulation:")

for i in avg_list:
  our_table.add_row([i[0], i[1], i[2]])
print(our_table)


b_table = PrettyTable()
b_table.field_names = ['NODE', 'C0','C1']
d_table = PrettyTable()
d_table.field_names = ['n0','n1']

for n in node_list:
      b_table.add_row([n.name,n.c0,n.c1])
for i in avg_list:
      d_table.add_row([i[1], i[2]])
      
z = PrettyTable()
z_rows = []
counter = 0
for i in b_table.rows:
    i.extend(d_table.rows[counter])
    counter += 1
    z_rows.append(i)

field = []
field.extend(b_table.field_names)
field.extend(d_table.field_names)

z.field_names = field
z.add_rows(z_rows)
      
print("\n Comparison: SCOAP VS Monte Carlo")
print(z)






print("Finished - bye!")
