from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QApplication
from PyQt6.QtCore import Qt, pyqtSignal


class ProjectsContainer(QWidget):
    reordered = pyqtSignal(list)   # list of project paths in new order

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectsContainer")
        self.setAcceptDrops(True)

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 4, 0, 4)
        self._lay.setSpacing(1)
        self._lay.addStretch()

        self._indicator = QFrame(self)
        self._indicator.setObjectName("DropIndicator")
        self._indicator.setFixedHeight(2)
        self._indicator.hide()

    # ── Public API ────────────────────────────────────────────────────────────

    def add_card(self, card, idx: int = -1):
        if idx < 0:
            idx = self._lay.count() - 1   # insert before trailing stretch
        self._lay.insertWidget(idx, card)

    def remove_card(self, card):
        self._lay.removeWidget(card)

    def cards(self) -> list:
        from ui.project_card import ProjectCard
        return [
            self._lay.itemAt(i).widget()
            for i in range(self._lay.count())
            if isinstance(self._lay.itemAt(i).widget(), ProjectCard)
        ]

    # ── Drag-drop internals ───────────────────────────────────────────────────

    def _insert_idx_at_y(self, y: int) -> int:
        for i, card in enumerate(self.cards()):
            if y < card.y() + card.height() // 2:
                return i
        return len(self.cards())

    def _place_indicator(self, insert_idx: int):
        cards = self.cards()
        if not cards:
            self._indicator.hide()
            return
        if insert_idx == 0:
            y = cards[0].y() - 2
        elif insert_idx >= len(cards):
            last = cards[-1]
            y = last.y() + last.height()
        else:
            above = cards[insert_idx - 1]
            below = cards[insert_idx]
            y = (above.y() + above.height() + below.y()) // 2
        self._indicator.setGeometry(6, y, self.width() - 12, 2)
        self._indicator.show()
        self._indicator.raise_()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-clog-project"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-clog-project"):
            y = event.position().toPoint().y()
            self._place_indicator(self._insert_idx_at_y(y))
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._indicator.hide()

    def dropEvent(self, event):
        self._indicator.hide()
        if not event.mimeData().hasFormat("application/x-clog-project"):
            return
        path = bytes(event.mimeData().data("application/x-clog-project")).decode()
        y = event.position().toPoint().y()
        target = self._insert_idx_at_y(y)

        all_cards = self.cards()
        drag_card = next((c for c in all_cards if c.project_path == path), None)
        if drag_card is None:
            return

        src = all_cards.index(drag_card)
        if src == target or src + 1 == target:
            event.acceptProposedAction()
            return

        all_cards.pop(src)
        if target > src:
            target -= 1
        all_cards.insert(target, drag_card)

        for card in all_cards:
            self._lay.removeWidget(card)
        for i, card in enumerate(all_cards):
            self._lay.insertWidget(i, card)

        event.acceptProposedAction()
        self.reordered.emit([c.project_path for c in all_cards])
