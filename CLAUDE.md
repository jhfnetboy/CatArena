# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

CatArena is a **greenfield repository**. At present it contains only project scaffolding — no application source, no `package.json`, no build/test tooling. The details below describe what is established so far; expand this file as real code and commands land.

## Established conventions

- **Package manager: pnpm.** The `.gitignore` is a Node.js template and specifically ignores `.pnpm-store`, so this is a Node/JavaScript/TypeScript project managed with pnpm. Use `pnpm` (not `npm` or `yarn`).
- **License: Apache 2.0** (see `LICENSE`).

## Nezha task orchestration

`.nezha/config.toml` configures [Nezha](https://github.com/hanshuaikang/nezha), a task runner that dispatches work to AI agents. Key settings:

- Default agent: `claude`
- Default permission mode: `ask`
- Nezha also auto-generates git commit messages via an AI agent using the prompt in `[git].commit_prompt`.

That commit prompt defines the repo's **commit message convention** — follow it for hand-written commits too:

- Imperative mood ("Add feature", not "Added feature")
- First line: `type(scope): short summary` (≤50 chars), where type ∈ `feat, fix, docs, style, refactor, test, chore`
- Optional blank line + brief body explaining what and why

## When adding tooling

Once the project takes shape, document here the concrete commands that are not discoverable from a glance — especially: the build command, lint command, how to run the full test suite, and **how to run a single test** — plus the high-level architecture that spans multiple files.


---


---

## 狗头协同（Goutou Multi-Repo Coordination）

This repo participates in the Goutou coordination system. Config is in `.goutou.json` (gitignored).

### Skills（全局已安装，直接用）

```bash
/goutou                   # 查看并回复分配给本仓库的协同任务（单次）
/loop 5m /goutou          # 每 5 分钟自动轮询
/goutou-commander <需求>  # 发起跨仓库协同任务（任意仓库均可）
/goutou-status            # 查看全局任务状态矩阵（只读）
```

### 前置条件（已满足）

- `seeder` MCP 已在 `~/.claude.json` 全局配置
- `.goutou.json` 已在本仓库根目录（含 `coordProjectId`）
- 所有 skill 已安装至 `~/.claude/skills/`

### 协同流程

1. 任意仓库 `/goutou-commander <需求>` → Seeder 创建任务并路由到相关仓库
2. 各仓库 `/loop 5m /goutou` → 自动发现并回复任务
3. `/goutou-converge`（在 goutou 仓库）→ 汇总结论、更新任务状态