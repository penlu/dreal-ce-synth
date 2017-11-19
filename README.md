# Counterexample-Guided Program Synthesis with dReal

Counterexample-guided program synthesis (CEGIS) is a method of synthesizing a
program given:
1. a specification of the desired input/output behavior
2. a solver or two
3. possibly a sketch or some other syntactic constraint
CEGIS attempts to solve the problem of considering quantifications over the
space of all possible inputs by only paying attention to a subset of the
inputs.

CEGIS works by doing something like the following:
* Maintain a subset S of inputs: those on which we will *actually* check the I/O
  specification in each iteration.
* Repeat until convergence:
  * Request the solver to produce a candidate program C obeying (3) the
    syntactic constraints and satisfying (1) the input/output spec on all inputs
    in S. We hereby avoid quantifying over the input space.
  * Request the solver to produce a counterexample input I on which C violates
    the desired input/output behavior.
    * If I is found: add I to S.
    * If I is not found: C is a correct program.

In this case we're trying to synthesize expressions using + and * over floats
and a single variable X to approximate analytical expressions that may use some
of a set of functions.

As an example we're using the following sketch:
```
exp(X) = ?? * X^4 + ?? * X^3 + ?? * X^2 + ?? * X + ??
```

To clarify what the py scripts are doing, we can look at some of the generated
files.

One run's exptest4.dr:
```
var:
[0, 5] X;
[-10, 10] sk0;
[-10, 10] sk1;
[-10, 10] sk2;
[-10, 10] sk3;
[-10, 10] sk4;
ctr:
exp(X) - ( sk0 * X ^ 4.0 + sk1 * X ^ 3.0 + sk2 * X ^ 2.0 + sk3 * X + sk4 ) = 0;
exp(0.00110446301037) - ( sk0 * 0.00110446301037 ^ 4.0 + sk1 * 0.00110446301037 ^ 3.0 + sk2 * 0.00110446301037 ^ 2.0 + sk3 * 0.00110446301037 + sk4 ) = 0;
exp(0.00219913691566) - ( sk0 * 0.00219913691566 ^ 4.0 + sk1 * 0.00219913691566 ^ 3.0 + sk2 * 0.00219913691566 ^ 2.0 + sk3 * 0.00219913691566 + sk4 ) = 0;
exp(0.0102653615623) - ( sk0 * 0.0102653615623 ^ 4.0 + sk1 * 0.0102653615623 ^ 3.0 + sk2 * 0.0102653615623 ^ 2.0 + sk3 * 0.0102653615623 + sk4 ) = 0;
exp(0.0346415914635) - ( sk0 * 0.0346415914635 ^ 4.0 + sk1 * 0.0346415914635 ^ 3.0 + sk2 * 0.0346415914635 ^ 2.0 + sk3 * 0.0346415914635 + sk4 ) = 0;
```
The original problem is here for templating, plus constraints given particular
example values of input X.

exptest4.dr.model:
```
delta-sat with the following box:
	X : [0.0005312773907578769, 0.001062554781515754];
	sk0 : [-10, -9.9993896484375];
	sk1 : [0.6502222940893829, 0.6511125535565807];
	sk2 : [0.4948998334800267, 0.4949365306952006];
	sk3 : [1.000012760276706, 1.000013000854446];
	sk4 : [0.9999999911799154, 0.9999999914919041]
```
This proposes assignments to the variables sk0-4 to generate a candidate
program. dReal also produces a box for X where this works; this box can be
ignored. (In particular the output of dReal is an interval of values for each
variable, within which a selection of any tuple renders the constraints
delta-satisfiable.)

exptest4\_counter.dr:
```
var:
[0, 5] X;
[-9.99973746352,-9.99973746352] sk0;
[0.650998787653,0.650998787653] sk1;
[0.494903371199,0.494903371199] sk2;
[1.00001292546,1.00001292546] sk3;
[0.999999991407,0.999999991407] sk4;
ctr:
exp(X) - ( sk0 * X ^ 4.0 + sk1 * X ^ 3.0 + sk2 * X ^ 2.0 + sk3 * X + sk4 )  > 0.001;
```
Ask dReal to generate counterexamples to the candidate program.

exptest4\_counter.dr.model:
```
delta-sat with the following box:
	X : [0.0958442199497171, 0.09678930944557371];
	sk0 : [-9.999737463520001, -9.999737463520001];
	sk1 : [0.650998787653, 0.650998787653];
	sk2 : [0.494903371199, 0.494903371199];
	sk3 : [1.00001292546, 1.00001292546];
	sk4 : [0.999999991407, 0.999999991407]
```
Counterexample found with given box for X.
