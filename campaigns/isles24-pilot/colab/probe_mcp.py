#!/usr/bin/env python3
"""Synthetic MCP handshake only. Never claims notebook execution from connection."""
import argparse
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def probe(command):
    async with stdio_client(StdioServerParameters(command=command,args=[])) as (read,write):
        async with ClientSession(read,write) as session:
            initialized=await session.initialize()
            tools=await session.list_tools()
            print(json.dumps({'server':initialized.serverInfo.model_dump(),'tools':[t.name for t in tools.tools],
                              'notebook_execution_verified':False,'result_retrieval_verified':False,
                              'reason':'browser session and runtime not connected'},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--server',required=True); a=ap.parse_args()
    asyncio.run(asyncio.wait_for(probe(a.server),timeout=30))
