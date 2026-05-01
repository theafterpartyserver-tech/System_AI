---
name: codegen_linter_skill
description: code generation with local linter hook
tags: codegen,linter_hook
---

Use this skill when you are asked to write Python code. First, generate the code, then call the `lint_code` tool to check it. Only return the code if the linter passes or if the user explicitly allows minor issues.
