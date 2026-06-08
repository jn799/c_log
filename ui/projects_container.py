from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal


class ProjectsContainer(QWidget):
    reordered = pyqtSignal(list)   # ordered list of pinned project paths after drag

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

        self._n_pinned = 0   # number of pinned cards at the top of the layout

    # ── Public API ────────────────────────────────────────────────────────────

    def rebuild(self, pinned_cards: list, unpinned_cards: list):
        """Re-layout all cards: pinned first (in given order), then unpinned."""
        from ui.project_card import ProjectCard
        # Collect and remove all existing card widgets
        existing = [
            self._lay.itemAt(i).widget()
            for i in range(self._lay.count())
            if isinstance(self._lay.itemAt(i).widget(), ProjectCard)
        ]
        for w in existing:
            self._lay.removeWidget(w)
        # Re-insert in new order; stretch stays at the end
        self._n_pinned = len(pinned_cards)
        for i, card in enumerate(pinned_cards + unpinned_cards):
            self._lay.insertWidget(i, card)

    def remove_card(self, card):
        from ui.project_card import ProjectCard
        if isinstance(card, ProjectCard) and card._pinned:
            self._n_pinned = max(0, self._n_pinned - 1)
        self._lay.removeWidget(card)

    def cards(self) -> list:
        from ui.project_card import ProjectCard
        return [
            self._lay.itemAt(i).widget()
            for i in range(self._lay.count())
            if isinstance(self._lay.itemAt(i).widget(), ProjectCard)
        ]

    # ── Drag-drop (pinned zone only) ──────────────────────────────────────────

    def _pinned_insert_idx_at_y(self, y: int) -> int:
        """Drop index within the pinned section (0..n_pinned)."""
        pinned = self.cards()[:self._n_pinned]
        for i, card in enumerate(pinned):
            if y < card.y() + card.height() // 2:
                return i
        return self._n_pinned

    def _place_indicator(self, insert_idx: int):
        pinned = self.cards()[:self._n_pinned]
        if not pinned:
            self._indicator.hide()
            return
        if insert_idx == 0:
            y = pinned[0].y() - 2
        elif insert_idx >= len(pinned):
            last = pinned[-1]
            y = last.y() + last.height()
        else:
            above = pinned[insert_idx - 1]
            below = pinned[insert_idx]
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
            self._place_indicator(self._pinned_insert_idx_at_y(y))
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._indicator.hide()

    def dropEvent(self, event):
        self._indicator.hide()
        if not event.mimeData().hasFormat("application/x-clog-project"):
            return
        path = bytes(event.mimeData().data("application/x-clog-project")).decode()
        y = event.position().toPoint().y()
        target = self._pinned_insert_idx_at_y(y)

        all_cards = self.cards()
        drag_card = next((c for c in all_cards if c.project_path == path), None)
        if drag_card is None or not drag_card._pinned:
            return

        pinned_cards = all_cards[:self._n_pinned]
        unpinned_cards = all_cards[self._n_pinned:]

        src = pinned_cards.index(drag_card)
        if src == target or src + 1 == target:
            event.acceptProposedAction()
            return

        pinned_cards.pop(src)
        if target > src:
            target -= 1
        pinned_cards.insert(target, drag_card)

        for card in pinned_cards + unpinned_cards:
            self._lay.removeWidget(card)
        for i, card in enumerate(pinned_cards + unpinned_cards):
            self._lay.insertWidget(i, card)

        event.acceptProposedAction()
        self.reordered.emit([c.project_path for c in pinned_cards])
