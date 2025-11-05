import configparser
import math
import os
from typing import List

from sha_learning.case_studies.WeakEqFail.sul_functions import label_event, parse_data, get_wef_param, \
    is_chg_pt
from sha_learning.domain.lshafeatures import RealValuedVar, FlowCondition, Trace
from sha_learning.domain.sigfeatures import Event, Timestamp
from sha_learning.domain.sulfeatures import SystemUnderLearning
from sha_learning.learning_setup.teacher import Teacher

CLOSED_R = 100.0
OFF_DISTR = (100.0, 1.0, 200)
ON_DISTR = (0.7, 0.01, 200)
DRIVER_SIG = 's.loc'
DEFAULT_M = 0
DEFAULT_DISTR = 0

config = configparser.ConfigParser()
config.sections()
config.read(
    os.path.dirname(os.path.abspath(__file__)).split('sha_learning')[0] + 'sha_learning/resources/config/config.ini')
config.sections()
CASE_STUDY = config['SUL CONFIGURATION']['CASE_STUDY']

try:
    CS_VERSION = int(config['SUL CONFIGURATION']['CS_VERSION'].replace('\n', ''))
except ValueError:
    CS_VERSION = None


def model(interval: List[Timestamp], T_0: float):
    interval = [ts.to_secs() for ts in interval]
    #return [T_0 + (t - interval[0]) for t in interval]
    return [1.0] * len(interval)
    #return [1 for t in interval]

#def model(interval: List[Timestamp], T_0: float):
#    interval = [ts.to_secs() for ts in interval]
#    return [T_0 * math.exp(-1 / OFF_DISTR[0] * (t - interval[0])) for t in interval]

fc = FlowCondition(0, model)

models: List[FlowCondition] = [fc]

#events = []

#if CS_VERSION in [1]:
a_event = Event('', 'a', 'a')
b_event = Event('', 'b', 'b')
c_event = Event('', 'c', 'c')
start_event = Event('', 'start', 'start')
events = [start_event, a_event, b_event, c_event]
#events = [start_event, a_event, b_event]

#if CS_VERSION in [1]:
#    on_event = Event('', 'on', 'h_0')
#    off_event = Event('', 'off', 'c_0')
#    events = [on_event, off_event]
#if CS_VERSION in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
#    on_event = Event('!open', 'on', 'h_0')
#    off_event = Event('!open', 'off', 'c_0')
#    on_event2 = Event('open', 'on', 'h_1')
#    off_event2 = Event('open', 'off', 'c_1')
#    events = [on_event, off_event, on_event2, off_event2]
#if CS_VERSION in [3, 8, 9, 10]:
#    on_event3 = Event('open2', 'on', 'h_2')
#    off_event3 = Event('open2', 'off', 'c_2')
#    events += [on_event3, off_event3]
#if CS_VERSION in [9, 10]:
#    on_fc2 = FlowCondition(2, off_model_2)
#    models += [on_fc2]
#if CS_VERSION in [8]:
#    on_fc2 = FlowCondition(2, on_model_2)
#    off_fc2 = FlowCondition(3, off_model_2)
#    models += [on_fc2, off_fc2]

model_to_distr = {}
for m in models:
    model_to_distr[m.f_id] = []

temperature = RealValuedVar(models, [], model_to_distr, label='s.slope')
args = {'name': 'WeakEqFail', 'driver': DRIVER_SIG, 'default_m': DEFAULT_M, 'default_d': DEFAULT_DISTR}
WeakEqFail_cs = SystemUnderLearning([temperature], events, parse_data, label_event, get_wef_param, is_chg_pt,
                                    args=args)

test = False
if test:
    # test event configuration
    print(WeakEqFail_cs.symbols)

    # test trace processing
    wef_traces = [file for file in os.listdir('./resources/traces/uppaal') if file.startswith('WEAK_EQ_FAIL')]
    for trace in wef_traces:
        WeakEqFail_cs.process_data('./resources/traces/uppaal/' + trace)

    test_trace = Trace([a_event])
    plot_traces = [(i, t) for i, t in enumerate(WeakEqFail_cs.traces) if t.startswith(test_trace)]

    # test visualization
    for tup in plot_traces[:1]:
        print(tup[1])
        WeakEqFail_cs.plot_trace(index=tup[0], title='test', xlabel='time [s]', ylabel='degrees C°')

    # test segment identification
    segments = WeakEqFail_cs.get_segments(test_trace)
    print(len(segments))

    # test model identification query
    teacher = Teacher(WeakEqFail_cs)
    id_flow = teacher.mi_query(test_trace)
    print(id_flow)

    # test hypothesis testing query
    metrics = [get_wef_param(s, id_flow) for s in segments]
    print(metrics)
    print(WeakEqFail_cs.vars[0].model2distr[0])
    #print(teacher.ht_query(Trace([on_event]), on_fc, save=True))
    print(WeakEqFail_cs.vars[0].model2distr[0])
    print(WeakEqFail_cs.vars[0].model2distr[1])
    #print(teacher.ht_query(Trace([on_event, off_event]), off_fc, save=True))
    print(WeakEqFail_cs.vars[0].model2distr[1])
    #WeakEqFail_cs.plot_distributions()