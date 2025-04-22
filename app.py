import os
from flask import Flask, request
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    elif request.method == "POST":
        data = request.get_json()
        print("Received POST request:", data)

        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    if "messages" in value:
                        msg = value["messages"][0]
                        phone = msg["from"]

                        # Text message trigger
                        if msg["type"] == "text":
                            text = msg["text"]["body"].lower()
                            if text == "hi":
                                send_button_message(phone)

                        # Button response
                        elif msg["type"] == "interactive":
                            interactive = msg["interactive"]

                            if "button_reply" in interactive:
                                button_id = interactive["button_reply"]["id"]
                                if button_id == "ug_button":
                                    send_ug_list(phone)
                                elif button_id == "pg_button":
                                    send_pg_list(phone)

                            elif "list_reply" in interactive:
                                row_id = interactive["list_reply"]["id"]
                                if row_id == "ug_eng":
                                    send_text_message(phone, "UG Engineering: Choose from CS, ECE, Mech.")
                                elif row_id == "ug_med":
                                    send_text_message(phone, "UG Medical: Options include MBBS, BDS, BPT.")
                                elif row_id == "pg_mba":
                                    send_text_message(phone, "PG MBA: Specializations in Finance & Mark, HR, Marketing.")
                                elif row_id == "pg_mtech":
                                    send_text_message(phone, "PG MTech: Choose from AI, VLSI, Thermal Engg.")

        return "OK", 200


def send_button_message(phone):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Choose your program:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "ug_button",
                            "title": "UG"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "pg_button",
                            "title": "PG"
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Button response:", response.status_code, response.text)


def send_ug_list(phone):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "Select a UG course:"
            },
            "action": {
                "button": "Choose UG Course",
                "sections": [
                    {
                        "title": "UG Courses",
                        "rows": [
                            {
                                "id": "ug_eng",
                                "title": "Engineering"
                            },
                            {
                                "id": "ug_med",
                                "title": "Medical"
                            }
                        ]
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print("UG List response:", response.status_code, response.text)


def send_pg_list(phone):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "Select a PG course:"
            },
            "action": {
                "button": "Choose PG Course",
                "sections": [
                    {
                        "title": "PG Courses",
                        "rows": [
                            {
                                "id": "pg_mba",
                                "title": "MBA"
                            },
                            {
                                "id": "pg_mtech",
                                "title": "MTech"
                            }
                        ]
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print("PG List response:", response.status_code, response.text)


def send_text_message(phone, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "text": {
            "body": message
        },
        "type": "text"
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Text response:", response.status_code, response.text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
