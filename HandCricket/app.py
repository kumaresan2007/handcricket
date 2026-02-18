from flask import Flask, render_template, request, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "handcricketsecret"


# ---------------- HOME ----------------
@app.route("/")
def home():
    session.clear()
    return render_template("index.html")


# ---------------- TOSS ----------------
@app.route("/toss", methods=["GET", "POST"])
def toss():

    if request.method == "POST":
        user_choice = request.form["choice"]
        toss_result = random.choice(["heads", "tails"])

        session["toss_result"] = toss_result

        # ✅ USER WINS TOSS
        if user_choice == toss_result:
            session["toss_winner"] = "user"

            return render_template(
                "toss.html",
                result="You won the toss! Choose Bat or Bowl.",
                choose=True,
                auto_start=False
            )

        # ✅ COMPUTER WINS TOSS
        else:
            session["toss_winner"] = "computer"

            comp_choice = random.choice(["bat", "bowl"])
            session["first_player"] = (
                "computer" if comp_choice == "bat" else "user"
            )

            return render_template(
                "toss.html",
                result=f"Computer won the toss and chose to {comp_choice.upper()}!",
                choose=False,
                auto_start=True
            )

    return render_template("toss.html", result="", choose=False, auto_start=False)


# ---------------- DECISION AFTER TOSS ----------------
@app.route("/decision", methods=["POST"])
def decision():

    user_decision = request.form["decision"]

    if user_decision == "bat":
        session["first_player"] = "user"
    else:
        session["first_player"] = "computer"

    return redirect(url_for("game"))


# ---------------- GAME ----------------
@app.route("/game", methods=["GET", "POST"])
def game():

    # Initialize game state
    if "innings" not in session:
        session["innings"] = 1
        session["user_score"] = 0
        session["computer_score"] = 0
        session["target"] = None
        session["game_over"] = False

    message = session.get("last_ball", "")

    # -------- PLAY BALL --------
    if request.method == "POST" and not session["game_over"]:

        user_num = int(request.form["number"])
        comp_num = random.randint(1, 6)

        session["last_ball"] = f"You played {user_num} | Computer played {comp_num}"
        message = session["last_ball"]

        # Who is batting?
        batting_user = (
            (session["innings"] == 1 and session["first_player"] == "user") or
            (session["innings"] == 2 and session["first_player"] == "computer")
        )

        # -------- OUT CONDITION --------
        if user_num == comp_num:

            message = f"OUT! Both chose {user_num}"

            # End of 1st innings
            if session["innings"] == 1:

                first_score = (
                    session["user_score"]
                    if session["first_player"] == "user"
                    else session["computer_score"]
                )

                session["target"] = first_score + 1
                session["innings"] = 2

                message += f" | Target: {session['target']}"

            # End of 2nd innings
            else:
                session["game_over"] = True

        # -------- SCORE ADD --------
        else:

            if batting_user:
                session["user_score"] += user_num
            else:
                session["computer_score"] += comp_num

            # Check target in 2nd innings
            if session["innings"] == 2:

                chasing_score = (
                    session["user_score"]
                    if session["first_player"] == "computer"
                    else session["computer_score"]
                )

                if chasing_score >= session["target"]:
                    session["game_over"] = True
                    message = "🎯 Target reached!"

        session.modified = True

    # -------- RESULT --------
    winner = ""

    # Only decide winner AFTER 2nd innings
    if session["game_over"] and session["innings"] == 2:

        if session["user_score"] > session["computer_score"]:
            winner = "🏆 User Wins!"
        elif session["computer_score"] > session["user_score"]:
            winner = "💻 Computer Wins!"
        else:
            winner = "🤝 Match Draw!"

    return render_template(
        "game.html",
        user_score=session["user_score"],
        computer_score=session["computer_score"],
        innings=session["innings"],
        target=session["target"],
        message=message,
        game_over=session["game_over"],
        winner=winner
    )


if __name__ == "__main__":
    app.run(debug=True)

