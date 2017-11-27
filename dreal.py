
# -----------------------------------------------------------------------------
# a compiler for a sketching language for approximations to dReal input format
# -----------------------------------------------------------------------------

tokens = (
    'VAR','HOLE','NUMBER',
    'PLUS','MINUS','TIMES','DIVIDE','POWER',
    'EQUALS',
    'LPAREN','RPAREN',
#    'AND','OR',
    'NAME'
    )

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_POWER   = r'\^'
t_EQUALS  = r'='
#t_LE      = r'<='
#t_GE      = r'>='
#t_LT      = r'<'
#t_GT      = r'>'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
#t_AND     = r'/\\'
#t_OR      = r'\\/'
t_VAR     = r'X'
t_HOLE    = r'\?\?'
t_NAME    = r'[a-z][a-z]*'

def t_NUMBER(t):
    r'[\d.]+'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Float value too large %d", t.value)
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
#    ('left','AND','OR'),
    ('right', 'CHOICE'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('left','POWER'),
    ('right','UMINUS'),
    )

# we might consider just not attempting to interpret the analytic constraint...
def p_constraint_equals(t):
  'constraint : analytic EQUALS sketch'
  generate_dreal(t[1], t[3])

def p_analytic_expr(t):
  'analytic : expression'
  t[0] = t[1]

def p_sketch_expr(t):
  'sketch : skexpression'
  t[0] = t[1]

def p_expression_binop(t):
  '''expression : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression'''
  t[0] = (t[2], t[1], t[3])

def p_skexpression_power(t):
  '''expression : expression POWER NUMBER'''
  t[0] = ('^', t[1], (t[3],))

def p_expression_uminus(t):
  'expression : MINUS expression %prec UMINUS'
  t[0] = ('-', t[2])

def p_expression_group(t):
  'expression : LPAREN expression RPAREN'
  t[0] = t[2]

def p_expression_app(t):
  'expression : NAME LPAREN expression RPAREN'
  t[0] = ('app', t[1], t[3])

def p_expression_number(t):
  'expression : NUMBER'
  t[0] = (t[1],)

def p_expression_var(t):
  'expression : VAR'
  t[0] = ('X',)

def p_skexpression_binop(t):
  '''skexpression : skexpression PLUS skexpression
                  | skexpression MINUS skexpression
                  | skexpression TIMES skexpression
                  | skexpression DIVIDE skexpression'''
  t[0] = (t[2], t[1], t[3])

def p_skexpression_power(t):
  '''skexpression : skexpression POWER NUMBER'''
  t[0] = ('^', t[1], (t[3],))

def p_skexpression_uminus(t):
  'skexpression : MINUS skexpression %prec UMINUS'
  t[0] = ('-', t[2])

def p_skexpression_group(t):
  'skexpression : LPAREN skexpression RPAREN'
  t[0] = t[2]

def p_skexpression_number(t):
  'skexpression : NUMBER'
  t[0] = (t[1],)

def p_skexpression_var(t):
  'skexpression : VAR'
  t[0] = ('X',)

def p_skexpression_hole(t):
  'skexpression : HOLE'
  t[0] = ('??',)

def p_skexpression_choice(t):
  'skexpression : LPAREN HOLE skexplist RPAREN'
  t[0] = ('??', t[3])

def p_skexplist(t):
  '''skexplist : skexpression skexplist %prec CHOICE
               | skexpression'''
  if len(t) == 2:
    t[0] = [t[1]]
  else:
    t[0] = [t[1]] ++ t[2]

def p_error(t):
  print("Syntax error at '%s'" % str(t))


# compiler fxns

# return fresh var
count = 0
def fresh(f):
  global count
  v = "sk%d" % count
  f.write("[-10, 10] %s;\n" % v)
  count += 1
  return v

def generate_analytic(expr, prec):
  prec = 100 # always parenthesize
  # leaf node
  if len(expr) == 1:
    if type(expr[0]) == type(0.): # number
      return str(expr[0])
    elif expr[0] == 'X':
      return 'X'
  # some operation node
  else:
    if expr[0] == "+":
      s1 = generate_analytic(expr[1], 0)
      s2 = generate_analytic(expr[2], 0)
      s = s1 + " + " + s2
      if prec > 0:
        s = "(" + s + ")"
      return s
    elif expr[0] == "*":
      s1 = generate_analytic(expr[1], 1)
      s2 = generate_analytic(expr[2], 1)
      s = s1 + " * " + s2
      if prec > 1:
        s = "(" + s + ")"
      return s
    elif expr[0] == "/":
      s1 = generate_analytic(expr[1], 1)
      s2 = generate_analytic(expr[2], 1)
      s = s1 + " / " + s2
      if prec > 1:
        s = "(" + s + ")"
      return s
    elif expr[0] == "^":
      s1 = generate_analytic(expr[1], 2)
      s2 = generate_analytic(expr[2], 2)
      s = s1 + " ^ " + s2
      if prec > 2:
        s = "(" + s + ")"
      return s
    elif expr[0] == "-":
      if len(expr) == 2: # unary
        return "(-" + generate_analytic(expr[1], 3) + ")"
      else:
        s1 = generate_analytic(expr[1], 0)
        s2 = generate_analytic(expr[2], 0)
        s = s1 + " - " + s2
        if prec > 0:
          s = "(" + s + ")"
        return s
    elif expr[0] == "app":
      return expr[1] + "(" + generate_analytic(expr[2], 0) + ")"
  raise Exception("expression undefined: %s" % str(expr))
      
def generate_sketch(f, expr, prec):
  prec = 100 # always parenthesize
  # leaf node
  if len(expr) == 1:
    if type(expr[0]) == type(0.): # number
      return str(expr[0])
    elif expr[0] == 'X':
      return 'X'
    elif expr[0] == '??':
      return fresh(f)
  # some operation node
  else:
    if expr[0] == "+":
      s1 = generate_sketch(f, expr[1], 0)
      s2 = generate_sketch(f, expr[2], 0)
      s = s1 + " + " + s2
      if prec > 0:
        s = "(" + s + ")"
      return s
    elif expr[0] == "*":
      s1 = generate_sketch(f, expr[1], 1)
      s2 = generate_sketch(f, expr[2], 1)
      s = s1 + " * " + s2
      if prec > 1:
        s = "(" + s + ")"
      return s
    elif expr[0] == "/":
      s1 = generate_sketch(f, expr[1], 1)
      s2 = generate_sketch(f, expr[2], 1)
      s = s1 + " / " + s2
      if prec > 1:
        s = "(" + s + ")"
      return s
    elif expr[0] == "^":
      s1 = generate_sketch(f, expr[1], 2)
      s2 = generate_sketch(f, expr[2], 2)
      s = s1 + " ^ " + s2
      if prec > 2:
        s = "(" + s + ")"
      return s
    elif expr[0] == "-":
      if len(expr) == 2: # unary
        return "(-" + generate_sketch(f, expr[1], 3) + ")"
      else:
        s1 = generate_sketch(f, expr[1], 0)
        s2 = generate_sketch(f, expr[2], 0)
        s = s1 + " - " + s2
        if prec > 0:
          s = "(" + s + ")"
        return s
  raise Exception("skexpression undefined: %s" % str(expr))

# this accepts two halves of an ad hoc AST
# analytic is the analytic expression we're approximating
# sketch is the sketch we'll use
# final output:
# var:
# [some # of lines of form [-10, 10] [varname];]
# ctr:
# [the constraints in question]
# we generate a fresh variable for every real hole ??
# CHOICE IS CURRENTLY UNIMPLEMENTED
# for choice, we do a couple of things
# if the choice appears at the top level:
# - create a fresh variable to represent the choice
# - generate a series of equality constraints w/ analytic
# - disjunction over these constraints
# if the choice appears inside:
# - we have to do more work: result variable + uncertainty tracking
# - create a fresh variable to represent the choice
# - create a fresh variable to receive the contents
# - split up delta uncertainties
def generate_dreal(analytic, sketch):
  print "analytic"
  print analytic
  print "sketch"
  print sketch

  a = generate_analytic(analytic, 0)
  s = generate_sketch(outfile, sketch, 0) # outputs sketch vars
  outfile.write("ctr:\nabs( %s - ( %s ) ) < 0.002;\n" % (a, s))
    
import sys
import ply.yacc as yacc
parser = yacc.yacc()

if len(sys.argv) != 3:
  print "Usage: %s [sketch file] [output file]" % sys.argv[0]
  exit(0)

outfile = open(sys.argv[2], "w")

with open(sys.argv[1]) as f:
  bounds = f.readline()

  # variable section
  outfile.write("var:\n")

  # our function variable
  outfile.write(bounds)

  # parse rest of file as sketch
  s = f.read()
  parser.parse(s)

outfile.close()
