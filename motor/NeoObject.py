from os import listdir
import pandas as pd
import numpy as np
from quantities import s, ms
from neo.core import Block, Segment, ChannelIndex, Unit, SpikeTrain, AnalogSignal, Event
from experimentData import ExperimentData

class NeoObject():
    """docstring for NeoObject."""
    def __init__(self):
        self.experimentID = ['m4404ee', 'c6404ee']

    def createDataBlock(self, experimentID):

        eData = ExperimentData()
        # prepare SpikesDataFrame
        SpikesDataFrame = eData.createSpikes_DF(experimentID)
        # prepate unitNames
        unitNames = eData.getUnitNames_L(experimentID)
        # prepare trTarget
        trTarget = eData.getTrTarget_A(experimentID)
        # prepare Tbhv
        Tbhv = eData.getTbhv_A(experimentID)
        TbhvLabels = np.array(['start of trials','in Center','cue onset','go signals','move onset','in peripheral target'])
        # prepare ANdat
        ANdat_A = eData.getANdat_A(experimentID)
        # prepare analogAx
        analogAx = eData.getAnalogAx_A(experimentID)

        # create a Block of m4404ee
        blk = Block(name=experimentID)

        # create a segment for each trials
        trial_num = len(SpikesDataFrame)
        for trial_index in range(trial_num):
            seg = Segment(name='trial %i' % trial_index, index=trial_index)
            seg.annotate(trTarget=trTarget[trial_index])
            blk.segments.append(seg)

        # create a channel index
        chx = ChannelIndex(index=None, name='tetrode')
        blk.channel_indexes.append(chx)

        # create units
        for unitName in unitNames:
            unit = Unit(name=unitName)
            chx.units.append(unit)

        # starting time and stoppingtime of trial
        startTime = -1000
        stopTime = 3001

        # set spike trains into segment and unit
        for trial_index, seg in enumerate(blk.segments):
            for unitName in unitNames:
                spikeTrain_array = SpikesDataFrame[unitName].values[trial_index]
                spikeTimes_array = np.where(spikeTrain_array==1)[0] + startTime
                spikeTrain = SpikeTrain(spikeTimes_array*ms,t_start=startTime,t_stop=stopTime)
                seg.spiketrains.append(spikeTrain)

                unit = [unit for unit in chx.units if unit.name == unitName][0]
                unit.spiketrains.append(spikeTrain)

        # set Tbhv into segment
        for trial_index, seg in enumerate(blk.segments):
            evt = Event(Tbhv[trial_index]*ms, labels=TbhvLabels, name='Tbhv')
            seg.events.append(evt)

        return blk

    def binarize_spiketrain(spiketrain, sampling_rate=None, t_start=None, t_stop=None, type='int'):
        units = spiketrain.units
        if t_start is None:
            t_start = spiketrain.t_start
        if t_stop is None:
            t_stop = spiketrains.t_stop

        t_start = t_start.rescale(units).magnitude
        t_stop = t_stop.rescale(units).magnitude

        edges = np.arange(t_start, t_stop)
        res = np.histogram(spiketrain, edges)[0].astype(type)

        return res
