#!/bin/bash

QUERY=sql_inject

cd ../../examples
PQLHOME=../bin/ python ../bin/do_static.py sample.CompleteSql $QUERY.query
java -jar ../bin/PQL-0.2.jar $QUERY.query sample $QUERY.query.static
mv $QUERY.query.qry inst/query.qry
cd inst/
java -cp .:../../bin/PQL-0.2.jar sample.CompleteSql
