import requests
import json
import pandas as pd
from datetime import datetime

def run_workflow(workflow_id, parameters=None, is_async=False, bot_id=None):
    """
    执行扣子工作流
    
    参数:
        workflow_id: 工作流 ID
        parameters: 工作流输入参数(字典格式)
        is_async: 是否异步执行(需要进阶版及以上)
        bot_id: Bot ID(可选)
    
    返回:
        响应结果字典
    """
    
    # API 端点
    url = "https://api.coze.cn/v1/workflow/run"
    
    # 请求头 - 请替换为你的实际 token
    headers = {
        "Authorization": "Bearer pat_NevCqPkDxQtBhYLLarQKEf1aITp3gZsWHDQ9Yiuz5nyZBFCK7zcqmm3R9o9yz8jr",  # 替换为你的实际 token
        "Content-Type": "application/json"
    }
    
    # 请求体
    payload = {
        "workflow_id": workflow_id
    }
    
    # 添加可选参数
    if parameters:
        payload["parameters"] = parameters
    
    if is_async:
        payload["is_async"] = is_async
    
    if bot_id:
        payload["bot_id"] = bot_id
    
    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, json=payload)
        
        # 解析响应
        result = response.json()
        
        # 检查响应状态
        if result.get("code") == 0:
            print("✅ 工作流执行成功!")
            print(f"执行 ID: {result.get('execute_id')}")
            print(f"调试链接: {result.get('debug_url')}")
            
            # 如果有输出数据
            if result.get("data"):
                print(f"输出结果: {result.get('data')}")
            
            return result
        else:
            print(f"❌ 工作流执行失败!")
            print(f"错误码: {result.get('code')}")
            print(f"错误信息: {result.get('msg')}")
            return result
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {str(e)}")
        return None


def save_to_excel(outputList, filename=None):
    """
    将 outputList 写入 Excel 文件
    
    参数:
        outputList: 要写入的数据列表，每个元素应该是一个字典
        filename: Excel 文件名，如果不指定则使用时间戳生成
    """
    if not outputList:
        print("⚠️ outputList 为空，无法写入 Excel")
        return
    
    # 如果没有指定文件名，使用时间戳生成
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"notes_output_{timestamp}.xlsx"
    
    # 定义字段顺序
    column_order = [
        'id',
        'bstudio_create_time',
        'user_id',
        'user_name',
        'posted_time',
        'note_title',
        'note_content',
        'liked_count',
        'comment_count',
        'share_count',
        'collect_count'
    ]
    
    try:
        # 将列表转换为 DataFrame
        df = pd.DataFrame(outputList)
        
        # 筛选并按照指定顺序排列列
        # 只保留存在的列，并按照 column_order 的顺序排列
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # 写入 Excel 文件
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"✅ 数据已成功写入 Excel 文件: {filename}")
        print(f"   共写入 {len(outputList)} 条记录")
        print(f"   字段: {', '.join(df.columns.tolist())}")
        
        return filename
    except Exception as e:
        print(f"❌ 写入 Excel 文件失败: {str(e)}")
        return None


def export_notes_to_excel(workflow_id, note_count, user_URL, user_cookie, user_name, filename=None):
    """
    导出小红书笔记数据到Excel文件

    参数:
        workflow_id: 工作流ID
        note_count: 要导出的笔记数量
        user_URL: 用户主页URL
        user_cookie: 用户Cookie
        user_name: 用户名
        filename: 输出文件名(可选)

    返回:
        {
            'success': bool,
            'filename': str,
            'record_count': int,
            'error': str
        }
    """
    try:
        # 调用工作流
        parameters = {
            "note_count": note_count,
            "user_URL": user_URL,
            "user_cookie": user_cookie,
            "user_name": user_name
        }

        result = run_workflow(workflow_id=workflow_id, parameters=parameters)

        if not result:
            return {
                'success': False,
                'filename': None,
                'record_count': 0,
                'error': '工作流调用失败'
            }

        # 检查响应状态
        if result.get("code") != 0:
            error_msg = result.get("msg", "未知错误")
            return {
                'success': False,
                'filename': None,
                'record_count': 0,
                'error': f'工作流执行失败: {error_msg}'
            }

        # 提取数据
        data = result.get("data")
        if not data:
            return {
                'success': False,
                'filename': None,
                'record_count': 0,
                'error': '工作流返回结果中没有数据'
            }

        # 解析数据
        if isinstance(data, str):
            data = json.loads(data)

        # 提取 outputList
        if isinstance(data, dict) and "outputList" in data:
            outputList = data["outputList"]
        elif isinstance(data, list):
            outputList = data
        else:
            return {
                'success': False,
                'filename': None,
                'record_count': 0,
                'error': '无法从结果中提取有效的笔记数据'
            }

        if not outputList or not isinstance(outputList, list):
            return {
                'success': False,
                'filename': None,
                'record_count': 0,
                'error': '提取的数据为空或格式不正确'
            }

        # 写入 Excel 文件
        output_filename = save_to_excel(outputList, filename)

        if output_filename:
            return {
                'success': True,
                'filename': output_filename,
                'record_count': len(outputList),
                'error': None
            }
        else:
            return {
                'success': False,
                'filename': None,
                'record_count': 0,
                'error': 'Excel文件写入失败'
            }

    except json.JSONDecodeError as e:
        return {
            'success': False,
            'filename': None,
            'record_count': 0,
            'error': f'JSON解析失败: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'filename': None,
            'record_count': 0,
            'error': f'处理过程中出错: {str(e)}'
        }


# 使用示例 1: 基本调用
if __name__ == "__main__":

    result = export_notes_to_excel(
        workflow_id="7573588596402225171",
        note_count=278,
        user_URL="https://www.xiaohongshu.com/user/profile/565a5df882718c306ecad934",
        user_cookie="abRequestId=b5058dd1-34fe-5c04-9ee5-e81a77a5d7c6; a1=193d2809a70csiom44cbhnuhn2veudhgh1tuthwhd30000165331; webId=aa551de9439151079f6edb919f040d6e; gid=yjqfJY804ixKyjqfJY8j0yxEW8SM3l644SDx9xfI7xIJh7q8d7fxk9888yK2qqy8220jD484; x-user-id-creator.xiaohongshu.com=565a5df882718c306ecad934; customerClientId=891408610260220; x-user-id-ark.xiaohongshu.com=565a5df882718c306ecad934; webBuild=4.85.1; xsecappid=xhs-pc-web; web_session=0400695c8723d5aa89627f9a2f3b4b86b5f167; acw_tc=0a4a6fd717633711654212516e61d696341b85b2aff17e0dcb374c23c7a3f2; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=25829e72-0698-4b82-a3d4-4537fde04816; unread={%22ub%22:%22690c9c6b0000000003012d26%22%2C%22ue%22:%2268fe05030000000005033bc2%22%2C%22uc%22:25}; loadts=1763372589388",
        user_name="Jing（泽雉）"
    )

    if result['success']:
        print(f"✅ 导出成功! 文件: {result['filename']}, 记录数: {result['record_count']}")
    else:
        print(f"❌ 导出失败: {result['error']}")

