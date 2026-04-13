#!/usr/bin/env python3
"""
Quill Conformance Vector Generator — ISA Test Vector Tool

Generates test vectors for FLUX ISA conformance testing.
Each vector specifies bytecode, expected register state, and expected output.

Usage:
    python3 conformance-generator.py --opcode ADD --format A
    python3 conformance-generator.py --all-core
"""

import argparse
import json
from datetime import datetime, timezone


# FLUX ISA opcode reference (cloud ISA, fixed 4-byte encoding)
OPCODES = {
    # Stack operations (0x01-0x0F)
    "PUSH": {"value": 0x01, "format": "A", "stack_effect": "+1"},
    "POP": {"value": 0x02, "format": "A", "stack_effect": "-1"},
    "DUP": {"value": 0x03, "format": "A", "stack_effect": "+1"},
    "SWAP": {"value": 0x04, "format": "A", "stack_effect": "0"},
    # Arithmetic (0x10-0x1F)
    "ADD": {"value": 0x10, "format": "A", "semantics": "rd = rd + imm"},
    "SUB": {"value": 0x11, "format": "A", "semantics": "rd = rd - imm"},
    "MUL": {"value": 0x12, "format": "A", "semantics": "rd = rd * imm"},
    "DIV": {"value": 0x13, "format": "A", "semantics": "rd = rd / imm"},
    # Register operations (0x20-0x2F)
    "MOV": {"value": 0x20, "format": "B", "semantics": "rd = rs"},
    "CMP": {"value": 0x30, "format": "B", "semantics": "flags = rd - rs"},
    # Control flow (0x40-0x4F)
    "JMP": {"value": 0x41, "format": "C", "semantics": "PC = addr16"},
    "CALL": {"value": 0x40, "format": "C", "semantics": "push PC; PC = addr16"},
    "RET": {"value": 0x02, "format": "A", "semantics": "PC = pop()"},
    # Memory (0x50-0x5F)
    "LD": {"value": 0x50, "format": "D", "semantics": "rd = [addr]"},
    "ST": {"value": 0x51, "format": "D", "semantics": "[addr] = rd"},
    # System
    "NOP": {"value": 0x00, "format": "A", "semantics": "(no operation)"},
    "HALT": {"value": 0x01, "format": "A", "semantics": "stop execution"},
}


def generate_vector(opcode_name: str, description: str, bytecode_hex: str,
                    initial_state: dict, expected_state: dict,
                    expected_output: str = "") -> dict:
    """Generate a single conformance test vector."""
    return {
        "id": f"CV-{opcode_name}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
        "opcode": opcode_name,
        "description": description,
        "bytecode": bytecode_hex,
        "bytecode_bytes": [int(b, 16) for b in bytecode_hex.split() if b],
        "initial_state": initial_state,
        "expected_state": expected_state,
        "expected_output": expected_output,
        "isa_version": "v2",
        "target": "all",  # All runtimes should pass
        "created": datetime.now(timezone.utc).isoformat(),
        "author": "quill",
    }


def generate_core_vectors() -> list:
    """Generate conformance vectors for core opcodes."""
    vectors = []

    # NOP — should do nothing
    vectors.append(generate_vector(
        "NOP", "NOP should leave state unchanged",
        "00 00",  # NOP + HALT
        {"pc": 0, "r0": 0, "r1": 0, "r2": 0, "r3": 0, "sp": 255, "flags": "0000"},
        {"pc": 1, "r0": 0, "r1": 0, "r2": 0, "r3": 0, "sp": 255, "flags": "0000", "halted": True},
    ))

    # ADD — basic addition
    vectors.append(generate_vector(
        "ADD", "ADD r0, 5 should set r0 to 5",
        "10 00 00 05 01",  # ADD r0, 5 + HALT
        {"pc": 0, "r0": 0, "r1": 0, "sp": 255, "flags": "0000"},
        {"pc": 1, "r0": 5, "r1": 0, "sp": 255, "flags": "0000", "halted": True},
    ))

    # MOV — register copy
    vectors.append(generate_vector(
        "MOV", "MOV r1, r0 should copy r0 to r1",
        "20 01 00 00 01",  # MOV r1, r0 + HALT
        {"pc": 0, "r0": 42, "r1": 0, "sp": 255, "flags": "0000"},
        {"pc": 1, "r0": 42, "r1": 42, "sp": 255, "flags": "0000", "halted": True},
    ))

    # JMP — forward jump
    vectors.append(generate_vector(
        "JMP", "JMP 0x0010 should skip to address 16",
        "41 00 00 10 01",  # JMP 0x0010 + HALT (should not reach)
        {"pc": 0, "sp": 255},
        {"pc": 16, "sp": 255, "halted": False},
    ))

    # CMP — set flags
    vectors.append(generate_vector(
        "CMP", "CMP r0=5, r1=5 should set ZF",
        "30 00 01 00 01",  # CMP r0, r1 + HALT (r0=5, r1=5)
        {"pc": 0, "r0": 5, "r1": 5, "sp": 255, "flags": "0000"},
        {"pc": 1, "r0": 5, "r1": 5, "sp": 255, "flags": "0001", "halted": True},  # ZF set
    ))

    return vectors


def main():
    parser = argparse.ArgumentParser(description="Quill Conformance Vector Generator")
    parser.add_argument("--opcode", help="Generate vector for specific opcode")
    parser.add_argument("--format", help="Opcode format (A/B/C/D/E)")
    parser.add_argument("--all-core", action="store_true", help="Generate all core vectors")
    parser.add_argument("--output", "-o", help="Output file (JSON)")
    parser.add_argument("--count", type=int, default=1, help="Number of vectors to generate")
    args = parser.parse_args()

    vectors = []

    if args.all_core:
        vectors = generate_core_vectors()
        print(f"Generated {len(vectors)} core conformance vectors:")
        for v in vectors:
            print(f"  {v['id']}: {v['description']}")
    elif args.opcode:
        info = OPCODES.get(args.opcode.upper())
        if not info:
            print(f"Unknown opcode: {args.opcode}")
            print(f"Known opcodes: {', '.join(sorted(OPCODES.keys()))}")
            return
        print(f"Opcode: {args.opcode} = 0x{info['value']:02X} (Format {info['format']})")
        print(f"Semantics: {info.get('semantics', 'N/A')}")
    else:
        parser.print_help()
        return

    if args.output:
        with open(args.output, "w") as f:
            json.dump(vectors, f, indent=2)
        print(f"\nWritten to {args.output}")


if __name__ == "__main__":
    main()
