from PySide6.QtCore import QObject, Signal


class ArrowSizeController(QObject):
    _arrow_size_changed: Signal

    def __init__(self, initial_size: int = 12) -> None:
        super().__init__()

        self._arrow_size: int = initial_size
        self._arrow_size_changed = Signal(int)

    @property
    def arrow_size(self) -> int:
        """
        Get or set the arrow size.
        
        When setting a new arrow size, the `arrow_size_changed` signal is emitted.
        """
        return self._arrow_size

    @arrow_size.setter
    def arrow_size(self, size: int) -> None:
        if self._arrow_size != size:
            self._arrow_size = size
            self._arrow_size_changed.emit(self._arrow_size)
            