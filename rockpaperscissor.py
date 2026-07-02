import json
import random
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


CHOICES = ("rock", "paper", "scissors")
CHOICE_NUMBERS = {
	"1": "rock",
	"2": "paper",
	"3": "scissors",
}


def get_winner(user_choice, computer_choice):
	if user_choice == computer_choice:
		return "tie"

	winning_pairs = {
		"rock": "scissors",
		"paper": "rock",
		"scissors": "paper",
	}

	if winning_pairs[user_choice] == computer_choice:
		return "user"

	return "computer"


def play_game(user_choice):
	user_choice = user_choice.strip().lower()
	if user_choice not in CHOICES:
		raise ValueError("Invalid choice")

	computer_choice = random.choice(CHOICES)
	winner = get_winner(user_choice, computer_choice)
	return {
		"user_choice": user_choice,
		"computer_choice": computer_choice,
		"winner": winner,
		"message": get_result_message(winner),
	}


def get_result_message(winner):
	if winner == "tie":
		return "It's a tie!"
	if winner == "user":
		return "You win!"
	return "Computer wins!"


def get_user_choice():
	while True:
		print("Select your choice:")
		print("1. Rock")
		print("2. Paper")
		print("3. Scissors")
		choice = input("Enter Rock, Paper, Scissors, or 1-3: ").strip().lower()
		choice = CHOICE_NUMBERS.get(choice, choice)
		if choice in CHOICES:
			return choice
		print("Invalid choice. Please select Rock, Paper, Scissors, or 1-3.")


def play_round():
	user_choice = get_user_choice()
	result = play_game(user_choice)

	print(f"You chose: {result['user_choice']}")
	print(f"Computer chose: {result['computer_choice']}")
	print(result["message"])


class RockPaperScissorsHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path in ("/", "/index.html"):
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
			result = play_game(data.get("choice", ""))
		except (json.JSONDecodeError, ValueError):
			self.send_json({"error": "Please choose rock, paper, or scissors."}, 400)
			return

		self.send_json(result)

	def send_html(self):
		file_path = Path(__file__).with_name("index.html")
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
	server = HTTPServer(("localhost", 8000), RockPaperScissorsHandler)
	print("Open http://localhost:8000 in your browser to play.")
	print("Press Ctrl+C to stop the server.")
	server.serve_forever()


def main():
	print("Rock Paper Scissors")

	while True:
		play_round()
		play_again = input("Play again? (y/n): ").strip().lower()
		if play_again != "y":
			print("Thanks for playing!")
			break


if __name__ == "__main__":
	if "--cli" in sys.argv:
		main()
	else:
		start_server()
