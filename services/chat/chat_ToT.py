#from services.RAG_support.RAG_processor import RAG
from openai import OpenAI
import os
from dotenv import load_dotenv
import re
import json
import base64
from abc import ABC, abstractmethod
from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe
from services.image_to_text.product_processor import Image_Analyzer

"""langfuse = Langfuse(
  secret_key="sk-lf-5be7ebc4-7576-4267-aee9-3ba43a84dac5",
  public_key="pk-lf-69c8d5a6-c174-4ddb-93d1-1b8146792e23",
  host="https://cloud.langfuse.com"
)"""

langfuse = Langfuse(
  secret_key=os.environ['LANGFUSE_SECRET_KEY'],
  public_key=os.environ['LANGFUSE_PUBLIC_KEY'],
  host=os.environ['LANGFUSE_HOST']
)

load_dotenv()  # Load environment variables from .env file
client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY']
)

### Node ###
class Node():
    def __init__(self, name:str, description:str, parameters, required = []):
    
        # Use re.match to check if name matches naming pattern
        naming_pattern = r'^[a-zA-Z0-9_-]+$'
        if not(re.match(naming_pattern, name)):
            raise TypeError(f"Naming Error: '{name}' expected to be a string that matches the pattern '^[a-zA-Z0-9_-]+$'")
        
        # Validate parameters format
        if not isinstance(parameters, dict):
            raise TypeError("Parameters must be a dictionary")
            
        for param_name, param_details in parameters.items():
            if not isinstance(param_details, dict):
                raise TypeError(f"Parameter '{param_name}' details must be a dictionary")
                
            if "type" not in param_details:
                raise ValueError(f"Parameter '{param_name}' is missing 'type' field")
                
            if "description" not in param_details:
                raise ValueError(f"Parameter '{param_name}' is missing 'description' field")
        
        
        # If required list is empty, include all parameter names
        if required is None or required == []:
            self.required = list(parameters.keys())
        else:
            # Validate that all required parameters exist in parameters or if no one is required
            for param_name in required:
                if param_name not in parameters and param_name != "None":
                    raise ValueError(f"Required parameter '{param_name}' not found in parameters")

        self.corpus = {"type": "function",
                       "function":{"name": name,
                       "description":description,
                       "parameters": {
                            "type": "object",
                            "properties": parameters,
                            "required": required,
                            "additionalProperties": False
                        }}}
        
        # node description for function calling and graph interactions
        self.childs_tools = []

        # Interactive nodes: Code_Nodes only for graph-customers interactions
        self.is_interactive_node = False

    #Method to call node in graph execution
    @abstractmethod
    def call(self):
        pass


### LLM call Node ###
class LLM_Node(Node):
    def __init__(self,name, description, parameters, template, model:str, required=[], retriver=None):
        super().__init__(name, description, parameters, required)

        if name == "backup_system":
            # Check for exact keys
            valid_backup_system = True
            required_keys = {"user_message", "route_info", "error_type"}
            if set(parameters.keys()) != required_keys:
                valid_backup_system= False
            
            # Check types
            valid_backup_system= (parameters["user_message"]["type"] == "string" and 
                    parameters["route_info"]["type"] == "string" and 
                    parameters["error_type"]["type"] == "string")
            
            if not valid_backup_system:
                raise ValueError("A backup_system node must have only 'user_message', 'route_info', 'error_type' keys (strings)")

        self.template = template
        self.__model = model
        self.retriver = retriver
        self.sys_prompt = """You are an e-commerce support assistant. Maintain a helpful, solution-focused approach with customers while following these guidelines:
        
                Use a warm, professional tone with concise responses
                Identify and address the customer's primary concern first
                Ask clarifying questions when needed, one at a time
                Provide direct solutions without unnecessary steps
                Acknowledge when issues require human escalation
                Confirm resolution before ending conversations
                Never share sensitive customer information
                Avoid making promises outside established policies

                Your core function is resolving customer inquiries efficiently while creating positive experiences. Specific product details and company policies will be provided separately."""
    @observe()                    
    def call(self, arg, history, trase=True, sys_data = {}):
        request = self.template.format(**arg)
        is_retrieved = False
        if self.retriver:
            # Execute the retriever to get documents and Format the retrieved content into a string
            retrieved_docs = self.retriver.invoke(request)
            is_retrieved = True
            context_text = "\n".join([doc.page_content for doc in retrieved_docs])

            inner_template = self.sys_prompt + f"""Answer the request based only on the following context:
            {context_text}"""
        else:
            inner_template = self.sys_prompt

        if sys_data:
            request = f"If and only if it is necessary include System data/Order details: {sys_data}\n\n" + request

        messages = [{"role": "system", "content": inner_template}] + history + [{"role": "user", "content": request}]

        langfuse_context.update_current_trace(
                name=self.corpus["function"]["name"],
                tags=[self.__model, f"retrieve = {is_retrieved}"], metadata=self.corpus,
            )

        if self.childs_tools:
            completion = client.chat.completions.create(
                model=self.__model,
                store=trase,
                messages=messages,
                tools=self.childs_tools,tool_choice='required'
            )
            tool_calling = completion.choices[0].message.tool_calls[0].function
            # return "next node name", "next node arguments"
            return tool_calling.name, json.loads(tool_calling.arguments)
        else:
            completion = client.chat.completions.create(
                model=self.__model,
                store=trase,
                messages=messages
            )
            # return "no next node", "answer"    
            return None, completion.choices[0].message

### python Node ###
class Code_Node(Node):
    def __init__(self,name, description, parameters, function:callable, required=[], is_interactive=False):
        super().__init__(name, description, parameters, required)

        if name == "backup_system":
            raise ValueError("backup_system node must be a LLM_Node. Review Documentation")

        self.core_function = function
        self.is_interactive_node = is_interactive
    def call(self, arg, history, trase=True, sys_data = {}):
        if self.is_interactive_node and not self.childs_tools:
            raise ValueError(f"Interactive nodes, as {self.corpus["function"]["name"]}, must have one and only one connection")
        return self.core_function(arg, trase=trase, childs_tools=self.childs_tools)

class Image_to_Text_Node(Node):
    def __init__(self, name, description, parameters, model:str, yolo_model= "yolov8n.pt",required=[]):
        super().__init__(name, description, parameters, required)
        self.image_analyzer = Image_Analyzer(
            openai_api_key=os.environ['OPENAI_API_KEY'],
            fundational_model= model,
            yolo_model_path=yolo_model  # Will download automatically if not present
        )

    def call(self, arg, history, trase=True, sys_data = {}):
        image_analysis = self.image_analyzer.analyze_product(arg["image"])

        if 'gpt_analysis' not in image_analysis:
            return image_analysis['description']
        
        # Processed Image
        main_product_details = image_analysis['preprocessing_results']['detected_objects'][image_analysis['preprocessing_results']['main_product_id']]
        gpt_analysis = image_analysis['gpt_analysis']

        ## Product
        product_detected = main_product_details['class']
        product_confidence = main_product_details['confidence']

        ## Condition
        condition = gpt_analysis["condition"]
        confidence = gpt_analysis["confidence"]
        description = gpt_analysis["description"]
        defects_found = gpt_analysis["defects_found"]
        overall_assessment = gpt_analysis["overall_assessment"]

        return image_analysis

### Chat Tree of Thoghts ###
class ChatToT():
    def __init__(self, root:Node):
        self.root_name = root.corpus["function"]["name"]
        self.__graph ={self.root_name:{"node":root, "childs":[]}}
        self.__sys_data = {}

    def conect_node_to_node(self, from_name:str, to_Node:Node):

        # Load parent node graph representation
        from_node_rep = self.__graph[from_name]

        # Check interactive nodes has only one child
        if from_node_rep["node"].is_interactive_node and from_node_rep["childs"]:
            raise TypeError(f"Interactive nodes, as {from_name}, must have one and only one connection")
        # Update graph connections if it don't already exist
        if to_Node.corpus["function"]["name"] not in from_node_rep["childs"]:
            from_node_rep["node"].childs_tools.append(to_Node.corpus)
            from_node_rep["childs"].append(to_Node.corpus["function"]["name"])
            if to_Node.corpus["function"]["name"] not in self.__graph:
                    self.__graph.update({to_Node.corpus["function"]["name"]:{"node":to_Node, "childs":[]}})
        else:
            raise TypeError(f"{to_Node.corpus["function"]["name"]} alrady connected from {from_name}")
            
    def run_from(self, message, history, image, from_node_name=None, trase=True, max_retries=3):
        arg = {"user_message": message, "image": image}
        
        # Store nodes execution path for retries
        execution_path = []
        
        # Start from the specified node or root
        if from_node_name:
            current_node_name = from_node_name
        else:
            current_node_name = self.root_name
            
        # Main execution loop
        while current_node_name:
            retry_count = 0
            success = False
            
            # Add current node to execution path
            if current_node_name not in execution_path:
                execution_path.append(current_node_name)
            
            # Retry loop for current node
            while retry_count < max_retries and not success:
                try:
                    print(f"Executing {current_node_name} (attempt {retry_count + 1}/{max_retries}) -> {arg}")
                    current_node = self.__graph[current_node_name]["node"]
                    
                    if current_node.is_interactive_node:
                        next_node_name, arg, callback= current_node.call(arg, history, trase=trase, sys_data = self.__sys_data)
                        self.__sys_data |= callback
                        success = True
                        # For interactive nodes, we break the main loop after successful execution
                        if success:
                            current_node_name = next_node_name
                            break
                    else:
                        next_node_name, arg = current_node.call(arg, history, trase=trase, sys_data = self.__sys_data)
                        success = True
                        if success:
                            current_node_name = next_node_name
                    
                except Exception as e:
                    retry_count += 1
                    print(f"Error in node {current_node_name}: {str(e)}")
                    
                    if retry_count >= max_retries:
                        print(f"Maximum retries reached for node {current_node_name}")
                        
                        # Call backup_system node if system has one
                        if "backup_system" in self.__graph.keys():
                            current_node_name = "backup_system"
                            arg = {
                                "user_message":  str(arg),
                                "route_info":  f"Error in node {current_node_name}: {self.__graph[current_node_name]["node"].corpus["function"]["description"]}",
                                "error_type": str(e)}
                        # Go back one step in the execution path if possible
                        elif len(execution_path) > 1:
                            execution_path.pop()  # Remove current failed node
                            current_node_name = execution_path[-1]  # Go back to previous node
                            print(f"Retrying from previous node: {current_node_name}")
                            retry_count = 0  # Reset retry count for the previous node
                        else:
                            print("No previous nodes to retry from. Execution failed.")
                            return None, arg
            
            # Break main loop if interactive node was executed successfully
            if current_node.is_interactive_node and success:
                break

        # Clear callbacks in output nodes 
        if current_node_name == "":
            self.__sys_data = {}

        return current_node_name, arg
    
    def visualize_graph(self, figsize=(20, 16), node_size=4000, font_size=10, 
                   llm_node_color='lightblue', code_node_color='lightgreen', 
                   default_node_color='gray', llm_edge_color='black', code_edge_color='red',
                   layout='shell', title=None):
            import networkx as nx
            import matplotlib.pyplot as plt
            from matplotlib.patches import Patch
            
            # Create a directed graph
            G = nx.MultiDiGraph()
            
            # Store node types for coloring
            node_types = {}
            node_colors = []
            edge_colors = []
            
            # Add all nodes first with their type information
            for node_name, node_data in self.__graph.items():
                G.add_node(node_name)
                # Get node type from node object if available
                if hasattr(node_data["node"], "__class__"):
                    node_type = node_data["node"].__class__.__name__
                else:
                    # Try to determine type from corpus if available
                    try:
                        node_type = node_data["node"].corpus.get("type", "Unknown")
                    except (AttributeError, KeyError):
                        node_type = "Unknown"
                
                node_types[node_name] = node_type
            
            # Add all edges
            for node_name, node_data in self.__graph.items():
                for child_name in node_data["childs"]:
                    G.add_edge(node_name, child_name)
            
            # Create the figure
            fig, ax = plt.subplots(figsize=figsize)
            
            # Choose the layout
            if layout == 'spring':
                pos = nx.spring_layout(G, seed=42)
            elif layout == 'circular':
                pos = nx.circular_layout(G)
            elif layout == 'kamada_kawai':
                pos = nx.kamada_kawai_layout(G)
            elif layout == 'shell':
                pos = nx.shell_layout(G)
            elif layout == 'spectral':
                pos = nx.spectral_layout(G)
            else:
                pos = nx.spring_layout(G, seed=42)  # Default to spring layout
            
            # Determine color for each node based on its type
            for node in G.nodes():
                if "LLM_Node" in node_types[node]:
                    node_colors.append(llm_node_color)
                    edge_colors.append(llm_edge_color)
                elif "Code_Node" in node_types[node]:
                    node_colors.append(code_node_color)
                    edge_colors.append(code_edge_color)
                else:
                    node_colors.append(default_node_color)
                    edge_colors.append(default_node_color)
            
            # Draw the graph
            nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=node_colors, alpha=0.8, ax=ax)
            # Draw edges with a minimum distance
            nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowsize=30, 
                                 min_source_margin=20, min_target_margin=25, ax=ax)
            nx.draw_networkx_labels(G, pos, font_size=font_size, font_family='sans-serif', ax=ax)
            
            # Create legend
            legend_elements = [
                Patch(facecolor=llm_node_color, edgecolor='k', label='LLM Node'),
                Patch(facecolor=code_node_color, edgecolor='k', label='Code Node'),
                Patch(facecolor=default_node_color, edgecolor='k', label='Other Node')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            # Add title if provided
            if title:
                ax.set_title(title, fontsize=16)
            
            # Turn off axis
            ax.axis('off')
            
            # Tight layout
            plt.tight_layout()
            
            return fig