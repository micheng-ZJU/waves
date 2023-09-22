from .qaFunctions import *


################
#     WebQA    #
################
def search(message):
    result = ''
    if message.find('引擎查询') != -1 or message.upper().find('SEARCH ENGINE') != -1:
        result = results_to_string(
            message.upper().replace("使用引擎查询", "").replace("WITH SEARCH ENGINE", "").replace("FNGPT:", "").strip())
        return result

    return result
