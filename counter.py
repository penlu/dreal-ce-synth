import sys
import string

# transform synthesized into counterexample search
# in particular, flip the equality...

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
  box = string.split(m, "[")[1]
  box = string.split(box, "]")[0]
  
  # get var from original
  var = string.split(v)[-1]

  out.write("[" + box + "] " + var + "\n")

# finally, write new constraint
c = orig.readline()
out.write(string.split(c, "=")[0] + " > 0.001;")

