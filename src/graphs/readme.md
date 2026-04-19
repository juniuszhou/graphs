# Graph

##

in general, graph just define the node, edge and trigger the state update and message flow.

## concept

node
edge
condition_edge
command
send

### checkpoints

以thread id 为key，来存放所有的状态

### store

memory, redis and postgres

### superstep

每个superstep都会把结果放到checkpoints里面，如果设置了它。
一个superstep都是图计算，pregel的一个阶段。它把图按照从begin 到 end 切分成若干个superstep。
一个superstep可能会触发多个节点的计算，或者是一个。

### reducer

当多个状态改变发生时，如何把状态进行合并。是覆盖，还是add到一个列表。不同的方式

## Send

one node can send message to multiple node.
multiple node returned state will be reduced later according to the order.

## Command

dynamic to set the message flow

## Durable Execution

Duration 针对的是checkpoint， 不是store。

是为了保证graph可以在中断后，继续执行。所以在设计graph的执行的时候，需要考虑这个。
比如官网提到的，如果在 @entrypoint里面做打开文件，写入的操作，那么会重复执行。

但是你使用一个node来执行就不会，因为在上一个superstep执行过了，checkpoint 会记住graph的状态。
这样当恢复的时候，就会跳过这个node的调用了。

durability="sync"
exit persist change when program exit. no persist if crash.
sync persist after each superstep, guarantee persist is completed
async persist async, no guarantee persist is completed

## Pregel

### channels

EphemeralValue: 计算完清空
LastValue： 计算完保留最后的值
Topic：channel里面的值可能在多个step中发生变化，比如二个node都写数据进去。那么值可以是 accumulate，累加。或者值保留最后一个值
BinaryOperatorAggregate： 使用某种二元操作符来计算

Topic 在 accumulate=False的时候，也和LastValue是不一样的。
superstep 在执行的时候，如果LastValue，它只会有一个值。
而Topic会有多个值，然后根据accumulate的选择，看是否只保留最后一个。
它在状态保存，debug的时候会非常有用。

在定义图的时候，如果一个channel是有多个输入，那么只能使用Topic。
单个输入就用LastValue

### subgraph state

- per invocation: 每个call都是独立的，subgraph 不需要记住之前的状态。但是它会继承 parent graph过来的state
-

###

LangGraph 的底层执行引擎（runtime）

LangGraph 的 Pregel 执行引擎（也叫 PregelLoop 或 Pregel runtime）是其核心运行时，灵感来源于 Google 2010 年的 Pregel 系统（一个用于大规模图处理的 BSP — Bulk Synchronous Parallel 模型）。它不是简单的异步多线程或事件循环，而是采用超级步（Superstep） 的同步并行执行模型，专门为复杂、有状态、可能带循环的 AI Agent/Workflow 设计。
Pregel 执行模型的核心机制（超级步流程）
每个超级步（Superstep）分为三个清晰阶段：

Plan（规划）：根据上一个超级步中通道（Channels）的更新，决定本步要激活哪些节点（Actors）。只有收到新消息/状态更新的节点才会被选中执行（类似“think like a vertex”：节点自己决定是否工作或休眠）。
Execution（执行）：选中的所有节点并行执行（利用线程池或 async），各自读取输入通道的数据，运行自己的逻辑（LLM 调用、Tool 执行等），并向输出通道写入更新。重要：执行期间的写入对其他节点不可见，避免了竞争条件。
Update + Barrier（同步屏障）：所有节点完成后，进行全局同步（barrier）。统一应用所有通道更新（通过 Reducers 合并冲突），然后进入下一个超级步。

这种“读 → 并行执行 → 写 → 全局同步”的模式，是 Pregel 的精髓。
Pregel 执行引擎的优势（为什么选择它）
相比纯异步多线程（asyncio + gather）、事件驱动、或简单 DAG 执行引擎（如某些 workflow 框架），Pregel 有以下关键优势，尤其适合生产级 AI Agent：

确定性（Deterministic）与可预测性：
尽管节点内部并行执行，但超级步之间有全局同步点，保证执行顺序和状态转换是可重现的。
不会出现 race condition（竞态），Reducers 在 barrier 处统一合并状态。这对调试复杂 Agent（多分支、循环）非常友好。

天然支持循环（Cycles）和动态路由：
传统 DAG 引擎很难处理循环（如 ReAct Agent 的思考-行动循环），Pregel 通过消息传递 + 节点“唤醒”机制原生支持循环，且不会无限死循环（可结合 recursion_limit 等 guardrails）。
条件边（conditional edges）可以根据当前状态动态决定下一批节点。

高效的并行性与资源利用：
在一个超级步内，所有就绪节点最大化并行执行（例如同时调用多个 Tool、多个子 Agent、并行数据获取），大幅降低延迟（最慢节点决定该步耗时，而不是累加）。
超级步之间有 barrier，避免了无谓的上下文切换和锁竞争，整体资源效率高。
对比纯多线程：异步模型容易出现顺序依赖混乱或饥饿，Pregel 的结构化同步让并行更“安全且高效”。

内置持久化、Checkpointing 和 Human-in-the-Loop：
每个超级步结束时可以轻松 checkpoint 完整状态（时间旅行调试：从任意步 replay、branch）。
支持长时间运行的 Agent（故障恢复、中断等待人类输入），这是许多其他引擎缺失的生产级特性。

可扩展性与容错：
设计上便于未来扩展到分布式（多进程/多机），原 Google Pregel 就是为万亿边图设计的。
版本化通道（channel_versions）让变更检测非常高效（O(1)），无需对比实际值。

状态管理优雅：
使用 Channels + Reducers 处理共享状态（而不是全局变量或锁），支持不同类型的状态更新逻辑（append、override 等）。

为什么高效？

最大并行 + 最小开销：只执行“有事做”的节点，空闲节点休眠。并行发生在超级步内，同步开销主要在 barrier（通常很轻量）。
避免常见性能陷阱：无锁争用、无隐式顺序依赖、无内存爆炸（状态通过 checkpoint 可控）。
规模友好：从小 Agent（几个节点）到大规模多 Agent 系统，性能曲线平滑。LangGraph 官方提到，它在保持 API 稳定的同时，通过 runtime 优化（如 PregelLoop 内部改进）显著提升了吞吐量。
与 LLM 特性匹配：LLM 调用、Tool 使用往往是 I/O 密集型，并行执行能显著降低端到端延迟，而确定性让 prompt engineering 和监控更可靠。

简单对比：

纯 asyncio 多线程风格（如某些框架）：更快原型，但容易出现不可预测的顺序、调试难、持久化麻烦。
Pregel：稍微多一点“同步开销”，但换来的是生产级可靠性、可调试性、循环支持和长期运行的效率。许多开发者反馈，在复杂 workflow 中，LangGraph 的整体体验和稳定性远超 ad-hoc 实现。

总之，Pregel 不是追求“最快单次执行”，而是追求在复杂、有状态、可能循环的 Agent 场景下，可靠、高效、可扩展的执行。这也是 LangGraph 能被用于生产环境（Klarna、Uber 等）的重要原因。

## State

reducer 如何合并状态
