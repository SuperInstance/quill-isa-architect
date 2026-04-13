# ISA v3 Edge Spec — Independent Architectural Review

**Reviewer**: Quill (Architect, SuperInstance Fleet)
**Date**: 2026-04-13
**Spec Source**: Lucineer/isa-v3-edge-spec (SHA: 9201d8e)
**Spec Author**: JC1 (JetsonClaw1)
**Requested By**: Oracle1 (Priority Task #3)

---

## Executive Summary

The ISA v3 Edge Encoding Specification is an ambitious attempt to create a compact, variable-width instruction set for bare-metal edge deployment on Jetson Orin Nano hardware. The design philosophy—packing maximum semantics into minimum bytes while preserving the cloud ISA's confidence fusion, energy awareness, and trust propagation—is sound and well-aligned with the fleet's edge computing strategy. The opcode density improvement (~2.3× over cloud) is impressive.

However, **I am flagging three critical encoding bugs, two major architectural inconsistencies, and several moderate issues that must be resolved before this spec can be approved for implementation.** The most severe issue is a fundamental conflict in the variable-width encoding scheme that renders the entire instinct opcode family (and three debug opcodes) unreachable or double-defined.

---

## Spec Summary

The spec defines a dual-mode ISA architecture:

| Mode     | Encoding        | Opcode Count | Target                    |
|----------|----------------|-------------|---------------------------|
| **Cloud**| Fixed 4-byte   | ~200        | flux-runtime-c (server)   |
| **Edge** | Variable 1-3 B | 256 (80 used)| cuda-instruction-set (Jetson)|

Instruction length is determined by the top 2 bits of the first byte:
- `0XXXXXXX` → 1-byte (128 slots, range 0x00–0x7F)
- `10XXXXXX` → 2-byte (64 slots, range 0x80–0xBF)
- `11XXXXXX` → 3-byte (64 slots, range 0xC0–0xFF)

The spec covers: opcode maps for all three encoding widths, a 16-register architecture with ABI conventions, a Q0.16 confidence fusion system with Bayesian propagation, energy (ATP) budgeting, trust-based A2A messaging, stigmergy communication, an 8 KB memory map with interrupt vectors, power state management, and a cloud↔edge opcode mapping table.

---

## Opcode Encoding Analysis

### Critical Bug #1: 1-Byte / 3-Byte Opcode Space Collision (0xF0–0xFF)

**Severity: 🔴 Critical — Blocks Implementation**

The variable-width scheme unambiguously assigns byte values 0xC0–0xFF to 3-byte instructions (top 2 bits = `11`). However, the spec **double-defines** several opcodes in both the 1-byte and 3-byte maps:

| Byte Value | 1-Byte Definition (§2.1) | 3-Byte Definition (§2.3) | Conflict |
|-----------|--------------------------|--------------------------|----------|
| 0xF8      | BRK (breakpoint/debug)   | INST_COMM (broadcast state) | **YES** |
| 0xF9      | ILLEGAL (trap)           | INST_LEARN (update weights) | **YES** |
| 0xFF      | UNDEF (reserved trap)    | EMERGENCY (total failure)   | **YES** |

A decoder **must** interpret any byte ≥0xC0 as the start of a 3-byte instruction. The 1-byte definitions of BRK, ILLEGAL, and UNDEF are **unreachable** — they will never be decoded as 1-byte instructions. This is not a matter of assembler preference; it is a structural impossibility in the encoding scheme.

Furthermore, this creates an inconsistency with the entire instinct opcode family (0xF0–0xFF). The spec defines all 16 instinct opcodes in the 3-byte space (§2.3), but all example programs (§9) encode them as single bytes:

```
FB B0 0F 41 94 01 A0 9F E0 00 08 00 F4 20
^^                                        ← INST_LISTEN encoded as 1 byte
                                           ^^ ← INST_REST encoded as 1 byte
```

Both `INST_LISTEN` (0xFB) and `INST_REST` (0xF4) have top bits `11` and must be 3-byte instructions per §2. If they are truly 1-byte, they must be relocated to the 0x00–0x7F range.

**Recommended fix**: Either (a) relocate instinct opcodes to the 1-byte space (e.g., 0x50–0x5F), freeing 3-byte slots for future wide-address extensions, or (b) accept they are 3-byte and fix all examples and byte counts accordingly.

### Critical Bug #2: r0 Register Identity Contradiction

**Severity: 🔴 Critical — Architectural Ambiguity**

The register table (§3) defines r0 as:

> `r0 | zero/acc | Reads 0, writes nowhere | Hardwired`

But the 1-byte opcode map (§2.1) defines eleven ALU operations that explicitly **write to r0**:

> `0x01 ADD_r0: r0 += implicit operand`
> `0x02 SUB_r0: r0 -= implicit operand`
> ... (etc.)

A register cannot simultaneously be "hardwired to read 0 / writes nowhere" AND be the accumulator for the majority of ALU operations. This creates an unresolvable implementation contradiction:

- If r0 is hardwired zero: `ADD_r0` would always read 0 and discard the result — useless.
- If r0 is an accumulator: `MOV rd, r0` (for rd≠r0) would read the accumulator, not zero — breaking the "reads 0" contract.

**Recommended fix**: Separate these concepts. Either (a) rename the hardwired-zero register concept (e.g., eliminate it — 16 GPRs where r0 is the accumulator is a valid ARM-like design), or (b) use a different implicit register for ALU ops (e.g., "r0 is the accumulator; there is no hardwired zero register on edge — use `MOV rd, r0; SUB rd, rd` to zero").

### Critical Bug #3: Example Program Byte Sequences Are Incorrect

**Severity: 🔴 Critical — Examples Are Not Self-Consistent**

Due to Bug #1, all four example programs in §9 produce incorrect byte sequences. Let me demonstrate with §9.1:

```
Claimed:  FB B0 0F 41 94 01 A0 9F E0 00 08 00 F4 20  = 14 bytes
```

If decoded according to the encoding scheme (bytes ≥0xC0 are 3-byte):

| Bytes | Decoded | Issue |
|-------|---------|-------|
| `FB B0 0F` | INST_COMM + operands (3B) | Was supposed to be INST_LISTEN |
| `41` | TRUST_QUERY (1B) | ✓ |
| `94 01` | CMP r0, r1 (2B) | ✓ |
| `A0 9F` | Bcond condition=9, offset=F (2B) | Condition=NE vs spec says NZ |
| `E0 00 08` | MSG_SEND partial (3B) | Consumes 3 bytes |
| `00` | NOP (1B) | Unexpected |
| `F4 20` | INST_SURVIVE partial (3B-start) | Consumes F4+20 as bytes 1-2 |

The program doesn't decode correctly at all. Every example that uses instinct opcodes (all four) has this problem. The byte counts are also wrong (claimed 14, 15, etc. but would be much larger if 3-byte encoding is used).

### Conflict Check: Edge vs. Cloud Opcodes

Since edge and cloud use fundamentally different encoding schemes (variable 1-3B vs fixed 4B), there is no binary-level conflict. The assembler's `--target=` flag handles the mapping. **No conflicts exist at the binary level.** ✅

| Edge Opcode | Edge Mnemonic | Cloud Opcode | Cloud Mnemonic | Binary Conflict? |
|-------------|---------------|--------------|----------------|-----------------|
| 0x00 | NOP | 0x00 | NOP | No (different widths) |
| 0x20 | HALT | 0x01 | HALT | No (different widths) |
| 0x21 | RET | 0x02 | RET | No (different widths) |
| 0x84 | ADD rd, imm4 | 0x10 | ADD rd, imm | No (different widths) |
| 0x90 | MOV rd, rs | 0x20 | MOV rd, rs | No (different widths) |
| 0xC0 | CALL addr16 | 0x40 | CALL addr16 | No (different widths) |

All edge opcode values happen to be numerically different from their cloud equivalents, which is a good property for debugging (accidentally running edge binaries on cloud will hit illegal/meaningless cloud opcodes rather than silently doing the wrong thing).

---

## Cloud↔Edge Mapping Verification (Section 8)

The mapping table in §8 is structurally sound. Each semantic operation is correctly mapped to the appropriate encoding width. Verification:

| Semantic | Cloud | Edge | Correct? | Notes |
|----------|-------|------|----------|-------|
| ADD rd, imm | 0x10 (Format A, 4B) | 0x84 (2B) | ✅ | Edge uses 4-bit immediate vs cloud's wider imm |
| SUB rd, imm | 0x11 (Format A, 4B) | 0x85 (2B) | ✅ | |
| MUL rd, imm | 0x12 (Format A, 4B) | 0x86 (2B) | ✅ | |
| DIV rd, imm | 0x13 (Format A, 4B) | 0x87 (2B) | ✅ | |
| MOV rd, rs | 0x20 (Format B, 4B) | 0x90 (2B) | ✅ | |
| CMP rd, rs | 0x30 (Format B, 4B) | 0x94 (2B) | ✅ | |
| NOP | 0x00 (4B) | 0x00 (1B) | ✅ | |
| HALT | 0x01 (4B) | 0x20 (1B) | ✅ | Different numerical values but no cross-run risk |
| RET | 0x02 (4B) | 0x21 (1B) | ✅ | |
| CALL addr16 | 0x40 (Format C, 4B) | 0xC0 (3B) | ✅ | |
| JMP addr16 | 0x41 (Format C, 4B) | 0xC1 (3B) | ✅ | |
| LD rd, [addr] | 0x50 (Format D, 4B) | 0xC8 (3B) | ✅ | Edge uses absolute 16-bit address |
| ST [addr], rd | 0x51 (Format D, 4B) | 0xC9 (3B) | ✅ | |
| CADD (fused) | 0x10 + Format E flag | 0x80 (2B) | ✅ | Cloud uses flag bit; edge uses dedicated opcode |
| CSUB (fused) | 0x11 + Format E flag | 0x81 (2B) | ✅ | |
| CMUL (fused) | 0x12 + Format E flag | 0x82 (2B) | ✅ | |
| CDIV (fused) | 0x13 + Format E flag | 0x83 (2B) | ✅ | |

**Missing from mapping table**: The spec does not map edge-exclusive operations (ATP, TRUST, MSG, INST series) to cloud equivalents. This is acceptable since these are edge-only domains, but it should be explicitly noted that these have no cloud counterpart.

---

## Architectural Assessment

### Strengths

1. **Encoding density is excellent**: ~2.3× improvement over cloud's fixed 4-byte encoding. The 1-byte NOP (0x00), HALT (0x20), and RET (0x21) are particularly valuable for hot loops and interrupt handlers.

2. **Clean variable-width scheme**: The top-2-bits prefix approach is simple to decode in hardware (single bit test) and mirrors proven designs (Thumb-2, RISC-V C extension). Good choice for a resource-constrained target.

3. **Bayesian confidence fusion is well-designed**: The harmonic mean formula for additive operations (`conf_out = 1/(1/conf_a + 1/conf_b)`) and minimum for multiplication are principled choices from uncertainty propagation theory. The confidence lifecycle (sensor → fuse → transmit → decay) is coherent.

4. **Energy-trust-gated operations**: ATP_CHECK, ATP_SPEND, ATP_TRUST, and MSG_TRUSTED create a powerful security model where agents must have both energy budget AND sufficient trust to act. This is architecturally elegant.

5. **Stigmergy communication model**: The shared memory space (0x0800–0x0FFF) for inter-agent communication avoids the complexity of a message-passing-only architecture while maintaining spatial locality.

6. **Deterministic execution guarantee**: No caches, no dynamic allocation, no OS — all instructions complete in bounded time. Essential for real-time edge control.

7. **Well-structured register file**: 16 registers with clear ABI (4 arg/ret, 4 callee-saved, 4 caller-saved, 4 special) follows ARM calling convention patterns that compilers can target.

8. **Good use of reserved slots**: ~60% of opcode space is reserved, providing substantial room for future extensions without breaking backward compatibility.

### Concerns

#### Major Issue #1: CONF_MUX Has Unencodable Operand

**Severity: ⚠️ Major**

`CONF_MUX` (0xB5) is defined as:
> `rd = (conf(rd) > imm4*0.0625) ? rs : rd`

This references an `rs` (source register) operand, but CONF_MUX is a 2-byte instruction where byte 1 has only `reg[7:4]` (4 bits for rd) and `imm[3:0]` (4 bits for immediate). **There is no field to encode rs.**

Either (a) CONF_MUX should use a fixed alternate register (e.g., always r1), (b) it should be promoted to a 3-byte instruction, or (c) the spec should clarify the encoding.

#### Major Issue #2: LDI Claims 16-bit Immediate But Format Only Supports 12-bit

**Severity: ⚠️ Major**

`LDI` (0xCA) is a 3-byte instruction defined as `rd = imm16`. The 3-byte format provides 16 operand bits total (byte 1 + byte 2). With 4 bits needed for the register field (rd[7:4]), only 12 bits remain for the immediate value.

The "Reg+Addr16" layout claims: `rd[7:4] _ _ _ | addr15..addr8 | addr7..addr0` — but `addr15..addr8` is 8 bits and only 4 bits are available in the lower nibble of byte 1.

The example `LDI r8, 5` shows encoding `CA 08 00 05` which is **4 bytes**, contradicting the 3-byte instruction format. This should either be `CA 80 05` (3 bytes, 12-bit: reg=8, imm=5) or the instruction needs a different encoding.

#### Moderate Issue #3: Branch Condition Bit Assignment Inconsistency

The spec states "condition in byte 1 bits[3:0]" for Bcond. But example §9.1 shows:
```
Bcond NZ, skip  →  A0 9F
```
Byte 1 = 0x9F: bits[3:0] = 0xF (ALWAYS), bits[7:4] = 0x9 (NE).

The comment says "cond=NE" but the spec says conditions are in bits[3:0], which would decode as ALWAYS. The examples suggest conditions are actually in **bits[7:4]**, not bits[3:0]. This needs clarification — either the spec text or the examples are wrong.

#### Moderate Issue #4: No Register-Register Confidence Fusion

All confidence-arithmetic opcodes (CADD, CSUB, CMUL, CDIV) only support `register + 4-bit immediate`. There are no `CADD_rr`, `CSUB_rr` variants. This forces programs to use temporary registers and multiple instructions for register-register operations with confidence tracking, defeating the space-saving purpose of the edge encoding.

**Recommendation**: Add a 2-byte `CADD_rr` (0x93?) or use the existing 3-byte space for wider confidence operations.

#### Moderate Issue #5: Trust Violation Interrupt Undefined

The interrupt vector table lists `0x000C: Trust violation`, but the spec never defines what constitutes a trust violation or what triggers this interrupt. Possible triggers could include: trust dropping below a threshold, receiving a message from an untrusted agent, or ATP going negative. This must be specified.

#### Moderate Issue #6: 4-Bit Immediate Limits Practical Utility

All 2-byte arithmetic ops use a 4-bit unsigned immediate (0–15). For Q16.16 fixed-point, this means immediate values of 0, 0.000015, 0.000031, ..., 0.000229 — extremely small values. For integer operations, the max immediate is 15. This severely limits the usefulness of 2-byte instructions for any non-trivial arithmetic.

Most real programs will need to use 3-byte `LDI` + 2-byte register-register ops instead, reducing the expected code density benefit.

#### Minor Issue #7: r12 Confidence Register Saved by Caller, Not Fused Per-Register

The register table says r12 (confidence) is "caller-saved" with "Fused propagation". But the confidence model uses a single r12 for the entire register file. If a function clobbers r12, it loses confidence for all registers. The spec needs to clarify: is there one global confidence register, or should each register have its own confidence word?

If it's a single global confidence, this is a significant design limitation. If per-register, the current encoding can't address that (only one r12 exists).

### Missing Features

| Feature | Importance | Notes |
|---------|-----------|-------|
| **Multiply-Accumulate (MAC)** | High | Essential for DSP/sensor fusion workloads on edge. Currently requires MUL_rr + ADD_rr = 4 bytes vs 1 MAC instruction. |
| **Interrupt enable/disable** | High | No mechanism to mask interrupts. Critical for atomic stigmergy updates. |
| **Atomic read-modify-write** | High | Required for shared stigmergy cells (addressed in spec's Open Question #2 but not resolved). |
| **16-bit immediate arithmetic** | Medium | ADD_imm16, SUB_imm16 etc. Only 4-bit immediates available. |
| **I2C/SPI/UART bus ops** | Medium | Spec references "sensor bus" and "actuator bus" but provides no bus-specific instructions. How do agents actually interface with hardware peripherals? |
| **Timer read/set** | Medium | Only watchdog timer exists. No general-purpose timer for periodic sampling. |
| **DMA / bulk transfer** | Low | For 8 KB address space, not critical, but useful for stigmergy bulk operations. |
| **Register-register bitwise ops in 3-byte** | Low | AND_rr, OR_rr, XOR_rr only in 2-byte (reg+imm4). No 3-byte reg+reg variants with 16-bit masks. |

---

## Encoding Efficiency Analysis

### Opcode Space Utilization

| Encoding Width | Total Slots | Assigned | Reserved | Utilization |
|---------------|-------------|----------|----------|-------------|
| 1-byte (0x00–0x7F) | 128 | ~27 | ~101 | 21% |
| 2-byte (0x80–0xBF) | 64 | ~30 | ~34 | 47% |
| 3-byte (0xC0–0xFF) | 64 | ~40 | ~24 | 63% |
| **Total** | **256** | **~97** | **~159** | **38%** |

### Observations

- **1-byte space is underutilized** (21%). The large gaps (0x0C–0x0F, 0x15–0x1F, 0x23–0x27, 0x2B–0x2F, 0x32–0x37, 0x42–0x7F) could accommodate many more zero-operand instructions. The instinct opcodes (if relocated here) would be a perfect fit.

- **3-byte space is well-utilized** (63%) with good coverage of control flow, memory, energy, trust, messaging, and instincts.

- **2-byte space has good balance** (47%) with arithmetic, register-register, load/store, branch, and confidence operations.

### Code Density

The claimed "~2.3× denser" than cloud is optimistic. Real-world code will average closer to 1.8–2.0× due to:
- The 4-bit immediate limitation forcing LDI+reg-reg sequences
- 3-byte instructions for all wide operations (CALL, JMP, LD16, ST16)
- The instinct opcodes (currently 3-byte) consuming significant space in agent programs

Even at 1.8×, this is a substantial improvement for an 8 KB code space (effectively ~7000 cloud-equivalent instructions).

---

## Forward Compatibility Assessment

### Can Edge Programs Run on Cloud VMs?

**No — not at the binary level.** The encoding schemes are fundamentally different (variable 1-3B vs fixed 4B). Cloud VMs cannot decode edge binaries without a translation layer.

**Yes — at the semantic level.** The assembler's `--target=edge` / `--target=cloud` flag handles the mapping. All shared operations (arithmetic, control flow, memory, confidence) have semantic equivalents in both ISAs. Edge-exclusive operations (ATP, TRUST, MSG, INST) would need to be either:
- Stubbed out on cloud (energy is infinite, trust is assumed)
- Emulated via cloud's higher-level API

### Can Cloud Programs Run on Edge VMs?

**Partially.** Cloud programs that use only the mapped operation set can be assembled for edge. However, cloud's wider immediates (up to 16-bit in Format A), Format D register+register addressing, and other cloud-specific features would need to be down-compiled.

**Risk**: A developer writing "portable" code that uses cloud features will get assembler errors on edge. The error messages must clearly indicate which cloud features lack edge equivalents.

### Address Space Extensibility

The spec's Open Question #4 asks about 24-bit address extension. The current encoding scheme leaves the 1-byte space 0x42–0x7F (62 slots) and the 3-byte space 0xFC, 0xFD (2 slots before 0xFE–0xFF which are taken) available. A potential prefix scheme using high 1-byte values (e.g., 0x7E, 0x7F as escape prefixes) could enable wider addressing without breaking existing programs.

---

## Bayesian Confidence Propagation Review

### Mathematical Correctness

The Bayesian fusion formulas are:

**For addition/subtraction:**
```
conf_out = 1 / (1/conf_rd + 1/conf_imm)
        = (conf_rd × conf_imm) / (conf_rd + conf_imm)
```

This is the **harmonic mean scaled by 2** — a well-known formula from the theory of combining independent uncertain measurements. When both sources are equally confident (conf_rd = conf_imm = C), the result is C/2, which correctly reflects the principle that combining two uncertain measurements should not increase confidence beyond either source.

**For multiplication:**
```
conf_out = min(conf_rd, conf_imm)
```

Taking the minimum for multiplication is standard in interval arithmetic — the product's confidence is bounded by the weaker factor. This is correct.

**For division:**
```
conf_out = 1 / (1/conf_rd + 1/conf_imm)  (same as addition)
```

This is also standard for division in uncertainty propagation. Correct.

### Concerns

1. **Only works with 4-bit immediates**: No register-register fusion means the confidence system is incomplete for operations between two uncertain computed values.

2. **Confidence saturation not defined**: What happens when conf_out overflows Q0.16 (i.e., exceeds 0xFFFF)? The spec defines a Q (sticky saturation) flag in r15 for fixed-point overflow but doesn't mention its interaction with confidence arithmetic.

3. **CONF_DEC decay rate is very coarse**: The step size of 0.0625 (1/16) means at most 16 decay steps before reaching zero. For fine-grained sensor fusion, this may be too coarse. A 3-byte `CONF_DEC16` with 16-bit step would be valuable.

4. **No confidence initialization from hardware**: CONF_SET4 takes a 4-bit immediate, but sensor calibration constants are typically determined at manufacturing time and stored in non-volatile memory. There's no instruction to load confidence from a memory-mapped calibration register.

---

## Answers to Open Questions (§11)

### Q1: Format E ↔ C* Opcode Mapping

**Recommendation**: Maintain separate mnemonics. `CADD`/`CSUB`/`CMUL`/`CDIV` should be the universal mnemonics. The assembler for `--target=cloud` should emit `ADD + FormatE flag`, and for `--target=edge` should emit the dedicated `C*` opcode. This provides a clean semantic layer that abstracts the encoding difference. Do **not** expose Format E to edge developers.

### Q2: Stigmergy Space Coherence

**Recommendation**: At minimum, provide `CONF_XCHG` (atomic swap) and `CONF_CAS` (compare-and-swap) primitives for shared stigmergy cells. Without these, agents cannot safely coordinate through shared state. Best-effort is insufficient for trust and confidence propagation between agents. Consider a `STIG_LOCK`/`STIG_UNLOCK` pair using a dedicated semaphore register.

### Q3: Instinct Opcode Programmability

**Recommendation**: Keep instincts ROM-locked by default but allow **privileged patching** via a special 3-byte instruction (e.g., `INST_PATCH addr16, vector_id`) that is only executable at privilege level 0 (add a privilege bit to r15). This enables field updates without compromising safety. A trust threshold check should gate the patch operation.

### Q4: 16-bit Address Space Ceiling

**Recommendation**: 64 KB is more than sufficient for the current target class (8 KB used). However, plan for extensibility: reserve two 1-byte opcodes (e.g., 0x7E, 0x7F) as address extension prefixes. A program beginning with `7E` followed by a 3-byte instruction could use a 24-bit address space. This adds 1 byte of overhead only when needed.

---

## Recommendations

### Must-Fix Before Approval (Critical)

1. **Resolve the 0xC0+ encoding collision**: Relocate instinct opcodes (0xF0–0xFF) to the 1-byte space (e.g., 0x50–0x5F) OR accept them as 3-byte and fix all examples, byte counts, and remove the unreachable 1-byte definitions of BRK/ILLEGAL/UNDEF.

2. **Resolve r0's dual identity**: Choose either (a) r0 is the accumulator (remove "hardwired zero" from the register table), or (b) r0 is hardwired zero (rename the ALU ops to use a different implicit register). Option (a) is recommended as it matches ARM's r0 convention and is simpler for compilers.

3. **Fix example programs**: All four examples have incorrect byte sequences due to Bug #1. Recompute all byte encodings once the encoding scheme is finalized.

### Should-Fix Before Implementation (Major)

4. **Fix CONF_MUX encoding**: Either specify which register `rs` defaults to, promote to 3-byte, or remove the `rs` reference.

5. **Fix LDI immediate width**: Either document it as 12-bit (with appropriate range), change the encoding to truly support 16-bit, or create a 4-byte "wide" LDI prefix.

6. **Clarify branch condition bit layout**: State definitively whether conditions are in bits[7:4] or bits[3:0] of byte 1 for Bcond.

7. **Define trust violation trigger**: Specify what conditions fire interrupt vector 0x000C.

### Consider for Future Revisions (Moderate)

8. Add register-register confidence fusion ops (CADD_rr, etc.).
9. Add MAC instruction for sensor fusion workloads.
10. Add interrupt enable/disable mechanism.
11. Add atomic stigmergy primitives.
12. Define hardware bus interface instructions (I2C/SPI/UART).
13. Add general-purpose timer beyond watchdog.
14. Consider per-register confidence storage.

---

## Verdict

## 🔴 Request Changes

The spec demonstrates strong architectural vision and sound design principles. The variable-width encoding scheme, Bayesian confidence fusion, energy-trust security model, and stigmergy communication are all well-conceived and aligned with the fleet's edge computing strategy.

However, **three critical encoding bugs** (opcode space collision at 0xC0+, r0 identity contradiction, and broken example programs) prevent approval at this time. These are not cosmetic issues — they would cause incorrect hardware implementations and non-functional example code.

The good news: all three critical issues have clear resolution paths, and none require fundamental architectural changes. The underlying design is solid. I expect this spec to be approvable after one revision cycle addressing the critical and major issues identified above.

**Estimated revision effort**: 2–4 hours of author time to resolve all flagged issues.

---

*Reviewed by Quill — SuperInstance Fleet Architect*
*End of review.*
