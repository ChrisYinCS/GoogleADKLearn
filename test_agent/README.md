# 纷享销客CRM集成工具 (Python版本)

## 功能说明

本工具集提供了纷享销客CRM的完整集成功能，包括：

- **认证管理** (`FxiaokeAuthManager`): 自动获取和刷新企业访问令牌
- **用户管理** (`FxiaokeUserManager`): 根据手机号获取用户信息
- **CRM对象管理** (`FxiaokeCRMClient`): 获取CRM对象列表和字段信息
- **CRM数据查询** (`FxiaokeCRMDataClient`): 查询CRM业务对象数据
- **统一服务类** (`FxiaokeCRMService`): 提供简化的统一接口

## 主要特性

- ✅ 自动认证和token管理
- ✅ 内置频率限制和重试机制
- ✅ 完整的错误处理
- ✅ 支持批量操作
- ✅ 详细的日志记录
- ✅ 模块化设计，易于扩展
- ✅ 异步支持，提高性能
- ✅ 统一的服务接口，简化使用

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 使用统一的FxiaokeCRMService类（推荐）

```python
import asyncio
from index_run import FxiaokeCRMService, generate_field_projection

async def main():
    # 配置信息
    config = {
        'appId': 'your_app_id',
        'appSecret': 'your_app_secret',
        'permanentCode': 'your_permanent_code'
    }
    
    # 创建CRM服务实例
    crm_service = FxiaokeCRMService(config)
    
    try:
        # 1. 获取用户ID
        user_id = await crm_service.get_user_id_by_mobile('13800138000')
        
        # 2. 获取所有CRM对象
        crm_objects = await crm_service.get_crm_objects(user_id)
        
        # 3. 获取指定对象的字段信息
        if crm_objects:
            object_api_name = crm_objects[0]['apiName']
            fields = await crm_service.get_object_fields(user_id, object_api_name)
            
            # 4. 生成字段投影
            field_labels = ['名称', '创建时间']  # 根据实际字段标签调整
            field_projection = generate_field_projection(fields, field_labels)
            
            # 5. 查询数据
            data = await crm_service.query_object_data(
                user_id, 
                object_api_name, 
                field_projection, 
                limit=10
            )
            
            print(f"查询到 {len(data)} 条数据")
            
    finally:
        # 清理资源
        crm_service.destroy()

# 运行
asyncio.run(main())
```

### 查看完整示例

运行 `example_usage.py` 查看详细的使用示例：

```bash
python example_usage.py
```

## 使用方法

### 1. 基本使用

```python
import asyncio
from fxiaoke_auth import FxiaokeAuthManager
from fxiaoke_user import FxiaokeUserManager

async def main():
    # 创建授权管理器
    config = {
        'appId': 'your_app_id',
        'appSecret': 'your_app_secret',
        'permanentCode': 'your_permanent_code'
    }
    
    auth_manager = FxiaokeAuthManager(config)
    user_manager = FxiaokeUserManager(auth_manager)
    
    # 根据手机号获取用户信息
    mobile = '18211565695'
    user_info = await user_manager.get_user_by_mobile(mobile)
    print('用户信息:', user_info)
    
    # 获取currentOpenUserId
    current_open_user_id = await user_manager.get_current_open_user_id(mobile)
    print('currentOpenUserId:', current_open_user_id)
    
    # 清理资源
    auth_manager.destroy()
    user_manager.destroy()

# 运行
asyncio.run(main())
```

### 2. 批量处理

```python
async def batch_example():
    auth_manager = FxiaokeAuthManager(config)
    user_manager = FxiaokeUserManager(auth_manager)
    
    mobiles = ['18211565695', '13800138000', '13900139000']
    results = await user_manager.batch_get_users_by_mobile(mobiles)
    
    for result in results:
        if result['success']:
            print(f"{result['mobile']}: 成功")
        else:
            print(f"{result['mobile']}: 失败 - {result['error']}")
    
    auth_manager.destroy()
    user_manager.destroy()
```

### 3. CRM对象查询

```python
async def crm_example():
    auth_manager = FxiaokeAuthManager(config)
    user_manager = FxiaokeUserManager(auth_manager)
    crm_client = FxiaokeCRMClient(auth_manager)
    
    # 获取用户ID
    current_open_user_id = await user_manager.get_current_open_user_id('13800138000')
    
    # 获取所有CRM对象
    crm_objects = await crm_client.get_crm_object_list_descriptions({
        'currentOpenUserId': current_open_user_id
    })
    
    for obj in crm_objects:
        print(f"对象: {obj['displayName']} ({obj['apiName']})")
    
    auth_manager.destroy()
    user_manager.destroy()
```

### 4. CRM数据查询

```python
async def crm_data_example():
    auth_manager = FxiaokeAuthManager(config)
    user_manager = FxiaokeUserManager(auth_manager)
    crm_data_client = FxiaokeCRMDataClient(auth_manager)
    
    # 获取用户ID
    current_open_user_id = await user_manager.get_current_open_user_id('13800138000')
    
    # 查询客户数据
    customer_data = await crm_data_client.find_customer_data({
        'currentOpenUserId': current_open_user_id,
        'fieldProjection': ['_id', 'name', 'mobile', 'email'],
        'searchQueryInfo': {
            'limit': 10,
            'offset': 0
        }
    })
    
    print('客户数据:', customer_data)
    
    auth_manager.destroy()
    user_manager.destroy()
```

## API接口说明

### FxiaokeAuthManager

#### get_corp_access_token()

获取企业访问令牌

**返回:**
- Dict[str, Any]: token信息字典

### FxiaokeUserManager

#### get_user_by_mobile(mobile)

根据手机号获取用户信息

**参数:**
- `mobile` (str): 手机号

**返回:**
- Dict[str, Any]: 用户信息对象

#### get_current_open_user_id(mobile)

根据手机号获取用户的currentOpenUserId

**参数:**
- `mobile` (str): 手机号

**返回:**
- str: openUserId

#### get_user_detail(mobile)

根据手机号获取用户详细信息

**参数:**
- `mobile` (str): 手机号

**返回:**
- Dict[str, Any]: 用户详细信息

#### batch_get_users_by_mobile(mobiles)

批量获取用户信息

**参数:**
- `mobiles` (List[str]): 手机号列表

**返回:**
- List[Dict[str, Any]]: 结果列表

### FxiaokeCRMClient

#### get_crm_object_list(params)

获取CRM对象列表

**参数:**
- `params` (Dict[str, Any]): 查询参数

**返回:**
- List[Dict[str, Any]]: CRM对象数组

#### get_crm_object_describe(params)

获取单个CRM对象的详细描述信息

**参数:**
- `params` (Dict[str, Any]): 查询参数

**返回:**
- Dict[str, Any]: 对象详细描述信息

### FxiaokeCRMDataClient

#### find_simple_data(params)

通用数据查询方法

**参数:**
- `params` (Dict[str, Any]): 查询参数

**返回:**
- List[Dict[str, Any]]: 数据数组

#### find_customer_data(params)

查询客户数据

**参数:**
- `params` (Dict[str, Any]): 查询参数

**返回:**
- List[Dict[str, Any]]: 客户数据列表

#### find_contact_data(params)

查询联系人数据

**参数:**
- `params` (Dict[str, Any]): 查询参数

**返回:**
- List[Dict[str, Any]]: 联系人数据列表

#### find_opportunity_data(params)

查询销售机会数据

**参数:**
- `params` (Dict[str, Any]): 查询参数

**返回:**
- List[Dict[str, Any]]: 销售机会数据列表

## 测试运行

### 运行所有测试
```bash
python index_run.py
```

### 运行特定测试
```bash
# 用户管理测试
python index_run.py user

# CRM对象测试
python index_run.py crm

# CRM数据查询测试
python index_run.py data

# 精简CRM测试
python index_run.py simple
```

## 配置说明

在使用前，请确保正确配置了以下参数：

```python
config = {
    'appId': 'your_app_id',           # 应用ID
    'appSecret': 'your_app_secret',   # 应用密钥
    'permanentCode': 'your_permanent_code'  # 永久授权码
}
```

## 频率限制

- 单接口调用限制：100次/20秒
- 总接口调用次数限制：根据购买的Open API资源包

## 错误处理

类会自动处理以下错误：
- 网络连接错误
- API返回错误
- 参数验证错误
- 频率限制错误

所有错误都会包含详细的错误信息，便于调试。

## 注意事项

1. 确保在使用前正确配置了授权信息
2. 手机号必须是有效的中国大陆手机号格式
3. 建议在生产环境中设置合适的重试和频率限制配置
4. 记得在应用关闭时调用destroy()方法清理资源
5. CRM数据查询接口有频率限制，请合理控制查询频率
6. 查询字段时建议只选择需要的字段，避免返回过多数据
7. 所有方法都是异步的，需要使用await调用

## 与JavaScript版本的差异

1. **异步处理**: Python版本使用async/await，JavaScript版本使用Promise
2. **类型注解**: Python版本使用typing模块提供类型提示
3. **日志记录**: Python版本使用logging模块
4. **错误处理**: Python版本使用异常处理机制
5. **HTTP请求**: Python版本使用requests库，JavaScript版本使用axios

## 文件结构

```
crm-python/
├── fxiaoke_auth.py          # 认证管理类
├── fxiaoke_user.py          # 用户管理类
├── fxiaoke_crm.py           # CRM客户端类
├── fxiaoke_crm_data.py      # CRM数据查询类
├── index_run.py             # 主运行文件
├── requirements.txt         # 依赖文件
└── README.md               # 说明文档
``` 