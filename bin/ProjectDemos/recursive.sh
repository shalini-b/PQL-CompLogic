#!/bin/bash

QUERY=simple_inject

cd ../../examples
java -jar ../bin/PQL-0.2.jar $QUERY.query sample
mv $QUERY.query.qry inst/query.qry
rm $QUERY.points
cd inst/
java -cp .:../../bin/PQL-0.2.jar sample.Sample

