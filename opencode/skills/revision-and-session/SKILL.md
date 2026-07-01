---
name: revision-and-session
description: Use when handling incremental revisions, user feedback on sub-agent results, session reuse, context persistence, or managing agent session lifecycle. Covers revision channel flow, differentiated session lifecycle, status summary format and truncation rules.
---

# Revision Channel + 差异化 Session 管理

## 修订通道（增量修正）

当用户对子 Agent 的执行结果不满意时，macro **不应从头走完整意图重构流程**。

### 触发条件

| 场景 | 走修订通道 | 走完整意图重构 |
|------|-----------|--------------|
| "这个方案方向对，但细节需要调整" | ✅ | ❌ |
| "改得不够好，换一种方式实现" | ✅ | ❌ |
| "我想完全换一种做法" | ❌ 需求已变 | ✅ 全新需求 |
| "再加一个功能" | ❌ 新需求叠加 | ✅ 合并到新任务 |

### 修订通道流程

1. **提取差异需求** — 从用户反馈中提取"要改什么"，而非重新执行三要素精炼
2. **复用上下文** — 使用 `task_id` 延续同一子 Agent 的 session（基于上一次的状态摘要）
3. **增量修正** — 在 prompt 中说明："基于上次结果做增量修正。不需要重新实现已有功能，只需调整以下部分：…"
4. **验证** — 修正完成后，如果变更涉及代码逻辑，同样经过 verify（按变更影响评估规则）
5. **循环限制** — 同一需求走修订通道不超过 **3 次**。超过后建议用户重新提炼需求

> ⚠️ 修订通道不等于跳过意图重构。如果用户反馈意味着需求本质变化，必须回到完整意图重构流程。

## 差异化 Session 生命周期管理

同一需求的连续分发，应优先使用 `task_id` 复用子 Agent 的 session。

### 差异化复用策略

| 任务类型 | Session 复用上限 | 轮换策略 |
|---------|-----------------|---------|
| 🔍 **explore** | **不缓存**（一次性用完即弃） | 每次新建 session |
| 📝 **code** | 同一 session ≤ **3 次**复用（共 4 轮） | 超过后开新 session，通过状态摘要迁移关键上下文 |
| 🏗️ **plan→build→verify 流水线** | 整条流水线共用同一 session | **p/b/v 各自分界点做上下文截断**；流水线完成后自动归档，不跨需求复用 |
| 🔧 **修订通道** | 同一 session ≤ **3 次**修正 | 超过后建议用户重新提需求 |
| 🎨 **innovate** | 同一 session ≤ **3 次**复用（共 4 轮） | 超过后开新 session |
| ✅ **verify** | **不缓存** | 每次新建 session，结果通过摘要传递 |

### 状态摘要格式

macro 要求子 Agent 在返回末尾附加：

```markdown
#### 状态摘要
- **已分析/修改的文件**: file1.ts, file2.ts
- **关键决策**: ...
- **待办事项**: ...
```

### 上下文持久化规则

1. 第一次分派时正常调用 `task`（无 task_id）
2. 子 Agent 返回后，在其结果末尾查找「状态摘要」小节
3. 若找到，在分派下一个相关 Agent 时，将摘要内容注入 prompt 前缀
4. 对于紧密耦合的连续步骤（如 plan→build），优先使用同一个 `task_id` 延续 session

### 状态摘要截断规则

当 session 超过以下阈值时，不再将完整状态摘要注入 prompt：

| Agent 类型 | 截断阈值 | 保留内容 |
|-----------|---------|---------|
| **code** | ≥ 4 轮对话 | 关键决策结论 + 变更文件清单（≤300 字） |
| **plan→build→verify** | ≥ 10 轮对话 | 关键决策结论 + 变更文件清单（≤500 字） |

超过阈值后，详细分析过程留存在已归档的 session 中，不再传递。
