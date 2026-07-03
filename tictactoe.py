import json
import random
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


EMPTY = ""
USER = "X"
COMPUTER = "O"
BOARD_SIZE = 9
WINNING_LINES = (
	(0, 1, 2),
	(3, 4, 5),
	(6, 7, 8),
	(0, 3, 6),
	(1, 4, 7),
	(2, 5, 8),
	(0, 4, 8),
	(2, 4, 6),
)


def create_board():
	return [EMPTY] * BOARD_SIZE


def validate_board(board):
	if not isinstance(board, list) or len(board) != BOARD_SIZE:
		raise ValueError("Invalid board")

	for cell in board:
		if cell not in (EMPTY, USER, COMPUTER):
			raise ValueError("Invalid board")

	if board.count(COMPUTER) > board.count(USER):
		raise ValueError("Invalid board")

	if board.count(USER) - board.count(COMPUTER) > 1:
		raise ValueError("Invalid board")

	return board


def get_winner(board):
	for first, second, third in WINNING_LINES:
		if board[first] and board[first] == board[second] == board[third]:
			return board[first]

	if EMPTY not in board:
		return "tie"

	return None


def available_moves(board):
	return [index for index, cell in enumerate(board) if cell == EMPTY]


def find_winning_move(board, player):
	for move in available_moves(board):
		trial_board = board.copy()
		trial_board[move] = player
		if get_winner(trial_board) == player:
			return move

	return None


def choose_computer_move(board):
	winning_move = find_winning_move(board, COMPUTER)
	if winning_move is not None:
		return winning_move

	blocking_move = find_winning_move(board, USER)
	if blocking_move is not None:
		return blocking_move

	for move in (4, 0, 2, 6, 8):
		if board[move] == EMPTY:
			return move

	return random.choice(available_moves(board))


def play_turn(board, user_move):
	board = validate_board(board).copy()

	if get_winner(board):
		return build_result(board, None)

	if not isinstance(user_move, int) or user_move not in range(BOARD_SIZE):
		raise ValueError("Invalid move")

	if board[user_move] != EMPTY:
		raise ValueError("That square is already taken")

	board[user_move] = USER
	if not get_winner(board):
		computer_move = choose_computer_move(board)
		board[computer_move] = COMPUTER
	else:
		computer_move = None

	return build_result(board, computer_move)


def build_result(board, computer_move):
	winner = get_winner(board)
	messages = {
		USER: "You win!",
		COMPUTER: "Computer wins!",
		"tie": "It's a tie!",
		None: "Your move.",
	}
	return {
		"board": board,
		"computer_move": computer_move,
		"winner": winner,
		"message": messages[winner],
	}


def print_board(board):
	values = [cell or str(index + 1) for index, cell in enumerate(board)]
	print(f" {values[0]} | {values[1]} | {values[2]} ")
	print("---+---+---")
	print(f" {values[3]} | {values[4]} | {values[5]} ")
	print("---+---+---")
	print(f" {values[6]} | {values[7]} | {values[8]} ")


def get_user_move(board):
	while True:
		choice = input("Choose a square from 1-9: ").strip()
		if choice.isdigit():
			move = int(choice) - 1
			if move in available_moves(board):
				return move

		print("Invalid move. Choose an empty square from 1-9.")


def play_cli_game():
	board = create_board()
	print("Tic Tac Toe")
	print("You are X. Computer is O.")

	while not get_winner(board):
		print_board(board)
		result = play_turn(board, get_user_move(board))
		board = result["board"]
		print(result["message"])

	print_board(board)


class TicTacToeHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path in ("/", "/tictactoe.html"):
			self.send_html()
		else:
			self.send_error(404, "Page not found")

	def do_POST(self):
		if self.path != "/play":
			self.send_error(404, "Page not found")
			return

		content_length = int(self.headers.get("Content-Length", 0))
		body = self.rfile.read(content_length).decode("utf-8")

		try:
			data = json.loads(body)
			result = play_turn(data.get("board"), data.get("move"))
		except (json.JSONDecodeError, ValueError) as error:
			self.send_json({"error": str(error)}, 400)
			return

		self.send_json(result)

	def send_html(self):
		file_path = Path(__file__).with_name("tictactoe.html")
		self.send_response(200)
		self.send_header("Content-Type", "text/html; charset=utf-8")
		self.end_headers()
		self.wfile.write(file_path.read_bytes())

	def send_json(self, data, status=200):
		response = json.dumps(data).encode("utf-8")
		self.send_response(status)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(response)))
		self.end_headers()
		self.wfile.write(response)

	def log_message(self, format, *args):
		return


def start_server():
	server = HTTPServer(("localhost", 8001), TicTacToeHandler)
	print("Open http://localhost:8001 in your browser to play Tic Tac Toe.")
	print("Press Ctrl+C to stop the server.")
	server.serve_forever()


if __name__ == "__main__":
	if "--cli" in sys.argv:
		play_cli_game()
	else:
		start_server()