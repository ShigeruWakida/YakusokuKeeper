# Yakusoku Keeper

**A rule-based prompting MCP server that enforces consistent LLM behavior through input count and time-based triggers.**

Yakusoku (約束) means "promise" in Japanese - this tool helps Claude Code keep its promises by automatically applying configured rules at specified intervals.

## Features

- 🎯 **Automatic Rule Application**: Rules are automatically triggered based on input count or elapsed time
- 🔄 **Dynamic Rule Management**: Add, remove, and modify rules in real-time
- ⚙️ **Flexible Configuration**: Support for user-level and project-specific rules
- 📊 **Multiple Trigger Types**: First-time, every N inputs, and every N minutes rules
- 🔌 **Claude Code Integration**: Seamless MCP server integration with Claude Code

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ShigeruWakida/YakusokuKeeper.git
cd YakusokuKeeper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Test the server:
```bash
python yakusoku_keeper.py
```

### Claude Code Configuration

Add the server using the Claude Code CLI:

```bash
claude mcp add yakusoku_keeper --scope project -- python /path/to/YakusokuKeeper/yakusoku_keeper.py
```

Or manually add this to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "yakusoku_keeper": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/YakusokuKeeper/yakusoku_keeper.py"],
      "env": {}
    }
  }
}
```

## How It Works

### Rule Types

- **`first`**: Triggers on the very first interaction
- **`every_N_inputs`**: Triggers every N user inputs (e.g., every 5 interactions)
- **`every_N_minutes`**: Triggers after N minutes have elapsed since the last trigger

### Configuration Files

Yakusoku Keeper uses a two-tier configuration system:

- **`~/.yakusoku/yakusoku_config.yml`**: Global rules (created commented-out by default)
- **`.yakusoku/project.yml`**: Project-specific rules (created active by default)

### Example Configuration

```yaml
# --- First time rules ---
first:
  - At the beginning of the response, insert the string that follows "say".
  - say Hello! I am Yakusoku Keeper.
  - Generate code using the K&R coding style.
  - Use only < and <= operators for all comparisons.
  - Read and follow ./docs/README_CODING_STANDARDS.md
  - When using replace_symbol_body, insert_after_symbol, or insert_before_symbol, you MUST present the code block—preferably in diff format—and you MUST obtain explicit approval before applying any change.

# --- Input count based rules ---
every_5_inputs:
  - Generate code using the K&R coding style.
every_10_inputs:
  - Use only < and <= operators for all comparisons.
  - When using replace_symbol_body, insert_after_symbol, or insert_before_symbol, you MUST present the code block—preferably in diff format—and you MUST obtain explicit approval before applying any change.

# --- Time based rules ---
every_60_minutes:
  - Read and follow ./docs/README_CODING_STANDARDS.md
```

## MCP Tools

### Core Tools

- **`get_rules()`**: Returns rules that match current conditions (called automatically)
- **`reset()`**: Resets input counters and time triggers
- **`initial_instructions()`**: Provides high-priority instructions to Claude Code

### Rule Management Tools

- **`add_rule(rule_type, rule_content, target, value)`**: Dynamically add new rules
- **`remove_rule(rule_type, rule_content, target, value)`**: Remove existing rules

#### Examples

```python
# Add a first-time rule
add_rule("first", "Always be polite and helpful")

# Add an input-based rule (every 3 inputs)
add_rule("every_N_inputs", "Check code for best practices", value=3)

# Add a time-based rule (every 30 minutes)
add_rule("every_N_minutes", "Suggest taking a break", value=30)

# Remove a rule
remove_rule("first", "Always be polite and helpful")
```

## Project Structure

```
YakusokuKeeper/
├── yakusoku_keeper.py    # Main MCP server
├── README.md           # This file
├── requirements.txt    # Dependencies
├── LICENSE            # MIT License
└── .yakusoku/          # Project configuration (auto-created)
```

## Use Cases

- **Coding Standards**: Automatically remind about code style requirements
- **Documentation**: Prompt for documentation at regular intervals
- **Code Review**: Trigger quality checks every few interactions
- **Break Reminders**: Suggest breaks during long coding sessions
- **Greeting Messages**: Consistent welcome messages for new sessions

## Combo: YakusokuKeeper + mcp-win-toast

[mcp-win-toast](https://github.com/ShigeruWakida/mcp-win-toast) is an MCP server that lets AI assistants send Windows toast notifications and dialog boxes. By combining it with YakusokuKeeper, you can build a **self-managing AI assistant** that notifies you at the right moments — automatically, without being asked.

### Break Reminder

Add a time-based rule to remind you to take a break every 30 minutes, delivered as a toast notification.

```yaml
every_30_minutes:
  - "Call show_toast with title 'Break Time' and message 'You have been working for 30 minutes. Stand up and stretch!'"
```

### Progress Report at Regular Intervals

Have Claude automatically summarize what it has done every 10 interactions and notify you.

```yaml
every_10_inputs:
  - "Summarize what you have accomplished so far in 2-3 bullet points, then call show_toast with title 'Progress Report' and the summary as the message."
```

### Critical File Protection

Show a blocking dialog for confirmation whenever Claude is about to modify important files.

```yaml
first:
  - "Before editing any file matching *.env, *.config, or docker-compose.*, always call show_dialog with title 'Confirm Edit' and a message describing which file you are about to modify. Wait for the user to acknowledge before proceeding."
```

### Session Duration Warning

Warn the user with a dialog box after a long session so they can decide whether to continue.

```yaml
every_60_minutes:
  - "Call show_dialog with title 'Long Session' and message 'You have been working for over an hour. Would you like to wrap up or continue?' to check in with the user."
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for MCP server implementation
- Designed for seamless integration with [Claude Code](https://claude.ai/code)