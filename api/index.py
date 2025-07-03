import requests
import random
import json
from flask import Flask, jsonify, request


class GameInfo:

    def __init__(self):
        titleider: str = "D1170"
        secretkey: str = "XKX5PGCI3GX3KJSJJ9Q8I9KID6R1KC4MHYBRET3YONMEXT56CO"
        self.ApiKey: str = "OC|9854960547962773|7ba002d9ed45473ed2783f4621709be4"

    def GetAuthHeaders(self) -> dict:
        return {
            "content-type": "application/json",
            "X-SecretKey": secretkey
        }

def GetTitle(self) -> str:
        return titleider


settings = GameInfo()
app: Flask = Flask(__name__)
playfabCache: dict = {}
muteCache: dict = {}

titleider = ""
secretkey = ""
settings.ApiKey = ""


def ReturnFunctionJson(data, funcname, funcparam={}):
    rjson = data["FunctionParameter"]
    userId: str = rjson.get("CallerEntityProfile").get("Lineage").get(
        "TitlePlayerAccountId")

    req = requests.post(
        url=f"https://{titleider}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers=settings.GetAuthHeaders())

    if req.status_code == 200:
        return jsonify(
            req.json().get("data").get("FunctionResult")), req.status_code
    else:
        return jsonify({}), req.status_code


def GetIsNonceValid(nonce: str, oculusId: str):
    req = requests.post(
        url=f'https://graph.oculus.com/user_nonce_validate?nonce=' + nonce +
        '&user_id=' + oculusId + '&access_token=' + settings.ApiKey,
        headers={"content-type": "application/json"})
    return req.json().get("is_valid")


@app.route("/", methods=["POST", "GET"])
def main():
    return "idk man 6 7"


@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfabauthentication():
    rjson = request.get_json()

    if rjson.get("CustomId") is None:
        return jsonify({
            "Message": "Missing CustomId parameter",
            "Error": "BadRequest-NoCustomId"
        })
    if rjson.get("Nonce") is None:
        return jsonify({
            "Message": "Missing Nonce parameter",
            "Error": "BadRequest-NoNonce"
        })
    if rjson.get("AppId") is None:
        return jsonify({
            "Message": "Missing AppId parameter",
            "Error": "BadRequest-NoAppId"
        })
    if rjson.get("Platform") is None:
        return jsonify({
            "Message": "Missing Platform parameter",
            "Error": "BadRequest-NoPlatform"
        })
    if rjson.get("OculusId") is None:
        return jsonify({
            "Message": "Missing OculusId parameter",
            "Error": "BadRequest-NoOculusId"
        })

    if rjson.get("AppId") != titleider:
        return jsonify({
            "Message": "Request sent for the wrong App ID",
            "Error": "BadRequest-AppIdMismatch"
        })
    if not rjson.get("CustomId").startswith("OC") and not rjson.get(
            "CustomId").startswith("PI"):
        return jsonify({
            "Message": "Bad request",
            "Error": "BadRequest-No OC or PI Prefix"
        })

    url = f"https://{titleider}.playfabapi.com/Server/LoginWithServerCustomId"
    login_request = requests.post(url=url,
                                  json={
                                      "ServerCustomId": rjson.get("CustomId"),
                                      "CreateAccount": True
                                  },
                                  headers=settings.GetAuthHeaders())

    if login_request.status_code == 200:
        data = login_request.json().get("data")
        sessionTicket = data.get("SessionTicket")
        entityToken = data.get("EntityToken").get("EntityToken")
        playFabId = data.get("PlayFabId")
        entityType = data.get("EntityToken").get("Entity").get("Type")
        entityId = data.get("EntityToken").get("Entity").get("Id")

        print(
            requests.post(
                url=f"https://{titleider}.playfabapi.com/Client/LinkCustomID",
                json={
                    "ForceLink": True,
                    "CustomId": rjson.get("CustomId")
                },
                headers=settings.GetAuthHeaders()).json())

        return jsonify({
            "PlayFabId": playFabId,
            "SessionTicket": sessionTicket,
            "EntityToken": entityToken,
            "EntityId": entityId,
            "EntityType": entityType
        })
    else:
        errorDetails = login_request.json().get('errorDetails')
        firstBan = next(iter(errorDetails))
        return jsonify({
            "BanMessage": str(firstBan),
            "BanExpirationTime": str(errorDetails[firstBan])
        })


@app.route("/api/CachePlayFabId", methods=["POST"])
def cacheplayfabid():
    rjson = request.get_json()

    playfabCache[rjson.get("PlayFabId")] = rjson

    return jsonify({"Message": "Success"}), 200


@app.route('/api/TitleData', methods=['POST'])
def titled_data():
    return jsonify({"MOTD":"ADD UR MOTD HERE"})


@app.route("/api/CheckForBadName", methods=["POST", "GET"])
def check_for_bad_name():
    rjson = request.get_json()
    function_result = rjson["FunctionArgument"]

    name = function_result["name"].upper()  

    bad_words = {
        "KKK", "PENIS", "NIGG", "NEG", "NIGA", "MONKEYSLAVE", "SLAVE", "FAG",
        "NAGGI", "TRANNY", "QUEER", "KYS", "DICK", "PUSSY", "VAGINA", "BIGBLACKCOCK",
        "DILDO", "HITLER", "KKX", "XKK", "NIGA", "NIGE", "NIG", "NI6", "PORN",
        "JEW", "JAXX", "TTTPIG", "SEX", "COCK", "CUM", "FUCK", "PENIS", "DICK",
        "ELLIOT", "JMAN", "K9", "NIGGA", "TTTPIG", "NICKER", "NICKA",
        "NLGGA", "NII", "@here", "!", " ", "JMAN", "PPPTIG", "CLEANINGBOT", "JANITOR", "K9",
        "H4PKY", "MOSA", "NIGGER", "NIGGA", "IHATENIGGERS", "@everyone", "TTT", "_", "NEGRO",
        "KNEEGROW", "NI9", "NATEHIGGERS"
    }

    if name in bad_words:
            return jsonify({"result": 2})
    else:
        return jsonify({"result": 0})


@app.route("/api/consumeiap", methods=["POST", "GET"])
def consumeoculusiap():
    rjson = request.get_json()

    accessToken = rjson.get("userToken")
    userId = rjson.get("userID")
    playFabId = rjson.get("playFabId")
    nonce = rjson.get("nonce")
    platform = rjson.get("platform")
    sku = rjson.get("sku")
    debugParams = rjson.get("debugParemeters")

    req = requests.post(
        url=
        f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={userId}&sku={sku}&access_token="
        + settings.ApiKey,
        headers={"content-type": "application/json"})

    if bool(req.json().get("success")):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})


@app.route("/api/photon", methods=["POST"])
def photonauth():
    print(f"Received {request.method} request at /api/photon")
    getjson = request.get_json()
    Ticket = getjson.get("Ticket")
    Nonce = getjson.get("Nonce")
    Platform = getjson.get("Platform")
    UserId = getjson.get("UserId")
    nickName = getjson.get("username")
    if request.method.upper() == "GET":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        userId = Ticket.split('-')[0] if Ticket else None
        print(f"Extracted userId: {UserId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        if Platform != 'Quest':
            return jsonify({
                'Error': 'Bad request',
                'Message': 'Invalid platform!'
            }), 403

        if Nonce is None:
            return jsonify({
                'Error': 'Bad request',
                'Message': 'Not Authenticated!'
            }), 304

        req = requests.post(
            url=f"https://{titleider}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers={
                "content-type": "application/json",
                "X-SecretKey": secretkey
            })

        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
            nickName = req.json().get("UserInfo",
                                      {}).get("UserAccountInfo",
                                              {}).get("Username")
            if not nickName:
                nickName = None

            print(
                f"Authenticated user {userId.lower()} with nickname: {nickName}"
            )

            return jsonify({
                'resultCode': 1,
                'message':
                f'Authenticated user {userId.lower()} title {titleider.lower()}',
                'userId': f'{userId.upper()}',
                'nickname': nickName
            })
        else:
            print("Failed to get user account info from PlayFab")
            return jsonify({
                'resultCode': 0,
                'message': "Something went wrong",
                'userId': None,
                'nickname': None
            })

    elif request.method.upper() == "POST":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        ticket = rjson.get("Ticket")
        userId = ticket.split('-')[0] if ticket else None
        print(f"Extracted userId: {userId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        req = requests.post(
            url=f"https://{titleider}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers={
                "content-type": "application/json",
                "X-SecretKey": secretkey
            })

        print(f"Authenticated user {userId.lower()}")
        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
            nickName = req.json().get("UserInfo",
                                      {}).get("UserAccountInfo",
                                              {}).get("Username")
            if not nickName:
                nickName = None
            return jsonify({
                'resultCode': 1,
                'message':
                f'Authenticated user {userId.lower()} title {titleider.lower()}',
                'userId': f'{userId.upper()}',
                'nickname': nickName
            })
        else:
            print("Failed to get user account info from PlayFab")
            successJson = {
                'resultCode': 0,
                'message': "Something went wrong",
                'userId': None,
                'nickname': None
            }
            authPostData = {}
            for key, value in authPostData.items():
                successJson[key] = value
            print(f"Returning successJson: {successJson}")
            return jsonify(successJson)
    else:
        print(f"Invalid method: {request.method.upper()}")
        return jsonify({
            "Message":
            "Use a POST or GET Method instead of " + request.method.upper()
        })


def ReturnFunctionJson(data, funcname, funcparam={}):
    print(f"Calling function: {funcname} with parameters: {funcparam}")
    rjson = data.get("FunctionParameter", {})
    userId = rjson.get("CallerEntityProfile",
                       {}).get("Lineage", {}).get("TitlePlayerAccountId")

    print(f"UserId: {userId}")

    req = requests.post(
        url=f"https://{titleider}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers={
            "content-type": "application/json",
            "X-SecretKey": secretkey
        })

    if req.status_code == 200:
        result = req.json().get("data", {}).get("FunctionResult", {})
        print(f"Function result: {result}")
        return jsonify(result), req.status_code
    else:
        print(f"Function execution failed, status code: {req.status_code}")
        return jsonify({}), req.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8067)
