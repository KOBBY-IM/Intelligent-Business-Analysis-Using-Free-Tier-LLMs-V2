# Debug Directory

This folder contains debugging utilities and diagnostic tools for troubleshooting the LLM evaluation system.

## Debug Tools

### Session Debugging
- `debug_session.py` - Interactive debugging session utilities
  - Inspect Streamlit session state
  - Debug user authentication flows
  - Analyze data collection processes

## Usage

```bash
# Run debug session
python debug/debug_session.py

# Interactive debugging
python -i debug/debug_session.py
```

## When to Use
- **Development Issues**: When encountering unexpected behavior
- **State Inspection**: To examine Streamlit session variables
- **Data Flow Analysis**: To trace data through the system
- **Integration Problems**: To isolate issues between components

## Best Practices
- Use debug tools in development environment only
- Don't run debug scripts on production data
- Clean up debug outputs after troubleshooting
- Document any persistent issues found through debugging

## Output
Debug tools may generate:
- Console output with system state information
- Temporary debug files (should be cleaned up)
- Diagnostic reports for issue tracking 