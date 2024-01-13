import pickle
from typing import List

import pytest
from PyQt5 import QtCore

from nbs.controller.clipboard import MIMETYPE, mimeDataToSelection, selectionToMimeData
from nbs.core.data import Note


@pytest.fixture
def selection():
    return [
        Note(
            tick=0,
            layer=0,
            instrument=0,
            key=39,
            velocity=100,
            panning=0,
        ),
        Note(
            tick=2,
            layer=2,
            instrument=5,
            key=45,
            velocity=75,
            panning=-100,
        ),
        Note(
            tick=4,
            layer=4,
            instrument=10,
            key=51,
            velocity=75,
            panning=100,
        ),
    ]


def test_selection_to_mimedata(selection: List[Note]) -> None:
    mimeData = selectionToMimeData(selection)
    assert mimeData.hasFormat(MIMETYPE)
    assert mimeData.data(MIMETYPE) == pickle.dumps(selection)


def test_mimedata_to_selection(selection: List[Note]) -> None:
    mimeData = selectionToMimeData(selection)
    assert mimeDataToSelection(mimeData) == selection


def test_mimedata_to_selection_invalid() -> None:
    mimeData = QtCore.QMimeData()
    mimeData.setData(MIMETYPE, b"")
    with pytest.raises(EOFError):
        mimeDataToSelection(mimeData)


def test_mimedata_to_selection_invalid_format() -> None:
    mimeData = QtCore.QMimeData()
    mimeData.setData("text/plain", b"")
    with pytest.raises(ValueError):
        mimeDataToSelection(mimeData)
