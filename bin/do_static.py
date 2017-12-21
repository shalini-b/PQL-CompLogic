#!/bin/env python
import sys
import os
import os.path
import re

# Do all the steps necessary to run a PQL analysis statically.
#
# ./do_static.py <mainclass> <pql_query_file>
#
# will jam the program for which main is defined in <mainclass> into
# the bddbddb system, do the pointer analysis on it, convert the PQL
# query into an appropriate query on the pointer analysis, run the PQL
# query, and dump the results into "results/relevant.tuples".  That
# file is a list of indices into the invocation-site map.  As joeq
# can't actually talk about bytecodes, this currently only works for
# queries that can be expressed without recourse to array accesses or
# field dereferences.
#
# Running this repeatedly on the same application duplicates a lot of
# work (in particular, multiple PQL queries on the same codebase can
# re-use the pointer analysis results), but as perturbing the target
# program requires a redo from start, this isn't a huge priority.

# Define the PQLHOME variable to specify where the binary is.
# Alternatively, hack the default (current directory).

# This stuff gets checked on MODULE LOAD, for fail-fast.

pql_home = os.getenv ("PQLHOME", os.path.curdir)
java_cmd = "java"

# If True, delete all the temporary Datalog &c files.
#cleanup = False
cleanup = True

basecp = os.getenv ("CLASSPATH", ".").split (os.path.pathsep)
print "base classpath directories: %s" % str(basecp)

verbose = True

def check_env_vars ():
    global pql_home, pql_jar
    
    pql_ok = pql_home is not None and os.path.exists(os.path.join(pql_home, "PQL-0.2.jar"))

    if not pql_ok:
        print "PQLHOME is not set or set to improper directory"

    pql_jar = os.path.join (pql_home, "PQL-0.2.jar")

# Clear old results
def clean (resultdir="results"):
    if not resultdir.endswith (os.path.sep):
        resultdir += os.path.sep
    for (root, subs, files) in os.walk(resultdir, False):
        for f in files:
            if verbose:
                print "Deleting file "+os.path.join(root, f)
                os.remove (os.path.join(root, f))
        if verbose:
            print "Deleting directory "+root
        os.rmdir(root)

# Generate CI relations, including the maps and tuples the translator needs

# TODO: switches for selecting bogosity of summaries
def gen_relations (main_class, path_dirs, resultdir="results"):
    if not resultdir.endswith (os.path.sep):
        resultdir += os.path.sep
    classpath = os.path.pathsep.join([os.path.curdir, pql_jar] + path_dirs)
    cmd = '%s -cp "%s" -Xmx1024m -Dpa.dumppath=%s -Dpa.specialmapinfo=yes -Dpa.dumpunmunged=yes -Dpa.signaturesinlocs=yes joeq.Main.GenRelations %s' % (java_cmd, classpath, resultdir, main_class)
    if verbose:
        print cmd
    (in_p, out_p) = os.popen4(cmd)
    result_str = out_p.read()
    out_p.close()
    in_p.close()
    if verbose:
        print result_str
    cmd = '%s -mx100m -Dbasedir=%s -Dresultdir=%s -Dpa.discovercallgraph=yes -cp "%s" net.sf.bddbddb.BuildEquivalenceRelation H0 H0 heap.map I0 invoke.map' % (java_cmd, resultdir, resultdir, classpath)
    if verbose:
        print cmd
    (in_p, out_p) = os.popen4(cmd)
    result_str = out_p.read()
    out_p.close()
    if verbose:
        print result_str
    # TODO: Make generic with calls in os
    os.system ("mv map_* results/")

# Generic solver routines
def datalog_solve(program, filename, numberingtype="scc"):
    f = file (filename, "wt")
    print>>f, program
    f.close()
    classpath = os.path.pathsep.join ([pql_jar, os.path.curdir])
    cmd = '%s -cp "%s" -mx256m -Dlearnbestorder=n -Dsingleignore=yes -Dbasedir=./results/ -Dbddcache=1500000 -Dbddnodes=40000000 -Dnumberingtype=%s -Dpa.clinit=no -Dpa.filternull=yes -Dpa.unknowntypes=no net.sf.bddbddb.Solver %s' % (java_cmd, classpath, numberingtype, filename)
    if verbose:
        print cmd
    (in_p, out_p) = os.popen2(cmd)
    result_str = out_p.read()
    out_p.close()    
    in_p.close()
    if cleanup:
        os.remove (filename)
    print result_str
    return result_str
    
# Number contexts, fixing VC if necessary

numbering = """# -*- Mode: C; indent-tabs-mode: nil; c-basic-offset: 4 -*-
### Context-sensitive inclusion-based pointer analysis using cloning
# 
# Calculates the numbering based on the call graph relation.
# 
# Author: John Whaley

.basedir "results"
.include "fielddomains.pa"

.bddnodes 10000000
.bddcache 1000000

# found by findbestorder:
#.bddvarorder G0_C0_C1_N0_F0_I0_M1_M0_V1xV0_VC1xVC0_T0_Z0_T1_H0_H1
.bddvarorder C0_C1_N0_F0_I0_M1_M0_V1xV0_VC1xVC0_T0_Z0_T1_H0_H1_G0

### Relations

mI (method:M0, invoke:I0, name:N0) input
IE0 (invoke:I0, target:M0) input

roots (method:M0) input

mI0 (method:M0, invoke:I0)
IEnum (invoke:I0, target:M0, ccaller:VC1, ccallee:VC0) output

### Rules

mI0(m,i) :- mI(m,i,_).
IEnum(i,m,vc2,vc1) :- roots(m), mI0(m,i), IE0(i,m). number
"""

def fix_contexts():
    f_str = datalog_solve (numbering, "number.dtl")
    m = re.search(r"paths = (\d+)", f_str)
    if m is not None:
        paths = m.group(1)
        print "Requires %s paths." % paths
        domains = []
        i = file(os.path.join("results", "fielddomains.pa"), "rt")
        for l in i:
            if l.startswith("VC "):
                domains.append("VC %s" % paths)
            else:
                domains.append(l.strip())
        i.close()
        i = file(os.path.join("results", "fielddomains.pa"), "wt")
        for l in domains:
            print>>i, l
        i.close()

# Run context-sensitive pointer analysis

pacs="""# -*- Mode: C; indent-tabs-mode: nil; c-basic-offset: 4 -*-
### Context-sensitive inclusion-based pointer analysis using cloning
# 
# Calculates the numbering based on the call graph relation.

.basedir "results"
.include "fielddomains.pa"

.bddnodes 10000000
.bddcache 1000000

# found by findbestorder:
#.bddvarorder G0_C0_C1_N0_F0_I0_M1_M0_V1xV0_VC1xVC0_T0_Z0_T1_H0_H1
.bddvarorder C0_G0_N0_F0_I0_M1_M0_V1xV0_VC1xVC0_T0_Z0_T1_H0_H1

### Relations

vP0 (v:V0, h:H0) input
A (dest:V0, source:V1) input
S (base:V0, field:F0, src:V1) input
L (base:V0, field:F0, dest:V1) input
actual (invoke:I0, num:Z0, actualparam:V1) input
formal (method:M0, num:Z0, formalparam:V0) input
Mret (method:M0, v:V1) input
Mthr (method:M0, v:V1) input
Iret (invoke:I0, v:V0) input
Ithr (invoke:I0, v:V0) input
mI (method:M0, invoke:I0, name:N0) input
IE0 (invoke:I0, target:M0) input
IE1 (invoke:I0, target:M0) 
vT (var:V0, type:T0) input
hT (heap:H0, type:T1) input
aT (type:T0, type:T1) input
cha (type:T1, name:N0, method:M0) input
hP0 (ha:H0, field:F0, hb:H1) input
mV(m : M0, v : V0) input

IEnum (invoke:I0, target:M0, ccaller:VC1, ccallee:VC0) input
vPfilter (v:V0, h:H0)
IEcs (ccaller:VC0, invoke:I0, ccallee:VC1, target:M0) output
cA (vcdest:VC0, dest:V0, vcsrc:VC1, source:V1) output
cvP (vc:VC0, v:V0, h:H0) output

hP (ha:H0, field:F0, hb:H1) output
IE (invoke:I0, target:M0) output
vP (v:V0, h:H0) output 

### Rules

cvP(_,v,h) :- vP0(v,h).
cA(_,v1,_,v2) :- A(v1,v2).
IEcs(vc2,i,vc1,m) :- IE0(i,m), IEnum(i,m,vc2,vc1).
vPfilter(v,h) :- vT(v,tv), aT(tv,th), hT(h,th).
cA(vc1,v1,vc2,v2) :- formal(m,z,v1), IEcs(vc2,i,vc1,m), actual(i,z,v2).
cA(vc2,v2,vc1,v1) :- Mret(m,v1), IEcs(vc2,i,vc1,m), Iret(i,v2).
#cA(vc2,v2,vc1,v1) :- Mthr(m,v1), IEcs(vc2,i,vc1,m), Ithr(i,v2).

cvP(vc1,v1,h) :- cA(vc1,v1,vc2,v2), cvP(vc2,v2,h), vPfilter(v1,h).
hP(h1,f,h2) :- S(v1,f,v2), cvP(vc1,v1,h1), cvP(vc1,v2,h2).
cvP(vc1,v2,h2) :- L(v1,f,v2), cvP(vc1,v1,h1), hP(h1,f,h2), vPfilter(v2,h2). split

vP(v, h) :- cvP(_, v, h).
IE(i, m) :- IEcs (_,i,_,m).
"""

# Do the PQL query

dumptypes = """.basedir "results"

### Domains

.include "fielddomains.pa"

.bddvarorder M1_I0_N0_F0_M0_V1xV0_H1_Z0_T0_T1_H0
### Relations

aT (type1:T0, type2:T1) input outputtuples
"""

def run_pql(pql_query):
    datalog_solve (dumptypes, "dumpat.dtl")

    pql_cp = os.path.pathsep.join([os.path.curdir, pql_jar])
    cmd = "%s -cp %s -Dpql.datalog.pacs=no net.sf.pql.datalog.DatalogGenerator %s" % (java_cmd, pql_cp, pql_query)
    if verbose:
        print cmd
    (i_p, o_p, e_p) = os.popen3 (cmd)
    dtl = o_p.read()
    problems = e_p.read()
    print problems
    datalog_solve (dtl, "pql_conv.dtl")

# Map resulting tuples to invocation sites
def tuple_map (src, names, target):
    src = os.path.join(os.path.curdir, "results", src)
    names = os.path.join(os.path.curdir, "results", names)
    n = [x.strip() for x in file(names)]
    l = [n[int(x)] for x in file(src) if x[0] != '#' and int(x) < len(n)]
    o = file(target, "wt")
    for x in l:
        print>>o, x
    o.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s <main_class> <pql_query>"
        sys.exit(1)
    check_env_vars()
    clean()
    print "Generating relations..."
    gen_relations (sys.argv[1], basecp)
    print "Counting contexts..."
    fix_contexts()
    print "Numbering contexts..."
    datalog_solve (numbering, "numbering.dtl")
    print "Performing pointer analysis..."
    datalog_solve (pacs, "pacs.dtl")
    print "Performing PQL analysis..."
    run_pql(sys.argv[2])
    print "Mapping tuples to invocation sites..."
    tuple_map ("instrument.tuples", "invoke.map", "%s.static" % sys.argv[2])
    print "Done!"
