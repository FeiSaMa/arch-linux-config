---
name: intent-refinement
description: Use when performing intent refinement, pre-flight checks, distributing tasks to sub-agents, or planning build→verify chaining. Covers three-element prompt expansion, pre-flight checklist, distribution format, plan→build chaining, info filtering, and batch packing.
---

# Intent Refinement — 意图重构完整流程

## 三要素精炼

将用户模糊提问扩写为包含以下三要素的精确 prompt：

- 【明确目标】这个任务要达成什么具体结果
- 【模版来源要求】数据/代码/配置的来源或参考依据（如参考现有文件、遵循已有模式）
- 【计算逻辑】具体的实现步骤、技术选型、约束条件

## 预检清单（强制）

精炼完成后**必须**逐项检查：

- [ ] **路径明确** — 所有文件路径是否已明确指定？
- [ ] **参数完整** — 所有关键参数/配置项是否已提供？
- [ ] **逻辑一致** — 需求是否自相矛盾或与已知约束冲突？
- [ ] **技术可行** — 是否存在已知的不可行因素？
- [ ] **参考完备** — 若涉及参考文档（refs），是否已检查？

**预检结果处理：**
- ✅ 全部通过 → 展示"✅ 预检通过"，进入展示确认
- ❌ 存在问题 → 指出具体问题，格式：
  ```
  ⚠️ **预检问题**：
  1. [具体问题1] — 请确认...
  2. [具体问题2] — 请补充...
  ```

## 展示确认

将扩充后的 prompt 用代码块展示给用户，等待用户回复"确认"。

## 执行分发

收到"确认"后，根据任务性质分派子 Agent。分发格式：

> → 分派给 `explore` agent（搜索浏览 / V4-Flash）— [任务简述]
> → 分派给 `plan` agent（方案设计 / V4-Pro / 只读）— [任务简述]
> → 分派给 `build` agent（复杂开发 / V4-Pro）— [任务简述]
> → 分派给 `code` agent（日常编码 / V4-Flash）— [任务简述]
> → 分派给 `verify` agent（验证 / V4-Flash）— [任务简述]
> → 分派给 `create` agent（创意 / V4-Flash）— [任务简述]

## plan → build 串联规则

对于复杂任务，遵循「先分析后实现」的分步策略：

**判断标准：**
- 跨模块重构、API 变更、架构调整 → **必须**走 plan → build → verify 三阶段
- 新功能开发（>3 个文件或涉及新模块） → 建议走 plan → build → verify
- 单文件修改/bug 修复 → 直接分派给 `code`，跳过 plan

### plan → build 信息过滤规则

**传递给 build 的内容**（精简版）：
1. **技术选型结论** — 选了什么技术/库/方案
2. **变更文件清单** — 要改/新建哪些文件
3. **关键接口签名** — 新增/修改的 API 定义
4. **约束条件** — 必须遵守的限制（兼容性、性能目标）
5. **实现建议** — plan 提出的具体实现方向

**不传递给 build 的内容**（过滤掉）：
- plan 的探索过程（试错的路径）
- 被否决的备选方案细节
- 代码库结构描述（build 已可自行阅读）

## 批量打包量化标准

连续多个小变更时合并为一个 task：

| 条件 | 策略 |
|------|------|
| ≤3 个文件 & 每文件变更 ≤15 行 | 合并为一个 task 派给 `code` |
| 4-5 个文件，变更较小且无架构耦合 | 合并为一个 task 派给 `code` |
| >5 个文件 或 涉及架构变更 | 拆分为 plan（分析）+ build（实现） |
| 跨模块重构/API 变更 | 拆分为 plan（方案）+ build（实现）+ verify（验证） |

判断原则：当批量打包的 prompt 超过 2000 字时，说明 task 太大，应拆分。

## 紧急绕过机制

若用户输入以 `!!` 或 `!urgent` 开头：
- **仍须执行精炼**（用代码块展示给用户，但不等用户确认）
- **仍须执行预检**
- **仍须遵守 todo 纪律**
- **仍须分发公示**
- 跳过的是 **用户确认等待** 环节
- 最终仍须汇总结果并展示执行日志
