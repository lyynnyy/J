// Auto-generated task definitions for Cursor Task Board
// Analysis Agent Engineering Kanban
// 精简工程计划（修订版｜含 LLM 接入说明）

const TASKS = [

/* =========================
   STEP 0 · 基础闭环与 Web 形态（Baseline）
========================= */

{
  step: "STEP 0",
  ticket_id: "STEP-0",
  title: "基础闭环与 Web 形态（Baseline）",
  goal: "验证分析型智能体的基本交互形态与分析闭环成立",
  definition_of_done: [
    "Web 对话界面（结论卡 / 下钻卡）",
    "多按钮结论卡（可重复点击）",
    "状态管理（state 驱动）",
    "L0 → L2 → L3 分析闭环"
  ],
  status: "已完成",
  llm_note: "❌ 不接入 LLM - 保证结构与分析真值稳定"
},

/* =========================
   STEP 1 · 数据模型与分析工具层
========================= */

{
  step: "STEP 1",
  ticket_id: "STEP-1",
  title: "数据模型与分析工具层",
  goal: "构建稳定、可验证的分析计算基础",
  definition_of_done: [
    "行为 / 旅程 / 商品 / 订单数据模型",
    "样例数据（u9 / u10 等）",
    "L0–L3 分层分析工具",
    "SQL 与计算逻辑固化"
  ],
  status: "部分完成",
  llm_note: "❌ 不接入 LLM - 保证结构与分析真值稳定"
},

/* =========================
   STEP 2 · 业务分析能力（C3 决策分析）
========================= */

{
  step: "STEP 2",
  ticket_id: "STEP-2",
  title: "业务分析能力（C3 决策分析）",
  goal: "形成稳定、可复用的业务分析能力单元",
  definition_of_done: [
    "决策阶段双问题诊断（路径问题 + 偏好问题）",
    "C31 / C32 下钻能力",
    "证据结构化输出"
  ],
  status: "部分完成",
  llm_note: "❌ 不接入 LLM - 保证结构与分析真值稳定"
},

/* =========================
   STEP 3 · 分析模式化 & 规划（Pattern / Planner）
========================= */

{
  step: "STEP 3",
  ticket_id: "STEP-3",
  title: "分析模式化 & 规划（Pattern / Planner）",
  goal: "让系统具备「选择分析方法」的能力",
  definition_of_done: [
    "Pattern Registry（P-DEC-01）",
    "Drill Contract",
    "Evidence Contract",
    "Analysis Plan 结构",
    "Planner（规则 / LLM）"
  ],
  status: "未完成",
  llm_note: "✅ LLM 的第一次正式接入点 - 仅用于模式选择（从用户自然语言中选择分析模式，生成结构化 analysis_plan）。禁止：指标计算、SQL/数据聚合、结论真值判断"
},

/* =========================
   STEP 4 · 分析 → 行动映射（Action Layer）
========================= */

{
  step: "STEP 4",
  ticket_id: "STEP-4",
  title: "分析 → 行动映射（Action Layer）",
  goal: "让分析结果天然可对接运营动作",
  definition_of_done: [
    "Action Contract",
    "UI / 人群 / 商品策略结构化输出",
    "结论表达结构"
  ],
  status: "未完成",
  llm_note: "⚠️ LLM 可选接入 - 仅允许用于结论语言润色、不同受众的表达转换。禁止：新增事实、改变结论方向"
},

/* =========================
   STEP 5 · 智能演进（预留）
========================= */

{
  step: "STEP 5",
  ticket_id: "STEP-5",
  title: "智能演进（预留）",
  goal: "为规模化与长期智能预留结构",
  definition_of_done: [
    "Pattern Library",
    "跨分析沉淀"
  ],
  status: "预留",
  llm_note: "🚫 当前版本不实施，仅作为长期预留"
}

];

export default TASKS;
