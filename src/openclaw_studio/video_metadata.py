from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoMetadata:
    frame_count: int
    duration_seconds: float
    fps: float


@dataclass(frozen=True)
class _Atom:
    type_name: str
    start: int
    size: int
    header_size: int

    @property
    def content_start(self) -> int:
        return self.start + self.header_size

    @property
    def end(self) -> int:
        return self.start + self.size


_CONTAINER_TYPES = {
    "moov",
    "trak",
    "mdia",
    "minf",
    "stbl",
}


def read_mp4_video_metadata(path: str | Path) -> VideoMetadata:
    target = Path(path).expanduser().resolve()
    data = target.read_bytes()

    moov = _find_first_path(data, ("moov",))
    if moov is None:
        raise ValueError(f"No encontre la caja moov en {target}.")

    for trak in _iter_child_atoms(data, moov):
        if trak.type_name != "trak":
            continue

        hdlr = _find_first_path(data, ("mdia", "hdlr"), parent=trak)
        if hdlr is None or _read_handler_type(data, hdlr) != "vide":
            continue

        mdhd = _find_first_path(data, ("mdia", "mdhd"), parent=trak)
        stsz = _find_first_path(data, ("mdia", "minf", "stbl", "stsz"), parent=trak)
        stts = _find_first_path(data, ("mdia", "minf", "stbl", "stts"), parent=trak)
        if mdhd is None:
            continue

        timescale, duration_units = _read_mdhd_timing(data, mdhd)
        if timescale <= 0 or duration_units <= 0:
            continue

        frame_count = 0
        if stsz is not None:
            frame_count = _read_stsz_sample_count(data, stsz)
        if frame_count <= 0 and stts is not None:
            frame_count = _read_stts_sample_count(data, stts)
        if frame_count <= 0:
            continue

        duration_seconds = duration_units / float(timescale)
        fps = frame_count / duration_seconds if duration_seconds > 0 else 0.0
        return VideoMetadata(
            frame_count=frame_count,
            duration_seconds=duration_seconds,
            fps=fps,
        )

    raise ValueError(f"No encontre una pista de video legible en {target}.")


def _find_first_path(
    data: bytes,
    path: tuple[str, ...],
    *,
    parent: _Atom | None = None,
) -> _Atom | None:
    atoms = [_Atom(type_name="root", start=0, size=len(data), header_size=0)]
    if parent is not None:
        atoms = [parent]

    current: _Atom | None = atoms[0]
    for type_name in path:
        if current is None:
            return None
        next_atom = None
        for atom in _iter_child_atoms(data, current):
            if atom.type_name == type_name:
                next_atom = atom
                break
        current = next_atom
    return current


def _iter_child_atoms(data: bytes, parent: _Atom):
    offset = parent.content_start
    limit = parent.end
    while offset + 8 <= limit:
        size = int.from_bytes(data[offset : offset + 4], "big")
        type_name = data[offset + 4 : offset + 8].decode("latin-1")
        header_size = 8
        if size == 1:
            if offset + 16 > limit:
                break
            size = int.from_bytes(data[offset + 8 : offset + 16], "big")
            header_size = 16
        elif size == 0:
            size = limit - offset
        if size < header_size:
            break
        atom = _Atom(
            type_name=type_name,
            start=offset,
            size=size,
            header_size=header_size,
        )
        yield atom
        if size <= 0:
            break
        offset += size


def _read_handler_type(data: bytes, atom: _Atom) -> str:
    content = atom.content_start
    return data[content + 8 : content + 12].decode("latin-1")


def _read_mdhd_timing(data: bytes, atom: _Atom) -> tuple[int, int]:
    content = atom.content_start
    version = data[content]
    if version == 1:
        timescale = int.from_bytes(data[content + 20 : content + 24], "big")
        duration = int.from_bytes(data[content + 24 : content + 32], "big")
        return timescale, duration
    timescale = int.from_bytes(data[content + 12 : content + 16], "big")
    duration = int.from_bytes(data[content + 16 : content + 20], "big")
    return timescale, duration


def _read_stsz_sample_count(data: bytes, atom: _Atom) -> int:
    content = atom.content_start
    return int.from_bytes(data[content + 8 : content + 12], "big")


def _read_stts_sample_count(data: bytes, atom: _Atom) -> int:
    content = atom.content_start
    entry_count = int.from_bytes(data[content + 4 : content + 8], "big")
    offset = content + 8
    total_samples = 0
    for _ in range(entry_count):
        sample_count = int.from_bytes(data[offset : offset + 4], "big")
        total_samples += sample_count
        offset += 8
    return total_samples


__all__ = ["VideoMetadata", "read_mp4_video_metadata"]
