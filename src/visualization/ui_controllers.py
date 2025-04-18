from typing import Literal

from PySide6.QtCore import QObject, Signal, SignalInstance

type ScrollDir = Literal["up", "down"]


class NoteSizeController(QObject):
    _note_size_changed = Signal(int)

    def __init__(self, initial_size: int = 10) -> None:
        super().__init__()

        self._note_size: int = initial_size

    @property
    def signal(self) -> SignalInstance:
        return self._note_size_changed

    @property
    def note_size(self) -> int:
        """
        Get or set the note size.

        When setting a new note size, the `note_size_changed` signal is emitted.
        """
        return self._note_size

    @note_size.setter
    def note_size(self, size: int) -> None:
        if self._note_size != size and size > 0 and size < 100:
            self._note_size = size
            self._note_size_changed.emit(self._note_size)


class ScrollDirController(QObject):
    _scroll_dir_changed = Signal(str)

    def __init__(self, initial_scroll_dir: ScrollDir = "up") -> None:
        super().__init__()

        self._scroll_dir: ScrollDir = initial_scroll_dir

    def toggle_dir(self):
        if self._scroll_dir == "up":
            self.scroll_dir = "down"
        elif self._scroll_dir == "down":
            self.scroll_dir = "up"

    @property
    def signal(self) -> SignalInstance:
        return self._scroll_dir_changed

    @property
    def scroll_dir(self) -> ScrollDir:
        """
        Get or set the scroll direction.

        When setting a new scroll direction, the `scroll_dir_changed` signal is emitted.
        """
        return self._scroll_dir

    @scroll_dir.setter
    def scroll_dir(self, dir: ScrollDir) -> None:
        if self._scroll_dir != dir:
            self._scroll_dir = dir
            self._scroll_dir_changed.emit(self._scroll_dir)
