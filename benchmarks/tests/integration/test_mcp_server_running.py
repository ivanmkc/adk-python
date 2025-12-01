
import pytest
import asyncio
import json
import os

@pytest.mark.asyncio
@pytest.mark.parametrize("server_name", ["context7"])
async def test_mcp_server_running(server_name: str):
    """
    Verifies that the specified MCP server is running and connected
    within the Gemini CLI Docker container.
    """
    image_name = "gemini-cli-mcp" 
    
    # Ensure real credentials for the Gemini CLI to function
    if not os.environ.get("GEMINI_API_KEY"):
      pytest.skip("GEMINI_API_KEY environment variable not set. Cannot run Gemini CLI calls.")

    # The entrypoint script will automatically pick up GEMINI_API_KEY
    # We need to pass the real API key to the docker container
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    env_vars = ["-e", f"GEMINI_API_KEY={gemini_api_key}"] if gemini_api_key else []
    
    # Ask a question that requires context from the ADK codebase
    question = "What is the name of the base class for all agents in google.adk.agents?"
    expected_answer_part = "BaseAgent"
    
    cmd = [
        "docker", "run", "--rm",
        *env_vars,
        image_name,
        question, 
        "--output-format", "json"
    ]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await proc.communicate()
    stdout_str = stdout.decode()
    stderr_str = stderr.decode()
    
    assert proc.returncode == 0, f"Docker command failed with code {proc.returncode}.\nStderr: {stderr_str}\nStdout: {stdout_str}"
    
    try:
        data = json.loads(stdout_str)
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse JSON output from Gemini CLI.\nStdout: {stdout_str}\nStderr: {stderr_str}")
        
    print(f"DEBUG: Gemini CLI Output: {json.dumps(data, indent=2)}")
    
    # 1. Verify the answer is correct (implies context access)
    response_text = data.get("response", "")
    assert expected_answer_part in response_text, f"Expected answer '{expected_answer_part}' not found in response: {response_text}"
    
    # 2. Verify tool usage in stats (implies MCP server usage)
    # The 'context7' server serves the repo, so we expect tools like 'list_directory', 'read_file' 
    # or specific MCP tools to be present in stats.
    
    tools_stats = data.get("stats", {}).get("tools", {}).get("byName", {})
    
    # We check if *any* tool was used, or specifically if known MCP-provided tools were used.
    # Since we don't know the exact tool names exposed by 'context7' (mcp serve --repo),
    # we'll look for evidence of file system or repo interaction tools.
    
    # Common tools exposed by 'mcp serve --repo' or similar might be:
    # - list_directory
    # - read_file
    # - search_file_content
    # - or prefixed names like context7__list_directory
    
    found_mcp_tool = False
    for tool_name in tools_stats.keys():
        # Check for prefixed tools or standard file system tools
        if "context7" in tool_name or tool_name in ["read_file", "list_directory", "search_file_content"]:
            found_mcp_tool = True
            break
            
    assert found_mcp_tool, f"No relevant MCP tools (context7*, read_file, etc.) found in usage stats. Tools used: {list(tools_stats.keys())}"
        
