# 实验 Baseline 使用说明

本文档说明在 `agents/run.py` 中新增的实验 baseline 开关如何使用。

> 核心原则：**不加任何新参数时，行为和以前完全一样**（每个 agent 把计划广播到聊天里、彼此可见、可转移物品）。所有 baseline 都是独立开关，可自由组合（少数互斥情况见下文）。

---

## 1. 快速开始

启动方式和以前一样，只是在原命令后面追加 baseline 参数：

```bash
# 默认行为（不变）
python3 agents/run.py \
  --task data_v0.1_multi/.../task_02_arrow_production.yaml \
  --agent agents/configs/qwen_agent.yaml \
  --output logs/

# 例：完全不让交流 + 固定 20 回合预算
python3 agents/run.py \
  --task data_v0.1_multi/.../task_02_arrow_production.yaml \
  --agent agents/configs/qwen_agent.yaml \
  --output logs/ \
  --no-communication --max-rounds 20
```

---

## 2. 行为类 Baseline（5 个）

| 参数 | 含义 |
|------|------|
| `--single-agent-upper-bound` | **全程只有一个 agent 参与**，没有其他 agent 被创建，也没有讨论/聊天/转移物品。这个 solo agent 需要自己完成所有事情；为保证这是 upper bound，会把原任务里所有 agent 的能力合并到它身上（技能取每项最大值、库存累加、装备并集；位置/用户名用 agent_1 的）。 |
| `--discussion-rounds N` | **前 N 回合只能聊天**（其它动作工具全部禁用），第 N 回合之后**彻底断开交流**。这 N 回合会消耗回合预算。 |
| `--no-communication` | **从第 1 回合就断开交流**：没有 chat 工具、不能转移物品、看不到聊天记录、也看不到其他 agent。 |
| `--shared-plan-only` | 断开交流，但在每个 agent 的 prompt 里注入一份**共享计划**（来源：任务 YAML 的 `shared_plan` 字段，没有就用 `relevant_game_context`）。各自照着计划独立执行。 |
| `--random-agent` | **完全不调用 LLM**，每回合从当前可观测到的合法动作里随机选一个执行（随机移动 / 采集可见资源 / 攻击可见怪 / 装备可装备物品 / sleep；若允许交流还包括 chat / transfer）。 |

> ⚠️ `--no-communication`、`--discussion-rounds`、`--shared-plan-only` **三选一**（互斥），同时传会报错退出。
>
> `--single-agent-upper-bound` 本身就是 solo run：只有一个 agent，全程不交流。

### "交流"到底指什么？

断开交流（上面后三个 baseline）会同时去掉：
- `chat` 工具（不能发全局聊天）
- `transfer_items` 工具（不能转移物品）
- 聊天记录（prompt 里的 CHAT HISTORY 清空）
- 其他 agent 的可见性（PARTY AGENT STATUS 区块 + observation 里的 `players` 数组）

只剩下对世界本身的观测（资源、怪、自己的库存等）。

---

## 3. 设计类开关（可与任意 baseline 组合）

| 参数 | 含义 |
|------|------|
| `--max-rounds N` | 覆盖回合预算。优先级：**`--max-rounds` > 任务 YAML 的 `rounds` 字段 > 默认 55**。真实预算会注入到 prompt 里。 |
| `--no-roles` | 在 prompt 里把身份显示成通用的 `Agent_1 / Agent_2`，并加一句"角色未预先分配，别从名字推断分工，团队自己组织"。只改 prompt，不改技能/库存/用户名。 |
| `--random-spawn` | 用随机坐标替换每个 agent 在 YAML 里配置的出生点（由 `--seed` 控制可复现）。 |
| `--spawn-region X1 Y1 X2 Y2` | 给 `--random-spawn` 指定坐标范围框；不给则在原出生点的包围盒里抖动。**必须和 `--random-spawn` 一起用**。 |
| `--no-task-docs` | 从 prompt 里去掉任务专属文档（`relevant_game_context`）。 |
| `--seed N` | 给 `--random-spawn` 和 `--random-agent` 的随机数播种，保证可复现。 |

---

## 4. 任务 YAML 新增可选字段

在任务 YAML 顶层可以加（都可选）：

```yaml
rounds: 25          # 回合预算（被 --max-rounds 覆盖；都没有则用 55）
shared_plan: |      # 给 --shared-plan-only 用的共享计划文本
  1. lumberjack 去砍 3 根原木
  2. 全部材料汇总给 fletcher
  3. fletcher 制作 15 支箭
```

---

## 5. 常用组合示例

```bash
# 单 agent 上限：全程只有一个 agent 自己完成所有事情（无讨论、无交流）
python3 agents/run.py --task task.yaml --agent agents/configs/qwen_agent.yaml \
  --output logs/ --single-agent-upper-bound

# 先讨论 5 回合再各干各的 + 随机出生点（可复现）
python3 agents/run.py --task-folder data_v0.1_multi/.../ \
  --agent agents/configs/qwen_agent.yaml --output logs/ \
  --discussion-rounds 5 --random-spawn --seed 1

# 共享计划但禁止后续交流
python3 agents/run.py --task task.yaml --agent agents/configs/qwen_agent.yaml \
  --output logs/ --shared-plan-only

# 随机动作 baseline（不花 LLM token），跑整个文件夹
python3 agents/run.py --task-folder data_v0.1_multi/.../ \
  --agent agents/configs/qwen_agent.yaml --output logs/ \
  --random-agent --seed 42

# 给定范围内的随机出生
python3 agents/run.py --task task.yaml --agent agents/configs/qwen_agent.yaml \
  --output logs/ --random-spawn --spawn-region 380 1 400 10 --seed 3

# 不给任务文档 + 缩短预算（压力测试）
python3 agents/run.py --task task.yaml --agent agents/configs/qwen_agent.yaml \
  --output logs/ --no-task-docs --max-rounds 15
```

完整参数列表随时可查：

```bash
python3 agents/run.py --help
```

---

## 6. 输出 / 日志

输出目录结构与原来一致（runner 主日志、每个 agent 的 JSON trace、任务 summary、文件夹 batch summary）。
baseline 不改变日志格式，方便和默认跑法直接对比。

---

## 7. 关于 prompt 里"55 rounds"的提示

agent 配置 YAML（如 `agents/configs/qwen_agent.yaml`）的 system prompt 里写死了"55 rounds"。
由于那段文字在用户可编辑的 YAML 里，`run.py` 会通过模板变量 `{{max_rounds}}` 和追加的 `ROUND BUDGET` 区块把**真实预算**注入 prompt，所以实际预算永远是对的。
如果想彻底避免文字上的不一致，建议把 YAML 里写死的 `55` 改成 `{{max_rounds}}`。

---

## 8. 涉及的代码文件

- `agents/experiment.py` — 新增：`ExperimentConfig`（参数解析/校验/合并/出生点/限制）和 `RandomAgentPolicy`。
- `agents/base_agent.py` — 新增交流限制钩子（`allow_chat` / `allow_transfer` / `hide_chat_history` / `hide_other_players` / `discussion_phase`、`_rebuild_tools()`、observation 过滤）。
- `agents/run.py` — 新增 CLI 参数、配置构建/校验、单 agent 塌缩、随机出生、prompt 开关、回合预算解析、讨论阶段交流门控、random-agent 回合路由。
