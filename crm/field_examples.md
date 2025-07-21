# 纷享销客CRM字段标签示例

## 销售订单 (SalesOrder) 常用字段标签

### 基本信息
- `订单名称` → `name`
- `订单编号` → `order_number`
- `创建时间` → `created_time`
- `最后修改时间` → `last_modified_time`
- `订单状态` → `status`

### 客户信息
- `客户名称` → `customer_name`
- `客户ID` → `customer_id`
- `联系人姓名` → `contact_name`
- `联系人电话` → `contact_phone`

### 金额信息
- `订单金额` → `total_amount`
- `折扣金额` → `discount_amount`
- `实收金额` → `actual_amount`
- `币种` → `currency`

### 时间信息
- `预计交付时间` → `expected_delivery_time`
- `实际交付时间` → `actual_delivery_time`
- `创建人` → `creator_name`
- `负责人` → `owner_name`

## 客户 (Customer) 常用字段标签

### 基本信息
- `客户名称` → `name`
- `客户编号` → `customer_number`
- `客户类型` → `customer_type`
- `客户级别` → `customer_level`

### 联系信息
- `手机号码` → `mobile`
- `电话号码` → `phone`
- `邮箱地址` → `email`
- `公司地址` → `address`

### 业务信息
- `行业` → `industry`
- `公司规模` → `company_size`
- `年营业额` → `annual_revenue`
- `创建时间` → `created_time`

## 联系人 (Contact) 常用字段标签

### 基本信息
- `联系人姓名` → `name`
- `性别` → `gender`
- `职位` → `position`
- `部门` → `department`

### 联系信息
- `手机号码` → `mobile`
- `电话号码` → `phone`
- `邮箱地址` → `email`
- `QQ号码` → `qq`

### 关联信息
- `所属客户` → `customer_name`
- `客户ID` → `customer_id`
- `创建时间` → `created_time`

## 销售机会 (Opportunity) 常用字段标签

### 基本信息
- `机会名称` → `name`
- `机会编号` → `opportunity_number`
- `机会阶段` → `stage`
- `机会来源` → `source`

### 金额信息
- `预计金额` → `expected_amount`
- `实际金额` → `actual_amount`
- `币种` → `currency`

### 时间信息
- `预计成交时间` → `expected_close_date`
- `实际成交时间` → `actual_close_date`
- `创建时间` → `created_time`

## 使用方法

在 `index.run.js` 中修改相关常量：

### 修改目标对象：
```javascript
const TARGET_OBJECT_NAME = '销售订单'; // 或 '客户', '联系人', '销售机会'
```

### 修改查询字段：
```javascript
// 查询销售订单的基本信息
const TARGET_FIELD_LABELS = ['订单名称', '创建时间', '最后修改时间', '订单状态'];

// 查询客户信息
const TARGET_FIELD_LABELS = ['客户名称', '手机号码', '邮箱地址', '客户类型'];

// 查询联系人信息
const TARGET_FIELD_LABELS = ['联系人姓名', '手机号码', '职位', '所属客户'];

// 查询销售机会信息
const TARGET_FIELD_LABELS = ['机会名称', '机会阶段', '预计金额', '预计成交时间'];
```

### 修改分页参数：
```javascript
const QUERY_LIMIT = 10;  // 查询条数
const QUERY_OFFSET = 0;  // 查询偏移量（用于分页）
```

## 注意事项

1. 字段标签必须完全匹配，区分大小写
2. 如果找不到匹配的字段，会在控制台显示警告
3. `_id` 字段会自动包含在查询结果中
4. 建议先运行测试查看可用的字段标签，再设置目标字段
5. 分页参数说明：
   - `QUERY_LIMIT`: 每次查询返回的数据条数（建议不超过100）
   - `QUERY_OFFSET`: 数据偏移量，用于分页查询（0表示从第一条开始）
   - 例如：`limit=10, offset=20` 表示查询第21-30条数据

## 分页查询示例

```javascript
// 查询前10条数据
const QUERY_LIMIT = 10;
const QUERY_OFFSET = 0;

// 查询第11-20条数据
const QUERY_LIMIT = 10;
const QUERY_OFFSET = 10;

// 查询第21-30条数据
const QUERY_LIMIT = 10;
const QUERY_OFFSET = 20;

// 查询所有数据（一次性获取大量数据，谨慎使用）
const QUERY_LIMIT = 1000;
const QUERY_OFFSET = 0;
```

## 查看可用字段

运行测试时会显示：
- 目标字段标签匹配结果
- 可用的字段标签示例
- 生成的 fieldProjection 参数

这样可以帮助您了解当前对象支持哪些字段，并正确设置查询参数。 