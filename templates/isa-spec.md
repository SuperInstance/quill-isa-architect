# {SPEC_TITLE}

**Version**: {VERSION}
**Author**: Quill (Architect, SuperInstance Fleet)
**Date**: {DATE}
**Status**: {Draft/Proposed/Approved}

---

## 1. Overview

{What this specification defines and why it exists}

### 1.1 Motivation

{Why this spec is needed — what problem does it solve?}

### 1.2 Scope

{What is in scope and out of scope}

---

## 2. Opcode Encoding

### 2.1 Encoding Format

{Describe the byte-level encoding scheme}

| Byte(s) | Format | Opcode Range | Description |
|---------|--------|-------------|-------------|
| {bytes} | {format} | {range} | {description} |

### 2.2 Opcode Table

| Value | Mnemonic | Operand Encoding | Semantics |
|-------|----------|-----------------|-----------|
| 0x{XX} | {MNEMONIC} | {operands} | {description} |

---

## 3. Operational Semantics

### 3.1 State Model

{Describe the machine state: registers, memory, stack, flags}

### 3.2 Instruction Semantics

For each instruction, define:

**{MNEMONIC}**
- **Before**: {state before execution}
- **After**: {state after execution}
- **Flags affected**: {which flags change}
- **Traps**: {what conditions cause traps}

---

## 4. Interaction with Existing ISA

{How this spec integrates with or extends the existing ISA}

| New Opcode | Existing Conflict? | Resolution |
|-----------|-------------------|------------|
| {opcode} | {yes/no} | {how resolved} |

---

## 5. Conformance Vectors

{Test vectors proving correct implementation}

### Vector 1: {description}
```
Bytecode: {hex bytes}
Expected state: {registers, stack, flags}
Expected output: {output}
```

---

## 6. Migration Guide

{How to migrate from previous ISA version}

---

## Appendix A: Bit-Field Diagrams

{ASCII or table-based bit-field layouts}

---

*Specification authored by Quill — SuperInstance Fleet Architect*
