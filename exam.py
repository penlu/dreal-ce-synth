import sys
import string
import random

# take counterexample to new search with X filled in

orig = sys.argv[1]
model = sys.argv[2]
output = sys.argv[3]

orig = open(orig)
model = open(model)
out = open(output, "w")

# dump all lines, keeping the constraint line specially
global c
c = ""
while True:
  line = orig.readline()
  if line == "ctr:\n":
    out.write(line)
    c = orig.readline()
    line = c
  elif line == "":
    break
  out.write(line)

# dump first line of model
model.readline()

# get counterexample constraint
x = model.readline()
start = float(x.split("[")[1].split(",")[0])
stop = float(x.split("[")[1].split("]")[0].split(",")[1])

# finally, write new constraint
select = random.random() * (stop - start) + start
out.write(str(select).join(c.split("X")))

