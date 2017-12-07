#!/usr/bin/env python
#
# dnstats - Aggregate .NET Core runtime events and display statistics and
#           real-time data.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# Copyright (C) 2017 Sasha Goldshtein.

import ctypes as ct
import sys
import time
import threading

class Event(object):
    def __init__(self, parts):
        time_s, time_ns = parts[0][1:-1].split('.')
        self.time = time.mktime(time.strptime(time_s, '%H:%M:%S')) + \
                    (1e-9 * int(time_ns))
        self.host = parts[2]
        self.event_type = parts[3]
        self._parse_rest(parts[4:])

    def _parse_rest(self, parts):
        self.data = {}
        expecting_key = True
        expecting_value = False
        for tok in parts:
            if tok == "{" or tok == "}" or tok == "},":
                continue
            elif tok == "=":
                expecting_value = True
            elif expecting_key:
                key = tok if tok[-1] != ',' else tok[:-1]
                expecting_key = False
            elif expecting_value:
                self.data[key] = tok if tok[-1] != ',' else tok[:-1]
                expecting_value = False
                expecting_key = True

class GCStartEvent(Event):
    def __init__(self, parts):
        super(GCStartEvent, self).__init__(parts)
        self.gc_number = int(self.data["Count"])
        self.generation = int(self.data["Depth"])
        self.reason = int(self.data["Reason"])
        self.gc_type = int(self.data["Type"])

class GCEndEvent(Event):
    def __init__(self, parts):
        super(GCEndEvent, self).__init__(parts)
        self.gc_number = int(self.data["Count"])
        self.generation = int(self.data["Depth"])

class GCTriggeredEvent(Event):
    def __init__(self, parts):
        super(GCTriggeredEvent, self).__init__(parts)
        self.reason = int(self.data["Reason"])

class RawGCHeapStats(ct.Structure):
    _pack_ = 1
    _fields_ = [
            ('Gen0Size', ct.c_ulonglong),
            ('Gen0Promoted', ct.c_ulonglong),
            ('Gen1Size', ct.c_ulonglong),
            ('Gen1Promoted', ct.c_ulonglong),
            ('Gen2Size', ct.c_ulonglong),
            ('Gen2Promoted', ct.c_ulonglong),
            ('LOHSize', ct.c_ulonglong),
            ('LOHPromoted', ct.c_ulonglong),
            ('FinalizationPromotedSize', ct.c_ulonglong),
            ('FinalizationPromotedCount', ct.c_ulonglong),
            ('PinnedObjectCount', ct.c_uint),
            ('SinkBlockCount', ct.c_uint),
            ('GCHandleCount', ct.c_uint)
            ]

class GCHeapStatsEvent(Event):
    def __init__(self, parts):
        super(GCHeapStatsEvent, self).__init__(parts)
        # TODO Need to parse out the binary data based on src/inc/eventtrace.h
        #      The data structure is nested, which means our parsing completely
        #      messes it up...
        self._super_ugly_hack_parse(parts[4:])

    def _super_ugly_hack_parse(self, parts):
        reassembled = bytearray(94)
        for index, part in enumerate(parts):
            if part[0] == '[' and part[-1] == ']':
                the_byte = parts[index+2][:-1] \
                        if parts[index+2][-1] == ',' else  parts[index+2]
                reassembled[int(part[1:-1])] = int(the_byte) & 0xff
        self.heap_stats = RawGCHeapStats.from_buffer(reassembled)
        self.size_by_gen = {
                0: self.heap_stats.Gen0Size,
                1: self.heap_stats.Gen1Size,
                2: self.heap_stats.Gen2Size,
                3: self.heap_stats.LOHSize
                }

class GCAllocTickEvent(Event):
    def __init__(self, parts):
        super(GCAllocTickEvent, self).__init__(parts)
        self.allocation_amount = int(self.data["AllocationAmount64"])
        self.type_name = self.data["TypeName"][1:-1]

class ExceptionEvent(Event):
    def __init__(self, parts):
        super(ExceptionEvent, self).__init__(parts)
        self.exception_type = self.data["ExceptionType"]
        self.message = self.data["ExceptionMessage"]

class GCEventConsumer(object):
    def __init__(self):
        self.count = 0
        self.total_duration = 0
        self.gc_by_gen = {0:0, 1:0, 2:0}
        self.gc_durations = []
        self.gc_triggered = 0
        self.last_start = 0

    def consume(self, event):
        if isinstance(event, GCStartEvent):
            self.count += 1
            self.last_start = event.time
        elif isinstance(event, GCEndEvent):
            duration = event.time - self.last_start
            self.total_duration += duration
            self.gc_durations.append(duration)
            self.gc_by_gen[event.generation] += 1
        elif isinstance(event, GCTriggeredEvent):
            self.gc_triggered += 1
        elif isinstance(event, GCHeapStatsEvent):
            pass

    def print_event(self, event):
        if isinstance(event, GCEndEvent):
            print("GC finished in generation %d, took %3.8f seconds" % 
                    (event.generation, self.gc_durations[-1]))
        if isinstance(event, GCHeapStatsEvent):
            for gen in range(0, 3):
                print("  Gen {} size: {:,} bytes".format(
                    gen, event.size_by_gen[gen]))

    def print_summary(self):
        print("Total GC invocations: %d" % self.count)
        print("Total GC duration: %3.8f seconds" % self.total_duration)
        print("Total GC triggered: %d" % self.gc_triggered)
        print("Average GC duration: %3.8f seconds" %
                ((self.total_duration / self.count) if self.count > 0 else 0))
        for gen, count in self.gc_by_gen.items():
            print("Generation %d GC: %d" % (gen, count))

class AllocEventConsumer(object):
    def __init__(self):
        self.total_allocated_bytes = 0
        self.allocs_by_type = {}

    def consume(self, event):
        if not isinstance(event, GCAllocTickEvent):
            return
        self.total_allocated_bytes += event.allocation_amount
        if event.type_name not in self.allocs_by_type:
            self.allocs_by_type[event.type_name] = 1
        else:
            self.allocs_by_type[event.type_name] += 1

    def print_event(self, event):
        pass

    def print_summary(self):
        print("Total allocated bytes: {:,}".format(self.total_allocated_bytes))
        print("Top 10 allocated types:")
        for type_name, allocs in sorted(self.allocs_by_type.items(),
                key=lambda kv: -kv[1])[:10]:    # Top 10
            print("  %-30s %8d" % (type_name[:30], allocs))

class ExceptionEventConsumer(object):
    def __init__(self):
        self.total_exceptions = 0
        self.exceptions_by_type = {}

    def consume(self, event):
        if not isinstance(event, ExceptionEvent):
            return
        self.total_exceptions += 1
        if event.exception_type not in self.exceptions_by_type:
            self.exceptions_by_type[event.exception_type] = 1
        else:
            self.exceptions_by_type[event.exception_type] += 1

    def print_event(self, event):
        if isinstance(event, ExceptionEvent):
            print("Exception of type %s thrown: %s" % (event.exception_type,
                                                       event.message))

    def print_summary(self):
        print("Total exceptions thrown: %d" % self.total_exceptions)
        for exc, count in sorted(self.exceptions_by_type.items(),
                key=lambda kv: -kv[1]):
            print("  %-30s %d" % (exc[:30], count))

def create_event(line):
    parts = line.split()
    event_type = parts[3].split(':')[1]
    if event_type == "GCStart_V2":
        return GCStartEvent(parts)
    if event_type == "GCEnd_V1":
        return GCEndEvent(parts)
    if event_type == "GCTriggered":
        return GCTriggeredEvent(parts)
    if event_type == "GCHeapStats_V1":
        return GCHeapStatsEvent(parts)
    if event_type == "GCAllocationTick_V3":
        return GCAllocTickEvent(parts)
    if event_type == "ExceptionThrown_V1":
        return ExceptionEvent(parts)

# TODO Disable consumers based on the events chosen by the user, so they don't
#      pollute the output with empty messages.
consumers = [GCEventConsumer(), AllocEventConsumer(), ExceptionEventConsumer()]

interval = int(sys.argv[1]) if len(sys.argv) == 2 else -1

def print_summary_internal():
    print("--- EVENT SUMMARY ---")
    for consumer in consumers:
        consumer.print_summary()

def print_summary():
    timer = threading.Timer(interval, print_summary)
    timer.daemon = True
    timer.start()
    print_summary_internal()

if interval != -1:
    print_summary()

try:
    for line in sys.stdin:
        event = create_event(line)
        for consumer in consumers:
            consumer.consume(event)
            consumer.print_event(event) # This can print or do nothing
except KeyboardInterrupt:
    pass

print_summary_internal()    # Print one more time before exiting
