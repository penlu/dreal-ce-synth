import sys
import string
import random

# the worst code I've ever written

# transform synthesized candidate program into counterexample search problem
# in particular, we just flip the equality

orig = sys.argv[1]
model = sys.argv[2]
output = sys.argv[3]

orig = open(orig)
model = open(model)
out = open(output, "w")

# first two lines, var: and our fxn variable
out.write(orig.readline())
out.write(orig.readline())

# dump first two lines of model
model.readline()
model.readline()

# modify boxes
while True:
  v = orig.readline()

  # are we done?
  if v == "ctr:\n":
    out.write(v)
    break

  # get box from model
  m = model.readline()
  start = float(m.split("[")[1].split(",")[0])
  stop = float(m.split("[")[1].split("]")[0].split(",")[1])
  
  # get var from original (assuming model output preserves ordering!)
  var = string.split(v)[-1]

  box = random.random() * (stop - start) + start
  out.write("[" + str(box) + "," + str(box) + "] " + var + "\n")

# finally, write new constraint
c = orig.readline()
out.write(string.split(c, "=")[0] + " > 0.002;")

