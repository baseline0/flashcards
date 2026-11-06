# ADR 0004: Keep or replace the target-employer job description as a glossary source

**Status:** PROPOSED
**Date:** 2026-11-06
**Deciders:** Mark Alexiuk

## Context

`data/raw_glossaries/data_engineering/enterprise_semantic_layer.json:276-277` cites a target-employer job description as a source for a glossary entry. `TODO.md:25` records the open choice: keep or archive. The job description is a private source, and the repo is public.

## Options

1. Keep the citation as it is.
2. Replace the citation with a neutral, citable source, and archive the job description reference.

## Owner question

Should the job description stay cited as a source for this glossary entry?

## Consequences

- Option 1: the entry keeps a private source that is visible in a public repo.
- Option 2: the entry needs a new source and a tier classification under ADR 0001.
