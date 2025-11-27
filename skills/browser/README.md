# Browser Automation Skill

## Intention: Automate web browser interactions

**Required Skills:**
- [Web Search](skills/web-search/README.md) - Always use web search first for research before automating

This skill documents patterns, learnings, and best practices for browser automation using the browser MCP tools.

## ⚠️ When to Use Browser Automation vs Web Search

**ALWAYS use web search first (`skills/web-search.md`) for:**
- Researching APIs, documentation, or information
- Looking up how to do something
- Finding documentation or examples
- General web searches and information gathering

**ONLY use browser automation when:**
- You need to **interact** with web pages (clicking buttons, filling forms, navigating multi-step flows)
- You need to **control** the browser to complete a specific task
- Web search doesn't provide the information you need AND you need to navigate a complex site
- You're automating a specific workflow that requires page interaction

**Rule of thumb:** If you're just looking things up or researching, use web search. If you need to click, type, or navigate through a process, use browser automation.

## Known Issues & Patterns

### Chrome Crashes on Launch

**Issue: Chrome crashes immediately when browser automation tries to launch it**
- **Symptoms:** 
  - Chrome process starts then immediately crashes with `SIGTRAP` or `kill EPERM` errors
  - Browser automation fails with "Target page, context or browser has been closed"
  - Error logs show SSL handshake failures or process exit errors
- **Root cause:** Corrupted browser session directory storing Chrome automation state
- **Solution:** Clear the browser session directory for the current workspace:
  ```bash
  # Find the workspace storage directory (check Cursor workspaceStorage path)
  # Clear the browser-session directory:
  rm -rf "/Users/USERNAME/Library/Application Support/Cursor/User/workspaceStorage/WORKSPACE_ID/anysphere.cursor-browser-extension/browser-session"
  ```
  Or find all browser session directories:
  ```bash
  find "/Users/USERNAME/Library/Application Support/Cursor/User/workspaceStorage" -name "browser-session" -type d
  ```
- **Prevention:** 
  - If Chrome keeps crashing, clear browser session directory first
  - Restart Cursor if clearing doesn't work
  - Check macOS security permissions for Chrome if issue persists
- **Note:** This forces Cursor to create a fresh browser session on next launch

### Buttons Not Responding to Clicks

**Issue: Buttons not responding to clicks**
- **Symptoms:** Clicking buttons appears to work but page doesn't update
- **Possible causes:**
  - Button may be disabled but still shows as clickable in snapshot
  - Page may be in loading/processing state
  - Async operations may not be complete
  - Button may require multiple clicks or different interaction
  - **Open menus/dropdowns may block or interfere with button clicks** - close menus first
  - Dialog buttons may be blocked by overlapping UI elements (menus, tooltips, etc.)
- **Workarounds:**
  - Wait longer after page loads before clicking
  - Check for loading indicators/spinners before clicking
  - Try waiting for specific text to appear/disappear
  - **Check for open menus/dropdowns** - close them first (click outside or select an option)
  - **Check for overlapping UI elements** - may need to interact with them first
  - User may need to manually click if automation fails

### Not Detecting Manual User Actions

**Issue: Not detecting manual user actions**
- **Symptoms:** User manually completes action but AI doesn't detect the change
- **Possible causes:**
  - Snapshot only taken when explicitly requested
  - Page state changes happen between snapshots
  - Need to poll/check more frequently after user actions
- **Workarounds:**
  - After user says they completed an action, take immediate snapshot
  - Use `browser_wait_for` to wait for expected state changes
  - Check URL changes as indicator of navigation

### File Downloads Not Working

**Issue: File downloads not working with automation**
- **Symptoms:** Clicking download buttons appears to work but file doesn't download or isn't accessible
- **Root cause:** 
  - **File downloads are blocked/disabled when Chrome is controlled by automation tools** (Chrome DevTools Protocol/CDP/remote debugging)
  - This is a fundamental limitation of browser automation - downloads require a normal browser session not controlled by automation
  - Browser automation tools cannot access downloaded files - downloads happen outside browser context
- **Solution:**
  - **Users must download files in a normal browser** (not controlled by automation)
  - When automation reaches a download step, inform user they need to complete the download manually
  - Provide clear instructions: "Please open this URL in a normal browser (not controlled by automation) and download the file"
- **Workarounds after manual download:**
  - Ask user to manually download file and tell you when complete
  - Check Downloads folder after user confirms download
  - Use file system commands to locate downloaded file
  - Note: Downloads typically go to `~/Downloads/` on macOS

## Best Practices

### Before Clicking
1. **Check button state:** Verify button/link is not disabled (`[disabled]` attribute or `aria-disabled="true"`)
   - **Disabled elements cannot be clicked** - browser automation will timeout trying to click them
   - **If element is disabled:** Look for alternative ways to achieve the goal:
     - Navigate directly to the URL (if it's a link with href)
     - Find an alternative UI path (different button, menu option, etc.)
     - Check if there's a prerequisite action needed first
2. **Wait for page stability:** Use `browser_wait_for` to wait for loading indicators to disappear
3. **Verify element visibility:** Ensure element is in viewport and not hidden

### After Clicking
1. **Wait for response:** Don't immediately take snapshot - wait 1-2 seconds
2. **Check for error dialogs:** Always check for error dialogs after actions (look for `dialog "Error dialog"` in snapshot)
3. **Check for navigation:** URL change indicates successful action
4. **Look for success indicators:** Success messages, page changes, or new elements
5. **Check for loading states:** If loading spinner appears, wait for it to complete

### When User Intervenes
1. **Acknowledge immediately:** "Thanks, I see you completed that"
2. **Take fresh snapshot:** Get current state after user action
3. **Continue from new state:** Don't retry failed action

### Error Handling
1. **Always check for error dialogs:** After any action, scan snapshot for error dialogs
2. **Read error messages:** Error dialogs contain important context (e.g., organization policies blocking actions)
3. **Stacked dialogs:** When error occurs during dialog action, error dialog appears on top of underlying dialog
   - **Pattern:** Error dialog → Underlying dialog (e.g., "Error dialog" on top of "Create private key" dialog)
   - **Solution:** Cancel the underlying dialog first (click "Cancel" on underlying dialog), error dialog may auto-dismiss
   - **Alternative:** Error dialogs may not be dismissible via automation - may require canceling underlying action
4. **If click doesn't work:** Wait longer, try alternative selectors, or ask user
5. **If page doesn't update:** Check console messages for errors
6. **If stuck:** Navigate directly to expected URL instead of clicking
7. **Platform policies:** Some platforms may have policies blocking certain actions - check error dialogs for details
8. **Disabled links/buttons:** If a link/button is disabled (`aria-disabled="true"` or `disabled` attribute):
   - **DO NOT attempt to click** - it will timeout
   - **Try navigating directly to the href URL** if it's a link
   - **Look for alternative UI paths** to achieve the same goal
   - **Check if there are prerequisites** that need to be completed first
   - **Use browser_evaluate()** to inspect element state and get href/attributes
9. **When blocked or stuck:** If automation is blocked (permissions, disabled buttons, unclear errors):
  - **First, use web search skill** (`skills/web-search.md`) to research the issue and find solutions
  - **Only if web search doesn't work**, use `browser_navigate()` to Google search: `https://www.google.com/search?q=YOUR_QUESTION`
  - Read documentation links from search results
  - Look for official documentation or Stack Overflow answers
  - Apply learnings from search results to continue automation

## Common Patterns

### Form Filling
```javascript
// Pattern: Fill form fields, then submit
1. Type into textbox
2. Wait for auto-validation
3. Click submit button
4. Wait for navigation/confirmation
```

### Multi-Step Processes
```javascript
// Pattern: Wizard flows
1. Complete step 1 → wait for "complete" indicator
2. Click "Continue" → wait for step 2 to load
3. Skip optional steps → click "Continue" or "Done"
4. Verify final state
```

### Navigation
```javascript
// Pattern: Direct navigation vs clicking
- Use browser_navigate() for known URLs (faster, more reliable)
- Use browser_click() for dynamic flows or when URL is unknown
- **When URL returns "URL not found" or "Failed to load":**
  - Feature may exist but not be accessible via direct URL
  - Some features may require navigation through the UI
  - Solution: Use navigation menu/sidebar instead of direct URLs
  - Look for the feature in navigation menus, sidebar, or search
  - Check if account/project/context needs to be selected first
```

### Menu/Dropdown Interactions
```javascript
// Pattern: Menus and dropdowns
1. Click button/selector to open menu
2. Menu appears with options
3. Select option from menu (click menuitem)
4. Menu closes automatically
5. Note: Open menus may block other UI interactions
6. If button doesn't respond, check for open menus first
```

### Dialog with Open Menus
```javascript
// Pattern: Dialog buttons blocked by menus
1. Dialog opens
2. Dropdown/menu within dialog is opened/expanded
3. Menu overlays dialog buttons
4. Solution: Select from menu first OR click outside menu to close it
5. Then dialog buttons become clickable
```

### Searchable Dropdowns/Comboboxes
```javascript
// Pattern: Dropdowns with filter/search functionality
1. Click combobox to open dropdown
2. Dialog/menu opens with filter/search combobox
3. **Important:** The filter combobox is SEPARATE from the selector combobox
4. Type search text into the FILTER combobox (not the selector combobox)
5. Filter combobox is usually labeled "Filter" and appears at top of dialog
6. After typing, wait for filtered results to appear
7. Select option from filtered list
8. **Common mistake:** Trying to type into selector combobox instead of filter combobox
```

## Logging Learnings

When encountering new patterns or issues:

1. **Document the issue:** What happened, what was expected
2. **Note the context:** Which site, which page, which action
3. **Record the solution:** What worked (or didn't work)
4. **Update this file:** Add to appropriate section above

## Tools Available

- `browser_navigate(url)` - Navigate to URL
- `browser_snapshot()` - Get current page state
- `browser_click(element, ref)` - Click element
- `browser_type(element, ref, text)` - Type text
- `browser_wait_for(text/time)` - Wait for condition
- `browser_console_messages()` - Get console errors/warnings
- `browser_network_requests()` - See network activity

## Critical Patterns

### Error Detection Pattern
**ALWAYS check for error dialogs after actions:**
```javascript
1. Perform action (click, type, etc.)
2. Wait 1-2 seconds
3. Take snapshot
4. Scan for: dialog "Error dialog" or dialog containing "Error"
5. If error found:
   a. Read error message for context
   b. Check if underlying dialog exists (stacked dialogs)
   c. Cancel underlying dialog first (click "Cancel" on underlying dialog)
   d. Error dialog may auto-dismiss after canceling underlying action
   e. Inform user of error and adjust approach
6. If no error: Continue with next step
```

### Stacked Dialog Pattern
**When error occurs during dialog action:**
```javascript
// Pattern: Error dialog appears on top of action dialog
1. Action dialog opens (e.g., "Create" or "Confirm" dialog)
2. User/automation triggers action (e.g., click "Create" or "Confirm")
3. Error occurs → Error dialog appears on top
4. Error dialog may not be directly dismissible
5. Solution: Cancel underlying dialog first (click "Cancel" on underlying dialog)
6. Error dialog should auto-dismiss when underlying action is canceled
7. Note: Dialog dismissal may be async - wait 1-2 seconds after clicking Cancel
8. Verify dialog is gone by taking snapshot after waiting
```

### File Download Pattern
**When action triggers file download:**
```javascript
// IMPORTANT: File downloads DO NOT work when browser is controlled by automation
// Users must download files in a normal browser (not controlled by automation)

1. Recognize when a download is needed (e.g., "Download" or "Export" button)
2. Inform user: "File downloads don't work with browser automation. Please open this URL 
   in a normal browser (not controlled by automation) and download the file manually."
3. Provide the URL or guide user to the download page
4. Wait for user confirmation that download is complete
5. Ask user: "Did the file download? If so, where is it?"
6. Use file system commands to locate and move file
7. Never assume download succeeded - verify file exists
```

## Notes

- Browser automation is inherently fragile - pages change, timing matters
- **Always check for error dialogs** - they contain critical information
- File downloads require user intervention or file system access
- Platform policies can silently block actions - check error dialogs
- When in doubt, ask user to complete action manually
- Prefer direct navigation over complex click sequences when possible
- Always verify state after actions, don't assume success

