#Interactive checkers game
#Software Carpentry Fall 2025 Final Project
#Created by Stacia Subick

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import numpy as np

class SquareButton(QPushButton):
    '''
     """
    A QPushButton subclass representing a single square on the checkers board.

    Each SquareButton knows its board coordinates (row, col) and supports
    drag-and-drop behavior so that checkers pieces can be moved by dragging.
    The actual game-logic for validating moves is handled by the parent
    Checkers window; this class only forwards UI events to it.
    '''
    def __init__(self, row, col, parent=None):
        """
               Initialize a SquareButton at a specific board position.

               Parameters
               ---------
                   row (int): Row index of the square.
                   col (int): Column index of the square.
                   parent (QWidget, optional): Parent widget.
               """
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        """
              Handle mouse press events to start dragging a checker piece.

              If the user left-clicks this square, the method notifies the parent
              window (Checkers class) to attempt starting a drag operation from this
              square.

              Parameters
              ---------
                  event (QMouseEvent): The mouse event object.
              """
        if event.button() == Qt.LeftButton:
            self.window().start_drag(self.row, self.col, self)
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        """
                Handle drag entering this square.

                The drag is accepted if the incoming mime data contains text, which
                is how the Checkers class encodes the source coordinates of the piece
                being dragged.

                Parameters
                ---------
                    event (QDragEnterEvent): The drag event object.
                """
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """
                Handle dropping a dragged checker piece onto this square.

                The method reads the old coordinates stored in the drag mime data and
                calls the parent window's `finish_drag` method to attempt completing
                the move.

                Parameters
                ---------
                    event (QDropEvent): The drop event containing drag data.
                """
        data = event.mimeData().text()
        old_row, old_col = map(int, data.split(","))
        self.window().finish_drag(old_row, old_col, self.row, self.col)
        event.acceptProposedAction()



class Checkers(QMainWindow):
    '''
    main class defining the GUI window and the functions that define how pieces move
    '''
    def __init__(self):
        '''Initializes the attributes of each 'checkers' instance'''
        super(Checkers, self).__init__()
        self.setWindowTitle("Checkers")
        self.setGeometry(300, 300, 600, 600)

        # central widget + layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setSpacing(0)
        self.main_layout.addLayout(self.grid_layout)

        # --- Restart button ---
        self.restart_button = QPushButton("Restart Game")
        self.restart_button.clicked.connect(self.restart_game)
        self.main_layout.addWidget(self.restart_button)

        # initialize buttons and drag state
        self.buttons = []
        self.dragging_piece = None
        self.drag_start = None

        #add logic to force multijump sequence if available
        self.must_continue_jump = False #switches to true when player must continue jump sequence
        self.active_piece = None #coord of piece that has to continue jumping

        # create game board array
        self.board = self.setup_board()

        # call function to set up board visual
        self.setup_gui()

        #start turns with red pieces
        self.current_player = 'r'

        self.game_over = False


    def setup_board(self):
        """Creates an 8×8 array holding 'r' or 'b' that creates the colors of the checkers.

        Returns
        -------
        board
            list containing color assignments for checkers pieces: 'r','b' or None if no piece"""
        #initialize empty list of board spaces
        board = [[None for _ in range(8)] for _ in range(8)]

        #assign colors to pieces
        for row in range(8):
            for col in range(8):
                is_dark = (row + col) % 2 == 1
                if row in (0, 1, 2) and is_dark:
                    board[row][col] = "b"
                if row in (5, 6, 7) and is_dark:
                    board[row][col] = "r"

        return board

    def setup_gui(self):
        """Creates buttons that act as checkerboard squares.
        Returns
        -------
        None
        """
        for row in range(8):
            row_buttons = []
            for col in range(8):
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
        """Place icons on the board according to the array defined in by self.board.
        updates visual based on moves.

        Returns
        -------
        None
        """
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                button = self.buttons[row][col]

                if piece is None:
                    button.setIcon(QIcon())
                else:
                    icon = self.create_piece_icon(piece)
                    button.setIcon(QIcon(icon))
                    button.setIconSize(QSize(60, 60))

    def create_piece_icon(self, piece, size=60):
        ''' create circular icon to represent checkers piece
        and add yellow icon to represent king pieces

        Parameters
        ----------
            piece: string containing piece color
            size: int, size of checkers piece
        Returns
        -------
        pixmap
        '''
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        color = piece.lower()
        brush_color = QColor(200, 30, 30) if color == "r" else QColor(30, 30, 30)
        painter.setBrush(brush_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)

        #draw a crown if piece is a king
        if piece.isupper():
            yellow=QColor(255, 215, 0)
            painter.setPen(QPen(yellow))
            painter.setBrush(QBrush(yellow))

            crown = QPolygon([
                QPoint(int(size * 0.25), int(size * 0.55)),  # left base
                QPoint(int(size * 0.25), int(size * 0.20)),  # left spike

                QPoint(int(size * 0.50), int(size * 0.20)),  # middle spike (tallest)

                QPoint(int(size * 0.75), int(size * 0.20)),  # right spike
                QPoint(int(size * 0.75), int(size * 0.55)),  # right base
            ])
            painter.drawPolygon(crown)
        painter.end()

        return pixmap

    # def on_square_clicked(self, row, col):
    #     '''function prints the coordinates of square that was clicked for debugging'''
    #     print(f"Clicked square ({row}, {col})")

    def start_drag(self, row, col, button):
        '''
        define button behavior when piece is clicked and dragged.
        Parameters
            ----------
            row: int
            col: int
            button: SquareButton
        Returns
        -------
        None
        '''
        self.reset_highlights()

        # If a multi-jump is required, only allow dragging the active piece
        if self.must_continue_jump and self.active_piece != (row, col):
            return

        piece = self.board[row][col]
        if piece is None:
            return

        # check if piece matches current player
        if piece.lower() != self.current_player:
            return

        # otherwise highlight all valid moves
        moves = self.find_valid_moves(row, col)

        # If we're in multi-jump state, only highlight capture moves
        if self.must_continue_jump:
            moves = [m for m in moves if abs(m[0] - row) == 2]

        # add highlights for valid moves
        self.create_highlights(moves)

        drag = QDrag(button)
        mime = QMimeData()

        # encode starting location
        mime.setText(f"{row},{col}")
        drag.setMimeData(mime)

        # show the checker piece while dragging
        icon = button.icon()
        pixmap = icon.pixmap(60, 60)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(30, 30))

        drag.exec_(Qt.MoveAction)

    def finish_drag(self, old_row, old_col, new_row, new_col):
        '''define button behavior when piece is released
        Parameters
        ----------
            old_row: int
                original row index of piece
            old_col: int
                original column index of piece
            new_row: int
                new row index of piece
            new_col: int
                new column index of piece
        Returns
        -------
        None
        '''
        #clear highlights after move finishes
        self.reset_highlights()

        if not self.is_valid_move(old_row, old_col, new_row, new_col):
            print("Invalid move!")
            return

        piece = self.board[old_row][old_col]

        captured = False
        # Check if captured:
        if abs(new_row - old_row) == 2:
            mid_row = (old_row + new_row) // 2
            mid_col = (old_col + new_col) // 2
            self.board[mid_row][mid_col] = None  # remove captured piece
            captured = True

        # Move piece
        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        # if red reaches top row it becomes a king
        if piece == "r" and new_row == 0:
            self.board[new_row][new_col] = "R"

        # if black reaches bottom row it becomes a king
        if piece == "b" and new_row == 7:
            self.board[new_row][new_col] = "B"

        # If a capture occurred, check for further captures from the landing square
        if captured:
            followups = self.find_valid_moves(new_row, new_col)
            # Only keep capture-type followups (jumps of two rows)
            capture_followups = [m for m in followups if abs(m[0] - new_row) == 2]

            if capture_followups:
                # Multi-jump must continue with this piece
                self.must_continue_jump = True
                self.active_piece = (new_row, new_col)
                # highlight the capture followups only
                self.create_highlights(capture_followups)
                # update board visually (piece moved and captured removed)
                self.update_board()
                return  # do not end turn; user must continue jumping

        # No further captures → clear multi-jump state and finish turn
        self.must_continue_jump = False
        self.active_piece = None

        # Switch players
        self.current_player = 'b' if self.current_player == 'r' else 'r'
        # Check if the next player has lost
        self.check_if_winner()

        self.update_board()

    def find_valid_moves(self, row, col):
        """
            Compute all legal moves for the piece located at (row, col).

            Parameters
            ----------
            row : int
                The row index of the piece to evaluate (0–7).
            col : int
                The column index of the piece to evaluate (0–7).

            Returns
            -------
            list of (int, int)
                A list of coordinate tuples representing the legal destination
                squares the piece may move to. Each tuple is (new_row, new_col).
        """

        moves = []
        piece =self.board[row][col]
        if piece is None:
            return moves

        #assign movement direction
        if piece == 'r':
            directions = [(-1, -1), (-1, 1)]
        elif piece == 'b':
            directions = [(1, -1), (1, 1)]
        else: #kings can move up and down
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        #test single step moves
        for dr, dc in directions:
            #assign coords of potential moves
            nr = row +dr
            nc= col +dc
            #check if move is on the board and an empty spot
            if 0 <= nr < 8 and 0<= nc< 8:
                if self.board[nr][nc] is None:
                    moves.append((nr,nc))

        #test capturing moves
        for dr, dc in directions:
            nr = row +2*dr
            nc= col+2*dc
            #find middle square
            mr = row +dr
            mc= col +dc
            if (0 <= nr < 8 and 0 <= nc < 8) and (0 <= mr < 8 and 0 <= mc < 8):
                middle_checker = self.board[mr][mc]
                #check is middle piece exists and if its the same color as jumping piece
                if (middle_checker is not None and middle_checker.lower() != piece.lower()
                    and self.board[nr][nc] is None):
                    moves.append((nr,nc))

        return moves

    def create_highlights(self, moves, capture_only=False):
        """
        Parameters
        ----------
        moves: list of (r,c)
        If capture_only True OR a move is a capture (abs row diff == 2), color red, else yellow.

        Returns
        -------
        None
        """
        for (r, c) in moves:
            # detect if this move is a capture relative to current active piece
            is_capture = False
            if self.active_piece:
                ar, ac = self.active_piece
                if abs(r - ar) == 2:
                    is_capture = True

            color = "green" if is_capture else "yellow"
            self.buttons[r][c].setStyleSheet(f"background-color: {color};")


    def reset_highlights(self):
        '''
        resets highlighted squares to original colors

        Returns
        -------
        None
        '''
        for row in range(8):
            for col in range(8):
                button = self.buttons[row][col]
                if (row +col)%2 == 0:
                    button.setStyleSheet("background-color: tan;")
                else:
                    button.setStyleSheet("background-color: saddlebrown;")


    def is_valid_move(self, old_row, old_col, new_row, new_col):
        '''
        Checks if a move is valid

        Parameters
        ----------
        old_row : int
            original space row index
        old_col : int
            original space column index
        new_row : int
            new space row index
        new_col : int
            new space column index

        Returns
        -------
        True or False
            true if move is valid, false if not
        '''
        piece = self.board[old_row][old_col]
        if piece is None:
            return False

        # cannot move onto an occupied square
        if self.board[new_row][new_col] is not None:
            return False

        # decide allowed movement directions
        if piece == "r":  # red man
            allowed_rows = (-1,)
        elif piece == "b":  # black man
            allowed_rows = (1,)
        else:  # "R" or "B" = king
            allowed_rows = (-1, 1) #kings can move forward and backwards

        row_diff = new_row - old_row
        col_diff = new_col - old_col

        # single move forward
        if row_diff in allowed_rows and abs(col_diff) == 1:
            return True

        # two rows forward (capture move)
        if row_diff in tuple(d*2 for d in allowed_rows) and abs(col_diff) == 2:
            mid_row = (old_row + new_row) // 2
            mid_col = (old_col + new_col) // 2
            middle_piece = self.board[mid_row][mid_col]

            # Can capture only the opposite color
            if middle_piece is not None and middle_piece.lower() != piece.lower():
                return True

        return False

    def check_if_winner(self):
        '''function to check if either player has won (either run out of pieces or no legal moves)

        Returns
        -------
        True or False
        '''
        red_exists = False
        black_exists = False
        red_legal_moves = False
        black_legal_moves = False

        for r in range (8):
            for c in range(8):
                piece = self.board[r][c]

                #continue on if no piece in the square
                if piece is None:
                    continue
                #test if piece exists
                if piece.lower() == 'r':
                    red_exists = True
                if piece.lower() == 'b':
                    black_exists = True

                #test if there are legal moves
                moves = self.find_valid_moves(r, c)
                if moves:
                    if piece.lower() == 'r':
                        red_legal_moves = True
                    if piece.lower() =='b':
                        black_legal_moves = True

        #check for winning conditions
        if not red_exists or not red_legal_moves:
            self.show_winning_message("Black")
            return True
        if not black_exists or not black_legal_moves:
            self.show_winning_message("Red")
            return True

        return False

    def show_winning_message(self, winner):
        '''
        shows message box pop-up with which color won

        Returns
        -------
        None
        '''
        msg = QMessageBox()
        msg.setWindowTitle("Game Over")
        msg.setText(f"{winner} wins!")
        msg.exec_()

        self.game_over = True

    def restart_game(self):
        """Reset pieces, turn order, states, and UI.
        Returns
        -------
        None
        """
        # 1. Reset the board array
        self.board = self.setup_board()

        # 2. Reset game state
        self.current_player = 'r'
        self.must_continue_jump = False
        self.active_piece = None
        self.game_over = False

        # 3. Reset visual highlights
        self.reset_highlights()

        # 4. Update all piece icons
        self.update_board()

        # (Optional) Print for debugging
        print("Game restarted.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    checkers = Checkers()
    checkers.show()
    sys.exit(app.exec_())
