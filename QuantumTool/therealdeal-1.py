from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def print_status(qc: QuantumCircuit, shots: int = 1000) -> None:
    state = Statevector.from_instruction(qc)
    probs = {k: round(float(v), 4) for k, v in state.probabilities_dict().items()}
    counts = {str(k): int(v) for k, v in state.sample_counts(shots=shots).items()}

    print("\n" + "=" * 45)
    print("Circuit:")
    print(qc.draw("text"))
    print("\nStatevector:")
    print(state.draw("text"))
    print(f"\nProbabilities: {probs}")
    print(f"Sampled counts ({shots} shots): {counts}")
    print("=" * 45)


def run_tool() -> None:
    while True:
        raw_qubits = input("Number of qubits (1-4, default 2): ").strip()
        if not raw_qubits:
            num_qubits = 2
            break
        if raw_qubits.isdigit() and 1 <= int(raw_qubits) <= 4:
            num_qubits = int(raw_qubits)
            break
        print("Enter an integer between 1 and 4.")

    qc = QuantumCircuit(num_qubits)
    shots = 1000

    print(
        "\nCommands:\n"
        "  h <q>        - Hadamard gate on qubit q\n"
        "  x <q>        - Pauli-X (bit flip) on qubit q\n"
        "  z <q>        - Pauli-Z (phase flip) on qubit q\n"
        "  cx <c> <t>   - CNOT gate (control c, target t)\n"
        "  bell         - Preset Bell state: h 0, cx 0 1\n"
        "  shots <n>    - Set shot count (default 1000)\n"
        "  reset        - Clear circuit back to |0...0>\n"
        "  quit         - Exit tool"
    )
    print_status(qc, shots)

    while True:
        cmd = input("\n> ").strip().lower().split()
        if not cmd:
            continue

        op = cmd[0]

        if op in {"quit", "exit", "q"}:
            print("Exiting QuantumTool.")
            break

        if op == "reset":
            qc = QuantumCircuit(num_qubits)
            print("Circuit reset.")
            print_status(qc, shots)
            continue

        if op == "bell":
            if num_qubits < 2:
                print("Bell state requires at least 2 qubits.")
                continue
            qc.h(0)
            qc.cx(0, 1)
            print_status(qc, shots)
            continue

        if op == "shots":
            if len(cmd) == 2 and cmd[1].isdigit() and int(cmd[1]) > 0:
                shots = int(cmd[1])
                print(f"Shots set to {shots}.")
                print_status(qc, shots)
            else:
                print("Usage: shots <positive_integer>")
            continue

        if op in {"h", "x", "z"}:
            if len(cmd) != 2 or not cmd[1].isdigit():
                print(f"Usage: {op} <qubit_index>")
                continue
            target = int(cmd[1])
            if not (0 <= target < num_qubits):
                print(f"Qubit index must be between 0 and {num_qubits - 1}.")
                continue
            getattr(qc, op)(target)
            print_status(qc, shots)
            continue

        if op == "cx":
            if len(cmd) != 3 or not (cmd[1].isdigit() and cmd[2].isdigit()):
                print("Usage: cx <control_qubit> <target_qubit>")
                continue
            ctrl, targ = int(cmd[1]), int(cmd[2])
            if ctrl == targ or not (0 <= ctrl < num_qubits and 0 <= targ < num_qubits):
                print(f"Control and target must be distinct qubits in 0..{num_qubits - 1}.")
                continue
            qc.cx(ctrl, targ)
            print_status(qc, shots)
            continue

        print("Unknown command. Try: h 0, x 1, z 0, cx 0 1, bell, shots 500, reset, quit")


if __name__ == "__main__":
    run_tool()

