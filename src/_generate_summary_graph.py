import graphviz
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

def generate_graph_code(model, text: str) -> str:
    """Generate Graphviz code from input text using an agent."""
    prompt_template = """
    You are an AI that generates **only** valid Graphviz code.

    Generate Graphviz code for a hierarchical mind map based on the following text:

    {text}

    **Important**: 
    - Your output must start immediately with `digraph G `.
    - Do not include any explanation, markdown fences, or additional text outside the Graphviz code.
    - The mind map should be oriented left-to-right. **Use `rankdir=LR;` not `rankdir=BT`**.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model

    # Generate Graphviz code
    graph_code = chain.invoke({"text": text}).content
    return graph_code

def display_graph(graph_code: str):
    """Render and display Graphviz graph in Jupyter Notebook."""
    try:
        graph = graphviz.Source(graph_code)
        return graph
    except Exception as e:
        print(f"Error rendering graph: {e}")