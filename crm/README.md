# 纷享销客CRM集成工具

## 功能说明

本工具集提供了纷享销客CRM的完整集成功能，包括：

- **认证管理** (`FxiaokeAuthManager`): 自动获取和刷新企业访问令牌
- **用户管理** (`FxiaokeUserManager`): 根据手机号获取用户信息
- **CRM对象管理** (`FxiaokeCRMClient`): 获取CRM对象列表和字段信息
- **CRM数据查询** (`FxiaokeCRMDataClient`): 查询CRM业务对象数据

## 主要特性

- ✅ 自动认证和token管理
- ✅ 内置频率限制和重试机制
- ✅ 完整的错误处理
- ✅ 支持批量操作
- ✅ 详细的日志记录
- ✅ 模块化设计，易于扩展

## 主要特性

- ✅ 根据手机号获取用户信息
- ✅ 自动获取和刷新认证token
- ✅ 内置频率限制（100次/20秒）
- ✅ 自动重试机制
- ✅ 手机号格式验证
- ✅ 批量处理支持
- ✅ 错误处理和日志记录

## 安装依赖

```bash
npm install axios
```

## 使用方法

### 1. 基本使用

```javascript
const FxiaokeAuthManager = require('./fxiaoke_auth');
const FxiaokeUserManager = require('./fxiaoke_user');

// 创建授权管理器
const authManager = new FxiaokeAuthManager({
    appId: 'your_app_id',
    appSecret: 'your_app_secret',
    permanentCode: 'your_permanent_code'
});

// 创建用户管理器
const userManager = new FxiaokeUserManager(authManager);

// 根据手机号获取用户信息
const mobile = '18211565695';
const userInfo = await userManager.getUserByMobile(mobile);
console.log('用户信息:', userInfo);

// 获取currentOpenUserId
const currentOpenUserId = await userManager.getCurrentOpenUserId(mobile);
console.log('currentOpenUserId:', currentOpenUserId);

// 清理资源
authManager.destroy();
userManager.destroy();
```

### 2. 批量处理

```javascript
const mobiles = ['18211565695', '13800138000', '13900139000'];
const results = await userManager.batchGetUsersByMobile(mobiles);

results.forEach(result => {
    if (result.success) {
        console.log(`${result.mobile}: 成功`);
    } else {
        console.log(`${result.mobile}: 失败 - ${result.error}`);
    }
});
```

### 3. 配置自定义

```javascript
// 设置重试配置
userManager.setRetryConfig({
    maxRetries: 5,
    retryDelay: 2000
});

// 设置频率限制
userManager.setRateLimitConfig({
    maxRequestsPerWindow: 50,
    windowSize: 15000
});

// 设置超时时间
userManager.setTimeout(15000);
```

## API接口说明

### getUserByMobile(mobile)

根据手机号获取用户信息

**参数:**
- `mobile` (string): 手机号

**返回:**
- Promise<Object>: 用户信息对象

**示例:**
```javascript
const userInfo = await userManager.getUserByMobile('18211565695');
```

### getCurrentOpenUserId(mobile)

根据手机号获取用户的currentOpenUserId（实际返回的是openUserId）

**参数:**
- `mobile` (string): 手机号

**返回:**
- Promise<string>: openUserId

**示例:**
```javascript
const currentOpenUserId = await userManager.getCurrentOpenUserId('18211565695');
```

### getUserDetail(mobile)

根据手机号获取用户详细信息

**参数:**
- `mobile` (string): 手机号

**返回:**
- Promise<Object>: 用户详细信息，包含openUserId、fullName、mobile、email等字段

**示例:**
```javascript
const userDetail = await userManager.getUserDetail('18211565695');
console.log('用户ID:', userDetail.openUserId);
console.log('姓名:', userDetail.fullName);
```

### batchGetUsersByMobile(mobiles)

批量获取用户信息

**参数:**
- `mobiles` (Array<string>): 手机号数组

**返回:**
- Promise<Array>: 结果数组，每个元素包含success、data或error

**示例:**
```javascript
const results = await userManager.batchGetUsersByMobile(['18211565695', '13800138000']);
```

## 测试运行

### 模拟测试（推荐）
```bash
node crm/fxiaoke_user.run.js
```

### 真实API测试
```bash
TEST_MODE=real node crm/fxiaoke_user.run.js
```

### 批量测试
```bash
TEST_MODE=batch node crm/fxiaoke_user.run.js
```

### 使用示例
```bash
TEST_MODE=example node crm/fxiaoke_user.run.js
```

## 频率限制

- 单接口调用限制：100次/20秒
- 总接口调用次数限制：根据购买的Open API资源包

## API返回结构

根据手机号获取用户信息的API返回结构：

```json
{
  "empList": [
    {
      "enterpriseId": 564761,
      "openUserId": "FSUID_FE1DA7B9123157F98B797D9581456443",
      "account": "18692224663",
      "fullName": "曹悉",
      "name": "曹悉",
      "status": "NORMAL",
      "mobile": "18692224663",
      "email": "caoxi@laiye.com",
      "gender": "M",
      "isActive": true,
      "mainDepartmentIds": [1279],
      "departmentIds": [1279]
    }
  ],
  "errorCode": 0,
  "errorMessage": "success",
  "errorDescription": "成功",
  "traceId": "E-O.zhulilaiye.-10000-20250718110612-99f8b8"
}
```

**重要说明：**
- 用户信息在 `empList` 数组中
- `currentOpenUserId` 实际对应返回数据中的 `openUserId` 字段
- 如果手机号不存在，`empList` 将为空数组

## 错误处理

类会自动处理以下错误：
- 网络连接错误
- API返回错误
- 参数验证错误
- 频率限制错误

所有错误都会包含详细的错误信息，便于调试。

## CRM数据查询功能

### FxiaokeCRMDataClient 类

`FxiaokeCRMDataClient` 类提供了CRM业务对象数据查询功能，支持查询客户、联系人、销售机会等业务对象的数据。

#### 主要特性

- ✅ 支持所有CRM业务对象的数据查询
- ✅ 内置频率限制（100次/20秒）
- ✅ 自动重试机制
- ✅ 支持分页查询
- ✅ 支持条件过滤
- ✅ 支持时间范围查询
- ✅ 支持排序功能

#### 基本使用

```javascript
const FxiaokeAuthManager = require('./fxiaoke_auth');
const FxiaokeUserManager = require('./fxiaoke_user');
const FxiaokeCRMDataClient = require('./fxiaoke_crm_data');

// 创建管理器
const authManager = new FxiaokeAuthManager(config);
const userManager = new FxiaokeUserManager(authManager);
const crmDataClient = new FxiaokeCRMDataClient(authManager);

// 获取用户ID
const currentOpenUserId = await userManager.getCurrentOpenUserId('13800138000');

// 查询客户数据
const customerData = await crmDataClient.findCustomerData({
    currentOpenUserId: currentOpenUserId,
    fields: ['_id', 'name', 'mobile', 'email', 'last_modified_time'],
    limit: 10,
    offset: 0
});

console.log('客户数据:', customerData);
```

#### API方法

##### findSimpleData(params)

通用数据查询方法

**参数:**
- `currentOpenUserId` (string): 当前用户ID
- `dataObjectApiName` (string): 对象ApiName
- `fieldProjection` (Array<string>): 返回字段列表
- `searchQueryInfo` (Object): 查询条件
- `igonreMediaIdConvert` (boolean): 是否忽略MediaId转换

**示例:**
```javascript
const result = await crmDataClient.findSimpleData({
    currentOpenUserId: currentOpenUserId,
    dataObjectApiName: 'Customer',
    fieldProjection: ['_id', 'name', 'mobile', 'email'],
    searchQueryInfo: {
        limit: 10,
        offset: 0,
        orders: [{ fieldName: 'last_modified_time', isAsc: false }]
    }
});
```

##### findCustomerData(params)

查询客户数据

**参数:**
- `currentOpenUserId` (string): 当前用户ID
- `fields` (Array<string>): 返回字段列表
- `limit` (number): 查询条数
- `offset` (number): 查询偏移量
- `filters` (Object): 过滤条件
- `orders` (Array<Object>): 排序条件

**示例:**
```javascript
const customers = await crmDataClient.findCustomerData({
    currentOpenUserId: currentOpenUserId,
    fields: ['_id', 'name', 'mobile', 'email'],
    limit: 10,
    offset: 0
});
```

##### findContactData(params)

查询联系人数据

**参数:** 同findCustomerData

**示例:**
```javascript
const contacts = await crmDataClient.findContactData({
    currentOpenUserId: currentOpenUserId,
    fields: ['_id', 'name', 'mobile', 'email', 'company_name'],
    limit: 10
});
```

##### findOpportunityData(params)

查询销售机会数据

**参数:** 同findCustomerData

**示例:**
```javascript
const opportunities = await crmDataClient.findOpportunityData({
    currentOpenUserId: currentOpenUserId,
    fields: ['_id', 'name', 'amount', 'stage', 'expected_close_date'],
    limit: 10
});
```

##### findDataByTimeRange(params)

根据时间范围查询数据

**参数:**
- `currentOpenUserId` (string): 当前用户ID
- `dataObjectApiName` (string): 对象ApiName
- `fieldProjection` (Array<string>): 返回字段列表
- `startTime` (Date|string|number): 开始时间
- `endTime` (Date|string|number): 结束时间
- `timeField` (string): 时间字段名（默认'last_modified_time'）
- `limit` (number): 查询条数
- `offset` (number): 查询偏移量

**示例:**
```javascript
const recentData = await crmDataClient.findDataByTimeRange({
    currentOpenUserId: currentOpenUserId,
    dataObjectApiName: 'Customer',
    fieldProjection: ['_id', 'name', 'mobile', 'last_modified_time'],
    startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7天前
    endTime: new Date(),
    limit: 20
});
```

#### 测试运行

```bash
# CRM数据查询测试
TEST_MODE=data node crm/index.run.js

# 运行所有测试
node crm/index.run.js
```

## 注意事项

1. 确保在使用前正确配置了授权信息
2. 手机号必须是有效的中国大陆手机号格式
3. 建议在生产环境中设置合适的重试和频率限制配置
4. 记得在应用关闭时调用destroy()方法清理资源
5. CRM数据查询接口有频率限制，请合理控制查询频率
6. 查询字段时建议只选择需要的字段，避免返回过多数据