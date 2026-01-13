# 分析型智能体 Web POC

## 项目简介

这是一个"分析型智能体 Web POC（对话界面）"项目，场景是：比价→购买决策→完成购买。通过分析用户行为数据，识别转化率下降的原因，特别是购买决策阶段的流失问题。

## 功能特性

- **Web对话界面**：提供聊天消息流、输入框、建议问题按钮
- **L0结论卡**：总体转化率分析和下钻卡
- **L1下钻分析**：旅程阶段断点下钻、渠道下钻
- **L2细分分析**：购买决策阶段的无效浏览问题分析

## 技术栈

- **后端**：Python + Flask + SQLite
- **前端**：HTML/CSS/JavaScript（纯原生，无框架）
- **数据库**：SQLite (demo.db)

## 项目结构

```
poc_demo/
├── data.sql           # 示例数据SQL文件
├── db_build.py        # 数据库构建脚本
├── queries.py         # SQL查询函数（所有SQL在此）
├── rules.py           # 规则模块
├── cards.py           # 下钻卡定义
├── state.py           # 状态管理（state.json）
├── web_app.py         # Flask Web应用
├── templates/
│   └── index.html     # 前端HTML
├── static/
│   ├── app.js         # 前端JavaScript
│   └── styles.css     # 前端样式
└── README.md          # 项目文档
```

## 数据表结构

### users
- user_id (TEXT PRIMARY KEY)
- first_channel (TEXT)
- user_type (TEXT)
- created_at (TEXT)

### journey_events
- je_id (TEXT PRIMARY KEY)
- user_id (TEXT)
- ts (TEXT)
- journey_id (TEXT)
- step (TEXT)
- step_name (TEXT)
- order_id (TEXT)
- amount (REAL)

### decision_events
- de_id (TEXT PRIMARY KEY)
- user_id (TEXT)
- ts (TEXT)
- journey_id (TEXT)
- session_id (TEXT)
- page_name (TEXT)
- page_type (TEXT)
- action (TEXT)
- button_id (TEXT)
- is_key_page (INTEGER)

### items（新增）
- item_id (TEXT PRIMARY KEY)
- item_name (TEXT)
- category_name (TEXT)
- tag (TEXT)

### item_events（新增）
- ie_id (TEXT PRIMARY KEY)
- user_id (TEXT)
- ts (TEXT)
- journey_id (TEXT)
- session_id (TEXT)
- page_name (TEXT)
- event_name (TEXT)  -- 'item_impression' | 'item_click'
- item_id (TEXT)

### order_items（新增）
- oi_id (TEXT PRIMARY KEY)
- order_id (TEXT)
- user_id (TEXT)
- item_id (TEXT)
- qty (INTEGER)
- amount (REAL)

## 时间窗

- **prev_7d**: 2026-01-01 至 2026-01-07
- **curr_7d**: 2026-01-08 至 2026-01-14

## 快速开始

### 1. 构建数据库

```bash
cd poc_demo
python3 db_build.py
```

这将创建 `demo.db` 数据库并导入示例数据。

### 2. 启动Web应用

```bash
python3 web_app.py
```

应用将在 `http://localhost:5000` 启动。

### 3. 使用浏览器访问

打开浏览器访问 `http://localhost:5000`

## API接口

- `GET /api/suggestions` - 获取建议问题列表
- `POST /api/ask` - 提交问题，返回L0结论卡+下钻卡
  - Body: `{"question": "..."}`
- `POST /api/drill` - 下钻分析
  - Body: `{"card_id": "C1|C2|C3"}`
- `GET /api/state` - 获取当前状态
- `POST /api/reset` - 重置状态

## 使用流程

1. **启动应用**后，浏览器会显示建议问题按钮
2. **点击建议问题**或输入自定义问题，系统返回L0结论卡
3. **点击下钻卡**（C1/C2/C3）进行深度分析
   - **C1**: 旅程阶段断点下钻（L1）
   - **C2**: 渠道下钻（L1）
   - **C3**: 购买决策细分下钻（L2）
4. 根据下钻结果，可以继续点击下一步下钻卡

## 下钻分析说明

### L0结论卡
- 总体转化率对比（curr_7d vs prev_7d）
- 提供3个下钻卡选项

### L1下钻（C1：旅程阶段断点下钻）
- 分析 compare→decide、decide→purchase 的转化/流失
- 识别最大断点边
- 提供C3下钻卡继续分析

### L1下钻（C2：渠道下钻）
- 按渠道分析 decide→purchase 断点
- 输出Top渠道流失情况

### L2下钻（C3：购买决策细分下钻）
- 分析进入决策阶段但未购买的用户
- 同时识别两类问题：
  1. **问题A：无效页面浏览过多**
     - 平均无效浏览次数
     - Top无效页面列表
  2. **问题B：列表无点击**
     - 到达商品列表页（category）的用户数
     - 未点击任何商品的用户数和比例
     - 平均曝光商品数
- 输出运营策略：
  - UI策略：删除/合并无效页面、优化路径建议
  - 人群策略：输出人群筛选条件（不真正创建人群包）
  - 商品策略：基于历史购买偏好（需通过C32下钻获取）
- 提供下一步下钻卡：C31、C32

### L3下钻（C31：无效页面名称下钻）
- 输出Top无效页面（page_name + users/events）
- 用于UI调整/删除页面

### L3下钻（C32：未点击商品用户偏好下钻）
- 圈出"到达列表页但未点击商品"的用户
- 分析历史购买偏好：
  - 历史购买Top类目
  - 历史购买Top商品
- 输出运营策略：
  - 人群策略：结构化人群筛选条件
  - 商品策略：基于历史购买偏好，定义"优先展示哪些商品/类目"

## 验收步骤

### 1. 构建数据库
```bash
cd poc_demo
python3 db_build.py
```

验证输出应包含：
- 用户数: 9（包含原有7个 + 新增u9/u10）
- 商品数: 6
- 商品事件数: 6
- 订单商品数: 8

### 2. 启动Web应用
```bash
python3 web_app.py
```

### 3. 浏览器验收

#### 3.1 触发C3下钻
1. 访问 `http://localhost:5000`
2. 点击建议问题或输入问题，触发L0结论卡
3. 点击C1（旅程阶段断点下钻）
4. 在C1结果中点击C3（购买决策细分下钻）

#### 3.2 验证C3结果
C3结论卡应同时显示两类问题：
- **问题A**：无效页面浏览过多（应显示平均无效浏览次数）
- **问题B**：列表无点击（应显示到达category但未点击商品的用户数和比例）

C3应显示：
- 证据：包含两类问题的详细数据
- 运营策略：UI策略、人群策略（筛选条件）、商品策略（提示需C32下钻）
- 下一步下钻卡：C31、C32

#### 3.3 验证C31下钻
1. 在C3结论卡上点击C31按钮
2. 应显示Top无效页面列表（page_name + events/users）
3. 验证：可以多次点击C31按钮，每次都能正常返回结果

#### 3.4 验证C32下钻（关键验收点）
1. **回到同一张C3结论卡**（不刷新页面）
2. 点击C32按钮
3. 应显示：
   - 人群大小（应显示2人：u9和u10）
   - 历史购买Top类目（u9偏好Sports，u10偏好KidsSnack）
   - 历史购买Top商品（u9购买i101/i102，u10购买i201/i202）
   - 运营策略：
     - 人群策略：结构化筛选条件
     - 商品策略：优先展示类目和商品（基于历史购买偏好）

#### 3.5 验证按钮点击不失效（关键验收点）
1. 在同一张C3结论卡上：
   - 先点C31 → 正常返回
   - 再点C32 → 仍然正常返回（不能失效）
   - 顺序反过来也成立
2. 同一个按钮可重复点击多次，每次都能正常返回

### 4. 数据验证
使用SQLite命令行验证数据：
```bash
sqlite3 demo.db
```

验证关键数据：
```sql
-- 验证u9/u10到达category但无item_click
SELECT de.user_id, COUNT(DISTINCT de.de_id) as de_count
FROM decision_events de
WHERE de.user_id IN ('u9', 'u10')
AND (de.page_name = 'category' OR de.is_key_page = 1)
GROUP BY de.user_id;

-- 验证u9/u10无item_click
SELECT user_id, COUNT(*) as click_count
FROM item_events
WHERE user_id IN ('u9', 'u10')
AND event_name = 'item_click'
GROUP BY user_id;
-- 应返回0行

-- 验证历史购买偏好
SELECT oi.user_id, i.category_name, COUNT(*) as purchase_count
FROM order_items oi
JOIN items i ON oi.item_id = i.item_id
WHERE oi.user_id IN ('u9', 'u10')
GROUP BY oi.user_id, i.category_name;
-- u9应偏好Sports，u10应偏好KidsSnack
```

## 注意事项

- 所有SQL查询都在 `queries.py` 中实现
- `web_app.py` 不包含SQL代码
- 状态保存在 `state.json` 文件中
- 关键页定义：`page_name='category'` 或 `is_key_page=1`
- 前端使用事件委托机制，确保按钮始终可点击
- 运营策略仅输出，不真正执行（不创建人群包、不修改UI）

## 开发说明

- 前端使用纯HTML/CSS/JS，无框架依赖
- 后端Flask应用，SQLite数据库
- 所有SQL查询函数集中在 `queries.py`
- 状态管理通过 `state.py` 模块
- 下钻卡定义在 `cards.py` 中

## 许可证

MIT License
