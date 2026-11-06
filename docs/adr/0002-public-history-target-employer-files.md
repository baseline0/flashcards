# ADR 0002: Remove target-employer files from public git history

**Status:** PROPOSED
**Date:** 2026-11-06
**Deciders:** Mark Alexiuk

## Context

Files tied to a target employer are in the git history of this public repository. The open item is recorded in `TODO.md:23`, a gitignored local backlog. Removing them means rewriting history and force-pushing. Every clone and fork then has to re-fetch. The affected commits are not yet listed in this repo.

## Options

1. Rewrite history to drop the files, then force-push `main`.
2. Keep history, and remove the files from the working tree only.

## Owner question

Do you approve a history rewrite and force push for this repository?

## Consequences

- Option 1: history changes and every clone must re-clone. Forks keep the old data unless they are rewritten too.
- Option 2: the files stay recoverable from public history.
- Either option needs explicit owner approval (ESC-1).
