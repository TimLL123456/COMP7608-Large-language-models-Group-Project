# ToolSandbox

> **Historical research note (2026-10-25):** This benchmark was explored as an alternative during topic selection. Group 9 has selected **KORA** on the **original BIRD Mini-Dev** for its Text-to-SQL evaluation. This file is retained as earlier topic-selection research; see the [submitted KORA proposal](../proposal/KORA/KORA_Group9_Proposal.pdf).

ToolSandbox is a benchmark and evaluation framework for **stateful, conversational and interactive tool use by LLM agents**. It was introduced by Apple researchers in 2024 and later published in the Findings of NAACL 2025.

It is different from a conventional question-answer dataset. A normal QA benchmark usually provides a question and a reference answer. ToolSandbox instead provides an **initial world state, a user request, a set of tools, an execution environment and trajectory-level evaluation criteria**.

For this project, its main value is that it measures whether an agent can **actually complete a task through tools**, not merely produce a plausible final sentence.

## 1. What is in ToolSandbox?

The ToolSandbox paper reports:

| Item | ToolSandbox |
| --- | ---: |
| Test cases | 1,032 |
| Tools | 34 |
| Tool domains | 11 |
| Average turns per scenario | 13.9 |
| Average tool calls per scenario | 3.80 |

The 34 tools cover 11 domains: Contact, Messaging, Reminder, System settings, Time utilities, Math utilities, Map, Weather, Stock, Conversion and Holiday.

A scenario is defined by four main pieces:

```text
Initial world state
+ Initial messages
+ Tools visible to the agent
+ Milestones / minefields used for evaluation
```

This makes ToolSandbox closer to a collection of executable agent tasks than a static table of questions and answers.

## 2. World state and execution context

ToolSandbox keeps state across conversation turns and stores a snapshot after each turn. The world state includes:

- **Settings**, such as cellular service and Wi-Fi status.
- **Contacts**, containing people and contact information.
- **Messaging**, containing messages that have been sent.
- **Reminders**, containing reminders that have been created or modified.
- **Conversation/tool traces**, recording interactions among the system, user, agent and execution environment.

This matters because a correct tool can still fail when a prerequisite state is wrong.

For example:

```text
Send a message
    ↓
requires cellular service
    ↓
cellular service may currently be OFF
```

An agent therefore needs to reason about both **what tool to call** and **what must already be true before the tool can work**.

## 3. Roles in the environment

| Role | Purpose |
| --- | --- |
| System | Supplies instructions and scenario setup |
| User | Requests a task and may answer clarification questions |
| Agent | Plans, talks to the user and calls tools |
| Execution environment | Executes calls and returns outputs or exceptions |

The user can be a human through the CLI or an LLM-based simulator. This supports **on-policy multi-turn evaluation**: the next user message can depend on what the tested agent actually said instead of replaying one fixed dialogue.

## 4. Stateful tool dependencies

The paper highlights four important forms of state dependency:

- **Cellular service:** messaging actions can depend on cellular service being enabled.
- **Wi-Fi:** RapidAPI-backed search tools depend on Wi-Fi.
- **Location service:** tools using the current location depend on location service.
- **Low battery mode:** turning on cellular, Wi-Fi or location can itself depend on low battery mode being disabled.

This can create nested dependencies:

```text
User asks for an action
        ↓
Required tool fails
        ↓
A setting must be enabled
        ↓
That setting cannot be enabled
        ↓
Disable low battery mode
        ↓
Enable required setting
        ↓
Retry original task
```

This is useful for evaluating error diagnosis and recovery rather than only first-attempt function calling.

## 5. Main scenario categories

### Single / multiple tool call

Tests whether a task needs one call or several coordinated calls.

### Single / multiple user turn

Tests whether the initial user request contains enough information or whether the agent must ask a clarification question.

### State dependency

Tests whether the agent discovers and satisfies implicit prerequisites in the environment.

### Canonicalization

Tests whether natural-language values are converted into the form required by a tool. Examples include converting `1k` to `1000` or resolving a phrase such as `this Friday` to a concrete date or timestamp.

### Insufficient information

Tests whether the agent recognizes that a task cannot be completed with the available information or tools. The desired behavior may be to ask the user or explain the limitation instead of inventing a value.

## 6. Worked example: sending a message

The official ToolSandbox documentation gives a useful example.

Initial condition:

```text
Cellular service = OFF
```

User task:

> Send a message to Fredrik Thordendal saying: "How's the new album coming along."

The task is not evaluated as a single static answer string. Critical milestones include:

1. Cellular service eventually becomes `True`.
2. The agent calls `search_contacts` with the name `Fredrik Thordendal`.
3. After the prerequisites are satisfied, the messaging database contains the message for the correct phone number with matching content.
4. After the message exists, the agent tells the user that it was sent.

The first two milestones can occur in either order:

```text
Enable cellular ─────┐
                     ├─→ message exists ─→ user confirmation
Search contact ──────┘
```

A possible successful trajectory is:

```text
User request
   ↓
search_contacts("Fredrik Thordendal")
   ↓
Obtain phone number
   ↓
Handle cellular-service prerequisite
   ↓
Send the message
   ↓
Messaging database changes
   ↓
Tell the user the message was sent
```

Another valid agent could enable cellular service before searching the contact. ToolSandbox therefore evaluates **required dependencies**, not one rigid action script.

## 7. What is the "answer"?

For HotpotQA or MuSiQue, evaluation often looks like:

```text
Question → Gold answer
```

ToolSandbox instead looks like:

```text
Task
  ↓
Agent trajectory
  ↓
Tool calls
  ↓
World-state changes
  ↓
Final user response
```

The closest equivalent to a gold answer is therefore the set of **Milestones** defining what must become true during the trajectory.

This distinction is important: an agent should not receive full credit for saying "done" when the requested state change never happened.

## 8. Milestones and milestone DAGs

A Milestone describes something that should happen, such as:

- a setting reaches a target value;
- a required tool call occurs with particular arguments;
- a message or reminder appears in a database;
- a final response accurately confirms the completed action.

Milestones form a **directed acyclic graph (DAG)**. The edges specify ordering constraints while still allowing multiple valid trajectories.

ToolSandbox matches milestone requirements against the observed trajectory and computes a similarity-based score. This is more flexible than exact trajectory matching because two competent agents can solve the same task with different valid action orders.

## 9. Minefields: what the agent must not do

ToolSandbox also defines **Minefields**, representing events that should not occur.

The paper illustrates this with an insufficient-information case where the current timestamp is unavailable. A bad agent may invent a timestamp and call `timestamp_diff` using the hallucinated value.

Conceptually:

```text
Required information is missing
        ↓
Correct: ask / explain / stop safely

Incorrect: invent a value
        ↓
call a tool with hallucinated argument
        ↓
MINEFIELD
```

In the official scoring formulation, a minefield violation can zero the trajectory score. This allows the benchmark to evaluate **restraint and hallucination control**, not only action-taking.

## 10. Tool augmentations

The framework can deliberately make tool use harder by:

- adding irrelevant distraction tools;
- scrambling tool names;
- removing argument descriptions;
- replacing argument names in documentation with generic names;
- removing argument type hints.

For example, an intuitive tool name such as `set_cellular_service_status` can be replaced by a less informative name. The agent must then rely more on the specification rather than the name itself.

These variants help test whether the agent genuinely understands tool documentation.

## 11. What capabilities can it evaluate?

| Capability | Evaluation question |
| --- | --- |
| Tool selection | Did the agent choose an appropriate tool? |
| Argument construction | Were parameters correct? |
| Multi-tool planning | Were several calls coordinated correctly? |
| State awareness | Did the agent understand the current environment? |
| Dependency handling | Were prerequisites satisfied before the action? |
| Error recovery | Did the agent repair the plan after a failed call? |
| Clarification | Did it ask the user when information was missing? |
| Canonicalization | Were natural-language values converted correctly? |
| Restraint | Did it avoid hallucinated tools or arguments? |
| Task completion | Did the intended state change actually occur? |
| User communication | Did the final response describe the real outcome? |
| Efficiency | How many calls, turns, tokens and seconds were used? |

## 12. Recommended COMP7608 experiment

A focused research question would be:

> **Does explicit prerequisite checking and execution-result verification improve tool-using agent success over a standard ReAct-style agent, and is the improvement worth the extra tool calls and latency?**

### Baseline

```text
User request
   ↓
ReAct-style agent
   ↓
Choose tool
   ↓
Execute
   ↓
Continue until final response
```

### Improvement

```text
User request
   ↓
Check information sufficiency
   ↓
Check likely state prerequisites
   ↓
Execute tool
   ↓
Verify result / state change
   ↓
If failed, identify prerequisite
   ↓
Repair and retry
   ↓
Confirm task outcome
```

For a fair experiment, keep fixed:

- the LLM;
- ToolSandbox version / commit;
- selected scenario set;
- user simulator model;
- tool augmentation setting;
- temperature / retry settings;
- maximum turn and tool-call budget.

The main variable should be the **agent orchestration strategy**, not a simultaneous model upgrade.

## 13. Evaluation metrics

The official trajectory / milestone similarity score should remain the primary benchmark signal.

Additional project metrics can include:

| Metric | Purpose |
| --- | --- |
| Mean trajectory similarity | Overall benchmark performance |
| Full-success rate | Fraction of scenarios completing all critical requirements |
| Score by category | Reveal state-dependency, canonicalization and information gaps |
| Minefield violation rate | Measure hallucinated / forbidden actions |
| Invalid tool-call rate | Measure bad tool or argument use |
| Clarification success | Measure handling of missing information |
| Retry / recovery success | Measure recovery after execution errors |
| Tool-call count | Measure agent overhead |
| Conversation turns | Measure interaction cost |
| Tokens | Measure model usage |
| Latency | Measure end-to-end runtime |
| Repeated-run variance | Measure stochastic reliability |

Results should be broken down by scenario category rather than reported only as one aggregate number.

## 14. Failure analysis

A useful failure taxonomy is:

- **Tool-selection failure:** wrong tool chosen.
- **Argument failure:** correct tool, wrong parameter or format.
- **State-awareness failure:** prerequisite state ignored.
- **Planning failure:** useful actions are ordered incorrectly.
- **Recovery failure:** execution error occurs but the agent does not repair the plan.
- **Clarification failure:** missing information is guessed instead of requested.
- **Canonicalization failure:** value conversion is incorrect.
- **Hallucination failure:** nonexistent tool or unsupported value is invented.
- **Premature-success failure:** agent claims success before the world state confirms it.
- **Efficiency failure:** the task succeeds but requires excessive calls, retries or turns.

Comparing failure distributions before and after an agent improvement can be more informative than only comparing average scores.

## 15. Why ToolSandbox is useful for an agentic project

A chatbot can say:

```text
"Your message has been sent."
```

A ToolSandbox agent must demonstrate that the environment actually changed:

```text
Correct contact found
+ prerequisite state satisfied
+ message exists in database
+ correct final confirmation
```

This gives a clear experimental distinction between **plausible response** and **verified task completion**.

Compared with multi-hop QA:

```text
HotpotQA / MuSiQue
Question → retrieve/reason → answer

ToolSandbox
User task → plan → use tools → manage state → recover → verify → complete
```

That makes ToolSandbox particularly suitable for studying tool selection, state tracking, recovery and hallucination control.

## 16. Practical setup

The official repository documents a Python 3.9 environment and installs dependencies with:

```bash
pip install '.[dev]'
```

The CLI can run a single scenario or the configured scenario suite. Some configurations require model API credentials, RapidAPI credentials for search tools, or Google Cloud authentication for Gemini models.

Evaluation artifacts are written under the repository's `data` directory, including result summaries and per-scenario conversation trajectories.

For a course project, the sensible starting point is a small fixed subset covering several scenario categories before attempting all 1,032 test cases.

## 17. Strengths and limitations

**Strengths**

- Evaluates actual tool execution rather than only function-call syntax.
- Maintains world state across turns.
- Supports multi-turn interaction with a user simulator.
- Includes implicit and nested state dependencies.
- Evaluates intermediate milestones as well as final outcomes.
- Minefields test whether the agent avoids harmful or hallucinated behavior.
- Scenario categories enable targeted failure analysis.
- Tool augmentations can stress-test specification understanding.

**Limitations**

- It is a simulated assistant environment rather than a production device.
- Some search scenarios depend on external services or credentials.
- Results can depend on the user simulator model and configuration.
- Running interactive scenarios costs more than evaluating a static QA file.
- The benchmark's tool set reflects its original release period, so versions should be pinned.
- A successful final state does not necessarily imply the agent used the most efficient reasoning path.

## 18. Recommended starting plan

If ToolSandbox is shortlisted:

1. Pin the repository commit and environment.
2. Reproduce one simple scenario locally.
3. Inspect the trajectory and result summary.
4. Run a small subset spanning the major scenario categories.
5. Build a simple baseline with a fixed LLM.
6. Add explicit prerequisite checking and post-action verification.
7. Keep the user simulator and environment fixed.
8. Record official scores plus tool-call, turn, token and latency metrics.
9. Compare results by category.
10. Classify failures using observable traces and state changes.
11. Repeat selected scenarios to estimate variance.
12. Scale to the full suite only if the evaluation budget allows.

ToolSandbox is therefore a **strong candidate for a tool-using agent project** because success is grounded in observable actions and state changes rather than only natural-language answers.

## License

The repository uses Apple's ToolSandbox software license. It permits use, reproduction, modification and redistribution subject to its terms and notice requirements. The repository also states that subcomponents may have separate notices and license terms in `ACKNOWLEDGEMENTS`.

Before redistributing modified code, review the current `LICENSE` and `ACKNOWLEDGEMENTS` files.

## References

- Official ToolSandbox repository: https://github.com/apple-aiml-research/ToolSandbox
- Apple Machine Learning Research page: https://machinelearning.apple.com/research/toolsandbox-stateful-conversational-llm-benchmark
- Lu, J., Holleis, T., Zhang, Y., et al. *ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities*: https://arxiv.org/abs/2408.04682
