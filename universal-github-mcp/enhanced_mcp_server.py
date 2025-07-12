#!/usr/bin/env python3
"""
Enhanced Universal GitHub MCP Server
Includes advanced file filtering and environment file generation tools
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path to import enhanced_github_uploader
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        CallToolRequest,
        ListToolsRequest,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
    from mcp.server.stdio import stdio_server
except ImportError:
    print("MCP library not found. Please install with: pip install mcp")
    sys.exit(1)

class EnhancedGitHubMCPServer:
    def __init__(self):
        self.server = Server("enhanced-github-mcp")
        self.setup_tools()
    
    def setup_tools(self):
        """Setup all MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools"""
            return [
                Tool(
                    name="enhanced_upload_with_filtering",
                    description="Upload files to GitHub repository with advanced filtering system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "account": {
                                "type": "string",
                                "description": "Target account (alex-cipher-ai or usemanusai)",
                                "enum": ["alex-cipher-ai", "usemanusai"]
                            },
                            "local_dir": {
                                "type": "string",
                                "description": "Local directory to upload (default: current directory)",
                                "default": "."
                            },
                            "batch_size": {
                                "type": "integer",
                                "description": "Number of files to upload per batch (default: 5)",
                                "default": 5
                            },
                            "generate_env_example": {
                                "type": "boolean",
                                "description": "Whether to generate .env.example file (default: true)",
                                "default": True
                            }
                        },
                        "required": ["account"]
                    }
                ),
                Tool(
                    name="generate_env_example",
                    description="Generate .env.example file from discovered environment files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "account": {
                                "type": "string",
                                "description": "Target account (alex-cipher-ai or usemanusai)",
                                "enum": ["alex-cipher-ai", "usemanusai"]
                            },
                            "local_dir": {
                                "type": "string",
                                "description": "Local directory to scan for .env files (default: current directory)",
                                "default": "."
                            },
                            "additional_vars": {
                                "type": "object",
                                "description": "Additional environment variables to include",
                                "default": {}
                            }
                        },
                        "required": ["account"]
                    }
                ),
                Tool(
                    name="list_filtering_rules",
                    description="List current file filtering rules and patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="add_custom_filter",
                    description="Add custom filtering pattern to exclude or include files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Filter pattern (e.g., '*.backup', 'temp/', 'node_modules/')"
                            },
                            "filter_type": {
                                "type": "string",
                                "description": "Type of filter (exclude or include)",
                                "enum": ["exclude", "include"],
                                "default": "exclude"
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
                Tool(
                    name="test_file_filtering",
                    description="Test file filtering rules without uploading (dry run)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "local_dir": {
                                "type": "string",
                                "description": "Local directory to test filtering on (default: current directory)",
                                "default": "."
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="scan_env_files",
                    description="Scan directory for environment files and show discovered variables",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "local_dir": {
                                "type": "string",
                                "description": "Local directory to scan (default: current directory)",
                                "default": "."
                            }
                        },
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            
            if name == "enhanced_upload_with_filtering":
                return await self.enhanced_upload_with_filtering(arguments)
            elif name == "generate_env_example":
                return await self.generate_env_example(arguments)
            elif name == "list_filtering_rules":
                return await self.list_filtering_rules(arguments)
            elif name == "add_custom_filter":
                return await self.add_custom_filter(arguments)
            elif name == "test_file_filtering":
                return await self.test_file_filtering(arguments)
            elif name == "scan_env_files":
                return await self.scan_env_files(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    async def enhanced_upload_with_filtering(self, arguments: dict) -> List[TextContent]:
        """Upload files with enhanced filtering system"""
        try:
            from enhanced_github_uploader import EnhancedGitHubUploader
            
            uploader = EnhancedGitHubUploader()
            target_account = arguments.get("account", "usemanusai")
            local_dir = arguments.get("local_dir", ".")
            batch_size = arguments.get("batch_size", 5)
            generate_env = arguments.get("generate_env_example", True)
            
            success = uploader.enhanced_upload_workspace(
                target_account, local_dir, batch_size, generate_env
            )
            
            result = {
                "success": success,
                "account": target_account,
                "local_dir": local_dir,
                "batch_size": batch_size,
                "generated_env_example": generate_env,
                "message": "Upload completed with enhanced filtering" if success else "Upload failed",
                "repository_url": f"https://github.com/{uploader.accounts[target_account]['target_repo']}"
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def generate_env_example(self, arguments: dict) -> List[TextContent]:
        """Generate .env.example file from discovered environment files"""
        try:
            from enhanced_github_uploader import EnhancedGitHubUploader
            
            uploader = EnhancedGitHubUploader()
            target_account = arguments.get("account", "usemanusai")
            local_dir = arguments.get("local_dir", ".")
            additional_vars = arguments.get("additional_vars", {})
            
            success = uploader.generate_env_example_tool(
                target_account, local_dir, additional_vars
            )
            
            result = {
                "success": success,
                "account": target_account,
                "local_dir": local_dir,
                "additional_vars_count": len(additional_vars),
                "message": ".env.example generated successfully" if success else "Failed to generate .env.example",
                "file_url": f"https://github.com/{uploader.accounts[target_account]['target_repo']}/blob/main/.env.example" if success else None
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def list_filtering_rules(self, arguments: dict) -> List[TextContent]:
        """List current file filtering rules"""
        try:
            from enhanced_github_uploader import EnhancedGitHubUploader
            
            uploader = EnhancedGitHubUploader()
            rules = uploader.list_filtering_rules()
            
            return [TextContent(type="text", text=json.dumps(rules, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def add_custom_filter(self, arguments: dict) -> List[TextContent]:
        """Add custom filtering pattern"""
        try:
            from enhanced_github_uploader import EnhancedGitHubUploader
            
            uploader = EnhancedGitHubUploader()
            pattern = arguments["pattern"]
            filter_type = arguments.get("filter_type", "exclude")
            
            success = uploader.add_custom_filter(pattern, filter_type)
            
            result = {
                "success": success,
                "pattern": pattern,
                "filter_type": filter_type,
                "message": f"Filter pattern {'added' if success else 'failed to add'}"
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def test_file_filtering(self, arguments: dict) -> List[TextContent]:
        """Test file filtering rules (dry run)"""
        try:
            from enhanced_github_uploader import EnhancedGitHubUploader
            from pathlib import Path
            
            uploader = EnhancedGitHubUploader()
            local_dir = arguments.get("local_dir", ".")
            local_path = Path(local_dir)
            
            total_files = 0
            excluded_files = 0
            excluded_list = []
            included_list = []
            
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    relative_path = str(file_path.relative_to(local_path)).replace('\\', '/')
                    
                    if uploader.should_exclude_file(file_path, local_path):
                        excluded_files += 1
                        excluded_list.append(relative_path)
                    else:
                        included_list.append(relative_path)
            
            included_files = total_files - excluded_files
            exclusion_rate = (excluded_files / total_files * 100) if total_files > 0 else 0
            
            result = {
                "total_files": total_files,
                "included_files": included_files,
                "excluded_files": excluded_files,
                "exclusion_rate": round(exclusion_rate, 1),
                "excluded_list": excluded_list[:20],  # Show first 20 excluded files
                "included_list": included_list[:20],  # Show first 20 included files
                "more_excluded": max(0, len(excluded_list) - 20),
                "more_included": max(0, len(included_list) - 20)
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def scan_env_files(self, arguments: dict) -> List[TextContent]:
        """Scan directory for environment files and show discovered variables"""
        try:
            from enhanced_github_uploader import EnhancedGitHubUploader
            from pathlib import Path
            
            uploader = EnhancedGitHubUploader()
            local_dir = arguments.get("local_dir", ".")
            local_path = Path(local_dir)
            
            env_files = uploader.scan_env_files(local_path)
            
            result = {
                "env_files_found": len(env_files),
                "env_files": {}
            }
            
            for file_path, variables in env_files.items():
                result["env_files"][file_path] = {
                    "variable_count": len(variables),
                    "variables": list(variables.keys())
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main function to run the MCP server"""
    server_instance = EnhancedGitHubMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="enhanced-github-mcp",
                server_version="2.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
