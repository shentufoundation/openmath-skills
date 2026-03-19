#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const AGENTS = ["claude", "cursor", "codex", "gemini"];
const DEFAULT_AGENT = "claude";

function getPackageSkillsDir() {
  return path.resolve(__dirname, "..", "skills");
}

function getInstallDir(agent, cwd) {
  const dir = process.env.OPENMATH_SKILLS_INSTALL_DIR;
  if (dir) return path.resolve(dir);
  return path.join(cwd, `.${agent}`, "skills");
}

function discoverSkills(skillsDir) {
  if (!fs.existsSync(skillsDir)) return [];
  return fs
    .readdirSync(skillsDir)
    .filter((name) => {
      const p = path.join(skillsDir, name, "SKILL.md");
      return fs.existsSync(p);
    })
    .sort();
}

function matchPattern(name, pattern) {
  const regex = new RegExp(
    "^" + pattern.replace(/\*/g, ".*").replace(/\?/g, ".") + "$"
  );
  return regex.test(name);
}

function cmdInstall(patterns, agent, verbose) {
  const skillsDir = getPackageSkillsDir();
  const installDir = getInstallDir(agent, process.cwd());
  const available = discoverSkills(skillsDir);

  const matched = available.filter((name) =>
    patterns.some((p) => matchPattern(name, p))
  );

  if (matched.length === 0) {
    console.error("No matching skills found.");
    console.error(`Available: ${available.join(", ") || "(none)"}`);
    process.exit(1);
  }

  fs.mkdirSync(installDir, { recursive: true });

  for (const name of matched) {
    const src = path.join(skillsDir, name);
    const dest = path.join(installDir, name);

    try {
      if (fs.existsSync(dest)) {
        const stat = fs.lstatSync(dest);
        if (stat.isSymbolicLink()) {
          fs.unlinkSync(dest);
        } else {
          if (verbose) console.log(`  [SKIP] ${name}: not a symlink`);
          continue;
        }
      }
      fs.symlinkSync(src, dest, "dir");
      console.log(`  installed ${name} -> ${src}`);
    } catch (e) {
      console.error(`  [ERROR] ${name}: ${e.message}`);
    }
  }

  console.log(`\nInstalled ${matched.length} skill(s) to ${installDir}`);
}

function cmdRemove(patterns, agent, dryRun, verbose) {
  const installDir = getInstallDir(agent, process.cwd());
  if (!fs.existsSync(installDir)) {
    console.error("No skills installed.");
    return;
  }

  const installed = fs
    .readdirSync(installDir)
    .filter((name) => {
      const p = path.join(installDir, name);
      return fs.lstatSync(p).isSymbolicLink();
    })
    .sort();

  const matched = installed.filter((name) =>
    patterns.some((p) => matchPattern(name, p))
  );

  if (matched.length === 0) {
    console.error("No matching installed skills to remove.");
    return;
  }

  for (const name of matched) {
    const dest = path.join(installDir, name);
    if (dryRun) {
      console.log(`  [would remove] ${name}`);
    } else {
      fs.unlinkSync(dest);
      console.log(`  removed ${name}`);
    }
  }
}

function cmdList(agent) {
  const skillsDir = getPackageSkillsDir();
  const installDir = getInstallDir(agent, process.cwd());
  const available = discoverSkills(skillsDir);

  const installed = fs.existsSync(installDir)
    ? fs
        .readdirSync(installDir)
        .filter((n) => fs.lstatSync(path.join(installDir, n)).isSymbolicLink())
        .sort()
    : [];

  const installedSet = new Set(installed);

  console.log("Installed:");
  if (installed.length === 0) {
    console.log("  (none)");
  } else {
    for (const name of installed) console.log(`  ${name}`);
  }

  console.log("\nAvailable (not installed):");
  const notInstalled = available.filter((n) => !installedSet.has(n));
  if (notInstalled.length === 0) {
    console.log("  (none)");
  } else {
    for (const name of notInstalled) console.log(`  ${name}`);
  }
}

function printUsage() {
  console.log(`openmath-skills - manage OpenMath AI agent skills

Usage:
  openmath-skills install <pattern...> [--agent <name>] [-v]
  openmath-skills remove <pattern...>  [--agent <name>] [--dry-run]
  openmath-skills list                 [--agent <name>]

Agents: ${AGENTS.join(", ")} (default: ${DEFAULT_AGENT})

Examples:
  npx openmath-skills install openmath-*
  npx openmath-skills install openmath-open-theorem --agent cursor
  npx openmath-skills list
  npx openmath-skills remove openmath-* --dry-run`);
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    printUsage();
    process.exit(0);
  }

  const command = args[0];
  const rest = args.slice(1);

  let agent = DEFAULT_AGENT;
  let verbose = false;
  let dryRun = false;
  const patterns = [];

  for (let i = 0; i < rest.length; i++) {
    if (rest[i] === "--agent" && i + 1 < rest.length) {
      agent = rest[++i];
      if (!AGENTS.includes(agent)) {
        console.error(`Unknown agent: ${agent}. Choose from: ${AGENTS.join(", ")}`);
        process.exit(1);
      }
    } else if (rest[i] === "-v" || rest[i] === "--verbose") {
      verbose = true;
    } else if (rest[i] === "--dry-run") {
      dryRun = true;
    } else if (!rest[i].startsWith("-")) {
      patterns.push(rest[i]);
    }
  }

  switch (command) {
    case "install":
    case "add":
      if (patterns.length === 0) {
        console.error("Usage: openmath-skills install <pattern...>");
        process.exit(1);
      }
      cmdInstall(patterns, agent, verbose);
      break;
    case "remove":
    case "rm":
      if (patterns.length === 0) {
        console.error("Usage: openmath-skills remove <pattern...>");
        process.exit(1);
      }
      cmdRemove(patterns, agent, dryRun, verbose);
      break;
    case "list":
    case "ls":
      cmdList(agent);
      break;
    default:
      console.error(`Unknown command: ${command}`);
      printUsage();
      process.exit(1);
  }
}

main();
