import os  
import requests
from requests.auth import HTTPBasicAuth  
import json
import base64  
import sys 

# 获取脚本文件所在的目录  
script_dir = os.path.dirname(os.path.abspath(__file__))  
  
# 打印脚本文件所在的目录  
print("脚本所在目录是:", script_dir)
print(12333333)

# 检查是否有足够的参数  
if len(sys.argv) < 2:  
    print("Usage: python example.py <parameter1> [<parameter2> ...]")  
    sys.exit(1)  
  
# 打印所有参数  
print("Script name:", sys.argv[0])  
for i in range(1, len(sys.argv)):  
    print("Parameter", i, ":", sys.argv[i])

organization = sys.argv[1]
project = sys.argv[2]
query_id = sys.argv[3]

def query_workitems(ql_str):

   # Azure DevOps组织URL（注意替换为你的组织名）  
   organization_url = organization
   # Azure DevOps项目的名称  
   project_name = project 
   # 你的个人访问令牌（PAT）  
   personal_access_token = query_id 
   wiql_url = f'{organization_url}/{project_name}/_apis/wit/wiql?api-version=6.0'  

   wiql = json.loads(ql_str)
   print(wiql_url, wiql)
   # 发送POST请求以执行Wiql查询  
   headers = {  
      'Content-Type': 'application/json',  
   }  
   response = requests.post(wiql_url, headers=headers, json=wiql, auth=HTTPBasicAuth('', personal_access_token))  

   # 检查响应状态码  
   if response.status_code == 200:  
      # 解析响应内容  
      work_items = response.json()['workItems']  
      for work_item in work_items[0:50]:  
         print(work_item)
         #print(f"Work Item ID: {work_item['id']}, Title: {work_item['fields']['System.Title']}")  

         # # 构造获取工作项详情的URL  
         # #print(work_item['url'].split("/")[-1])				  
         # wiql_url = f'{organization_url}/{project_name}/_apis/wit/workItems/{work_item['url'].split("/")[-1]}'  
         # # 创建头部信息  
         # encoded_credentials = base64.b64encode(f":{personal_access_token}".encode('ascii')).decode('ascii')  

         # headers = {  
         #    'Authorization': f'Basic {encoded_credentials}',  
         #    'Content-Type': 'application/json'  
         # }  
         # #print(wiql_url)
         # response = requests.get(wiql_url, headers=headers) 
         # # 检查响应状态码  
         # if response.status_code == 200:  
         #    # 解析响应内容  
         #    work_item = response.json()  
         #    # 打印工作项的详细信息  
         #    info = json.dumps(work_item, indent=4) 
         #    #print(info)
         #    print(work_item['_links']['workItemType']['href'])

         #    response = requests.get(work_item['_links']['workItemType']['href'], headers=headers) 
         #    if response.status_code == 200:  
         #       # 解析响应内容  
         #       work_item = response.json()  
         #       info = json.dumps(work_item, indent=4) 

         #       print(work_item["transitions"])
         #       for con in work_item["states"]:
         #          print(con)
         #       print(work_item["states"])
         #       for con in work_item["states"]:
         #          print(con)
         # else:  
         #    print(f"Failed to retrieve work item details. Status code: {response.status_code}")  
         #    print("Response content:")  
         #    print(response.text)

   else:  
      print(f"Failed to retrieve work items. Status code: {response.status_code}, Error: {response.text}")

ql_str = """  
{  
   "query": "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.WorkItemType] IN ('Epic', 'Feature') ORDER BY [System.Id]"  
}  
"""  

query_workitems(ql_str)

# 构造WIQL查询以获取Epic和Feature的基本信息  
ql_str = """
{  
   "query": "Select [System.Id], [System.Title] From WorkItems Where [System.WorkItemType] = 'User Story' AND [System.State] <> 'Closed' ORDER BY [System.ChangedDate] DESC"  
} 
""" 
#query_workitems(ql_str)
