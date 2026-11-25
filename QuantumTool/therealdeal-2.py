import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, Operator


PAULI_X = Operator.from_label("X").data
PAULI_Y = Operator.from_label("Y").data
PAULI_Z = Operator.from_label("Z").data


def get_bloch_vectors(state: Statevector) -> list[np.ndarray]:
    """Compute (x, y, z) Bloch vector for each qubit via partial trace."""
    n = state.num_qubits
    vectors = []
    for q in range(n):
        traced_out = [i for i in range(n) if i != q]
        rho = partial_trace(state, traced_out).data if traced_out else state.to_operator().data
        x = float(np.real(np.trace(rho @ PAULI_X)))
        y = float(np.real(np.trace(rho @ PAULI_Y)))
        z = float(np.real(np.trace(rho @ PAULI_Z)))
        vectors.append(np.array([x, y, z]))
    return vectors


class QuantumToolGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Quantum Gates Visualizer")
        self.root.geometry("1220x780")
        self.root.configure(bg="#111827")

        self.num_qubits = 2
        self.shots = 1000
        self.qc = QuantumCircuit(self.num_qubits)
        self.gate_history: list[tuple] = []

        self.current_vectors = [np.array([0.0, 0.0, 1.0]) for _ in range(self.num_qubits)]
        self.target_vectors = [np.array([0.0, 0.0, 1.0]) for _ in range(self.num_qubits)]
        self.anim_job = None

        self._build_ui()
        self._init_bloch_axes()
        self._refresh_state(animate=False)

    def _build_ui(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#F9FAFB", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#38BDF8")
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=5)

        # Top Control Bar
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Qubits:").pack(side=tk.LEFT, padx=(0, 4))
        self.qubit_var = tk.IntVar(value=2)
        qubit_box = ttk.Combobox(top, textvariable=self.qubit_var, values=[1, 2, 3, 4], width=3, state="readonly")
        qubit_box.pack(side=tk.LEFT, padx=(0, 12))
        qubit_box.bind("<<ComboboxSelected>>", self._on_qubit_count_change)

        ttk.Label(top, text="Target Qubit:").pack(side=tk.LEFT, padx=(0, 4))
        self.target_var = tk.IntVar(value=0)
        self.target_box = ttk.Combobox(top, textvariable=self.target_var, values=[0, 1], width=3, state="readonly")
        self.target_box.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(top, text="Control (CX):").pack(side=tk.LEFT, padx=(0, 4))
        self.ctrl_var = tk.IntVar(value=0)
        self.ctrl_box = ttk.Combobox(top, textvariable=self.ctrl_var, values=[0, 1], width=3, state="readonly")
        self.ctrl_box.pack(side=tk.LEFT, padx=(0, 14))

        for gate in ["H", "X", "Y", "Z", "S", "T"]:
            ttk.Button(top, text=gate, width=4, command=lambda g=gate.lower(): self._add_single_gate(g)).pack(
                side=tk.LEFT, padx=2
            )

        ttk.Button(top, text="CX", width=4, command=self._add_cx).pack(side=tk.LEFT, padx=(6, 2))
        ttk.Button(top, text="Bell (0,1)", command=self._add_bell).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Undo", command=self._undo).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Reset", command=self._reset).pack(side=tk.LEFT, padx=4)

        # Main Split Area
        main = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        main.pack(fill=tk.BOTH, expand=True)

        # Left Panel: Circuit + Statevector + Counts
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        ttk.Label(left, text="Quantum Circuit", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 4))
        self.circuit_text = tk.Text(
            left, width=48, height=13, bg="#1F2937", fg="#E5E7EB", font=("Consolas", 10), relief=tk.FLAT, padx=8, pady=8
        )
        self.circuit_text.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left, text="Statevector & Probabilities", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 4))
        self.state_text = tk.Text(
            left, width=48, height=12, bg="#1F2937", fg="#A7F3D0", font=("Consolas", 10), relief=tk.FLAT, padx=8, pady=8
        )
        self.state_text.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left, text="Sampled Counts (1000 shots)", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 4))
        self.counts_text = tk.Text(
            left, width=48, height=6, bg="#1F2937", fg="#FDE68A", font=("Consolas", 10), relief=tk.FLAT, padx=8, pady=8
        )
        self.counts_text.pack(fill=tk.BOTH, expand=True)

        # Right Panel: Animated 3D Bloch Spheres
        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Animated Bloch Spheres (Per Qubit)", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 4))
        self.fig = Figure(figsize=(7.5, 6.5), dpi=100, facecolor="#111827")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _init_bloch_axes(self) -> None:
        self.fig.clear()
        self.axes = []
        self.quivers = []
        self.coord_texts = []

        cols = 2 if self.num_qubits > 1 else 1
        rows = (self.num_qubits + 1) // 2 if self.num_qubits > 1 else 1

        u = np.linspace(0, 2 * np.pi, 24)
        v = np.linspace(0, np.pi, 16)
        xs = np.outer(np.cos(u), np.sin(v))
        ys = np.outer(np.sin(u), np.sin(v))
        zs = np.outer(np.ones_like(u), np.cos(v))

        for i in range(self.num_qubits):
            ax = self.fig.add_subplot(rows, cols, i + 1, projection="3d")
            ax.set_facecolor("#111827")
            ax.plot_wireframe(xs, ys, zs, color="#374151", linewidth=0.5, alpha=0.45)

            # Axes lines
            ax.plot([-1.15, 1.15], [0, 0], [0, 0], color="#6B7280", linewidth=0.8)
            ax.plot([0, 0], [-1.15, 1.15], [0, 0], color="#6B7280", linewidth=0.8)
            ax.plot([0, 0], [0, 0], [-1.15, 1.15], color="#6B7280", linewidth=0.8)

            # Basis state labels
            ax.text(0, 0, 1.28, "|0⟩", color="#F9FAFB", fontsize=9, ha="center")
            ax.text(0, 0, -1.35, "|1⟩", color="#F9FAFB", fontsize=9, ha="center")
            ax.text(1.28, 0, 0, "|+⟩", color="#9CA3AF", fontsize=8, ha="center")
            ax.text(0, 1.28, 0, "|+i⟩", color="#9CA3AF", fontsize=8, ha="center")

            ax.set_xlim([-1.2, 1.2])
            ax.set_ylim([-1.2, 1.2])
            ax.set_zlim([-1.2, 1.2])
            ax.set_box_aspect([1, 1, 1])
            ax.axis("off")
            ax.set_title(f"Qubit {i}", color="#38BDF8", fontsize=11, pad=2)

            vec = self.current_vectors[i]
            q_arrow = ax.quiver(0, 0, 0, vec[0], vec[1], vec[2], color="#F43F5E", linewidth=2.5, arrow_length_ratio=0.18)
            txt = ax.text2D(
                0.5, 0.02, f"({vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f})", transform=ax.transAxes,
                color="#D1D5DB", fontsize=8.5, ha="center"
            )

            self.axes.append(ax)
            self.quivers.append(q_arrow)
            self.coord_texts.append(txt)

        self.fig.tight_layout()
        self.canvas.draw()

    def _on_qubit_count_change(self, _event=None) -> None:
        self.num_qubits = self.qubit_var.get()
        indices = list(range(self.num_qubits))
        self.target_box["values"] = indices
        self.ctrl_box["values"] = indices
        self.target_var.set(0)
        self.ctrl_var.set(0)
        self._reset()

    def _rebuild_circuit(self) -> None:
        self.qc = QuantumCircuit(self.num_qubits)
        for item in self.gate_history:
            if item[0] == "single":
                getattr(self.qc, item[1])(item[2])
            elif item[0] == "cx":
                self.qc.cx(item[1], item[2])

    def _add_single_gate(self, gate: str) -> None:
        t = self.target_var.get()
        self.gate_history.append(("single", gate, t))
        self._rebuild_circuit()
        self._refresh_state(animate=True)

    def _add_cx(self) -> None:
        c = self.ctrl_var.get()
        t = self.target_var.get()
        if self.num_qubits < 2 or c == t:
            return
        self.gate_history.append(("cx", c, t))
        self._rebuild_circuit()
        self._refresh_state(animate=True)

    def _add_bell(self) -> None:
        if self.num_qubits < 2:
            return
        self.gate_history.append(("single", "h", 0))
        self.gate_history.append(("cx", 0, 1))
        self._rebuild_circuit()
        self._refresh_state(animate=True)

    def _undo(self) -> None:
        if not self.gate_history:
            return
        self.gate_history.pop()
        self._rebuild_circuit()
        self._refresh_state(animate=True)

    def _reset(self) -> None:
        if self.anim_job is not None:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None
        self.gate_history.clear()
        self.qc = QuantumCircuit(self.num_qubits)
        self.current_vectors = [np.array([0.0, 0.0, 1.0]) for _ in range(self.num_qubits)]
        self.target_vectors = [np.array([0.0, 0.0, 1.0]) for _ in range(self.num_qubits)]
        self._init_bloch_axes()
        self._refresh_state(animate=False)

    def _refresh_state(self, animate: bool = True) -> None:
        state = Statevector.from_instruction(self.qc)
        probs = state.probabilities_dict()
        counts = {str(k): int(v) for k, v in state.sample_counts(shots=self.shots).items()}

        # Update Circuit Text
        self.circuit_text.delete("1.0", tk.END)
        self.circuit_text.insert(tk.END, str(self.qc.draw("text")))

        # Update Statevector & Probabilities
        self.state_text.delete("1.0", tk.END)
        lines = ["Basis | Amplitude         | Prob"]
        lines.append("-" * 38)
        for idx, amp in enumerate(state.data):
            bitstr = format(idx, f"0{self.num_qubits}b")
            p = probs.get(bitstr, 0.0)
            lines.append(f"|{bitstr}⟩  | {amp.real:+.3f}{amp.imag:+.3f}j | {p * 100:5.1f}%")
        self.state_text.insert(tk.END, "\n".join(lines))

        # Update Counts
        self.counts_text.delete("1.0", tk.END)
        sorted_counts = dict(sorted(counts.items()))
        self.counts_text.insert(tk.END, f"{sorted_counts}")

        new_targets = get_bloch_vectors(state)
        if not animate:
            self.current_vectors = [v.copy() for v in new_targets]
            self.target_vectors = [v.copy() for v in new_targets]
            self._draw_vectors(self.current_vectors)
        else:
            start_vectors = [v.copy() for v in self.current_vectors]
            self.target_vectors = [v.copy() for v in new_targets]
            self._animate_step(start_vectors, self.target_vectors, step=1, total_steps=18)

    def _animate_step(self, start: list[np.ndarray], end: list[np.ndarray], step: int, total_steps: int) -> None:
        if self.anim_job is not None:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None

        # Smooth ease-out interpolation
        t = step / total_steps
        eased = 1 - (1 - t) ** 3

        interp = [(1 - eased) * s + eased * e for s, e in zip(start, end)]
        self.current_vectors = interp
        self._draw_vectors(interp)

        if step < total_steps:
            self.anim_job = self.root.after(20, self._animate_step, start, end, step + 1, total_steps)

    def _draw_vectors(self, vectors: list[np.ndarray]) -> None:
        for i, vec in enumerate(vectors):
            self.quivers[i].remove()
            norm = np.linalg.norm(vec)
            color = "#38BDF8" if norm < 0.15 else "#F43F5E"
            self.quivers[i] = self.axes[i].quiver(
                0, 0, 0, vec[0], vec[1], vec[2], color=color, linewidth=2.5, arrow_length_ratio=0.18
            )
            status = " (Entangled/Mixed)" if norm < 0.15 else ""
            self.coord_texts[i].set_text(f"({vec[0]:+.2f}, {vec[1]:+.2f}, {vec[2]:+.2f}){status}")
        self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumToolGUI(root)
    root.mainloop()