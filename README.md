# Customer Service Chatbot

A high-performance generative chatbot solution designed to handle customer service inquiries following company policies while interfacing with backend APIs.

## Project Overview

This project implements a fully generative chatbot that utilizes Large Language Models (LLMs) to formulate responses while adhering to company policies. The solution integrates with specific API endpoints and follows a modular architecture for flexibility and maintainability.

### Key Features

- **LLM-powered conversational interface** that understands natural language requests
- **API integration** for order cancellation and tracking
- **Policy enforcement** to ensure responses follow company guidelines
- **Tree of Thoughts decision-making** for structured handling of complex queries
- **Retrieval-Augmented Generation (RAG)** support for knowledge-based responses

## Architecture

### Core Components

- **ChatToT (Chat Tree of Thoughts)**: 
  The central framework enabling flexible pipeline construction that combines LLM decision-making with deterministic code execution.
  
- **LLM Nodes**:
  Specialized components that handle natural language processing, making decisions, and generating user-facing content.
  
- **Code Nodes**:
  Python functions integrated into the processing pipeline for executing business logic, API calls, and data transformations.
  
- **RAG Support**:
  Infrastructure for retrieving and leveraging information from policy documents and knowledge bases.

### Services

- **`chat/`**: CORE service powering the conversational abilities based on the ChatToT class
- **`mock_API/`**: Simulated API endpoints for testing and development
- **`RAG_support/`**: Services that provide document retrieval and context augmentation

## ChatToT Advantages

The Chat Tree of Thoughts (ChatToT) framework offers significant benefits:

1. **Flexible Pipeline Construction**: Easily combine LLM and code nodes in any configuration
2. **No Reasoning Overhead**: Leverages LLM strengths like one-shot decisions and low latency
3. **Data Processing**: Efficiently extracts and transforms data between pipeline stages
4. **Deterministic Decision Paths**: Ensures predictable handling of user requests
5. **RAG Integration**: Seamlessly incorporates knowledge from policy documents where needed

## Use Cases

- **Order Cancellation Assistant**: 
  - Validates eligibility per policy 
  - Processes cancellation through API interactions
  - Provides appropriate support and confirmation
  
- **Order Tracking Support**:
  - Retrieves order status from backend systems
  - Formats tracking information in user-friendly responses
  
- **Policy Question Resolution**:
  - Uses RAG to answer questions about company policies // or shopping
  - Ensures accurate and consistent policy application

## Getting Started

### Prerequisites

```
# Requirements listed in requirements.txt
langchain_community
langchain_openai
openai
pypdf
faiss-cpu
networkx
matplotlib
requests
langfuse
```

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` with:

    - OPENAI_API_KEY 
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_HOST

### Running the Application

1. Start the mock API service:
```bash
python API_main.py
```

2. In a separate terminal, start the chatbot service:
```bash
python main.py
```

## Project Structure

```
CUSTOMER_SERVICE_CHATBOT/
├── demo_front_page/
├── services/
│   ├── chat/                   # Core chatbot service
│   │   ├── _pycache_/
│   │   ├── prompts/
│   │   ├── api_requests.py
│   │   ├── chat_ToT.py         # Main ChatToT implementation
│   │   ├── node_utils.py
│   │   └── policies_chat.py
│   ├── mock_API/               # API simulation
│   │   ├── _pycache_/
│   │   ├── data_mocking.py
│   │   ├── data_models.py
│   │   └── endpoints.py
│   └── RAG_support/            # Retrieval Augmented Generation
│       ├── _pycache_/
│       ├── csv_files/
│       ├── pdf_files/
│       └── RAG_processor.py
├── .env                        # Environment variables
├── API_main.py                 # API service entry point
├── main.py                     # Main application entry point
├── my_graph.png                # Visualization of ChatToT graph
└── requirements.txt
```

## Experiment & Evaluation

### Human Feedback
The most direct form to evaluate this kind of system is human supervision. To support this, trace collection is implemented using Langfuse, providing detailed insight into pipeline execution and decision-making.
Metrics

    - Input-Output Fitting: Customer satisfaction metric measuring how well responses address user needs
    - Latency: Response time measurements across different request types
    - Token Counting: Usage analytics and model pricing (unfortunately the most recent Langfuse version doesn`t support GPT-4.1 models)
    - Feature Tagging: Tracking which capabilities are used (e.g., retrieval operations)

### Future Enhancements
Although not yet implemented, the following approaches would improve evaluation:

#### Synthetic Chatting: 
Development of a module to generate a high variety of synthetic interactions to:

    - Debug system robustness
    - Identify system errors and weak nodes
    - Test edge cases and unexpected messages
    - Validate backup systems
    - Reduce manual testing time by enabling direct evaluation of traces and terminal feedback


#### Pricing Optimization via Backpropagation Model Switching:

    - The system is currently tested with GPT-4.1, which works satisfactorily for this MVP
    - In the future, we could substitute human supervision with GPT-4.1 automatic evaluation over smaller models
    - This would reduce costs by identifying which nodes can use more efficient models without compromising quality
    - Evaluation would start at leaf nodes and walk back up the tree, replacing models where less expensive ones work well


#### NER Implementation:

    - Add Named Entity Recognition for additional tagging
    - Detect generation patterns and improve response customization

# Customer Service Chatbot

A high-performance generative chatbot solution designed to handle customer service inquiries following company policies while interfacing with backend APIs.

## Project Overview

This project implements a fully generative chatbot that utilizes Large Language Models (LLMs) to formulate responses while adhering to company policies. The solution integrates with specific API endpoints and follows a modular architecture for flexibility and maintainability.

### Key Features

- **LLM-powered conversational interface** that understands natural language requests
- **API integration** for order cancellation and tracking
- **Policy enforcement** to ensure responses follow company guidelines
- **Tree of Thoughts decision-making** for structured handling of complex queries
- **Retrieval-Augmented Generation (RAG)** support for knowledge-based responses

## Architecture

### Core Components

- **ChatToT (Chat Tree of Thoughts)**: 
  The central framework enabling flexible pipeline construction that combines LLM decision-making with deterministic code execution.
  
- **LLM Nodes**:
  Specialized components that handle natural language processing, making decisions, and generating user-facing content.
  
- **Code Nodes**:
  Python functions integrated into the processing pipeline for executing business logic, API calls, and data transformations.
  
- **RAG Support**:
  Infrastructure for retrieving and leveraging information from policy documents and knowledge bases.

### Services

- **`chat/`**: CORE service powering the conversational abilities based on the ChatToT class
- **`mock_API/`**: Simulated API endpoints for testing and development
- **`RAG_support/`**: Services that provide document retrieval and context augmentation

## ChatToT Advantages

The Chat Tree of Thoughts (ChatToT) framework offers significant benefits:

1. **Flexible Pipeline Construction**: Easily combine LLM and code nodes in any configuration
2. **No Reasoning Overhead**: Leverages LLM strengths like one-shot decisions and low latency
3. **Data Processing**: Efficiently extracts and transforms data between pipeline stages
4. **Deterministic Decision Paths**: Ensures predictable handling of user requests
5. **RAG Integration**: Seamlessly incorporates knowledge from policy documents where needed

## Use Cases

- **Order Cancellation Assistant**: 
  - Validates eligibility per policy (orders < 10 days old)
  - Processes cancellation through API
  - Provides appropriate confirmations or alternatives
  
- **Order Tracking Support**:
  - Retrieves order status from backend systems
  - Formats tracking information in user-friendly responses
  
- **Policy Question Resolution**:
  - Uses RAG to answer questions about company policies
  - Ensures accurate and consistent policy application

## Getting Started

### Prerequisites

```
# Requirements listed in requirements.txt
openai
python-dotenv
langfuse
```

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`

### Running the Application

1. Start the mock API service:
```bash
python API_main.py
```

2. In a separate terminal, start the chatbot service:
```bash
python main.py
```

## Project Structure

```
CUSTOMER_SERVICE_CHATBOT/
├── demo_front_page/
├── services/
│   ├── chat/                   # Core chatbot service
│   │   ├── _pycache_/
│   │   ├── prompts/
│   │   ├── api_requests.py
│   │   ├── chat_ToT.py         # Main ChatToT implementation
│   │   ├── node_utils.py
│   │   └── policies_chat.py
│   ├── mock_API/               # API simulation
│   │   ├── _pycache_/
│   │   ├── data_mocking.py
│   │   ├── data_models.py
│   │   └── endpoints.py
│   └── RAG_support/            # Retrieval Augmented Generation
│       ├── _pycache_/
│       ├── csv_files/
│       ├── pdf_files/
│       └── RAG_processor.py
├── .env                        # Environment variables
├── API_main.py                 # API service entry point
├── main.py                     # Main application entry point
├── my_graph.png                # Visualization of ChatToT graph
└── requirements.txt
```

## Experiment & Evaluation

### Human Feedback
The most direct form to evaluate this kind of system is human supervision. To support this, trace collection is implemented using **Langfuse**, providing detailed insight into pipeline execution and decision-making.

### Metrics
- **Input-Output Fitting**: Customer satisfaction metric measuring how well responses address user needs
- **Latency**: Response time measurements across different request types
- **Token Counting**: Usage analytics and model pricing (unfortunately the most recent Langfuse version doesn`t support GPT-4.1 models)
- **Feature Tagging**: Tracking which capabilities are used (e.g., retrieval operations)

### Future Enhancements
Although not yet implemented, the following approaches would improve evaluation:

- **Synthetic Chatting**: Development of a module to generate a high variety of synthetic interactions to:
  - Debug system robustness
  - Identify system errors and weak nodes
  - Test edge cases and unexpected messages
  - Validate backup systems
  - Reduce manual testing time by enabling direct evaluation of traces and terminal feedback

- **Pricing Optimization via Backpropagation Model Switching**: 
  - The system is currently tested with GPT-4.1, which works satisfactorily for this MVP
  - In the future, we could substitute human supervision with GPT-4.1 automatic evaluation over smaller models
  - This would reduce costs by identifying which nodes can use more efficient models without compromising quality
  - Evaluation would start at leaf nodes and walk back up the tree, replacing models where less expensive ones work well

- **NER Implementation**:
  - Add Named Entity Recognition for additional tagging
  - Detect generation patterns and improve response customization

## Development Notes

### Node Architecture

The system is built around two primary node types and supporting components:

#### LLM-Powered Nodes
```python
llm_based_node = LLM_Node(
    name="llm_based_name",           # Key identifier for building graphs
    description="description",        # Used for data transfer between nodes
    parameters={
        "variable": {
            "type": "variable type", # "string", "integer", "float"
            "description": "variable description"
        }
    },
    required=["list of necessary variables"],  # All variables included by default
    template="prompt template with {parameters}",
    model="openai model",            # GPT model to use
    retriver=retriever               # Optional RAG system for specific pdf_files
)
```

**Important Notes:**
1. No LLM node is interactive - it must have a Code child to send system messages
2. Use `user_message` and `system_message` variables for chatting interactions
3. LLM_Node class has a fixed `self.sys_prompt` to guide chat behavior, leveraging OpenAI API cache for reduced latency and consumption

#### Code Nodes
```python
code_based_node = Code_Node(
    name="code_based_name",          # Same naming convention as LLM_Node
    description="description",
    parameters={
        "variable": {
            "type": "variable type", # "string", "integer", "float"
            "description": "variable description"
        }
    },
    required=[],
    function=core_function,          # Function that processes parent data
    is_interactive=True              # Whether node interacts with user
)
```

**Implementation Requirements:**
1. All `core_function` must accept `(arg, childs_tools, trase=True)` arguments
2. `arg` is passed as python dict following `parameters` and `required` specifications
3. `childs_tools` contains the list of possible following nodes
4. Output must provide Next_Node_name and Message (both strings)
5. Interactive nodes must have exactly one child, and their core function must return an additional parameter (dict) with necessary retrieval data
6. No loop pipelines should end with a non-interactive Code_Node (no children) - all finished pipelines return to the root
7. A backup `just_chatting` node manages unexpected behaviors in pipelines

#### RAG Implementation
```python
document_rag = RAG("pdf file path")  # Generate or load retrieval database
document_rag.get_retriver()          # Create retriever object for pipelines
```

**Configuration Options:**
1. Customize chunking with `chunk_size=1000, chunk_overlap=100`
2. `get_retriver` parameters:
   - `request_type`: Search algorithm ("similarity" (default) or "mmr" (Maximum Marginal Relevance))
   - `k`: Number of chunks to retrieve
   - `filter`: Metadata filters to narrow search space (e.g., "finance", "cancellations")
   - `score_threshold`: Minimum similarity score threshold (-1 to 1)
   - `lambda_mult`: Controls diversity in hybrid search (0-1, where 0 maximizes diversity)

#### ChatToT Framework
- Initialize with a root node where every process begins
- `conect_node_to_node(from_name:str, to_Node:Node)` establishes node connections
- `run_from(message, history, image, from_node_name=None, trase=True, max_retries=3)` executes the tree
- `visualize_graph()` generates a visualization of tree nodes and edges

### Future Enhancements

- **Improved ToT Visualization**: Better tools for easier iteration processes
- **Pipeline Management**: Loading from storage files and connecting trees for cleaner code
- **Multimodal Support**: Adding nodes for image-to-text processing (e.g., product returns)

## License

### Educational and Interview Use License

Copyright (c) 2025

**Permitted Use:** This software and associated documentation files (the "Software") are provided for educational purposes and job interview evaluation only. You may view, study, and run the Software for learning purposes or to evaluate the author`s coding abilities.

**Restrictions:** Without explicit written permission from the author:
1. You may not use the Software or any derivative works for commercial purposes
2. You may not distribute, sublicense, or sell copies of the Software
3. You may not modify, adapt, or build upon the Software for purposes other than educational review

**Disclaimer:** THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For permissions beyond the scope of this license, please contact the author.

## Acknowledgments

- This project was developed as a technical demonstration for job interview purposes
- Special thanks to the developers of the following technologies that made this project possible:
  - **OpenAI** for providing the GPT API that powers the conversational components
  - **Langfuse** for the observation and evaluation capabilities
  - **LangChain** for components that inspired parts of the RAG implementation
  - **PyPDF** for PDF document processing capabilities
  - **NetworkX** and **Matplotlib** for graph visualization and analysis
  - **Requests** for HTTP communications with API endpoints
  
- Appreciation to the open source community for the wealth of knowledge and tools that informed the architecture
- The Tree of Thoughts concept builds upon academic research in the field of LLM reasoning frameworks
- Any resemblance to existing commercial systems is coincidental: this project was created independently for educational purposes

This project represents my approach to solving conversational AI challenges with a focus on reliability, modularity, and policy adherence. While drawing inspiration from various open-source projects and research papers, the implementation and design decisions are my own.