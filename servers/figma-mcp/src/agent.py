import json
import os
import sys

from dotenv import load_dotenv
from figma_tools import get_file_nodes, get_file_structure, post_comment
from openai import OpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables or .env file.")
    sys.exit(1)

client = OpenAI(api_key=api_key)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_file_nodes",
            "description": "Get specific nodes from a Figma file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_key": {
                        "type": "string",
                        "description": "The key of the Figma file"
                    },
                    "ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of node IDs to retrieve"
                    }
                },
                "required": ["file_key", "ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_structure",
            "description": "Get the structure of a Figma file (document tree)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_key": {
                        "type": "string",
                        "description": "The key of the Figma file"
                    }
                },
                "required": ["file_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "post_comment",
            "description": "Post a comment to a Figma file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_key": {
                        "type": "string",
                        "description": "The key of the Figma file"
                    },
                    "message": {
                        "type": "string",
                        "description": "The comment message"
                    },
                    "node_id": {
                        "type": "string",
                        "description": "Optional Node ID to attach the comment to"
                    }
                },
                "required": ["file_key", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write code to a file in the CapeControl frontend project",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "The path relative to CapeControl_React_Starter_Dark/src (e.g., 'components/Header.tsx')"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["relative_path", "content"]
            }
        }
    }
]

def write_file(relative_path, content):
    """Writes content to a file in the frontend project."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../CapeControl_React_Starter_Dark/src"))
    full_path = os.path.join(base_path, relative_path)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    try:
        with open(full_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {relative_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def execute_tool(tool_name, arguments):
    try:
        if tool_name == "get_file_nodes":
            # Convert list of IDs to comma-separated string
            ids_str = ",".join(arguments["ids"]) if isinstance(arguments["ids"], list) else arguments["ids"]
            return get_file_nodes(arguments["file_key"], ids_str)
        elif tool_name == "get_file_structure":
            return get_file_structure(arguments["file_key"])
        elif tool_name == "post_comment":
            return post_comment(
                arguments["file_key"], 
                arguments["message"], 
                arguments.get("node_id")
            )
        elif tool_name == "write_file":
            return write_file(arguments["relative_path"], arguments["content"])
        else:
            return f"Error: Unknown tool {tool_name}"
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"

def run_agent():
    print("Figma Agent Started. Type 'quit' to exit.")
    messages = [
        {"role": "system", "content": "You are a helpful assistant that can interact with Figma files and write code to the CapeControl frontend project. You can read file structure, get node details, post comments, and generate React components based on the design."}
    ]

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            
            if response_message.tool_calls:
                messages.append(response_message)
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"Calling tool: {function_name} with args: {function_args}")
                    
                    tool_result = execute_tool(function_name, function_args)
                    
                    # Truncate result if too long for display, but send full to model
                    display_result = str(tool_result)
                    if len(display_result) > 500:
                        display_result = display_result[:500] + "... (truncated)"
                    print(f"Tool Result: {display_result}")

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(tool_result)
                    })

                # Get final response after tool execution
                second_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )
                final_reply = second_response.choices[0].message.content
                print(f"\nAgent: {final_reply}")
                messages.append({"role": "assistant", "content": final_reply})
            
            else:
                reply = response_message.content
                print(f"\nAgent: {reply}")
                messages.append({"role": "assistant", "content": reply})

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_agent()
