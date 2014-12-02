#!/bin/bash
vms=$( virsh list --all --name )

for i in $vms
do
    virsh dumpxml $i > $1/$i.xml
done
