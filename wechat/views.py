import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.generic import View
import xml.etree.ElementTree as ET
# Create your views here.
from wechat.WXBizMsgCrypt3 import WXBizMsgCrypt
import xmltodict
import redis

rdp_local = redis.ConnectionPool(host='47.95.217.37', port=6379, db=0)  # 默认db=0，测试使用db=1
rdc_local = redis.StrictRedis(connection_pool=rdp_local)


class Wechat(View):
    def get(self, request):
        sToken = "hQybAUE112YajhcxCQ"
        sEncodingAESKey = "ytr9W97MuSuIDuDXbnwpBLjejBv47kycLRKCLCvWOMy"
        sCorpID = "ww12846bc6b96876c4"

        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
        # sVerifyMsgSig=HttpUtils.ParseUrl("msg_signature")
        # ret = wxcpt.VerifyAESKey()
        # print ret
        sVerifyMsgSig = request.GET.get("msg_signature")
        # sVerifyTimeStamp=HttpUtils.ParseUrl("timestamp")
        sVerifyTimeStamp = request.GET.get("timestamp")
        # sVerifyNonce=HttpUitls.ParseUrl("nonce")
        sVerifyNonce = request.GET.get("nonce")
        # sVerifyEchoStr=HttpUtils.ParseUrl("echostr")
        sVerifyEchoStr = request.GET.get("echostr")
        print(sVerifyEchoStr, sVerifyMsgSig, sVerifyNonce, sVerifyTimeStamp)
        ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
        if (ret != 0):
            print("ERR: VerifyURL ret: " + str(ret))
            return JsonResponse({"msg": "fail"}, safe=True)
        else:
            return HttpResponse(sEchoStr)

    def post(self, request):
        sToken = "hQybAUE112YajhcxCQ"
        sEncodingAESKey = "ytr9W97MuSuIDuDXbnwpBLjejBv47kycLRKCLCvWOMy"
        sCorpID = "ww12846bc6b96876c4"

        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

        # sReqMsgSig = HttpUtils.ParseUrl("msg_signature")
        sReqMsgSig = request.GET.get("msg_signature")
        sReqTimeStamp = request.GET.get("timestamp")
        sReqNonce = request.GET.get("nonce")
        sReqData = request.body
        sReqData = sReqData.decode('gbk')
        print(sReqData)
        ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        print(ret, sMsg)
        if (ret != 0):
            print("ERR: DecryptMsg ret: " + str(ret))
            return HttpResponse({"msg": "fail"})
        # 解密成功，sMsg即为xml格式的明文
        else:
            sMsg = sMsg.decode('utf8')
            json_str = xmltodict.parse(sMsg)
            print(json_str)
            # xml_tree = ET.fromstring(sMsg)
            # print(xml_tree)
            # content = xml_tree.find("Content").text
            # print(content)
            return HttpResponse("sucess!")


class MediaApi(View):
    def get(self, request):
        return JsonResponse({"result": "success"})

    def post(self, request):
        received_json_data = json.loads(request.body)
        data = received_json_data.get("data")
        account = received_json_data.get("account")
        from_id = received_json_data.get("from")
        realName = ""
        if isinstance(account, dict):
            phoneNumber = account.get("phoneNumber", "")
            realName = account.get("realName", "")
            if phoneNumber:
                account = phoneNumber
            elif realName:
                account = realName
        if data and account:
            if not isinstance(data, dict):
                data = json.loads(data)

            data["account"] = account
            # ios
            if from_id:
                data['ua'] = 'ios'
                data['adxml'] = from_id
                data['realName'] = realName
                rdc_local.lpush("all_data", json.dumps(data))
            else:
                rdc_local.lpush("all_data", json.dumps(data))
        return JsonResponse({"result": "success"})


class Weteam(View):
    def get(self, request):
        res = request.body.decode()
        print(json.loads(res))
        self.write_log(json.dumps(res))
        return JsonResponse({"result": "success"})

    def post(self, request):
        res = request.body.decode()
        print(json.loads(res))
        self.write_log(json.dumps(res))
        return JsonResponse({"result": "success"})

    def write_log(self, data):
        with open("./pyq.log", 'w') as f:
            f.writelines(data + "\n")