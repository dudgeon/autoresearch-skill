# Autoresearch Sources & References

Use these sources to stay current with the evolving pattern. If you need to
update this skill's references, check these links first.

## Canonical sources (Karpathy)

| Source | URL | What it contains |
|--------|-----|------------------|
| GitHub repo | https://github.com/karpathy/autoresearch | The original 3-file implementation (train.py, prepare.py, program.md) |
| Announcement tweet | https://x.com/karpathy/status/2030371219518931079 | "I packaged up the autoresearch project..." |
| Initial teaser | https://x.com/karpathy/status/2029701092347630069 | First mention of the 110-change overnight run |
| Results tweet | https://x.com/karpathy/status/2031135152349524125 | "20 changes improved validation loss, all additive" |
| "It's just an idea" | https://x.com/karpathy/status/2031137476438548874 | "you don't use it directly, it's just a recipe/idea" |
| No Priors podcast | Search: "Karpathy No Priors autoresearch loopy era" | Long-form discussion of the pattern and its implications |

## Community adaptations for Claude Code

| Repo | Stars* | Description |
|------|--------|-------------|
| [uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch) | ~600 | Claude Code skill with slash commands (/autoresearch, /autoresearch:plan, /autoresearch:debug). Install into .claude/skills/ and .claude/commands/. |
| [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | — | ARIS ("Auto-Research-In-Sleep"). Cross-model review loops (Claude executor + Gemini/DeepSeek reviewer). 42+ bundled skills. |
| [drivelineresearch/autoresearch-claude-code](https://github.com/drivelineresearch/autoresearch-claude-code) | — | Pure Claude Code skill port, no MCP server. Includes biomechanics case study. |

*Star counts as of March 2026; check repos for current numbers.

## Adaptations for other platforms

| Repo | Platform | Notes |
|------|----------|-------|
| [leo-lilinxiao/codex-autoresearch](https://github.com/leo-lilinxiao/codex-autoresearch) | OpenAI Codex CLI | Resume support, parallel experiments |
| [supratikpm/gemini-autoresearch](https://github.com/supratikpm/gemini-autoresearch) | Gemini CLI | Google Search grounding, 1M-token context, headless mode |
| [davebcn87/pi-autoresearch](https://github.com/davebcn87/pi-autoresearch) | Platform-agnostic | Live metrics dashboard, confidence tracking |

## Generalized frameworks

| Repo | Focus | Key idea |
|------|-------|----------|
| [jmilinovich/goal-md](https://github.com/jmilinovich/goal-md) | Any domain | Agent must first construct a measurable fitness function before optimizing |
| [zkarimi22/autoresearch-anything](https://github.com/zkarimi22/autoresearch-anything) | Prompts, APIs, landing pages, SQL | Generalized "anything with a score" framework |
| [multivmlabs/autoresearcher](https://github.com/multivmlabs/autoresearcher) | npm CLI | `autoresearcher init` / `autoresearcher run --iterations N`, JSONL logs, synthesized RESEARCH.md |

## Curated index

| Repo | Description |
|------|-------------|
| [alvinreal/awesome-autoresearch](https://github.com/alvinreal/awesome-autoresearch) | Comprehensive curated list of all autoresearch implementations, adaptations, and discussions (1,100+ stars). Check this first for new entries. |

## Analysis and commentary

| Source | URL | Focus |
|--------|-----|-------|
| Fortune | https://fortune.com/2026/03/17/andrej-karpathy-loop-autonomous-ai-agents-future/ | "The Karpathy Loop": 700 experiments, business implications |
| VentureBeat | https://venturebeat.com/technology/andrej-karpathys-new-open-source-autoresearch-lets-you-run-hundreds-of-ai | Technical overview and implications |
| The New Stack | https://thenewstack.io/karpathy-autonomous-experiment-loop/ | Distillation of the three primitives |
| DataCamp | https://www.datacamp.com/tutorial/guide-to-autoresearch | Step-by-step tutorial |
| Aakash Gupta (PM perspective) | https://www.news.aakashg.com/p/autoresearch-guide-for-pms | Product management angle |
| DeepWiki (program.md analysis) | https://deepwiki.com/karpathy/autoresearch/3.4-program.md-agent-instructions | Detailed analysis of the prompt structure |

## Updating this skill's references

If the pattern evolves (Karpathy updates the repo, major community shifts):

1. Check [github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)
   for README changes, new files, or structural shifts
2. Check [awesome-autoresearch](https://github.com/alvinreal/awesome-autoresearch)
   for new high-quality implementations
3. Search X/Twitter for `from:karpathy autoresearch` for new commentary
4. Update `references/pattern-overview.md` with any new constraints, best
   practices, or architectural changes
5. Update `templates/autoresearch-prompt.md` if the loop structure changes
