import streamlit as st
import chess
import chess.svg
import base64
import time

# Function to evaluate board position
def evaluate_board(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -float('inf')  # Black wins
        else:
            return float('inf')  # White wins
    if board.is_stalemate() or board.is_insufficient_material():
        return 0  # Draw

    # Material values (in centipawns)
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    score = 0

    # Material score
    for piece in piece_values:
        score += len(board.pieces(piece, chess.WHITE)) * piece_values[piece]
        score -= len(board.pieces(piece, chess.BLACK)) * piece_values[piece]

    return score
def alpha_beta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)
    
    # Move ordering: prioritize captures, checks, and promotions
    piece_values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}
    def move_priority(move):
        score = 0
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            attacking_piece = board.piece_at(move.from_square)
            if captured_piece and attacking_piece:
                captured_value = piece_values.get(captured_piece.piece_type, 0)
                attacker_value = piece_values.get(attacking_piece.piece_type, 0)
                score += captured_value * 10000 - attacker_value
        if board.gives_check(move):
            score += 50
        if move.promotion:
            score += 100000
        return -score  # Sort in descending order

    legal_moves.sort(key=move_priority)

    if maximizing:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval_score = alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval_score = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

# Function to get AI's best move with debugging output
def get_best_move(board, depth=5):
    if not board.legal_moves:
        return None
    best_move = None
    best_value = float('inf')  # Black is minimizing
    alpha = -float('inf')
    beta = float('inf')

    # Debug: Print all moves being considered and their scores
    st.write("**AI Move Evaluation (Black's turn):**")
    move_scores = []
    for move in board.legal_moves:
        board.push(move)
        move_value = alpha_beta(board, depth - 1, alpha, beta, False)
        board.pop()
        move_scores.append((move, move_value))
        st.write(f"Move: {move.uci()}, Score: {move_value}")

        if move_value < best_value:  # Black wants the lowest score
            best_value = move_value
            best_move = move

    # Debug: Print the chosen move
    st.write(f"**Chosen Move:** {best_move.uci()} with score {best_value}")
    return best_move

# Function to render chessboard with last move highlighted
def render_board(board, last_move=None):
    board_svg = chess.svg.board(board=board, size=400, lastmove=last_move)
    img_data = base64.b64encode(board_svg.encode("utf-8")).decode("utf-8")
    return f"<img src='data:image/svg+xml;base64,{img_data}' width='400'>"

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #2e2e2e;
        color: #f0f0f0;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background-color: #2e2e2e;
    }
    h1 {
        color: #d4a017;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>div>input {
        background-color: #3a3a3a;
        color: #f0f0f0;
        border: 1px solid #d4a017;
        border-radius: 5px;
        padding: 8px;
    }
    .status-box {
        background-color: #3a3a3a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #d4a017;
    }
    .move-history {
        background-color: #3a3a3a;
        padding: 15px;
        border-radius: 10px;
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #d4a017;
    }
    .move-history h3 {
        color: #d4a017;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title with chess icon
st.markdown("<h1>♟️ Chess: Human (White) vs AI (Black)</h1>", unsafe_allow_html=True)

# Initialize session state variables
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "last_move" not in st.session_state:
    st.session_state.last_move = None
if "waiting_for_ai" not in st.session_state:
    st.session_state.waiting_for_ai = False
if "move_history" not in st.session_state:
    st.session_state.move_history = []

board = st.session_state.board

# Layout with columns
col1, col2 = st.columns([2, 1])

# Column 1: Chessboard
with col1:
    st.markdown(render_board(board, last_move=st.session_state.last_move), unsafe_allow_html=True)

# Column 2: Game Information
with col2:
    # Status Box
    status_html = "<div class='status-box'>"
    if not board.is_game_over():
        status_html += f"<h3>{'White' if board.turn else 'Black'}'s Turn</h3>"
    else:
        status_html += f"<h3>Game Over!</h3><p>Result: {board.result()}</p>"
        st.session_state.game_over = True
    status_html += "</div>"
    st.markdown(status_html, unsafe_allow_html=True)

    # Move History
    if st.session_state.move_history:
        move_history_html = "<div class='move-history'><h3>Move History</h3><ul>"
        for i, move in enumerate(st.session_state.move_history, 1):
            move_history_html += f"<li>{i//2 + 1 if i % 2 != 0 else ''}. {move}</li>"
        move_history_html += "</ul></div>"
        st.markdown(move_history_html, unsafe_allow_html=True)

# Handle White's move (human player)
if board.turn == chess.WHITE and not st.session_state.game_over and not st.session_state.waiting_for_ai:
    user_move = st.text_input("Enter your move in UCI format (e.g., e2e4):", max_chars=5, key="move_input")
    
    if st.button("Make Move"):
        try:
            move = chess.Move.from_uci(user_move)
            if move in board.legal_moves:
                # Add move to history in algebraic notation
                san_move = board.san(move)
                st.session_state.move_history.append(san_move)
                board.push(move)
                st.session_state.last_move = move
                st.session_state.game_over = board.is_game_over()
                st.session_state.waiting_for_ai = True
                st.rerun()
            else:
                st.error("Illegal move! Try again.")
        except ValueError:
            st.error("Invalid move format! Use UCI notation (e.g., e2e4)")

# Handle Black's move (AI)
if board.turn == chess.BLACK and not st.session_state.game_over and st.session_state.waiting_for_ai:
    with st.spinner("AI thinking..."):
        time.sleep(1)  # Simulate thinking time
        ai_move = get_best_move(board)
        if ai_move:
            # Add move to history in algebraic notation
            san_move = board.san(ai_move)
            st.session_state.move_history.append(san_move)
            board.push(ai_move)
            st.session_state.last_move = ai_move
            st.session_state.game_over = board.is_game_over()
            st.session_state.waiting_for_ai = False
            st.rerun()
        else:
            st.error("AI failed to find a move!")
            st.session_state.waiting_for_ai = False

# Game Controls 
st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
if st.button("Restart Game"):
    st.session_state.board = chess.Board()
    st.session_state.game_over = False
    st.session_state.last_move = None
    st.session_state.waiting_for_ai = False
    st.session_state.move_history = []
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)