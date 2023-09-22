import configparser
import os
import time

import jieba
import openai

from .py3Aiml.Kernel import Kernel
from .webqa import webQA

jieba.setLogLevel(jieba.logging.INFO)
# Set up the API key
openai.api_key = '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'


class ChatBot:
    """
       基于 GPT 和 WebQA 的智能对话模型
    """

    def __init__(self, config_file: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.cfg')):
        config = configparser.ConfigParser()
        config.read(config_file)
        """
        初始化 ChatBot 类
        """

        self.load_file = config.get('Resource', 'load_file')  # AIML内核指定的文件路径

        # 初始化分词器
        jieba.initialize()

        # 初始化知识库
        self.mybot = Kernel()
        self.mybot.bootstrap(learnFiles=self.load_file, commands='LOAD AIML SEALS APAC')

        # 初始化学习库
        self.template = '<aiml version="1.0" encoding="UTF-8">\n{rule}\n</aiml>'
        self.category_template = '<category><pattern>{pattern}</pattern><template>{answer}</template></category>'

    def response(self, message: str) -> str:
        """
        ChatBot 回复函数，接收用户输入信息并生成相应的回复
        :param message: 用户输入信息
        :type message: str
        :return: ChatBot 生成的回复
        :return: ChatBot 生成的回复
        :rtype: str
        """
        # 限制字数
        if len(message) > 2000:
            return self.mybot.respond('MAX')
        elif not message:
            return self.mybot.respond('MIN')

        # 结束聊天
        if message in {'exit', 'quit'}:
            return self.mybot.respond('Bye')
        else:
            if "SSGPT:" in message.upper():
                # Make an API call
                for _ in range(3):
                    try:
                        message = [{"role": "user", "content": message}]
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=message
                        )
                        return response.choices[0].message['content'].strip()
                    except openai.error.APIConnectionError:
                        time.sleep(3)
                        continue
            else:
                # AIML和WebQA
                result = self.mybot.respond(''.join(jieba.lcut(message)))
                if not result.startswith('#'):  # AIML模式
                    return result
                elif '#NONE#' in result:  # 搜索模式
                    ans = webQA.search(message)
                    if ans:
                        return ans
                    else:
                        response = {
                            'result': "Unable to match the query against the SEALS APAC Knowledge base patterns. We "
                                      "will conduct a search using AI Model.",
                            'history': message
                        }
                        return response
