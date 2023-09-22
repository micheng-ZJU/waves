import requests


def search_duckduckgo(query):
    endpoint = "https://api.duckduckgo.com/"

    # API的参数
    params = {
        'q': query,
        'format': 'json',
        'pretty': 1,
        'no_html': 1
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    # 收集查询结果
    results = []

    # 从"Results"部分获取答案
    for r in data['Results']:
        title = r.get('Result', '').split(">")[1].split("<")[0]  # 这个用于提取Result中的标题
        results.append(title)

    # 如果Results部分没有足够的答案，那么从"Abstract"部分获取答案
    if data.get('AbstractText'):
        results.append(data['AbstractText'])

    return results[2:7]


def results_to_string(query):
    results = search_duckduckgo(query)
    # 拼接所有结果
    return ". ".join(results) + "."
