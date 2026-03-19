You are solving a Lean 4 formal theorem proving task.

The benchmark file is located at: {filepath}

Your goal: replace every `sorry` placeholder with a correct Lean 4 proof, then verify the file compiles cleanly.

You are allowed to run the Lean prover and to edit the file: run `lean` to check your work, and if it fails or `sorry` remains, modify the code and repeat until the file compiles with no `sorry`.

Steps to follow:

1. Read the file at {filepath}
2. Understand each theorem that contains `sorry`
3. Replace `sorry` with correct Lean 4 proof tactics/terms
4. Verify by running: lean {filepath}
5. If compilation fails or `sorry` remains, read the error output, revise, and retry
6. Repeat until `lean {filepath}` exits with code 0 AND the file has no `sorry`

Useful Lean 4 tactics: `omega`, `ring`, `simp`, `norm_num`, `decide`, `linarith`, `exact`, `apply`, `intro`, `cases`, `induction`, `constructor`, `rfl`, `simp [*]`, `tauto`, `trivial`, `assumption`, `contradiction`.

Important:

- Edit only {filepath}
- Do not create additional files
- The final working proof must be saved in {filepath}
- You are done when lean exits 0 with no `sorry` in the file

Access restriction:

- You may only read and write files inside the current working directory: {allowed_directory}
- Do not access, list, or read any path under the project's `answers/` directory (other than the current working directory).
- You are allowed to run `lean` to check your work, and if it fails or `sorry` remains, modify the code and repeat until the file compiles with no `sorry`.
