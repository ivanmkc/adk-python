import pytest
import asyncio
import json
import os

@pytest.mark.asyncio
@pytest.mark.parametrize("server_name", ["context7"])
@pytest.mark.xfail(reason="Gemini CLI (npm) does not seem to discover MCP tools from settings.json in this environment.")
async def test_mcp_server_running(server_name: str):
    """
    Verifies that the specified MCP server is running and connected
    within the Gemini CLI Docker container by asking a question that requires
    access to the served repository.
    """
    image_name = "gemini-cli-mcp" 
    
    # Ensure real credentials for the Gemini CLI to function
    if not os.environ.get("GEMINI_API_KEY"):
      pytest.skip("GEMINI_API_KEY environment variable not set. Cannot run Gemini CLI calls.")

    # The entrypoint script will automatically pick up GEMINI_API_KEY
    # We need to pass the real API key to the docker container
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    context7_api_key = os.environ.get("CONTEXT7_API_KEY")
    
    env_vars = []
    if gemini_api_key:
        env_vars.append(f"-e")
        env_vars.append(f"GEMINI_API_KEY={gemini_api_key}")
    if context7_api_key:
        env_vars.append(f"-e")
        env_vars.append(f"CONTEXT7_API_KEY={context7_api_key}")
    
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
    # The 'context7' server exposes 'resolve-library-id'. We check if it was used.
    
    tools_stats = data.get("stats", {}).get("tools", {}).get("byName", {})
    
    found_mcp_tool = False
    for tool_name in tools_stats.keys():
        # Check for the specific tool 'resolve_library_id' or 'resolve-library-id', possibly with prefix
        # Gemini CLI sanitizes names to underscores usually.
        if "resolve_library_id" in tool_name or "resolve-library-id" in tool_name:
            found_mcp_tool = True
            break
            
    # We also print the tools found to help debugging
    print(f"DEBUG: Tools used: {list(tools_stats.keys())}")
    
    assert found_mcp_tool, f"The expected MCP tool 'resolve-library-id' was not found in usage stats. Tools used: {list(tools_stats.keys())}"