# Jinja2 Template Support for Agent Configurations

This document describes the new Jinja2 template support for customizing agent prompts in AgentWorld.

## Overview

Agent configurations now support Jinja2 templates for both system prompts and user prompts, providing powerful templating capabilities with conditional logic, loops, and variable substitution.

## Configuration Fields

### system_prompt
The `system_prompt` field now supports Jinja2 template syntax. Available variables:
- `observation`: Current environment observation data
- `chat_messages`: Current chat message history

### user_prompt_template (New)
A new optional field that defines how task prompts are formatted. Available variables:
- `task_name`: Name of the task
- `task_description`: Description of the task
- `primary_objective`: Primary objective from the task config
- `secondary_objectives`: List of secondary objectives (empty list if none)
- `relevant_game_context`: Relevant game context (None if not provided)
- `success_criteria`: List of success criteria
- `objectives`: Full objectives dictionary for backward compatibility

## Example Configuration

```yaml
agent:
  name: "MyAgent"
  provider: "openai"
  # ... other config fields ...
  
  # System Prompt with Jinja2 template
  system_prompt: |
    You are an AI agent playing AgentWorld MMORPG.
    
    Current Environment:
    {{observation}}
    
    {% if chat_messages %}
    Recent Chat History:
    {{chat_messages}}
    {% endif %}

  # User Prompt Template with Jinja2
  user_prompt_template: |
    **Task:** {{task_name}}
    
    **Description:** {{task_description}}
    
    **Primary Objective:** {{primary_objective}}
    
    {% if secondary_objectives %}
    **Secondary Objectives:**
    {% for obj in secondary_objectives %}
    - {{obj}}
    {% endfor %}
    {% endif %}
    
    {% if relevant_game_context %}
    **Relevant Context:**
    {{relevant_game_context}}
    {% endif %}
    
    {% if success_criteria %}
    **Success Criteria:**
    {% for criteria in success_criteria %}
    - {{criteria}}
    {% endfor %}
    {% endif %}
```

## Jinja2 Features Supported

### Variable Substitution
```jinja2
{{variable_name}}
```

### Conditional Blocks
```jinja2
{% if condition %}
Content here
{% endif %}
```

### Loops
```jinja2
{% for item in list %}
- {{item}}
{% endfor %}
```

### Filters
Jinja2's built-in filters are available:
```jinja2
{{variable_name|upper}}
{{variable_name|default("fallback")}}
```

## Backward Compatibility

- If no `user_prompt_template` is provided, the system falls back to the original hardcoded format
- System prompts without Jinja2 syntax will still work with simple string replacement
- All existing agent configurations continue to work without modification

## Error Handling

- Template rendering errors fall back to simple string replacement for backward compatibility
- Invalid template syntax is logged but doesn't break the agent
- Missing variables default to empty strings or empty lists as appropriate

## Migration Guide

To migrate existing configurations:

1. **Add Jinja2 to requirements**: Already done in `agents/requirements.txt`
2. **Update system prompts**: Replace `{{variable}}` syntax with Jinja2 templates
3. **Add user prompt templates**: Define `user_prompt_template` field for custom task formatting
4. **Test thoroughly**: Verify templates render correctly with your task configurations

## Best Practices

1. **Use conditional blocks** to handle optional content gracefully
2. **Provide fallbacks** for optional variables using Jinja2's `default` filter
3. **Test templates** with various task configurations to ensure robustness
4. **Keep templates readable** by using proper indentation and spacing
5. **Document template variables** in comments for team collaboration
