import os  
import requests  
from requests.auth import HTTPBasicAuth  
   
# 获取脚本文件所在的目录  
script_dir = os.path.dirname(os.path.abspath(__file__))  
  
# 打印脚本文件所在的目录  
print("脚本所在目录是:", script_dir)
print(12333333)

# Azure DevOps组织URL（注意替换为你的组织名）  
organization_url = "https://dev.azure.com/ABB-BCI-PCP/"  
  
# Azure DevOps项目的名称  
project_name = "PCP-Test"  
  
# Azure DevOps REST API版本  
api_version = "6.0"  
  
# 你的个人访问令牌（PAT），请确保不要在代码库中直接暴露它  
# 为了安全起见，最好使用环境变量或加密的存储来管理PAT  
personal_access_token = "Jacob-xiao.yuan@cn.abb.com"  
  
# 构造获取仓库列表的URL  
repos_url = f"{organization_url}/{project_name}/_apis/git/repositories?api-version={api_version}"  
  
# 使用个人访问令牌进行身份验证  
# 注意：Azure DevOps REST API实际上期望将PAT作为用户名，并留空密码  
authentication = HTTPBasicAuth('', personal_access_token)  
  
# 发送GET请求  
response = requests.get(repos_url, auth=authentication)  
  
# 检查响应状态码  
if response.status_code == 200:  
    # 打印仓库列表  
    repos = response.json()['value']  
    for repo in repos:  
        print(f"Repository Name: {repo['name']}, ID: {repo['id']}, URL: {repo['remoteUrl']}")  
else:  
    print(f"Failed to retrieve repositories. Status code: {response.status_code}, Error: {response.text}")
