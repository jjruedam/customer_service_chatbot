import os
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import hashlib
import os


class RAG:
    def __init__(self, pdf_path, chunk_size=1000, chunk_overlap=100):
        self.pdf_path = pdf_path
        self.csv_path = f'services\\RAG_support\\csv_files' +"\\"+ os.path.basename(pdf_path) + ".csv"
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4.1")
        self.vectorstore = None
        
    def _calculate_pdf_hash(self):
        """Calculate MD5 hash of PDF file to detect changes"""
        with open(self.pdf_path, "rb") as file:
            file_hash = hashlib.md5(file.read()).hexdigest()
        return file_hash
    
    def _extract_and_chunk_pdf(self):
        """Extract text from PDF and split into chunks"""
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        chunks = text_splitter.split_documents(documents)
        return chunks
    
    def _save_chunks_to_csv(self, chunks, pdf_hash):
        """Save chunks to CSV file with their metadata"""
        data = []
        for i, chunk in enumerate(chunks):
            data.append({
                "chunk_id": i,
                "page": chunk.metadata.get("page", 0),
                "content": chunk.page_content,
                "source": self.pdf_path,
                "pdf_hash": pdf_hash
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.csv_path, index=False)
        return df
    
    def _load_chunks_from_csv(self):
        """Load chunks from CSV file"""
        return pd.read_csv(self.csv_path)
    
    def process_pdf(self, force_reprocess=False):
        """Process PDF and store chunks in CSV, or load existing chunks if available"""
        current_hash = self._calculate_pdf_hash()
        
        # Check if CSV exists and if PDF has changed
        if os.path.exists(self.csv_path) and not force_reprocess:
            df = self._load_chunks_from_csv()
            if len(df) > 0 and df["pdf_hash"].iloc[0] == current_hash:
                print(f"Loading existing chunks from {self.csv_path}")
                return df
        
        # Process PDF and save to CSV
        print(f"Processing PDF: {self.pdf_path}")
        chunks = self._extract_and_chunk_pdf()
        df = self._save_chunks_to_csv(chunks, current_hash)
        return df
    
    def build_vectorstore(self):
        """Build vector store from chunks"""
        df = self.process_pdf()
        
        # Create documents from DataFrame
        from langchain_core.documents import Document
        documents = [
            Document(
                page_content=row["content"],
                metadata={"page": row["page"], "source": row["source"]}
            )
            for _, row in df.iterrows()
        ]
        
        # Create vector store
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        return self.vectorstore
    
    def setup_rag_chain(self):
        """Set up the RAG chain"""
        if not self.vectorstore:
            self.build_vectorstore()
        
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        
        template = """Answer the question based only on the following context:
        {context}
        
        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain
    
    def query(self, question):
        """Query the RAG system"""
        rag_chain = self.setup_rag_chain()
        return rag_chain.invoke(question)
    
    def get_retriver(self, request_type="similarity", filter_key=None, top_k = 4, lambda_mult=1, score_threshold=0.8):
        """Setting a custom retriver"""
        if not self.vectorstore:
            self.build_vectorstore()
        
        retriever = self.vectorstore.as_retriever(request_type=request_type,
                                                  filter={"category": filter_key}, 
                                                  search_kwargs={"k": top_k},
                                                  score_threshold=score_threshold,
                                                  lambda_mult=lambda_mult)
        return retriever


# Example usage
if __name__ == "__main__":
    # Initialize the RAG system with a PDF path
    policy_rag = RAG(f"services\\RAG_support\\pdf_files\\TechStream Computing Web Store Policies.pdf")
    
    # Process the PDF (will only reprocess if the PDF has changed)
    policy_rag.process_pdf()
    
    # Build the vector store
    policy_rag.build_vectorstore()
    
    # Query the system
    query = "What is the company's policy on cancellations?"
    response = policy_rag.query(query)
    print(f"Query: {query}")
    print(f"Response: {response}")