import configparser
import math
import os
from typing import List

#from sha_learning.case_studies.gr3n.sul_definition import identified_distr
from sha_learning.case_studies.hri.sul_definition import CS_VERSION
from sha_learning.domain.lshafeatures import FlowCondition
from sha_learning.domain.sigfeatures import SampledSignal, Timestamp, Event, SignalPoint
from sha_learning.learning_setup.logger import Logger

config = configparser.ConfigParser()
config.sections()
config.read(
    os.path.dirname(os.path.abspath(__file__)).split('sha_learning')[0] + 'sha_learning/resources/config/config.ini')
config.sections()

try:
    CS_VERSION = int(config['SUL CONFIGURATION']['CS_VERSION'].replace('\n', ''))
except ValueError:
    CS_VERSION = None

ON_R = 100.0
LOGGER = Logger('SUL DATA HANDLER')


def is_chg_pt(curr, prev):
    return curr != prev


def label_event(events: List[Event], signals: List[SampledSignal], t: Timestamp):
    loc = signals[0]
    #wOpen = signals[2]
    t = t.to_secs()

    #identified_guard = ''
    #curr_wOpen = list(filter(lambda x: x.timestamp.to_secs() <= t, wOpen.points))[-1]
    #if CS_VERSION in [2, 4, 5, 6, 7]:
    #    identified_guard += events[0].guard if curr_wOpen.value == 1.0 else events[2].guard
    #if CS_VERSION in [3, 8, 9, 10]:
    #    if curr_wOpen.value == 2.0:
    #        identified_guard += events[4].guard
    #    elif curr_wOpen.value == 1.0:
    #        identified_guard += events[2].guard
    #    else:
    #        identified_guard += events[0].guard

    curr_loc = list(filter(lambda x: x.timestamp.to_secs() <= t, loc.points))[-1]
    if len(list(filter(lambda x: x.timestamp.to_secs() < t, loc.points))) > 0:
        old_loc = list(filter(lambda x: x.timestamp.to_secs() < t, loc.points))[-1]
    else: old_loc = -1

#    if curr_loc.value == 3 or (curr_loc.value == 4 and old_loc.value == 3):
#        identified_channel = events[2].chan
#    elif curr_loc.value == 1:
#        identified_channel = events[0].chan
#    elif curr_loc.value == 6:
#        identified_channel = events[3].chan
#    else: identified_channel = events[1].chan


    # if curr_loc.value == 1:
    #     identified_channel = events[0].chan
    # elif curr_loc.value == 7 or curr_loc.value == 6:
    #     identified_channel = events[2].chan
    # elif curr_loc.value == 4 and old_loc.value == 2:
    #     identified_channel = events[2].chan
    # else: identified_channel = events[1].chan


    if curr_loc.value == 1:
        identified_channel = events[0].chan
    elif curr_loc.value == 6:
        identified_channel = events[3].chan
    elif curr_loc.value == 3:
        identified_channel = events[2].chan
    elif curr_loc.value == 2 and (old_loc.value == 9 or old_loc.value == 7):
        identified_channel = events[2].chan
    else: identified_channel = events[1].chan

    #if curr_loc.value == 1:
    #    identified_channel = events[0].chan
    #if curr_loc.value == 6:
    #   identified_channel = events[2].chan
    #else: identified_channel = events[1].chan

    #if curr_loc.value == 1:
    #    identified_channel = events[0].chan
    #if curr_loc.value == 3 or (curr_loc.value == 4 and old_loc.value == 3):
    #    identified_channel = events[2].chan
    #elif curr_loc.value == 6:
    #    identified_channel = events[3].chan
    #else: identified_channel = events[1].chan

    # if curr_loc.value == 1:
    #     identified_channel = events[0].chan
    # elif curr_loc.value == 6:
    #     identified_channel = events[2].chan
    # elif curr_loc.value == 4 or curr_loc.value == 8:
    #     identified_channel = events[3].chan
    # else: identified_channel = events[1].chan


    #if curr_loc.value == 1:
    #    identified_channel = events[0].chan
    #elif curr_loc.value == 2:
    #    identified_channel = events[2].chan
    #elif curr_loc.value == 3 and old_loc.value == 1:
    #    identified_channel = events[1].chan
    #elif curr_loc.value == 3 and old_loc.value == 2:
    #    identified_channel = events[1].chan
    #else: identified_channel = events[3].chan


#    identified_channel = events[0].chan if (curr_loc.value == 2 or (curr_loc.value == 4 and old_loc.value == 2)) \
#       else events[1].chan

    #identified_event = [e for e in events if e.guard == identified_guard and e.chan == identified_channel][0]
    identified_event = [e for e in events if e.chan == identified_channel][0]
    return identified_event


def parse_data(path: str):
    # support method to parse traces sampled by ref query
    f = open(path, 'r')
    variables = ['s.loc', 's.slope']
    lines = f.readlines()
    split_indexes = [lines.index(k + ':\n') for k in variables]
    split_lines = [lines[i + 1:split_indexes[ind + 1]] for ind, i in enumerate(split_indexes) if
                   i != split_indexes[-1]]
    split_lines.append(lines[split_indexes[-1] + 1:len(lines)])
    new_signals: List[SampledSignal] = []
    for i, v in enumerate(variables):
        entries = [line.split(' ') for line in split_lines[i]][0][1:]
        entries = [entry.replace('(', '').replace(')', '').replace('\n', '') for entry in entries]
        t = [float(x.split(',')[0]) for x in entries]
        values = [float(x.split(',')[1]) for x in entries]
        ts = [Timestamp(0, 0, 0, 0, 0, i) for i in t]
        signal_pts: List[SignalPoint] = [SignalPoint(ts[i], values[i]) for i in range(len(ts))]
        new_signal: SampledSignal = SampledSignal(signal_pts, v)
        new_signals.append(new_signal)
    return new_signals


def get_wef_param(segment: List[SignalPoint], flow: FlowCondition):
    if len(segment) == 0:
        return -1
    return segment[-1].value
#    return 1