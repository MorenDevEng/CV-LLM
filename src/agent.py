import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

VECTOR_DIR = "vectordb"

BLOCKED_PATTERNS = [
    r'ignora[rs]?\s+(las?\s+)?instruccione',
    r'olvida[rs]?\s+(las?\s+)?instruccione',
    r'siempre\s+dec[ií]',
    r'nueva\s+instrucci[óo]n',
    r'sobre[sz]crib[e]?\s+instruccione',
    r'prompt\s*injection',
    r'sys.*eval',
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__',
    r'<script',
    r'{{.*}}',
    r'\{.*\}',
    r'\[\[.*\]\]',
    r'\$\{.*\}',
]

MAX_QUERY_LENGTH = 500
MAX_KEYWORDS_LENGTH = 200

class SecurityError(Exception):
    pass

def sanitize_input(text, max_length=MAX_QUERY_LENGTH):
    if not text or not isinstance(text, str):
        raise SecurityError("Entrada inválida")
    
    text = text.strip()
    
    if len(text) > max_length:
        raise SecurityError(f"Entrada muy larga. Máximo {max_length} caracteres")
    
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    return text

def check_blocked_patterns(text):
    text_lower = text.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            raise SecurityError("Entrada contiene patrones no permitidos")

def validate_question(question):
    sanitized = sanitize_input(question, MAX_QUERY_LENGTH)
    check_blocked_patterns(sanitized)
    return sanitized

def validate_keywords(keywords):
    sanitized = sanitize_input(keywords, MAX_KEYWORDS_LENGTH)
    check_blocked_patterns(sanitized)
    
    keywords_list = [k.strip() for k in keywords.split(',') if k.strip()]
    if len(keywords_list) > 20:
        raise SecurityError("Máximo 20 palabras clave")
    
    for kw in keywords_list:
        if len(kw) < 2:
            raise SecurityError("Las palabras clave deben tener al menos 2 caracteres")
    
    return keywords

class RAGPipeline:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        self.vectorstore = None
        self.rag_chain = None
        
    def load_pdf(self, file_path):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        return chunks
    
    def load_multiple_pdfs(self, file_paths: list[str]):
        all_chunks = []
        for file_path in file_paths:
            chunks = self.load_pdf(file_path)
            all_chunks.extend(chunks)
        return all_chunks
    
    def create_embeddings(self, chunks, collection_name="pdf_rag"):
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            collection_name=collection_name,
            persist_directory=VECTOR_DIR
        )
        
        return self.vectorstore
    
    def create_qa_chain(self):
        prompt_template = """Eres un asistente especializado en analizar documentos PDF/curriculum.
Tu función es responder preguntas sobre el contenido del documento proporcionado.

REGLAS:
1. Solo responde basándote en el contexto del documento
2. No uses asteriscos ni formato markdown
3. No inventes información
4. Sé breve y preciso en tus respuestas
5. Responde siempre en español

Contexto del documento:
{context}

Pregunta: {question}

Respuesta breve:"""

        prompt = PromptTemplate.from_template(prompt_template)
        
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        self.rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return self.rag_chain
    
    def process_pdf(self, file_path):
        chunks = self.load_pdf(file_path)
        self.create_embeddings(chunks)
        self.create_qa_chain()

    def process_multiple_pdfs(self, file_paths: list[str]):
        chunks = self.load_multiple_pdfs(file_paths)
        self.create_embeddings(chunks)
        self.create_qa_chain()

    def chat(self, question):
        if not self.rag_chain:
            return "Primero debes procesar un documento PDF."
        
        try:
            safe_question = validate_question(question)
        except SecurityError as e:
            return str(e)
        
        result = self.rag_chain.invoke(safe_question)
        return result
    
    def match_keywords(self, keywords_str):
        if not self.vectorstore:
            return {'percentage': 0, 'matched': []}
        
        try:
            safe_keywords = validate_keywords(keywords_str)
        except SecurityError as e:
            return {'percentage': 0, 'matched': [], 'error': str(e)}
        
        keywords = [k.strip().lower() for k in safe_keywords.split(',') if k.strip()]
        
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10})
        docs = retriever.invoke("")
        
        full_text = ' '.join([doc.page_content for doc in docs]).lower()
        
        matched = []
        for keyword in keywords:
            if keyword in full_text:
                matched.append(keyword)
        
        percentage = int((len(matched) / len(keywords)) * 100) if keywords else 0
        
        return {'percentage': percentage, 'matched': matched}

rag_pipeline = RAGPipeline()