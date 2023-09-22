import json
import re
import subprocess
from urllib.parse import unquote
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from core.chatbot import ChatBot
from azure.storage.blob import BlobServiceClient
import pandas as pd
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
import csv

app = Flask(__name__)
CORS(app)

data = [
    {'name': 'Feed Asset Set up Form information from SharePoint to wso',
     'description': 'The process of this RDA primarily encompasses retrieving corresponding Feed Asset information '
                    'from sharePoint and Excel files. Subsequently, this information is automatically populated into '
                    'Wall street Office.Wall Street Office is a desktop - level application of AppV.Through RDA '
                    'automation, human resources can be redirected towards more critical tasks.',
     'module': 'RDA, SharePoint, Excel, Wall street office, Browser, UI Automation'},
    {'name': 'FED Cash Mark Email Notification',
     'description': 'The process of this RDA include generate sOD margin for all FED Cash brokers, and draft margin '
                    'call emails/repriced amount emails to specific brokers only based on cash mark logic for that '
                    'particular day. The project involves the integration of Outlook and Excel, as well as the '
                    'handling of databases, ultimately saving users at least 30 minutes per day and reducing '
                    'associated risks.',
     'module': 'RDA, Outlook, Excel, databases, Browser, UI Automation, FED Cash brokers'},
    {'name': 'client KPI Automation',
     'description': 'The process of this RDA primarily encompasses compiling a final PowerPoint report, and copying '
                    'data from multiple Excel files and adjusting the2format based on the inserted data. To complete '
                    'the report, the RDA automation could compile over 120 slides, copy data from 10+ files and 150+ '
                    'tables, and adjust the format of tables and charts in PowerPoint.Through RDA automation, '
                    'human resources can be redirected towards more critical tasks.',
     'module': 'RDA, Powerpoint, Excel, csv, UI Automation'},
    {'name': 'eCFM Data Download and Extract',
     'description': 'The process of this RDA primarily encompasses retrieving corresponding information from POFs '
                    'which are downloaded from eCFM. The RDA automation could eliminate manual touch points. And '
                    'users could release more energy to focus on more value - added activities.The risk of error or '
                    'audit finding will be reduced. Users can use configuration files to cover multiple business '
                    'lines. The automated tool uses the OCRPortal activity to extract information from PDFs.',
     'module': 'RDA, PDF, Browser, UI Automation, eCFM'},
    {'name': 'Custody JPSS_GTM Trade Blotter Report',
     'description': 'The process of this RDA primarily encompasses downloading trade blotter file from GTM and saving '
                    'to daily task folder, doing general review of trade blotter file,doing checking against Mch/MYSS '
                    'data and make updates. The automated tool uses the method of invoking the OSA service instead of '
                    'Capturing data from the MCH through UMAS.',
     'module': 'RDA, GTM, Browser, UI Automation, MCH, MYSS, OSA'},
    {'name': 'AXA Collateral Reports Solution',
     'description': 'Its for collateral team which require send daily/weekly/monthly collateral report to AXA client '
                    'via email and the source data file is download from AXA citrix manually.This process will filter '
                    'required data from source file based on the inventory file, change values for some fields, '
                    'add password to protected the final report...draft mail with the report.',
     'module': 'RDA, AXA, citrix, Outlook, Browser, UI Automation, Excel'},
    {'name': 'West Lake Daily Report',
     'description': 'West Lake is an online reporting application and contains APAC OKRI and Client View two '
                    'dashboard to display manage reporting and client performance on accounting, custody, '
                    'failed trade and other ss service.It takes hours to manually prepare raw data for West Lake '
                    ' reports from shared folder, website, email, attachment and online box folder.',
     'module': 'RDA, West Lake, Browser, UI Automation, outlook, Excel'},
    {'name': 'HKE Price Download Upload ',
     'description': 'The process instead of manually completing the tasks of downloading source price from EPW, '
                    'calculating prices, and uploading reports to EPw, through this automation, business team can '
                    'save 30 mins every day.',
     'module': 'RDA, EPW, Browser, UI Automation'},
    {'name': 'SP Multiple Rate Update Automation',
     'description': 'Hangzhou Security Valuation team has 6 daily tasks to read from email body and attachments, '
                    'and update rates into MCH by 86_bexr_browse.xlsm and 169_ufwd_browse_book.xlsm. The process 100% '
                    'automate all tasks.Through RDA automation, business team can save 167 hours every year.',
     'module': 'RDA, Outlook, Macro, Excel, UI Automation, MCH'},
    {
        'name': 'UAT Regression Report Recon',
        'description': 'This process mainly realizes the function of comparing files instead of using Compare Tool '
                       'manually. The number of files is 2000+, so every time you use this robot, you can save at '
                       'least 8 hours for the business team.',
        'module': 'RDA, Desktop Application, Compare Tool, UI Automation'},
    {'name': 'JPB Monthly SD Holding Report',
     'description': 'provide all the securities position on settlement date as of last month end on monthly basis',
     'module': 'Alteryx, Excel, Macro, VBA'},
    {'name': 'FRS Currency Breakdown - FSDF',
     'description': 'Two customized reports are required to be delivered to client on monthly basis to show detailed '
                    'breakdown on Realized FX Gain/Loss and Translation Gain/Loss based on currency level for 9 funds.',
     'module': 'Alteryx, Excel, Macro, Python, VBA'},
    {'name': 'Customized Reporting -JPGC - Nippon Life Dividend Received Report',
     'description': 'Provide tax reclaim received report on daily basis',
     'module': 'Alteryx, Excel, Macro, Python, VBA'},
    {'name': 'Open Trade Check Automation',
     'description': 'Validate and provide comments for all open trades on custody and accounting side on daily basis',
     'module': 'Alteryx, Excel, Macro, VBA'},
    {'name': 'JtsB Bond Interest Report',
     'description': 'Bond Interest Report is a daily task by Japan GC team for JTSB client. This demand is to help BU '
                    'automatically audit the interest and principal of Bond trade which are processed by HCL team.',
     'module': 'Alteryx, Excel, Macro, Python, VBA'},
    {'name': 'JTSB/MTBJ Failed & Unmatched Trade',
     'description': 'Provide overall real time custody failed and unmatched trade reports to client service and hk '
                    'Transaction processing so that they could take proper actions accordingly.',
     'module': 'Alteryx, Excel, Macro'},
    {'name': 'JTSB Security Lending Report',
     'description': 'Provide client repont for daily loan transactions for stock funds',
     'module': 'Alteryx, Excel, Macro, Python, VBA'},
    {'name': 'JTSB Contractual Settlement Check',
     'description': 'To ensure both cash and share of all trades are properly settled on MCH as per contractual'
                    'settlement policy or non-contractual settlement policy. For which not apply contractual '
                    'settlement policy, user need to investigate reason and create report accordingly',
     'module': 'Alteryx, Excel, Macro, Python, VBA'},
    {'name': 'JTSB Corp Action Cash Settlement Report',
     'description': 'Provide the cash line for Corp Action event to client on a daily basis.',
     'module': 'Alteryx, Excel, Macro, Python, VBA'},
    {'name': 'Customized Reporting- JPGC - JTSB Net Amount Different check report',
     'description': 'To help BU automatically find the list of trades with on-book currencies that have difference '
                    'between contractual settlement amount and actual settlement amount.',
     'module': 'Alteryx, Excel, Macro, VBA'},
    {'name': 'Weekly Unpriced Stale Report',
     'description': 'The automation processes the medium-sized dataset and automate the comments for exceptions to '
                    'eliminate the manual work. It has optimized data processing, leading to faster insights, '
                    'improved accuracy. This achievement demonstrates the power of python automation.',
     'module': 'Python, Excel, Macro, Data Processing'},
    {'name': 'Failed Trade Report Solution',
     'description': 'The automation assists on failed trade checking and notification. It generates 100+ notification '
                    'reports every month to let operation team focus on value-added work.',
     'module': 'Python, Data Processing, Generate Reports'},
    {'name': 'CA Calculation Template',
     'description': 'The automation captures 14 Corporate Event to execute validation. It takes 10 seconds for each '
                    'event against 15 minutes for each event manually.',
     'module': 'Python, Capture Corporate Even, Validation'},
    {'name': 'Income Repatriation Transaction Report',
     'description': 'This is a bespoke report required by client. The automation comments the exception based on '
                    'business rule line by line. It allows the client service team focus on the audit process.',
     'module': 'Python, Comments Exception, Generate Reports'},
    {'name': 'Broker Statement Reconciliation',
     'description': 'This automation extracts transaction data from broker statement and reconciliate against that '
                    'from client perspective.',
     'module': 'Python, Extract Data, Data Processing'},
    {'name': 'Client Health Check',
     'description': 'This automation checks various indicators to validate the healthy status for client. It is able'
                    'to onboarding new client with the configuration and provides the whole picture for each client.',
     'module': 'Python, Various Indicators, Onboarding client'},
]

workflow_module = ['Extract', 'RDA', 'Alteryx', 'Python', 'Report']


def parse_aiml_template(result):
    lines = result.lstrip().rstrip(" ").split(' _newline')
    is_image = any('imageUrls' in line for line in lines)
    image_urls = []
    text = []
    if is_image:
        text.append(lines[0].lstrip().rstrip(" "))
        for line in lines[1:]:
            if line.lstrip().rstrip(" ").startswith('url'):
                image_url = line.lstrip().rstrip(" ").replace('url ', '').replace(' /url', '')
                print("image_url", image_url)
                image_urls.append(image_url)
    else:
        for line in lines[0:]:
            text.append(line.lstrip().rstrip(" ").replace('url ', '').replace(' /url', ''))

    respone = {
        'result': text,
        'isImage': is_image
    }

    if is_image:
        respone['imageUrls'] = image_urls

    return respone


def readexcel(file_name):
    try:
        # initiz
        xls = pd.ExcelFile(file_name)
        sheet_names = xls.sheet_names
        df = pd.read_excel(file_name, sheet_name=sheet_names[0])
        json_data = df.to_json(orient='records', indent=None)

        return json_data
    except FileNotFoundError:
        return jsonify({'error': "file '{file_name}' is not existed."})
    except Exception as e:
        return jsonify({'error': str(e)})


def readDelimiter(file_name):
    delimiters = [',', ';', '|', '\t']
    try:
        with open(file_name, 'r') as file:
            content = file.read()
            # first get frency to decide the delimiter
        delimiter_frequency = {delimiter: 0 for delimiter in delimiters}

        for char in content:
            if char in delimiter_frequency:
                delimiter_frequency[char] += 1

        most_common_char = max(delimiter_frequency, key=delimiter_frequency.get)
        delimiter = most_common_char

        # read csv data and convert to json data
        data = []
        with open(file_name, 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
            for row in csv_reader:
                data.append(row)

        json_data = json.dumps(data, indent=None)
        return jsonify({"success": "true", "data": json_data})
        # return  json_data
    except FileNotFoundError:
        return jsonify({'error': "file '{file_name}' is not existed."})
    except Exception as e:
        return jsonify({'error': str(e)})


def readImage(file_name):
    try:
        # key and endpoint
        # subscription_key = "a1f6fe5112aa4c8b9e828c9dc021a04c"
        # endpoint = "https://computervision187.cognitiveservices.azure.com/"
        # use company one
        subscription_key = "47d9313c1bfb4d35bc2cb8fc6243b85"
        endpoint = "https://computervision18777.cognitiveservices.azure.com/"

        # init credential and build up client
        credentials = CognitiveServicesCredentials(subscription_key)
        computervision_client = ComputerVisionClient(endpoint, credentials)

        list_data = []

        # set up image stream and regonized the printed text
        with open(file_name, "rb") as image_stream:
            detect_orientation_option = {
                "detectOrientation": "true"
            }

            read_results = computervision_client.recognize_printed_text_in_stream(image_stream,
                                                                                  textRecognitionLanguage="en",
                                                                                  detect_orientation="true")

            # read text from image
            for region in read_results.regions:
                for line in region.lines:
                    data = ""
                    for word in line.words:
                        data += word.text + ","
                    if data:
                        data = data[:-1]
                    list_data.append(data)

        return list_data
    except Exception as e:
        jsonify({'error': str(e)})


@app.route('/', methods=['POST'])
def process_request():
    data = request.json
    query_data = data.get('query')
    print('query_data', query_data)
    bot = ChatBot()
    result = bot.response(query_data)
    if isinstance(result, dict):
        response_data = result
    else:
        response_data = parse_aiml_template(result)

    response = jsonify(response_data)
    origin = request.headers.get('Origin')

    allowed_domains = [
        'http://localhost:3000',
        # ...添加其他允许的域名
    ]

    if origin in allowed_domains:
        response.headers['Access-Control-Allow-Origin'] = origin
        return response
    else:
        return jsonify({'error': 'Origin not allowed'}), 403

    return response


@app.route('/execute-robot', methods=['POST'])
def execute_robot():
    data = request.get_json()
    selected_value = data.get('selectedValue', 'default_value')
    print('selected_value', selected_value)
    command = [
        'C:\\Users\\azureuser\\AppData\\Local\\Programs\\UiPath\\Studio\\UiRobot.exe',
        '-f', selected_value
    ]

    try:
        result = subprocess.check_output(command, universal_newlines=True)
        print('Robot execution result: ', result)
        return jsonify(result=True)
    except subprocess.CalledProcessError as e:
        print('Error executing robot: ', e)
        return jsonify(result=False)


@app.route('/suggest-solution', methods=['GET'])
def get_data():
    originText = request.args.get('text', '')
    text = unquote(originText)
    matches = []

    for item in data:
        module = item['module']
        module_keywords = [keyword.strip().lower() for keyword in module.split(',')]
        text = text.lower()
        match_count = sum(1 for keyword in module_keywords if keyword in text)

        if match_count > 0:
            matches.append({'name': item['name'], 'description': item['description'], 'match_count': match_count})

    sorted_matches = sorted(matches, key=lambda x: x['match_count'], reverse=True)

    top_file_matches = sorted_matches[:5]

    return jsonify(top_file_matches)


@app.route('/initial-workflow', methods=['GET'])
def initial_workflow():
    result = {}
    originText = request.args.get('text', '')
    text = unquote(originText)
    content_lower = text.lower()

    specific_modules = ['RDA', 'Alteryx', 'Python']
    non_specific_modules = ['Extract', 'Report']

    # 找到所有specific_modules在content中的位置
    positions = [(solution_module, content_lower.index(solution_module.lower())) for solution_module in specific_modules
                 if solution_module.lower() in content_lower]
    positions.append((None, len(content_lower)))  # 添加文本结尾位置

    for i in range(len(positions) - 1):
        solution_module, start_index = positions[i]
        _, end_index = positions[i + 1]

        search_scope = content_lower[start_index:end_index]

        if 'name' in search_scope or '名字' in search_scope:
            # 获取匹配度最高的name
            best_match = None
            max_match_length = 0
            for item in data:
                matches = [m.group() for m in re.finditer(item['name'].lower(), search_scope)]
                if matches:
                    total_length = sum([len(match) for match in matches])
                    if total_length > max_match_length:
                        max_match_length = total_length
                        best_match = item['name']
            if best_match:
                result[solution_module] = best_match
        elif 'modules' in search_scope or '模块' in search_scope:
            # 获取匹配度最高的module
            best_match = None
            max_match_length = 0
            for item in data:
                for mod in item['module'].split(','):
                    matches = [m.group() for m in re.finditer(mod.lower().strip(), search_scope)]
                    if matches:
                        total_length = sum([len(match) for match in matches])
                        if total_length > max_match_length:
                            max_match_length = total_length
                            best_match = item['name']
            if best_match:
                result[solution_module] = best_match
        else:
            result[solution_module] = ""

    # 对于non_specific_modules
    for module in non_specific_modules:
        if module.lower() in content_lower:
            result[module] = ""

    return json.dumps(result, ensure_ascii=False)


@app.route('/compareFile', methods=['GET'])
def compareFileMethod():
    try:
        # data = request.json
        # replace with the value from front end
        file1 = "c:/test/src.xlsx"
        file2 = "c:/test/tar.xlsx"
        outputFileName = "diff.xlsx"

        # First upload these two files into blob
        # Connection and container string for build up blob client
        connection_string = "DefaultEndpointsProtocol=https;AccountName=hackathon2023187;AccountKey=F6yr7LNQKJFnpv3KSmLj8E8otFaoPD4UOKdVMTmgPU5RUVnem+LOTs3G2qQm2Fkx8XttLDbR0pFa+AStxjnDZw==;EndpointSuffix=core.windows.net"
        container_name = "sina187"
        src_blob_name = os.path.basename(file1)
        tar_blob_name = os.path.basename(file2)

        # Create a BlobServiceClient using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(container_name)

        # Create a blob client and upload the local file
        src_blob_client = container_client.get_blob_client(src_blob_name)
        tar_blob_client = container_client.get_blob_client(tar_blob_name)

        with open(file1, "rb") as data:
            src_blob_client.upload_blob(data, overwrite=True)

        with open(file2, "rb") as data:
            tar_blob_client.upload_blob(data, overwrite=True)

        # Azure Function' URL
        function_url = "https://comparefunctionjava.azurewebsites.net/api/CompareFunction?"

        request_body = {
            "outputFileName": outputFileName
        }

        # Post the data to trigger the function
        response = requests.post(function_url, json=request_body)

        if response.status_code == 200:
            logging.info("Azure Function call successfully")

        else:
            logging.info("Azure Function call failure and status ok is ", response.status_code)
            logging.info(response.text)

            # Download blob file to local
        output_blob_client = container_client.get_blob_client(outputFileName)
        local_file_path = "c:/test/" + outputFileName
        with open(local_file_path, "wb") as my_blob:
            blob_data = output_blob_client.download_blob()
            my_blob.write(blob_data.readall())

        df = pd.read_excel(local_file_path, sheet_name='Sheet1')
        json_data = df.to_json(orient='records', indent=4)

        return jsonify({'success': "true", "data": json_data})

    except FileNotFoundError:
        return jsonify({'error': "file '{file_name}' is not existed."})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/readData', methods=['GET'])
def readData():
    try:
        file_extension_functions = {
            'xlsx': readexcel,
            'txt': readDelimiter,
            'png': readImage,
        }

        # gonna replace the value return from frontend
        file_names = ['c:/test/excelData.xlsx', 'c:/test/delimiterDatabyComma.txt', 'c:/test/imageData.png']
        logging.info("received files " + file_names)

        data = {}
        count = 0
        for file_name in file_names:
            # get file extension
            file_extension = file_name.split('.')[-1]
            content = ""
            if file_extension in file_extension_functions:
                content = file_extension_functions[file_extension](file_name)
                data[file_name] = content
                count += 1
            else:
                content = "extension of this file format is not developed"
                data[file_name] = content

        logging.info("parse " + count + " files successfully")
        return data

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
