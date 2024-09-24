import json
import logging
import os
import secrets

import requests
from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, redirect, request, session, url_for
from flask_cors import CORS
from handler.mongoHandler import insertCompanyUser, insertWorkAttendance
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, StickerSendMessage, TextMessage, TextSendMessage
from utils.auto_calendar import *

# load dot env setting
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/static", static_cache_timeout=3600)
swagger = Swagger(app)
app.secret_key = os.urandom(24)

channelAccessToken = os.getenv("CHANNEL_ACCESS_TOKEN")
channelSecret = os.getenv("CHANNEL_SECRET")
lineLoginSecret = os.getenv("LINE_LOGIN_SECRET")
lineLoginChannelId = os.getenv("LINE_LOGIN_CHANNEL_ID")
lineLoginCallbackUrl = os.getenv("LINE_LOGIN_CALLBACK_URL")
lineAuthUrl = os.getenv("LINE_AUTHORIZATION_URL")
lineTokenUrl = os.getenv("LINE_TOKEN_URL")
lineProfileUrl = os.getenv("LINE_PROFILE_URL")
serviceUrl = os.getenv("SERVICE_URL")


CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000", "http://localhost:5000", serviceUrl],
)
logging.basicConfig(level=logging.INFO)

lineBotApi = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)


@app.route("/")
def index():
    """server health
    Test server is health
    ---
    definitions:
      Response:
        type: string
    responses:
      200:
        description: A runing string text
        schema:
          $ref: '#/definitions/Response'
    """
    return "Flask Backend is Running."


@app.route("/auth/line", methods=["GET"])
def auth_line():
    oauth_url = (
        "https://access.line.me/oauth2/v2.1/authorize?"
        f"response_type=code&client_id={lineLoginChannelId}"
        f"&redirect_uri={lineLoginCallbackUrl}"
        "&state=12345abcde&scope=profile%20openid"
    )
    return redirect(oauth_url)


@app.route("/auth/line/callback", methods=["POST"])
def auth_line_callback():
    code = request.args.get("code")
    state = request.args.get("state")

    logging.info("code: " + code)
    if not code:
        return "Authorization failed.", 400

    token_url = "https://api.line.me/oauth2/v2.1/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": lineLoginCallbackUrl,
        "client_id": lineLoginChannelId,
        "client_secret": lineLoginSecret,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post(token_url, data=data, headers=headers)
    token_json = token_response.json()

    access_token = token_json.get("access_token")
    if not access_token:
        return "Failed to obtain access token.", 400

    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get(lineProfileUrl, headers=headers)
    profile_json = profile_response.json()

    user_id = profile_json.get("userId")
    display_name = profile_json.get("displayName")
    picture_url = profile_json.get("pictureUrl")
    status_message = profile_json.get("statusMessage")

    session["user"] = {
        "user_id": user_id,
        "display_name": display_name,
        "picture_url": picture_url,
        "status_message": status_message,
    }

    return redirect("http://localhost:3000")


@app.route("/api/user", methods=["GET"])
def get_user():
    user = session.get("user")
    logging.debug(f"get_user called. Authenticated: {bool(user)}")
    if not user:
        return jsonify({"authenticated": False}), 401
    logging.debug(f"User data: {user}")
    return jsonify({"authenticated": True, "user": user})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully."})


@app.route("/callback", methods=["POST"])
def linebot():
    body = request.get_data(as_text=True)
    print("Request: " + body)
    try:
        jsonData = json.loads(body)
        signature = request.headers["X-Line-Signature"]
        handler.handle(body, signature)
        tk = jsonData["events"][0]["replyToken"]
        type = jsonData["events"][0]["message"]["type"]
        if type == "text":
            msg = jsonData["events"][0]["message"]["text"]
            if msg[:7] == "建立個人檔案:":
                fileMsg = msg[7:]
                reply = insertCompanyUser(jsonData, fileMsg)
            elif msg == "打卡":
                reply = insertWorkAttendance(jsonData)
            elif msg == "使用說明" or msg == "如何使用":
                emoji = [{"index": 10, "productId": "5ac1bfd5040ab15980c9b435", "emojiId": "009"}]
                message = "歡迎使用假勤寶寶系統$\n假勤寶寶主要是管理您上下班時間以及請假相關的事宜\n\n注意：在使用之前，請先建檔，建檔訊息格式為： 建立個人檔案:[公司名稱] [姓名] [工號] [生日] (ex. 建立個人檔案:開心公司 假勤寶寶 123456 1998/01/01)"
                reply = [
                    TextSendMessage(message, emojis=emoji),
                    StickerSendMessage(sticker_id="11825378", package_id="6632"),
                ]
            else:
                emoji = [{"index": 14, "productId": "5ac1bfd5040ab15980c9b435", "emojiId": "005"}]
                message = "指令超出本寶寶的理解範圍了啦$ 等本寶寶學習一下!"
                reply = [
                    TextSendMessage(message, emojis=emoji),
                    StickerSendMessage(sticker_id="52002750", package_id="11537"),
                ]
        else:
            emoji = [{"index": 12, "productId": "5ac1bfd5040ab15980c9b435", "emojiId": "005"}]
            message = "超出本寶寶的理解範圍了啦$ 等本寶寶學習一下!"
            reply = [
                TextSendMessage(message, emojis=emoji),
                StickerSendMessage(sticker_id="52002750", package_id="11537"),
            ]

        if isinstance(reply, list):
            lineBotApi.reply_message(tk, reply)
        else:
            lineBotApi.reply_message(tk, TextSendMessage(reply))
    except Exception as e:
        print("Process message fail. Reason: " + str(e))
    return "OK"


@app.route("/test", methods=["POST"])
def test():
    replyMsg = insertCompanyUser()
    return replyMsg


@app.route("/schedule", methods=["GET"])
def testGetCalendar():
    # define data
    employees = define_employees()
    shift_requirements = define_shift_requirements()
    max_consecutive_days = 5

    # create optimize problem
    prob = create_problem()

    # define var
    schedule = define_variables(employees, shift_requirements)

    # add condition
    is_five_day_streak, is_one_day_streak = add_constraints(
        prob, schedule, employees, shift_requirements, max_consecutive_days
    )

    # add oject function
    add_objective_function(
        prob, schedule, employees, shift_requirements, is_five_day_streak, is_one_day_streak
    )

    # solve problem
    solve_problem(prob)

    # get result
    schedule_result = get_schedule_result(schedule, employees, shift_requirements)

    return jsonify(schedule_result)


@app.route("/api/v1/auto_calendar", methods=["GET"])
def getCalendar():
    # define data
    employees = define_employees()
    shift_requirements = define_shift_requirements()
    max_consecutive_days = 5

    # create optimize problem
    prob = create_problem()

    # add var
    schedule = define_variables(employees, shift_requirements)

    # add condition
    is_five_day_streak, is_one_day_streak = add_constraints(
        prob, schedule, employees, shift_requirements, max_consecutive_days
    )

    # add oject function
    add_objective_function(
        prob, schedule, employees, shift_requirements, is_five_day_streak, is_one_day_streak
    )

    # solve problem
    solve_problem(prob)

    # get result
    schedule_result = get_schedule_result(schedule, employees, shift_requirements)

    return jsonify(schedule_result)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run()
