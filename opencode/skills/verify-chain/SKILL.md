---
name: verify-chain
description: Use after build or code agent completes a coding task, to determine whether to trigger verification. Covers change impact assessment table, verify trigger/skip conditions, verify prompt construction.
---

# Verify 调用链 + 变更影响评估

## 变更影响评估

在 build/code 执行完毕后，macro **先评估变更类型**，再决定是否触发 verify：

| 变更类型 | 示例 | 是否触发 verify |
|---------|------|---------------|
| 🔴 **高风险** | 函数逻辑变更、API 修改、跨模块改动、依赖更新 | ✅ **必须**触发 |
| 🟡 **中风险** | 单文件新增、配置文件值变更、CSS/样式修改 | ✅ **必须**触发（除非用户明确要求跳过） |
| 🟢 **低风险** | 纯文档/注释变更、README 更新、变量重命名 | ❌ **跳过** |
| ⚪ **无代码变更** | create/explore 执行的任务 | ❌ **跳过** |

**不确定时 → 触发 verify**，宁可多跑一次验证。

## Verify 执行流程

1. build/code 返回 → macro 检查变更文件列表和变更描述
2. 按上表判断风险等级
3. 高风险/中风险 → 创建 todo → 分派 `verify` Agent
4. 低风险/无变更 → 直接汇总展示给用户，备注"（低风险变更，跳过验证）"

## Verify 不触发条件

- 变更影响评估结果为"低风险"或"无代码变更"
- **中风险但用户明确要求跳过验证**
- create 或 explore 执行的任务（不产生代码变更）

## Verify prompt 构建

分派 verify 时，prompt 需包含以下信息：
1. 被修改的**文件列表**（完整路径，每行一个）
2. 项目**根目录**
3. 变更**简要描述**（让 verify 知道改了什么，便于确定测试范围）
4. 期望的验证范围（测试/lint/类型检查/构建，根据变更类型确定）

示例 prompt 结构：
```
请验证以下变更：
- 项目根目录：/home/user/project
- 修改文件列表：
  - /home/user/project/src/main.ts
  - /home/user/project/src/utils.ts
- 变更描述：重构了用户认证逻辑，从 JWT 切换到 Session-based auth
- 验证范围：类型检查 + 单元测试 + lint
```
