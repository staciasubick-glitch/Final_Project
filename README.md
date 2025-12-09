🏁 Checkers (PyQt5 GUI)
 
A playable Checkers game implemented in Python using PyQt5, supporting:
-Drag-and-drop piece movement
-Move highlighting
-Forced captures
-Multi-jump sequences
-Turn-based play (Red vs. Black)
-King promotion
-Win detection
-Restart button
-Clean, color-coded board UI

🧩 Code Structure
1. SquareButton Class
  A subclass of QPushButton representing each square on the board.
  Responsibilities:
  -Stores its board coordinates (row, col)
  -Handles mouse press to begin dragging
  -Accepts drag–enter events for dropping pieces
  -Calls back into the main Checkers window to complete moves

2. Checkers Main Class
  Manages:
  -The game board state (self.board)
  -Player turns (self.current_player)
  -Forced multi-jump sequences (self.must_continue_jump, self.active_piece)
  -Piece movement logic
  -GUI updates and color resets
  -Win detection
  -Restarting the board

  Key methods include:
  -find_valid_moves(row, col)
      Returns a list of all legal moves for the piece at (row, col).
      Used for highlighting and multi-jump logic.
  -is_valid_move(old_row, old_col, new_row, new_col)
      Returns True/False for a single move attempt.
      Used to validate drag-and-drop actions.
  -start_drag(row, col, button)
      Begins dragging a piece and highlights legal moves.
  -finish_drag(old_row, old_col, new_row, new_col)
      Validates and performs the move, handles captures, promotion, and turn switching.
  -check_for_winner()
      Determines if the game is over and displays the winning popup.

🛠 Installation
-install python
-install PyQt5
-run code to play
