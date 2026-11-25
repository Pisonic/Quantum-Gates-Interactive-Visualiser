# Interactive Quantum Gates
## What It Is
A basic interactive GUI and a primordial terminal based application that allows you to understand visually, the basic quantum gates. Built with python.
'therealdeal-1.py' is a rudimentary predecessor to 'therealdeal-2' (evident), there also exists a scratchpad for my initial experiments with qiskit.


## What It Can Do
1. **Circuit Construction and Manipulation**: Options to use X, Y, Z, H, S, T and CX (CNOT) gates, preset Bell States, undo/reset qubit controls and multi-qubit ops.
2. **Statevector and Shot Simulation**: You can inspect the exact statevector amplitudes, basis-state probabilities and shot based sampling counts.
3. **Interactive Bloch Spheres**: See them undergo changes in real time!

_Worth mentioning that the aforementioned are the features of 'therealdeal-2.py' only. There are no spheres in the primordial predecessor._


## Libraries Used
+ Tkinter
+ matplotlib
+ qiskit
+ numpy


## X, Y, Z, H, S, T and CX (CNOT) Gates
  ### Single Qubit Gates
1. **X Gate (Pauli-X/Bit flip)**: The quantum NOT gate. Flips $\vert{}0\rangle \leftrightarrow \vert{}1\rangle$ and leaves $\vert{}+\rangle$ unchanged. On the Bloch sphere, it is a $\pi$ rotation around the $X$-axis.
2. **Y Gate (Pauli-Y)**: Combines a bit flip and a phase flip (up to a global phase): maps $\vert{}0\rangle \to i\vert{}1\rangle$ and $\vert{}1\rangle \to -i\vert{}0\rangle$. On the Bloch sphere, it is a $\pi$ rotation around the $Y$-axis.
3. **Z Gate (Pauli-Z/Phase flip)**: Leaves $\vert{}0\rangle$ unchanged and flips the relative phase of $\vert{}1\rangle$ to $-\vert{}1\rangle$ (so $\vert{}+\rangle \leftrightarrow \vert{}-\rangle$). Measurement probabilities in the $\{\vert{}0\rangle, \vert{}1\rangle\}$ basis don't change immediately, but relative phase drives interference later. On the Bloch sphere, it is a $\pi$ rotation around the $Z$-axis.
4. **S Gate (Phase/$\sqrt{Z}$)**: Applies a $\frac{\pi}{2}$ phase shift to $\vert{}1\rangle$ ($\vert{}0\rangle \to \vert{}0\rangle$, $\vert{}1\rangle \to i\vert{}1\rangle$). Two S gates equal one Z gate ($S^2 = Z$), and on the Bloch sphere it rotates around the $Z$-axis by $90^\circ$.
5. **T Gate ($\pi/8$ Gate / $\sqrt{S}$)**: Applies a $\frac{\pi}{4}$ phase shift to $\vert{}1\rangle$ ($\vert{}0\rangle \to \vert{}0\rangle$, $\vert{}1\rangle \to e^{i\pi/4}\vert{}1\rangle$). Two T gates equal S ($T^2 = S$), and it is a key building block for universal quantum gate sets alongside Clifford gates.

  ### Two Qubit Gate
1. **CX Gate(CNOT/Controlled Not)**:Flips (X) the target qubit if and only if the control qubit is in state $\vert{}1\rangle$ ($\vert{}00\rangle \to \vert{}00\rangle$, $\vert{}01\rangle \to \vert{}01\rangle$, $\vert{}10\rangle \to \vert{}11\rangle$, $\vert{}11\rangle \to \vert{}10\rangle$). When paired with H on the control qubit, it generates entanglement (such as Bell states), where the combined two-qubit state cannot be factored into independent single-qubit states.
