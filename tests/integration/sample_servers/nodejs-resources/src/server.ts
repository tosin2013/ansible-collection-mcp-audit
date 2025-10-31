#!/usr/bin/env node
/**
 * SPDX-License-Identifier: MIT
 * Simple Node.js MCP resource server for integration testing
 * Demonstrates cross-language compatibility (TypeScript server <-> Python client)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  Resource,
  TextResourceContents,
} from "@modelcontextprotocol/sdk/types.js";

// Create server instance
const server = new Server(
  {
    name: "nodejs-resource-test-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      resources: {},
    },
  }
);

// Define test resources
const resources: Resource[] = [
  {
    uri: "file://test_data/config.json",
    name: "Test Config",
    mimeType: "application/json",
    description: "Test configuration file",
  },
  {
    uri: "file://test_data/document.txt",
    name: "Test Document",
    mimeType: "text/plain",
    description: "Test text document",
  },
  {
    uri: "file://test_data/data.yaml",
    name: "Test YAML Data",
    mimeType: "application/x-yaml",
    description: "Test YAML data file",
  },
];

// Handle list_resources request
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources,
  };
});

// Handle read_resource request
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri = request.params.uri;

  const resourceContents: Record<string, TextResourceContents> = {
    "file://test_data/config.json": {
      uri,
      mimeType: "application/json",
      text: '{"environment": "test", "enabled": true, "version": "1.0.0"}',
    },
    "file://test_data/document.txt": {
      uri,
      mimeType: "text/plain",
      text: "This is a test document for MCP resource testing.",
    },
    "file://test_data/data.yaml": {
      uri,
      mimeType: "application/x-yaml",
      text: "test:\n  key: value\n  items:\n    - item1\n    - item2\n",
    },
  };

  const content = resourceContents[uri];
  if (!content) {
    throw new Error(`Resource not found: ${uri}`);
  }

  return {
    contents: [content],
  };
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Node.js MCP Resource Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
