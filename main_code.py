#Interactive checkers game
#Software Carpentry Fall 2025 Final Project
#Created by Stacia Subick

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np

class SquareButton(QPushButton):
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setAcceptDrops(True)

    def mouseMoveEvent(self, e):
        if e.button() == Qt.LeftButton:
            drag =QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)

    def mousePressEvent(self, event):
        # call the top-level window's start_drag
        # window() returns the QMainWindow (your Checkers instance)
        self.window().start_drag(self.row, self.col)
        # call the base implementation so QPushButton internal state is correct
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # call the top-level window's end_drag
        self.window().end_drag(self.row, self.col)
        super().mouseReleaseEvent(event)


class Checkers(QMainWindow):
    def __init__(self):
        super(Checkers, self).__init__()
        self.setWindowTitle("Checkers")
        self.setGeometry(300, 300, 600, 600)

        # central widget + layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setSpacing(0)

        # initialize buttons and drag state
        self.buttons = []
        self.dragging_piece = None
        self.drag_start = None

        # create game board array
        self.board = self.setup_board()

        # make visual board
        self.setup_gui()

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            if pos.x() < w.x() + w.size().width() // 2:
                # We didn't drag past this widget.
                # insert to the left of it.
                self.blayout.insertWidget(n - 1, widget)
                break

        e.accept()

    def setup_board(self):
        """Creates an 8×8 array holding 'r', 'b', or None."""
        board = [[None for _ in range(8)] for _ in range(8)]

        for row in range(8):
            for col in range(8):
                is_dark = (row + col) % 2 == 1
                if row in (0, 1, 2) and is_dark:
                    board[row][col] = "b"
                if row in (5, 6, 7) and is_dark:
                    board[row][col] = "r"

        return board

    def setup_gui(self):
        """Creates 8×8 buttons that act as checkerboard squares."""
        for row in range(8):
            row_buttons = []
            for col in range(8):
                # IMPORTANT: parent should be the central widget (not the QMainWindow)
                button = SquareButton(row, col, parent=self.central_widget)
                button.setFixedSize(70, 70)

                # set square color
                if (row + col) % 2 == 0:
                    button.setStyleSheet("background-color: tan;")
                else:
                    button.setStyleSheet("background-color: saddlebrown;")

                # DO NOT connect clicked() while debugging mouse handlers
                # button.clicked.connect(lambda checked, r=row, c=col: self.on_square_clicked(r, c))

                self.grid_layout.addWidget(button, row, col)
                row_buttons.append(button)

            self.buttons.append(row_buttons)

        self.update_board()

    def update_board(self):
        """Place icons on the board according to self.board."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                button = self.buttons[row][col]

                if piece is None:
                    button.setIcon(QIcon())
                else:
                    icon = self.create_piece_icon("red" if piece == "r" else "black")
                    button.setIcon(QIcon(icon))
                    button.setIconSize(QSize(60, 60))

    def create_piece_icon(self, color, size=60):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        brush_color = QColor(200, 30, 30) if color == "red" else QColor(30, 30, 30)
        painter.setBrush(brush_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()

        return pixmap

    def on_square_clicked(self, row, col):
        print(f"Clicked square ({row}, {col})")

    # DEBUG prints to confirm functions are called
    def start_drag(self, row, col):
        piece = self.board[row][col]
        print("start_drag called for", (row, col), "piece:", piece)
        if piece is None:
            return
        self.dragging_piece = piece
        self.drag_start = (row, col)

    def end_drag(self, row, col):
        print("end_drag called for", (row, col), "dragging:", self.dragging_piece)
        if self.dragging_piece is None:
            return

        start_row, start_col = self.drag_start

        # Move the piece (no validation here — you'll add rules later)
        self.board[start_row][start_col] = None
        self.board[row][col] = self.dragging_piece

        self.dragging_piece = None
        self.drag_start = None
        self.update_board()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    checkers = Checkers()
    checkers.show()
    sys.exit(app.exec_())
