#!/bin/bash

sysctl -w vm.overcommit_memory=1
echo madvise > /sys/kernel/mm/transparent_hugepage/enabled

exec redis-server --bind 0.0.0.0 --protected-mode no --appendonly yes --port 6379