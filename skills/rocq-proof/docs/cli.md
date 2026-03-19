# Rocq CLI

The `rocq` CLI is the main entry point for interacting with the Rocq Prover from your terminal. It routes commands to various underlying tools for interactive evaluation, batch compilation, project building, and verification.

### 1. Primary Subcommands

The CLI separates interactive sessions from batch compilation.

- **`rocq repl`** (or `rocq top`): Starts the interactive read-eval-print-loop (toplevel). This is the environment you use to feed commands to Rocq line-by-line.
- **`rocq compile`** (or `rocq c`): Compiles a Rocq script (`.v` file) into a compiled object file (`.vo` file). The last component of the filename must be a valid Rocq identifier (containing only letters, digits, or underscores).
- **`rocqchk`** (or `rocq check`): A standalone checker for compiled `.vo` libraries. It re-verifies the compiled files to guarantee that they are well-typed and have not been maliciously forged or corrupted, entirely independent of the tactic engine.
- **`rocq makefile`**: Generates a standard GNU Makefile from a project configuration file to manage the compilation of multi-file projects.

------

### 2. Managing Load Paths and Logical Names

When working with multiple files, you must tell Rocq where to find your dependencies and how to name them. These options map physical directory paths to Rocq's logical paths.

- **`-Q directory dirpath`**: Maps the physical `directory` to the logical path `dirpath`. When loading files from this package, you must use the `From ... Require` syntax or provide a fully qualified name to avoid ambiguity.
- **`-R directory dirpath`**: Similar to `-Q`, but also allows you to use `Require` with a partially qualified name (omitting the `From` clause). We recommend using `-R` only for files within the same package, and `-Q` for external dependencies.
- **`-I directory`** (or `-include`): Adds a physical directory to the OCaml loadpath, which is necessary for loading OCaml plugins (`.cmo` or `.cmxs` files).

------

### 3. Fast Compilation (`-vos` and `-vok`)

For large projects, compiling proofs can be slow. Rocq provides compiled interfaces to skip opaque proofs during development.

- **`-vos`**: Instructs Rocq to completely skip the processing of opaque proofs (those ending in `Qed` or `Admitted`). It outputs a `.vos` file instead of a `.vo` file. This allows you to quickly typecheck definitions and theorem statements across a project.
- **`-vok`**: Checks a file completely (including proofs) but does not write a `.vo` file to disk. This is highly useful for parallelizing proof-checking across multiple cores without creating file bottlenecks.

------

### 4. Executing and Requiring Files

You can pass instructions directly to the CLI to load scripts or compiled libraries on startup.

- **`-l file`** (or `-load-vernac-source`): Loads and executes the Rocq script from `file.v` directly.
- **`-require qualid`**: Loads the compiled library `qualid` (equivalent to running `Require qualid` in the prompt).
- **`-ri qualid`**: Loads and imports the library (equivalent to `Require Import qualid`).
- **`-re qualid`**: Loads and transitively exports the library (equivalent to `Require Export qualid`).
- **`-rfrom dirpath qualid`**: Equivalent to `From dirpath Require qualid`. (Variants like `-rifrom` and `-refrom` also exist for importing and exporting).

*Note: The order of command-line options matters. File loading and setting options are executed in the exact order they are specified on the command line*.

------

### 5. Adjusting System Settings and Warnings

You can modify Rocq's state, parameters, and output directly from the CLI.

- **`-set "Option=Value"`**: Enables a flag or sets an option at startup. For flags, `-set "Flag Name"` is equivalent to setting it to `true`.
- **`-unset "Flag Name"`**: Disables the specified flag or option.
- **`-w (all|none|w1,...,wn)`**: Configures the display of warnings. You can enable a warning/category by passing its name, disable it by prefixing it with `-`, or turn it into a hard error by prefixing it with `+`.
- **`-time`**: Outputs timing information to standard output for every command executed.
- **`-profile file`**: Outputs deep profiling information to the given file in Google trace format, useful for benchmarking performance.

------

### 6. Project Management with `_CoqProject`

Instead of typing long lists of `-Q` and `-R` flags manually, best practice dictates organizing your project using a `_CoqProject` file.

A `_CoqProject` file contains the command-line options and a list of the `.v` files in your project. For example:

Plaintext

```
-R theories MyPackage
theories/File1.v
theories/SubDir/File2.v
```

You can then generate a Makefile by running:

Bash

```
rocq makefile -f _CoqProject -o CoqMakefile
```

After this, you simply run `make -f CoqMakefile` to build your entire project in the correct dependency order.

------

### 7. Environment Variables

Rocq respects several environment variables that alter its execution:

- **`ROCQPATH`**: Specifies the load path as a list of directories separated by colons (or semicolons on Windows).
- **`ROCQ_COLORS`**: Specifies the colors used by `rocq repl` to highlight output (like diffs), using ANSI escape codes.
- **`COQBIN`**: Used by makefiles generated by `rocq makefile` to locate the exact Rocq binaries.
