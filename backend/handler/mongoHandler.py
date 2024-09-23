import os
import re
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils.time import getCurrentTime, getCurrentMonth
from linebot.models import TextSendMessage, StickerSendMessage

mongoToken = 'yared612' # local端需替換成token
mongoUri = "mongodb+srv://yared:" + mongoToken + "@linetestcluster.qcd8g79.mongodb.net/?retryWrites=true&w=majority&appName=lineTestCluster"
client = MongoClient(mongoUri, server_api=ServerApi('1'))

def insertCompanyUser(jsonData, message):
    try:
        # User Data
        userFileList = re.split(r"\s+", message)
        companyName = userFileList[0]
        userName = userFileList[1]
        employeeId = userFileList[2]
        birthday = userFileList[3]
        createTime = getCurrentTime()

        # DB collection
        dataBase = client["companyUser"]
        collection = dataBase["test"]
        
        document = {
            "userId": jsonData["events"][0]["source"]["userId"],
            "companyName": companyName,
            "userName": userName,
            "employeeId": employeeId,
            "birthday": birthday,
            "createTime": createTime
        }
        print("insertCompanyUser mongo request: " + json.dumps(document))
        result = collection.insert_one(document) # 插入資料
        replyMsg = f"建檔成功$\n公司名稱：{companyName}\n姓名：{userName}\n工號：{employeeId}\n建檔時間：{createTime}"
        print("replyMsg: " + replyMsg)
        emoji = [
            {
                "index": 4,
                "productId": "5ac21e6c040ab15980c9b444",
                "emojiId": "002"
            }
        ]
        return [TextSendMessage(replyMsg, emojis=emoji), StickerSendMessage(sticker_id="51626520", package_id="11538")]
    except Exception as e:
        emoji = [
            {
                "index": 4,
                "productId": "5ac1bfd5040ab15980c9b435",
                "emojiId": "005"
            }
        ]
        print("Crate user file fail. Reason: " + e)
        return [TextSendMessage("建檔失敗$ 請檢查相關輸入是否有誤", emojis=emoji), StickerSendMessage(sticker_id="10551379", package_id="6136")]


def insertWorkAttendance(jsonData):
    try:
        userId = jsonData["events"][0]["source"]["userId"]

        # Check User Data
        userDataBase = client["companyUser"]
        userCollection = userDataBase["test"]
        query = {"userId": userId}
        queryUserDataResult = userCollection.find_one(query)
        if queryUserDataResult == None:
            emoji = [
                {
                    "index": 4,
                    "productId": "5ac1bfd5040ab15980c9b435",
                    "emojiId": "005"
                }
            ]
            return [TextSendMessage("打卡失敗$ 無法查詢到您的資本資料 請先進行建檔後再打卡~", emojis=emoji), StickerSendMessage(sticker_id="10551380", package_id="6136")]

        companyName = queryUserDataResult["companyName"]
        userName = queryUserDataResult["userName"]
        employeeId = queryUserDataResult["employeeId"]

        # Insert or Update Attendance Data
        attendanceDataBase = client["work"]
        attendanceCollection = attendanceDataBase["attendance"]
        queryAttendanceDataResult = attendanceCollection.find_one(query)
        createTime = getCurrentTime()
        if queryAttendanceDataResult == None:
            print("No data in attendance collection. Insert New Data.")
            document = {
                "userId": userId,
                "companyName": companyName,
                "userName": userName,
                "employeeId": employeeId,
                "attendanceList": [createTime]
            }
            print("insertWorkAttendance mongo request: " + json.dumps(document))
            result = attendanceCollection.insert_one(document) # 插入資料
        else:
            updateOperation = {"$push": {"attendanceList": createTime}}
            print("insertWorkAttendance mongo request: " + json.dumps(updateOperation))
            attendanceCollection.update_one(query, updateOperation)

        replyMsg = f"打卡成功!!$\n公司名稱：{companyName}\n姓名：{userName}\n工號：{employeeId}\n打卡時間：{createTime}"
        print("replyMsg: " + replyMsg)
        emoji = [
            {
                "index": 6,
                "productId": "5ac21e6c040ab15980c9b444",
                "emojiId": "002"
            }
        ]
        return [TextSendMessage(replyMsg, emojis=emoji), StickerSendMessage(sticker_id="1989", package_id="446")]
    except Exception as e:
        emoji = [
            {
                "index": 4,
                "productId": "5ac1bfd5040ab15980c9b435",
                "emojiId": "005"
            }
        ]
        print("Crate attendence fail. Reason: " + str(e))
        return [TextSendMessage("打卡失敗$ 請稍後嘗試~~"), StickerSendMessage(sticker_id="10551379", package_id="6136")]