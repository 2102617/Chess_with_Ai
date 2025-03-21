import streamlit as st
import chess
import chess.svg
import base64

# Function to render chessboard as an image
def render_board(board):
    board_svg = chess.svg.board(board=board, size=400)
    img_data = base64.b64encode(board_svg.encode("utf-8")).decode("utf-8")
    return f"<img src='data:image/svg+xml;base64,{img_data}' width='400'>"

st.title("♟️ Two-Player Chess Game")

# Initialize session state variables
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "turn" not in st.session_state:
    st.session_state.turn = "White"  # Track whose turn it is
if "game_over" not in st.session_state:
    st.session_state.game_over = False

board = st.session_state.board

# Display chessboard
st.markdown(render_board(board), unsafe_allow_html=True)

# Display current turn
if not board.is_game_over():
    st.write(f"**{st.session_state.turn}'s turn**")
else:
    st.write("**Game Over!** Result:", board.result())
    st.session_state.game_over = True

# User input move
user_move = st.text_input("Enter your move in UCI format (e.g., e2e4):", max_chars=5)

# Process move
if st.button("Make Move") and not st.session_state.game_over:
    try:
        move = chess.Move.from_uci(user_move)
        if move in board.legal_moves:
            board.push(move)
            # Switch turns
            st.session_state.turn = "Black" if st.session_state.turn == "White" else "White"
            
            # Check for game over
            if board.is_game_over():
                st.session_state.game_over = True
        else:
            st.error("Invalid move! Try again.")
    except ValueError:
        st.error("Invalid move format! Use UCI notation.")
    
    st.rerun()  # ✅ Fixed: Use st.rerun() instead of st.experimental_rerun()

# Restart Game
if st.button("Restart Game"):
    st.session_state.board = chess.Board()
    st.session_state.turn = "White"
    st.session_state.game_over = False
    st.rerun()  # ✅ Fixed: Use st.rerun()
