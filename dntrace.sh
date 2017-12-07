#!/bin/bash
#
# dntrace - Trace .NET Core runtime events in real-time.
#
# USAGE: dntrace [-p PID] [-d DURATION_SECS] [-i INTERVAL]
#                [-s SESSION] event [event ...]
#
# The supported events are:
#   gc      - Display GC start, end, and duration.
#   heap    - Display heap statistics (generation sizes etc.).
#   alloc   - Display statistics on allocated objects.
#   exc     - Display .NET exceptions thrown.
#
# REQUIREMENTS: The lttng and babeltrace packages.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# Copyright (C) 2017 Sasha Goldshtein.

opt_pid=0; pid=
opt_duration=0; duration=
opt_interval=0; interval=
gc_enabled=0; heap_enabled=0; alloc_enabled=0; exc_enabled=0
session="dntrace-session"

trap destroy INT QUIT TERM PIPE HUP

# TODO Make bash script printouts only available in -v (verbose) mode.
#      Otherwise, print output only from the analysis script (dnstats.py).

function usage {
	cat <<-END >&2
USAGE: dntrace [-p PID] [-d DURATION_SECS] [-i INTERVAL]
               [-s SESSION] event [event ...]

The supported events are:
  gc      - Display GC start, end, and duration.
  heap    - Display heap statistics (generation sizes etc.).
  alloc   - Display statistics on allocated objects.
  exc     - Display .NET exceptions thrown.
END
    exit
}

function destroy {
    sudo lttng stop $session
    sudo lttng destroy $session
    exit
}

function record {
    sudo lttng create $session --live --no-output

    if (( opt_pid )); then
        sudo lttng track --userspace --session $session --pid $pid
    fi

    sudo lttng add-context --userspace --type vpid
    sudo lttng add-context --userspace --type vtid
    sudo lttng add-context --userspace --type procname

    if (( gc_enabled )); then
        sudo lttng enable-event --userspace --tracepoint DotNETRuntime:GCStart*
        sudo lttng enable-event --userspace --tracepoint DotNETRuntime:GCEnd*
        sudo lttng enable-event --userspace --tracepoint DotNETRuntime:GCTriggered
    fi
    if (( heap_enabled )); then
        sudo lttng enable-event --userspace --tracepoint DotNETRuntime:GCHeapStats*
    fi
    if (( alloc_enabled )); then
        sudo lttng enable-event --userspace --tracepoint \
                                DotNETRuntime:GCAllocationTick*
    fi
    if (( exc_enabled )); then
        sudo lttng enable-event --userspace --tracepoint DotNETRuntime:Exception*
    fi

    sudo lttng start $session
}

function view {
    if (( opt_duration )); then
        timeout="timeout $duration"
    else
        timeout=
    fi
    $timeout babeltrace --input-format=lttng-live \
             net://localhost/host/`hostname`/$session | ./dnstats.py $interval
}

while getopts p:d:i:h? opt
do
    case $opt in
        p)    opt_pid=1; pid=$OPTARG ;;
        d)    opt_duration=1; duration=$OPTARG ;;
        i)    opt_interval=1; interval=$OPTARG ;;
        h|?)  usage ;;
    esac
done
shift $(( $OPTIND - 1 ))
if [ "$#" -eq 0 ]; then
    usage
fi
for event in "$@"; do
    case $event in
        gc)     gc_enabled=1 ;;
        heap)   heap_enabled=1 ;;
        alloc)  alloc_enabled=1 ;;
        exc)    exc_enabled=1 ;;
        *)      usage ;;
    esac
done
record
view
destroy
