import numpy as np
import pandas as pd

from models.charts.extended_chart import ChartHit, ExtendedChart
from models.responses.chart_response import ChartNote, ChartResponse

def extend_ffr_chart(ffr_chart: ChartResponse):
    return ExtendedChart(ffr_chart.info, ffr_chart.chart, compute_hits(ffr_chart))

def ffr_note_dir(note: ChartNote):
    return note.dir

def ffr_note_ms(note: ChartNote):
    return note.ms

def ffr_note_hand(note: ChartNote):
    return 0 if ffr_note_dir(note) <= 1 else 1

def ffr_note_finger(note: ChartNote):
    return ffr_note_dir(note) % 2

def compute_hits(ffr_chart: ChartResponse):
    np_notes = np.array([[ffr_note_ms(note), ffr_note_hand(note), ffr_note_dir(note), ffr_note_finger(note) + 1] for note in ffr_chart.chart])

    pd_notes = pd.DataFrame(np_notes)

    notes_by_hand = pd_notes.groupby(1, as_index=False)
    notes_left_hand = pd.DataFrame(np_notes[notes_by_hand.groups[0].values])
    notes_right_hand = pd.DataFrame(np_notes[notes_by_hand.groups[1].values])

    left_hits = notes_left_hand.groupby(0).sum().reset_index().values[:, [0, 3]]
    right_hits = notes_right_hand.groupby(0).sum().reset_index().values[:, [0, 3]]

    left_hits_with_gaps = np.c_[np.zeros(left_hits.shape[0], dtype=int).T, left_hits, np.diff(left_hits, axis=0, prepend=[[0, 0]])[:, 0]]
    right_hits_with_gaps = np.c_[np.ones(right_hits.shape[0], dtype=int).T, right_hits, np.diff(right_hits, axis=0, prepend=[[0, 0]])[:, 0]]

    all_hits = np.concatenate((left_hits_with_gaps, right_hits_with_gaps), axis=0)
    all_hits_sorted_time = all_hits[all_hits[:, 1].argsort()]
    
    return [ChartHit(int(hand), int(finger), int(ms), int(gap)) for (hand, ms, finger, gap) in all_hits_sorted_time]


    