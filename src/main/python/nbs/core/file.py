"""
Deals with type conversions between the internal format and
the actual data stored in the NBS file (parsed by `pynbs`).
"""

import os
from typing import Sequence, Union

import pynbs

from nbs.core.data import Instrument, Layer, Note, Song, SongHeader

PathLike = Union[str, bytes, os.PathLike]

CURRENT_NBS_VERSION = 5


def load_song(path: PathLike) -> Song:
    return convert_file_to_song(pynbs.read(path))


def save_song(song: Song, path: PathLike, version: int = CURRENT_NBS_VERSION):
    """Save a song to a file."""
    convert_song_to_file(song).save(path, version=version)


def convert_file_to_song(file: pynbs.File) -> Song:
    header = _parse_header(file.header)
    notes = _parse_notes(file.notes)
    layers = _parse_layers(file.layers)
    instruments = _parse_instruments(file.instruments)
    return Song(header, notes, layers, instruments)


def convert_song_to_file(song: Song) -> pynbs.File:
    header = _save_header(song.header)
    notes = _save_notes(song.notes)
    layers = _save_layers(song.layers)
    instruments = _save_instruments(song.instruments)
    return pynbs.File(header, notes, layers, instruments)


def _parse_header(header: pynbs.Header) -> SongHeader:
    """Parse header from `pynbs.Header` to `nbs.SongHeader`."""

    return SongHeader(
        version=header.version,
        default_instruments=header.default_instruments,
        title=header.song_name,
        author=header.song_author,
        original_author=header.original_author,
        description=header.description,
        tempo=header.tempo,
        time_signature=header.time_signature,
        minutes_spent=header.minutes_spent,
        left_clicks=header.left_clicks,
        right_clicks=header.right_clicks,
        blocks_added=header.blocks_added,
        blocks_removed=header.blocks_removed,
        loop=header.loop,
        max_loop_count=header.max_loop_count,
        loop_start_tick=header.loop_start,
    )


def _parse_notes(notes: Sequence[pynbs.Note]) -> list[Note]:
    """Parse notes from `pynbs.Note` to `nbs.Note`."""

    return [
        Note(
            tick=note.tick,
            layer=note.layer,
            instrument=note.instrument,
            key=note.key,
            velocity=note.velocity,
        )
        for note in notes
    ]


def _parse_layers(layers: Sequence[pynbs.Layer]) -> list[Layer]:
    """Parse layers from `pynbs.Layer` to `nbs.Layer`."""

    return [
        Layer(
            name=layer.name,
            lock=layer.lock == 1,
            solo=layer.lock == 2,  # Not specified in the NBS format
            volume=layer.volume,
            panning=layer.panning,
        )
        for layer in layers
    ]


def _parse_instruments(instruments: Sequence[pynbs.Instrument]) -> list[Instrument]:
    """Parse instruments from `pynbs.Instrument` to `nbs.Instrument`."""

    return [
        Instrument(
            name=ins.name,
            sound_path=ins.file,
            pitch=ins.pitch,
            press=ins.press_key,
        )
        for ins in instruments
    ]


def _save_header(header: SongHeader) -> pynbs.Header:
    """Parse header from `nbs.SongHeader` to `pynbs.Header`."""

    return pynbs.Header(
        version=header.version,
        default_instruments=header.default_instruments,
        song_name=header.title,
        song_author=header.author,
        original_author=header.original_author,
        description=header.description,
        tempo=header.tempo,
        time_signature=header.time_signature,
        minutes_spent=header.minutes_spent,
        left_clicks=header.left_clicks,
        right_clicks=header.right_clicks,
        blocks_added=header.blocks_added,
        blocks_removed=header.blocks_removed,
        loop=header.loop,
        max_loop_count=header.max_loop_count,
        loop_start=header.loop_start_tick,
    )


def _save_notes(notes: Sequence[Note]) -> list[pynbs.Note]:
    """Convert notes from `nbs.Note` to `pynbs.Note`."""

    return [
        pynbs.Note(
            tick=note.tick,
            layer=note.layer,
            instrument=note.instrument,
            key=note.key,
            velocity=note.velocity,
        )
        for note in notes
    ]


def _save_layers(layers: Sequence[Layer]) -> list[pynbs.Layer]:
    """Convert layers from `nbs.Layer` to `pynbs.Layer`."""

    return [
        pynbs.Layer(
            id=i,
            name=layer.name,
            lock=1 if layer.lock else 0,
            volume=layer.volume,
            panning=layer.panning,
        )
        for i, layer in enumerate(layers)
    ]


def _save_instruments(instruments: Sequence[Instrument]) -> list[pynbs.Instrument]:
    """Convert instruments from `nbs.Instrument` to `pynbs.Instrument`."""

    return [
        pynbs.Instrument(
            id=i,
            name=ins.name,
            file=ins.sound_path,
            pitch=ins.pitch,
            press_key=ins.press,
        )
        for i, ins in enumerate(instruments)
    ]
