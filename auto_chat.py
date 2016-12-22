from flask import Flask,request,make_response
import time,hashlib,re,requests
import xml.etree.ElementTree as ET
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from chatterbot import ChatBot as CB
from chatterbot.trainers import ChatterBotCorpusTrainer
#======================[ChatBot]==========
bot = CB("simple_one",
         storage_adapter="chatterbot.adapters.storage.JsonFileStorageAdapter",
         input_adapter="chatterbot.adapters.input.VariableInputTypeAdapter",
         output_adapter="chatterbot.adapters.output.OutputFormatAdapter",
         output_format='text',
         logic_adapters=[
         "chatterbot.adapters.logic.MathematicalEvaluation",
         "chatterbot.adapters.logic.TimeLogicAdapter",
         "chatterbot.adapters.logic.ClosestMatchAdapter"
         ],
         database="./database.json",
         read_only=True
        )
#======================[End ChatBot]==========

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/weixin',methods = ['GET','POST'])
def weixin():
    # Weixin
    if request.method == 'GET':
        token = 'li1gui1ying'
        query = request.args
        signature = query.get('signature','')
        timestamp = query.get('timestamp','')
        nonce = query.get('nonce','')
        echostr = query.get('echostr','')
        s = [timestamp,nonce,token]
        s.sort()
        s = ''.join(s)
        if hashlib.sha1(s).hexdigest() == signature:
            return make_response(echostr)
    else: # Post request
        xmlData = ET.fromstring(request.stream.read())
        msg_type = xmlData.find('MsgType').text
        if msg_type == 'text':
            ToUserName = xmlData.find('ToUserName').text
            FromUserName = xmlData.find('FromUserName').text
            # chatbot replay
            Content = bot.get_response(xmlData.find('Content').text)
            reply = '''<xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[%s]]></Content>
                    </xml>'''
            response = make_response( reply % (FromUserName, ToUserName, str(int(time.time())), Content ) )
            response.content_type = 'application/xml'
            return response

if __name__ == "__main__":
   bot.set_trainer(ChatterBotCorpusTrainer)
   bot.train(
     "chatterbot.corpus.english"
   )
   app.run(host='0.0.0.0', port=8000, debug=True)
