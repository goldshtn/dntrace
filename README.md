### dntrace

This tool traces .NET Core runtime events, displays them in real-time, and
aggregates them in memory to produce statistics. Only a small amount of events
is stored on the disk as a cache (at most 5M per-cpu), which provides for
lightweight monitoring that can be sustained for long time intervals.

> This tool is not production-ready; use at your own risk. It was briefly
> tested with .NET Core 2.0 on Fedora. Other distributions or versions might
> not work.

To run dntrace, you will need Python, [LTTng](https://lttng.org) and
Babeltrace. You will also need .NET Core, of course. The usage message should
provide the basic details. Basic example:

```
# ./dntrace.sh -p $(pidof myapp) gc heap alloc exc
Session dntrace-session created.
Traces will be written in net://127.0.0.1
Live timer set to 1000000 usec
PID 26357 tracked in session dntrace-session
UST context vpid added to all channels
UST context vtid added to all channels
UST context procname added to all channels
UST event DotNETRuntime:GCStart* created in channel channel0
UST event DotNETRuntime:GCEnd* created in channel channel0
UST event DotNETRuntime:GCTriggered created in channel channel0
UST event DotNETRuntime:GCHeapStats* created in channel channel0
UST event DotNETRuntime:GCAllocationTick* created in channel channel0
UST event DotNETRuntime:Exception* created in channel channel0
Tracing started for session dntrace-session
GC finished in generation 2, took 0.00997972 seconds
  Gen 0 size: 1,647,248 bytes
  Gen 1 size: 354,080 bytes
  Gen 2 size: 1,518,824 bytes
GC finished in generation 2, took 0.01372528 seconds
  Gen 0 size: 25,166,224 bytes
  Gen 1 size: 354,080 bytes
  Gen 2 size: 1,518,824 bytes
GC finished in generation 2, took 0.00824976 seconds
  Gen 0 size: 1,647,248 bytes
  Gen 1 size: 253,720 bytes
  Gen 2 size: 1,619,384 bytes
GC finished in generation 2, took 0.01258755 seconds
  Gen 0 size: 1,647,248 bytes
  Gen 1 size: 1,940,984 bytes
  Gen 2 size: 1,619,432 bytes
GC finished in generation 2, took 0.00863647 seconds
  Gen 0 size: 28,569,576 bytes
  Gen 1 size: 1,940,984 bytes
  Gen 2 size: 1,619,432 bytes
GC finished in generation 2, took 0.01345682 seconds
  Gen 0 size: 28,840,904 bytes
  Gen 1 size: 1,940,984 bytes
  Gen 2 size: 1,619,432 bytes
GC finished in generation 2, took 0.00807762 seconds
  Gen 0 size: 1,647,248 bytes
  Gen 1 size: 253,856 bytes
  Gen 2 size: 1,619,248 bytes
GC finished in generation 2, took 0.01396036 seconds
  Gen 0 size: 25,150,224 bytes
  Gen 1 size: 253,856 bytes
  Gen 2 size: 1,619,248 bytes
GC finished in generation 2, took 0.00838375 seconds
  Gen 0 size: 1,647,248 bytes
  Gen 1 size: 253,672 bytes
  Gen 2 size: 1,619,432 bytes
GC finished in generation 2, took 0.01298237 seconds
  Gen 0 size: 1,647,248 bytes
  Gen 1 size: 1,940,984 bytes
  Gen 2 size: 1,619,432 bytes
GC finished in generation 2, took 0.01299524 seconds
  Gen 0 size: 1,554,584 bytes
  Gen 1 size: 1,979,216 bytes
  Gen 2 size: 1,619,200 bytes
GC finished in generation 2, took 0.01552916 seconds
  Gen 0 size: 35,081,216 bytes
  Gen 1 size: 1,979,216 bytes
  Gen 2 size: 1,619,200 bytes
GC finished in generation 2, took 0.01511431 seconds
  Gen 0 size: 1,547,800 bytes
  Gen 1 size: 1,940,984 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 2, took 0.02407312 seconds
  Gen 0 size: 25,648,832 bytes
  Gen 1 size: 1,940,984 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 2, took 0.00887823 seconds
  Gen 0 size: 1,547,776 bytes
  Gen 1 size: 253,696 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 2, took 0.01282215 seconds
  Gen 0 size: 1,547,768 bytes
  Gen 1 size: 1,941,168 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 2, took 0.01746368 seconds
  Gen 0 size: 45,877,320 bytes
  Gen 1 size: 1,941,168 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 2, took 0.02003002 seconds
  Gen 0 size: 49,033,104 bytes
  Gen 1 size: 1,941,168 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 1, took 0.04814339 seconds
  Gen 0 size: 48 bytes
  Gen 1 size: 19,291,232 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 2, took 0.00750971 seconds
  Gen 0 size: 1,547,952 bytes
  Gen 1 size: 253,856 bytes
  Gen 2 size: 1,719,760 bytes
GC finished in generation 2, took 0.01276875 seconds
  Gen 0 size: 1,547,952 bytes
  Gen 1 size: 1,940,984 bytes
  Gen 2 size: 1,719,944 bytes
GC finished in generation 2, took 0.01215410 seconds
  Gen 0 size: 1,548,808 bytes
  Gen 1 size: 1,878,832 bytes
  Gen 2 size: 1,719,944 bytes
GC finished in generation 2, took 0.02393913 seconds
  Gen 0 size: 25,755,952 bytes
  Gen 1 size: 1,878,832 bytes
  Gen 2 size: 1,719,944 bytes
GC finished in generation 2, took 0.00891161 seconds
  Gen 0 size: 1,547,776 bytes
  Gen 1 size: 253,696 bytes
  Gen 2 size: 1,719,944 bytes
GC finished in generation 2, took 0.01272869 seconds
  Gen 0 size: 1,547,952 bytes
  Gen 1 size: 1,941,168 bytes
  Gen 2 size: 1,719,760 bytes
--- EVENT SUMMARY ---
Total GC invocations: 25
Total GC duration: 0.36310101 seconds
Total GC triggered: 25
Average GC duration: 0.01452404 seconds
Generation 0 GC: 0
Generation 1 GC: 1
Generation 2 GC: 24
Total allocated bytes: 898,366,608
Top 10 allocated types:
  System.String                      2095
  System.Xml.XmlName                 1527
  System.Xml.XmlElement              1151
  Entry                               835
  System.Char[]                       553
  Entry[]                             552
  System.Int32                        517
  System.Xml.XmlName[]                408
  System.Object[]                      35
  System.Diagnostics.Tracing.Eve       21
Total exceptions thrown: 0
Waiting for data availability
Tracing stopped for session dntrace-session
Session dntrace-session destroyed
```

Full usage message:

```
# ./dntrace.sh
USAGE: dntrace [-p PID] [-d DURATION_SECS] [-i INTERVAL]
               [-s SESSION] event [event ...]

The supported events are:
  gc      - Display GC start, end, and duration.
  heap    - Display heap statistics (generation sizes etc.).
  alloc   - Display statistics on allocated objects.
  exc     - Display .NET exceptions thrown.
```
