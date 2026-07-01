---
name: rollback
description: Use when handling rollback, recovery, backup restoration, task failure recovery, or when user says "回滚/恢复/撤销/退回". Covers backup tracking, rollback flow, diff preview, user confirmation, backup cleanup, and anomaly handling.
---

# Rollback — 回滚机制

## 备份追踪

macro 在分发 build/code 前，在 prompt 中指定 `session_id`（格式：`YYYYMMDD_HHmmss`），告知子 Agent 使用 `~/.cache/opencode-backup/{session_id}/` 作为备份目录。

子 Agent 在返回的「状态摘要」中需列出所有备份文件路径。macro 将备份清单记录在 todo 的上下文中，供回滚时使用。

## 回滚触发条件

| 触发方式 | 说明 |
|---------|------|
| 🔴 **自动触发** | build/code 重试 1 次后仍失败 → 自动回滚 |
| 🟡 **verify 失败** | verify 报告失败且用户未给进一步指示 → 询问用户是否回滚 |
| 🔵 **用户主动** | 用户说"回滚""恢复""撤销""退回"等 → 立即执行 |

## 回滚执行流程

1. macro 创建 todo 标记"回滚中"
2. **diff 预览**：分派 `code` agent 读取备份文件与原文件，对每个文件执行 `diff -u` 生成 unified diff
3. macro 将 diff 结果展示给用户，**等待用户确认**（"以上变更将被回滚，确认？Y/N"）
4. 用户确认后，分派 `code` agent 执行恢复：对清单中每个文件执行 `cp` 从备份恢复
5. code agent 返回恢复结果 + 执行日志
6. macro 更新 todo 为 completed，汇总告知用户
7. 清理 `~/.cache/opencode-backup/{session_id}/`（分派 explore 执行 `rm -rf`）
8. 若用户拒绝回滚，标记 todo 为 cancelled，保留备份不变

**说明**：
- diff 步骤和恢复步骤分两次分派，中间插入用户确认
- 用户确认前不执行任何恢复操作
- diff 使用标准 `diff -u` 格式

## 回滚后动作

- 回滚完成后，macro 标记当前 session 为"已回滚"
- 若用户继续提新需求 → 开启新 session（新 session_id）
- 修订通道计数重置

## 备份清理

| 时机 | 动作 |
|------|------|
| 新 session 开始（新意图重构流程） | 清理上一 session 的备份目录 `~/.cache/opencode-backup/{prev_session_id}/`（分派 explore 执行） |
| 回滚完成后 | 清理当前 session 的备份目录 |
| session 正常结束（用户确认结果） | 保留备份（不主动删除，由用户自行管理） |

## 异常处理（子 Agent 失败兜底）

| 异常类型 | 处理方式 |
|---------|---------|
| ⏰ **超时/无响应** | 重新分派同一任务给同一 Agent，重试 **1 次** |
| ❌ **执行错误** | 收集错误信息，降级路由：build 失败 → 尝试 code；plan 失败 → 尝试 explore |
| 🔄 **结果不完整** | 在汇总中标注缺失部分，询问用户是否继续或补充 |
| 🚫 **重试仍失败** | 汇总所有异常信息告知用户，请求进一步指示。若为 build/code 执行失败，**自动触发回滚**，完成后汇总：`❌ 任务失败，已自动回滚到修改前状态` |

**原则**：最多重试 1 次。重试仍失败且回滚也失败时，坦诚告知用户。
