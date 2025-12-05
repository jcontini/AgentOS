import { serve } from "bun";
import { resolve } from "path";

// Get project root (two levels up from this script)
const SCRIPT_DIR = import.meta.dir;
const PROJECT_ROOT = resolve(SCRIPT_DIR, "../..");

serve({
  port: 8000,
  fetch(req) {
    const url = new URL(req.url);
    let path = url.pathname;
    
    // Default to viewer.html
    if (path === "/" || path === "") {
      path = "/viewer.html";
    }
    
    // Map paths to file system
    let filePath;
    if (path === "/viewer.html" || path === "viewer.html") {
      filePath = resolve(SCRIPT_DIR, "viewer.html");
    } else if (path.startsWith("/skills-data/") || path.startsWith("skills-data/")) {
      // Serve from user/skills-data folder
      const relativePath = path.replace(/^\/?skills-data\//, "");
      filePath = resolve(PROJECT_ROOT, "user", "skills-data", relativePath);
    } else {
      // Serve from current directory (skills/flights)
      const relativePath = path.startsWith("/") ? path.slice(1) : path;
      filePath = resolve(SCRIPT_DIR, relativePath);
    }
    
    try {
      const file = Bun.file(filePath);
      return new Response(file);
    } catch (error) {
      return new Response("File not found: " + filePath, { status: 404 });
    }
  },
});

console.log("✓ Flight viewer server running on http://localhost:8000");
console.log("✓ Open http://localhost:8000/viewer.html in your browser");


