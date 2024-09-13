from pyecharts import options as opts  
from pyecharts.components import Table, Image
from pyecharts.charts import Bar, Pie, Line, HeatMap, Funnel, Gauge, Grid, Page, Tab
from pyecharts.options import ComponentTitleOpts 
import pandas as pd
from datetime import datetime, timedelta
import requests  
from requests.auth import HTTPBasicAuth  
import json
import base64
import os  
import sys
import subprocess  
  
# 参数设置
pd.set_option('display.expand_frame_repr',False) # False不允许换行
pd.set_option('display.max_rows', 100) # 显示的最大行数
pd.set_option('display.max_columns', 8) # 显示的最大列数
pd.set_option('display.precision', 2) # 显示小数点后的位数

def generate_table_html(df_data, title):
	# 获取列名（表头）  
	header = list(df_data.columns)  
	# 将 DataFrame 的每一行转换为列表，并确保数据类型为字符串  
	rows = [list(map(str, row)) for _, row in df_data.iterrows()]  
	
	table = Table()
	table.add(header, rows)
	table.set_global_opts(
		title_opts=ComponentTitleOpts(title=title) 
	)
	return table
	
def scan_folder_file(path):
	for dirpath, dirnames, filenames in os.walk(path):  
		print(f"当前目录: {dirpath}")  
		for dirname in dirnames:  
			print(f"子目录: {dirname}")  
		for filename in filenames:  
			 print(f"文件: {filename}")  
					
# generate workitems list
if True:
	# 查看根目录下文件
	scan_folder_file("/home/vsts/work/1/s")
					
	# 获取脚本文件所在的目录  
	script_dir = os.path.dirname(os.path.abspath(__file__))  

	# 打印脚本文件所在的目录  
	print("脚本所在目录是:", script_dir)
	
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
	
	# Azure DevOps组织URL（注意替换为你的组织名）  
	organization_url = sys.argv[1]
	# 你的个人访问令牌（PAT），请确保不要在代码库中直接暴露它  
	# 为了安全起见，最好使用环境变量或加密的存储来管理PAT  
	personal_access_token = sys.argv[3]
	
	# Azure DevOps项目的名称  
	project_name = sys.argv[2]
	
	# Azure DevOps REST API版本  
	api_version = "6.0"  
	
	DEF_TYPE = "Bug"
	
	if DEF_TYPE == "Bug":
		useful_info = {"id": "id",
						"rev": "rev",
						"System.WorkItemType": "Work Item Type",
						"System.State": "State",
						"System.IterationPath": "Iteration Path",	
						"System.AreaPath": "Area Path",		
						"System.CreatedBy._.displayName": "Created By",
						"System.CreatedDate": "Created Date",	
						"System.AssignedTo._.uniqueName": "Assigned To",		
						"System.Title": "Title",	
						"Microsoft.VSTS.Scheduling.Effort": "Effort",		
						"System.Tags": "Tags",	
						"System.Description": "Description",
						"System.ChangedBy._.displayName": "Changed By",
						"Microsoft.VSTS.Common.ClosedDate": "Closed Date",
						"Microsoft.VSTS.Common.ClosedBy._.displayName": "Closed By",
						"Microsoft.VSTS.Common.ActivatedDate": "Activated Date",
						"Microsoft.VSTS.Common.ActivatedBy._.displayName": "Activated By"
					
					}
	elif DEF_TYPE == 'Epic_Feature':
		# Target Date 
		# Start Date
		# Target System Release
		# Definition of Ready
		# Definition of Done
		# Acceptance Criteria
		# Parent
		useful_info = {"id": "id",
						"rev": "rev",
						"System.WorkItemType": "Work Item Type",
						"System.State": "State",
						"System.IterationPath": "Iteration Path",	
						"System.AreaPath": "Area Path",		
						"System.Reason": "Reason", 
						"Microsoft.VSTS.Common.Severity": "Severity",
						"Custom.ScopeBug": "ScopeBug",
						"Custom.Cloned": "Cloned",
						"Custom.HowFound": "HowFound",
						"System.CreatedBy._.displayName": "Created By",
						"System.CreatedDate": "Created Date",	
						"System.AssignedTo._.uniqueName": "Assigned To",		
						"System.Title": "Title",	
						"System.Tags": "Tags",	
						"System.Description": "Description",
						"System.ChangedBy._.displayName": "Changed By",
						"Microsoft.VSTS.Common.ClosedDate": "Closed Date",
						"Microsoft.VSTS.Common.ClosedBy._.displayName": "Closed By",
						"Microsoft.VSTS.Common.ActivatedDate": "Activated Date",
						"Microsoft.VSTS.Common.ActivatedBy._.displayName": "Activated By",
						"Microsoft.VSTS.Scheduling.Effort": "Effort"
					}
	else:
		useful_info = {}
	
	def flatten_dict(d, parent_key='', sep='_'):  
		"""  
		将嵌套字典扁平化为一个列表的键值对。  
	
		参数:  
		d -- 要扁平化的字典。  
		parent_key -- 用于构建键名的父键（递归时使用）。  
		sep -- 用于分隔键名级别的分隔符。  
	
		返回:  
		一个列表，包含扁平化后的键值对。  
		"""  
		items = []  
		for k, v in d.items():  
			new_key = parent_key + "." +sep + "." + k if parent_key else k  
			if isinstance(v, dict):  
				items.extend(flatten_dict(v, new_key, sep=sep).items())  
			else:  
				items.append((new_key, v))  
		return dict(items)  
	
	def get_project_id(name="PCP"):
	
		# 将PAT添加到HTTP请求的Authorization头中  
		encoded_creds = base64.b64encode(f":{personal_access_token}".encode()).decode()  
	
		# 将编码后的字符串添加到HTTP请求的Authorization头中  
		headers = {  
			'Authorization': f'Basic {encoded_creds}'  
		} 
		# API版本  
		api_version = "6.0"  
		
		# 发送GET请求以获取所有项目  
		projects_url = f"{organization_url}/_apis/projects?api-version={api_version}"  
		response = requests.get(projects_url, headers=headers)  
		
		# 检查响应状态码  
		if response.status_code == 200:  
			# 解析JSON响应  
			projects = response.json()  
			print("Available Projects:")  
			for project in projects['value']:  
				print(f"ID: {project['id']}, Name: {project['name']}, Description: {project['description']}")  
				if project['name'] == name:
					return project['id']
		else:  
			print(f"Error fetching projects: {response.status_code}, {response.text}")
	
		return "error"
	
	def query_workitems(area_path, ql_str):
	
		# Azure DevOps项目的名称  
		project_name = get_project_id("PCP") #"PCP-Test"  
		print(project_name)
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
			df_total = pd.DataFrame()
			for work_item in work_items:  
				print("第一级:", work_item)
				# 构造获取工作项详情的URL  
				#print(work_item['url'].split("/")[-1])				  
				wiql_url = f'{organization_url}/{project_name}/_apis/wit/workItems/{work_item["url"].split("/")[-1]}'  
				# 创建头部信息  
				encoded_credentials = base64.b64encode(f":{personal_access_token}".encode('ascii')).decode('ascii')  
	
				headers = {  
					'Authorization': f'Basic {encoded_credentials}',  
					'Content-Type': 'application/json'  
				}  
				#print(wiql_url)
				response = requests.get(wiql_url, headers=headers) 
				# 检查响应状态码  
				if response.status_code == 200:  
					# 解析响应内容  
					work_item = response.json()  
					# 打印工作项的详细信息  
					info = json.dumps(work_item, indent=4) 
					print(info)
	
					# 扁平化嵌套字典  
					work_item["fields"]["id"] = work_item["id"]
					work_item["fields"]["rev"] = work_item["rev"]
					flat_dict = flatten_dict(work_item["fields"])  
	
					# 将扁平化后的字典转换为DataFrame  
					df = pd.DataFrame.from_dict(flat_dict, orient='index').reset_index()
					df = df.set_index('index').T  
					df_total = pd.concat([df_total, df], ignore_index=True)
				else:  
					print(f"Failed to retrieve work item details. Status code: {response.status_code}")  
					print(f"Response content:\n{response.text}")  
	
			target_list = list(useful_info.keys())
			for col in target_list:
				if col not in df_total.columns:
					useful_info.pop(col)
	
			df_total = df_total.loc[:, list(useful_info.keys())]
			df_total = df_total.loc[:, list(useful_info.keys())]
			df_total = df_total.rename(columns=useful_info)  
			df_total = df_total.loc[df_total['Area Path'].isin([area_path])]
			df_total.to_csv(f'{script_dir }/output-{DEF_TYPE}.csv', index=False) 
			print(df_total)

			scan_folder_file(script_dir)
			
			# 假设CSV文件已经由Python脚本生成，并且位于当前工作目录下  
			csv_file = f'output-{DEF_TYPE}.csv'
			# csv_file = f'requirements.txt'
			  
			# Git命令将在这个目录下执行，切换到Git仓库的目录（如果当前工作目录不是Git仓库的根目录）  
			os.chdir(script_dir)  
			
			result = subprocess.run(['git', 'log', '--oneline', '-n', '5'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  
			print(569, result.stdout)  

			result = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True, check=True)  
			# 打印命令的输出结果  
			print(result.stdout)  
			
			subprocess.run(['git', 'push', 'origin', 'CI-project'], check=True)  
			# 执行命令并获取结果  
			result = subprocess.run(['git', 'status'], capture_output=True, text=True, check=True)  
			print(123, result.stdout)  
			# 添加CSV文件到暂存区  
			subprocess.run(['git', 'add', csv_file], check=True)  
			result = subprocess.run(['git', 'status'], capture_output=True, text=True, check=True)  
			print(234, result.stdout)  

			subprocess.run(['git', 'checkout', '-b', 'CI-Files-Store'], check=True)  
			result = subprocess.run(['git', 'status'], capture_output=True, text=True, check=True)  
			print(666, result.stdout) 
			
			# 提交更改到本地仓库  
			subprocess.run(['git', 'commit', '-m', 'Add CSV file: ' + csv_file], check=True)  
			result = subprocess.run(['git', 'status'], capture_output=True, text=True, check=True)  
			print(567, result.stdout) 
			# 如果需要，将更改推送到GitHub的远程仓库  
			# 替换'origin'为你的远程仓库名称，'main'或'master'或你的分支名为目标分支  
			# subprocess.run(['git', 'push', 'origin', 'main'], check=True)  # 根据实际情况调整分支名  
			  
			print('CSV文件已成功添加到Git仓库并推送到远程。')
		else:  
			print(f"Failed to retrieve work items. Status code: {response.status_code}, Error: {response.text}")
	
	def compare_feature_epic_state(baseline_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\NGT Engineering 7.0 lifecycle&readiness baseline M2.csv", 
						   current_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\7.0 CMS Feature 05312024.csv"
						   ):
		df_current = pd.read_csv(current_path)
		#####################################################################################################
		# epics
		define_type = ["Feature", "Epic"] 
	
		for key in define_type:
	
			df_latest = df_current.loc[(df_current["Work Item Type"] == key) & (df_current["State"] == "Closed")]
	
			# 将时间列转换为datetime类型  
			df_latest['Closed Date'] = df_latest['Closed Date'].apply(lambda x: x.split('T')[0])  
			df_latest['Closed Date'] = pd.to_datetime(df_latest['Closed Date'])
			# 使用.dt.strftime()将datetime对象格式化为仅包含年月日的字符串  
			df_latest['Closed Date'] = df_latest['Closed Date'].dt.strftime('%Y-%m-%d')  
			df_latest['Closed Date'] = pd.to_datetime(df_latest['Closed Date']) 
	
			# 计算当前日期减去一个月  
			one_month_ago = datetime.now() - timedelta(days=30)  
			df_latest = df_latest.loc[(df_latest["Closed Date"] >= one_month_ago) , ["id", "Title", "Work Item Type", "State", "Effort", "Area Path", "Closed Date"]]
	
			print(f"###In last month, {len(df_latest)} {key} closed with {df_latest['Effort'].sum()} manhours finished. Links to {key} closed since last STECO.")
			df_latest_md_table = df_latest.to_markdown()  
			print(df_latest_md_table)
	
			table1 = generate_table_html(df_latest, "Is effort being 'burned' as per plan? (M3-M5)? ")
			##############################################################################################
	
			df_latest = df_current.loc[(df_current["Work Item Type"] == key)]
			df_baseline = pd.read_csv(baseline_path)
			df_baseline = df_baseline.rename(columns={'ID':'id'})  
	
			data_latest = df_latest.loc[df_latest["Work Item Type"] == key, ["id", "Title", "State", "Effort", "Area Path", "Iteration Path"]]
			data_baseline = df_baseline.loc[df_baseline["Work Item Type"] == key, ["id", "Title", "State", "Effort", "Area Path", "Iteration Path"]]
	
			# 当发现ID是object时候单独处理成int
			data_baseline = data_baseline.dropna(subset=['id'])
			data_baseline["id"] = data_baseline["id"].astype(int) 
	
			# 找出新增的行（在data_latest中但不在data_baseline中）  
			new_rows = data_latest[~data_latest['id'].isin(data_baseline['id'])]  
			new_rows = new_rows.sort_values(by='Effort')  
			# 哪些行包含NaN值  
			new_rows_nan = new_rows[new_rows["Effort"].isnull()] # 新增包含NaN值
			# 哪些行不包含NaN值  
			new_rows_notnan = new_rows[new_rows["Effort"].notnull()] # 新增不包含NaN值
	
			print(f"Compared last STECO, {new_rows.shape[0]} new {key} added with {new_rows_notnan['Effort'].sum()} manhours increased. Link to increased Features\n")
			df_new_rows_md_table = new_rows.to_markdown()  
			print(df_new_rows_md_table)
	
			# 找出被筛除的行（在data_baseline中但不在data_latest中）  
			# removed_rows = data_baseline[~data_baseline['ID'].isin(data_latest['ID'])]  
			# print("removed rows:\n", removed_rows)  
	
			# 找出有变化的行（合并两个DataFrame并比较值）  
			merged = pd.merge(data_baseline, data_latest, on='id', suffixes=('_old', '_new'), how='outer')  
			changed_rows = merged[(~(merged['Effort_old'] == merged['Effort_new'])) & (merged["Effort_old"].notnull())]  
			print(f"{key} changed rows:\n", changed_rows)
	
			# convert to the html table display
			# 创建 Table 组件  
			include_result0 = generate_table_html(new_rows, f"Have {key} been added to the scope since last STECO? (M10)({len(new_rows)} {key} added, with {new_rows['Effort'].sum()} manhours (effort) in total)")
			include_result1 = generate_table_html(changed_rows, f"Has {key} effort increased since last STECO? (M3-M5) ({key} added {len(new_rows)} , {new_rows_notnan['Effort'].sum()} manhours increased, including {len(new_rows_nan)} without estimation)")
	
		#####################################################################################################
	
		# 创建一个图片组件
		image = Image()
		# 添加图片，参数依次为图片路径，图片宽度，图片高度
		image.add("C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\GetImage.png")
	
		df_empty = pd.DataFrame()
		table4_1 = generate_table_html(df_empty, "Is Static Code Analysis being applied as per expectations? (M19)\nPlease refer to SonarQube test report or dashboard. Add link if possible.")
		table4_2 = generate_table_html(df_empty, "Are fixes being applied to Static Code Analysis Findings? (M20)\nPlease refer to SonarQube test report or dashboard. Add link if possible.")
	
		page = (
			Page(layout=Page.DraggablePageLayout)
			.add(
				table1,
				include_result0,
				include_result1,
				table4_1,
				table4_2,
				image)
		)
		# 设置标题
		page.render("Development_Status_Demo.html")  # 生成HTML文件
	
	def compare_bugs(baseline_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Scope bugs 7.0&xP0 M2 Baseline.csv", 
				  introduced_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Introduced bugs 7.0_05312024.csv", 
					current_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Scope bugs 7.0_05312024.csv"):# Bugs 
	
		df_latest = pd.read_csv(current_path)
		df_baseline = pd.read_csv(baseline_path)
	
		data_latest = df_latest.loc[:, ["id", "Title",  "State", "Area Path", "Iteration Path"]]
		data_baseline = df_baseline.loc[:, ["ID", "Title",  "State", "Area Path"]]
		data_baseline = data_baseline.rename(columns={'ID':'id'})  
	
		# 找出新增的行（在data_latest中但不在data_baseline中）  
		new_rows = data_latest[~data_latest['id'].isin(data_baseline['id'])]  
		#print("new rows:\n", new_rows)
		table1 = generate_table_html(new_rows, "Have scope bugs been added to the release since last STECO? (M11)")
	
		df_introduced = pd.read_csv(introduced_path)
		data_introduced = df_introduced.loc[df_introduced["ScopeBug"] == 0, ["ID", "Title", "Severity", "ScopeBug", "State", "Area Path", "Iteration Path", "Created Date"]]
		data_introduced['Created Date'] = pd.to_datetime(data_introduced['Created Date'])  
	
		# 计算当前日期减去一个月  
		one_month_ago = datetime.now() - timedelta(days=30)  
		df_new_introduced = data_introduced.loc[(data_introduced["State"] != "Closed") & (data_introduced["Created Date"] <= one_month_ago) , ["ID", "Title", "Severity", "ScopeBug", "State", "Area Path", "Iteration Path", "Created Date"]]
		table2 = generate_table_html(df_new_introduced, "Is the backlog for introduced bugs increasing or are they being fixed in a timely manner (within the sprints)? (M8)")
	
		df_new_introduced_high = data_introduced.loc[(data_introduced["State"] != "Closed") & (data_introduced["Severity"] == "2 - High") & (data_introduced["Created Date"] <= one_month_ago) , ["ID", "Title", "Severity", "ScopeBug", "State", "Area Path", "Iteration Path", "Created Date"]]
		table3 = generate_table_html(df_new_introduced_high, "Has the number of critical and high bugs not fixed increased since last STECO? (M14)")
	
		print(f"Since last STECO, {len(df_new_introduced)} new critical, {len(df_new_introduced_high)} new high bugs added.\n")
		df_new_introduced_md_table = df_new_introduced.to_markdown()  
		print(df_new_introduced_md_table)
		df_new_introduced_high_md_table = df_new_introduced_high.to_markdown()  
		print(df_new_introduced_high_md_table)
	
		# 创建一个图片组件
		image = Image()
		# 添加图片，参数依次为图片路径，图片宽度，图片高度
		image.add("C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\GetImage1.png")
	
		page = (
			Page(layout=Page.DraggablePageLayout)
			.add(
				table1,
				table2,
				table3,
				image)
		)
		page.render("Bug_Status_Demo.html")  # 生成HTML文件
	
	
	# 构造WIQL查询以获取Epic和Feature的基本信息  
	#"PCP\\Operations\\NextGenHMI\\Certificate Management\\2.0\\2.0.0"
	#"PCP\\Operations\\NextGenHMI\\Operations Client\\3.0\\3.0.0"
	#"PCP\\Operations\\NextGenHMI\\Deploy Tool Components\\1.0\\1.0.0"
	#"PCP\\Operations\\NextGenHMI\\Configuration Manager\\1.0\\1.0.0"
	area_path = "PCP\\Operations\\NextGenHMI\\Operations Client\\3.0\\3.0.0"
	# 'PCP\\\\Operations\\\\NextGenHMI\\\\Certificate Management\\\\2.0\\\\2.0.0'
	# 'PCP\\\\Operations\\\\NextGenHMI\\\\Operations Client\\\\3.0\\\\3.0.0'
	# 'PCP\\\\Operations\\\\NextGenHMI\\\\Deploy Tool Components\\\\1.0\\\\1.0.0'
	# 'PCP\\\\Operations\\\\NextGenHMI\\\\Configuration Manager\\\\1.0\\\\1.0.0'
	ql_path = 'PCP\\\\Operations\\\\NextGenHMI\\\\Operations Client\\\\3.0\\\\3.0.0'
	
	if DEF_TYPE == 'Bug':
		ql_str = """
		{
			"query": "SELECT [System.Id], [System.WorkItemType], [System.Title], [System.State], [System.AreaPath] FROM WorkItems WHERE [System.WorkItemType] IN ('Bug') AND [System.AreaPath] UNDER 'PCP\\\\Operations\\\\NextGenHMI\\\\Operations Client\\\\3.0\\\\3.0.0' ORDER BY [System.Id] DESC"
		}
		"""
		query_workitems(area_path, ql_str)
	elif DEF_TYPE == 'Epic_Feature':
	
		ql_str = """
		{
			"query": "SELECT [System.Id], [System.WorkItemType], [System.Title], [System.State], [System.AreaPath] FROM WorkItems WHERE [System.WorkItemType] IN ('Epic', 'Feature') AND [System.AreaPath] UNDER 'PCP\\\\Operations\\\\NextGenHMI\\\\Operations Client\\\\3.0\\\\3.0.0' ORDER BY [System.Id] DESC"
		}
		"""
		query_workitems(area_path, ql_str)
	else:
		pass
	
	#"C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Baselines 7.0 HMI-07192024\\baseline 7.0 HMI-Feature-Epic.csv", 
	#"C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Baselines 7.0 HMI-07192024\\current output-Feature-Epic.csv"
	
	# compare_feature_epic_state(baseline_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\ALL baselines xP0 HMI - 07192024\\NGT HMI 7.0xP0 Features-Epic.csv", 
	# 					   current_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\ALL baselines xP0 HMI - 07192024\\output-Epic_Feature-Operations-Client.csv")
	
	#"C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Baselines 7.0 HMI-07192024\\Scope bugs 7.0 HMI-07192024.csv"
	#"C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Baselines 7.0 HMI-07192024\\Introduced bugs 7.0 HMI-7192024.csv"
	#"C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\Baselines 7.0 HMI-07192024\\output-Bugs.csv"
	# compare_bugs(baseline_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\ALL baselines xP0 HMI - 07192024\\Scope bugs xP0 7.0 HMI- 07192024.csv", 
	# 		  introduced_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\ALL baselines xP0 HMI - 07192024\\ALL Introduced bugs xP0 HMI - 07192024.csv",
	# 			current_path="C:\\Users\\CNJAYUA1\\Downloads\\ADO Project\\ALL baselines xP0 HMI - 07192024\\output-Bug-Operations-Client.csv")		   
