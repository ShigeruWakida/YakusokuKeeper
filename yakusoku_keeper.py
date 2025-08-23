"""
Yakusoku Keeper MCP Server
- get_rules(): returns rules that match current input count and elapsed time
- reset(): reset counters and timers
"""

import os
from pathlib import Path
import yaml
from datetime import datetime
from fastmcp import FastMCP

# --- Configuration paths ---
HOME_YAKUSOKU_DIR = Path.home() / ".yakusoku"
HOME_YAKUSOKU_FILE = HOME_YAKUSOKU_DIR / "yakusoku_config.yml"
PROJECT_YAKUSOKU_FILE = Path(".yakusoku/project.yml")


class YakusokuKeeper:
    """MCP logic for Yakusoku Keeper"""

    def __init__(self):
        self.input_count = 0
        self.last_executed_time = {}
        self.rules = []
        # Initialize default config files on startup
        self.initialize_config_files()

    def initialize_config_files(self):
        """Create default config files if they don't exist"""
        HOME_YAKUSOKU_DIR.mkdir(parents=True, exist_ok=True)
        if not HOME_YAKUSOKU_FILE.exists():
            self.create_default_home_rules()
        if not PROJECT_YAKUSOKU_FILE.parent.exists():
            PROJECT_YAKUSOKU_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not PROJECT_YAKUSOKU_FILE.exists():
            self.create_default_project_rules()
    
    def load_rules(self):
        """Load rules from project or home directory"""
        self.rules = []
        for f in [HOME_YAKUSOKU_FILE, PROJECT_YAKUSOKU_FILE]:
            if f.exists():
                with open(f, "r", encoding="utf-8") as yf:
                    try:
                        data = yaml.safe_load(yf)
                        if data:
                            self.rules.append(data)
                    except yaml.YAMLError:
                        pass

    def create_default_home_rules(self):
        default_home = """
# # --- First time rules ---
# first:
#   - At the beginning of the response, insert the string that follows "say".
#   - say Hello! I am Yakusoku Keeper.
#   - Generate code using the K&R coding style.
#   - Use only < and <= operators for all comparisons.
#   - Read and follow ./docs/README_CODING_STANDARDS.md
#   - When using replace_symbol_body, insert_after_symbol, or insert_before_symbol, you MUST present the code block—preferably in diff format—and you MUST obtain explicit approval before applying any change.
# 
# # --- Input count based rules ---
# every_5_inputs:
#   - Generate code using the K&R coding style.
# every_10_inputs:
#   - Use only < and <= operators for all comparisons.
#   - When using replace_symbol_body, insert_after_symbol, or insert_before_symbol, you MUST present the code block—preferably in diff format—and you MUST obtain explicit approval before applying any change.
# 
# # --- Time based rules ---
# every_60_minutes:
#   - Read and follow ./docs/README_CODING_STANDARDS.md
"""
        with open(HOME_YAKUSOKU_FILE, "w", encoding="utf-8") as f:
            f.write(default_home)

    def create_default_project_rules(self):
        default_project = """
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
"""
        with open(PROJECT_YAKUSOKU_FILE, "w", encoding="utf-8") as f:
            f.write(default_project)

    # --- Tools exposed to LLM ---
    def get_rules(self):
        """
        Return rules that match the current input count and elapsed time.
        Reload YAML files every time to reflect any updates.
        """
        self.input_count += 1
        self.load_rules()  # reload rules on every call
        applicable = []
        now = datetime.now()

        for rule_set in self.rules:
            # First-time rules
            first_rules = rule_set.get("first", [])
            if self.input_count == 1:
                applicable.extend(first_rules)

            # Input-count based rules
            for key, actions in rule_set.items():
                if key.startswith("every_") and "_inputs" in key:
                    n = int(key.split("_")[1])
                    if self.input_count % n == 0:
                        applicable.extend(actions)

                # Time-based rules
                if key.startswith("every_") and "_minutes" in key:
                    minutes = int(key.split("_")[1])
                    last_time = self.last_executed_time.get(key)
                    if last_time is None or (now - last_time).total_seconds() >= minutes * 60:
                        applicable.extend(actions)
                        self.last_executed_time[key] = now

        return applicable

    def reset(self):
        """Reset input count and time counters."""
        self.input_count = 0
        self.last_executed_time = {}
    
    def add_rule(self, rule_type, rule_content, target="project", value=None):
        """
        Add a new rule to the configuration file.
        
        Args:
            rule_type: Type of rule ('first', 'every_N_inputs', 'every_N_minutes')
            rule_content: The rule content to add
            target: 'project' or 'home' to specify which config file
            value: For 'every_N_inputs' or 'every_N_minutes', the N value
        
        Returns:
            dict with status and message
        """
        # Determine target file
        if target == "home":
            config_file = HOME_YAKUSOKU_FILE
        else:
            config_file = PROJECT_YAKUSOKU_FILE
        
        # Load existing configuration
        if not config_file.exists():
            return {"status": "error", "message": f"Config file {config_file} does not exist"}
        
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        try:
            # Parse YAML content
            config = yaml.safe_load(content) or {}
            
            # Determine the rule key
            if rule_type == "first":
                key = "first"
            elif rule_type == "every_N_inputs" and value:
                key = f"every_{value}_inputs"
            elif rule_type == "every_N_minutes" and value:
                key = f"every_{value}_minutes"
            else:
                return {"status": "error", "message": "Invalid rule type or missing value"}
            
            # Add the rule
            if key not in config:
                config[key] = []
            if rule_content not in config[key]:
                config[key].append(rule_content)
            else:
                return {"status": "warning", "message": "Rule already exists"}
            
            # Write back to file
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            return {"status": "success", "message": f"Rule added to {config_file.name}"}
            
        except yaml.YAMLError as e:
            return {"status": "error", "message": f"YAML parsing error: {str(e)}"}
    
    def remove_rule(self, rule_type, rule_content, target="project", value=None):
        """
        Remove a rule from the configuration file.
        
        Args:
            rule_type: Type of rule ('first', 'every_N_inputs', 'every_N_minutes')
            rule_content: The rule content to remove (must match exactly)
            target: 'project' or 'home' to specify which config file
            value: For 'every_N_inputs' or 'every_N_minutes', the N value
        
        Returns:
            dict with status and message
        """
        # Determine target file
        if target == "home":
            config_file = HOME_YAKUSOKU_FILE
        else:
            config_file = PROJECT_YAKUSOKU_FILE
        
        # Load existing configuration
        if not config_file.exists():
            return {"status": "error", "message": f"Config file {config_file} does not exist"}
        
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        try:
            # Parse YAML content
            config = yaml.safe_load(content) or {}
            
            # Determine the rule key
            if rule_type == "first":
                key = "first"
            elif rule_type == "every_N_inputs" and value:
                key = f"every_{value}_inputs"
            elif rule_type == "every_N_minutes" and value:
                key = f"every_{value}_minutes"
            else:
                return {"status": "error", "message": "Invalid rule type or missing value"}
            
            # Remove the rule
            if key not in config:
                return {"status": "warning", "message": f"Rule type '{key}' not found in config"}
            
            if rule_content in config[key]:
                config[key].remove(rule_content)
                
                # Remove empty rule sections
                if not config[key]:
                    del config[key]
                
                # Write back to file
                with open(config_file, "w", encoding="utf-8") as f:
                    if config:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                    else:
                        # If config is empty, write minimal comment
                        f.write("# Empty configuration\n")
                
                return {"status": "success", "message": f"Rule removed from {config_file.name}"}
            else:
                return {"status": "warning", "message": "Rule not found in config"}
            
        except yaml.YAMLError as e:
            return {"status": "error", "message": f"YAML parsing error: {str(e)}"}


# --- Instantiate MCP ---
keeper = YakusokuKeeper()
mcp = FastMCP("Yakusoku Keeper")

@mcp.tool()
def initial_instructions() -> str:
    """
    HIGH PRIORITY: Read and follow these instructions immediately.

    1) Before generating ANY user-facing response, CALL the tool "get_rules".
       - You MUST call it on every user input (each turn).
       - The tool returns mandatory rules that MUST be applied now (it only returns the ones that match the current conditions).
    2) Apply the returned rules with the highest priority. Do NOT ignore, dilute, or rewrite them.
       - If a rule instructs to insert or prepend text (e.g., lines starting with `say`), do so at the very beginning of your reply.
       - If a rule instructs a coding style or a constraint, enforce it consistently in your answer.
    3) If no rules are returned (empty list), proceed normally but STILL call get_rules() again on the next user input.
    4) You may call the tool "reset" to reset input counters and time triggers when starting a fresh session or upon user request.
    """
    return (
        "Yakusoku Keeper: Call get_rules() BEFORE every reply. Apply returned rules at highest priority; "
        "prepend required text immediately; enforce style/constraints. If none returned, proceed but keep calling."
    )
    
@mcp.tool
def get_rules() -> list[str]:
    """Call this BEFORE every reply. Returns ONLY the rules that match NOW (first/every_N_inputs/every_M_minutes)."""
    return keeper.get_rules()

@mcp.tool
def reset() -> dict:
    """Reset input counters and time triggers. Does NOT change rule files."""
    return keeper.reset()

@mcp.tool
def add_rule(rule_type: str, rule_content: str, target: str = "project", value: int = None):
    """
    Add a new rule to the configuration file.
    
    Args:
        rule_type: Type of rule ('first', 'every_N_inputs', 'every_N_minutes')
        rule_content: The rule content to add
        target: 'project' or 'home' to specify which config file (default: 'project')
        value: For 'every_N_inputs' or 'every_N_minutes', the N value
    
    Examples:
        add_rule("first", "Always start with a greeting")
        add_rule("every_N_inputs", "Review the code", value=3)
        add_rule("every_N_minutes", "Take a break", value=30)
    """
    return keeper.add_rule(rule_type, rule_content, target, value)

@mcp.tool
def remove_rule(rule_type: str, rule_content: str, target: str = "project", value: int = None):
    """
    Remove a rule from the configuration file.
    
    Args:
        rule_type: Type of rule ('first', 'every_N_inputs', 'every_N_minutes')
        rule_content: The exact rule content to remove
        target: 'project' or 'home' to specify which config file (default: 'project')
        value: For 'every_N_inputs' or 'every_N_minutes', the N value
    
    Examples:
        remove_rule("first", "Always start with a greeting")
        remove_rule("every_N_inputs", "Review the code", value=3)
        remove_rule("every_N_minutes", "Take a break", value=30)
    """
    return keeper.remove_rule(rule_type, rule_content, target, value)


if __name__ == "__main__":
    mcp.run()
