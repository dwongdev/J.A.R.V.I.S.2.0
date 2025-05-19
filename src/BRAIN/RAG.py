

# import os
# import tempfile
# import shutil
# from pathlib import Path

# from docling.datamodel.base_models import InputFormat
# from docling.datamodel.pipeline_options import PdfPipelineOptions
# from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption, SimplePipeline

# from langchain_community.document_loaders import UnstructuredMarkdownLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_ollama import OllamaEmbeddings, OllamaLLM
# from langchain_community.vectorstores import FAISS
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from src.FUNCTION.Tools.get_env import load_variable


# def get_document_format(file_path) -> InputFormat:
#     ext = Path(file_path).suffix.lower()
#     return {
#         '.pdf': InputFormat.PDF,
#         '.docx': InputFormat.DOCX,
#         '.doc': InputFormat.DOCX,
#         '.pptx': InputFormat.PPTX,
#         '.html': InputFormat.HTML,
#         '.htm': InputFormat.HTML
#     }.get(ext, None)


# def convert_document_to_markdown(doc_path, md_path) -> str:
#     try:
#         input_path = os.path.abspath(str(doc_path))
#         with tempfile.TemporaryDirectory() as temp_dir:
#             temp_input = os.path.join(temp_dir, os.path.basename(input_path))
#             shutil.copy2(input_path, temp_input)

#             pipeline_options = PdfPipelineOptions(do_ocr=True, do_table_structure=True)
#             converter = DocumentConverter(
#                 allowed_formats=[InputFormat.PDF, InputFormat.DOCX, InputFormat.HTML, InputFormat.PPTX],
#                 format_options={
#                     InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
#                     InputFormat.DOCX: WordFormatOption(pipeline_cls=SimplePipeline)
#                 }
#             )

#             conv_result = converter.convert(temp_input)
#             if not conv_result or not conv_result.document:
#                 raise ValueError(f"Failed to convert document: {doc_path}")

#             md = conv_result.document.export_to_markdown()
#             md_path = os.path.abspath(md_path)
#             with open(md_path, "w", encoding="utf-8") as fp:
#                 fp.write(md)
#             return md_path
#     except Exception as e:
#         print(f"Error converting document: {e}")
#         return None

# def load_or_create_vectorstore(markdown_path, vectorstore_path):
#     vectorstore_path = Path(vectorstore_path)
#     vectorstore_path.parent.mkdir(parents=True, exist_ok=True)

#     embeddings_model_name = load_variable("Embedding_model")
#     embeddings = OllamaEmbeddings(model=embeddings_model_name)

#     # Check if vectorstore folder exists
#     if vectorstore_path.exists():
#         print(f"Loading existing vectorstore from: {vectorstore_path}")
#         vectorstore = FAISS.load_local(str(vectorstore_path), embeddings ,  allow_dangerous_deserialization=True)
#         return vectorstore

#     # Create new vectorstore
#     print(f"Creating new vectorstore for: {markdown_path}")
#     loader = UnstructuredMarkdownLoader(str(markdown_path))
#     documents = loader.load()

#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
#     texts = text_splitter.split_documents(documents)

#     vectorstore = FAISS.from_documents(texts, embeddings)
#     vectorstore.save_local(str(vectorstore_path))  # Save properly

#     return vectorstore

# def setup_qa_chain(markdown_path, vectorstore_path):
#     llm = OllamaLLM(model=load_variable("Rag_model"), temperature=0)

#     vectorstore = load_or_create_vectorstore(markdown_path, vectorstore_path)
#     memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)

#     qa_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
#         memory=memory,
#         return_source_documents=False
#     )
#     return qa_chain


# def ask_question(qa_chain, question: str):
#     result = qa_chain.invoke({"question": question})
#     return result.get('answer', 'No answer found.')
#     #print(f"**Question:** {question}\n**Answer:** {result.get('answer', 'No answer found.')}")


# def setup_qa_session(subject: str):
#     subject = subject.lower().strip().replace(" ", "_")
#     doc_path = Path(f"./DATA/RAWKNOWLEDGEBASE/{subject}_data.pdf")
#     md_path = Path(f"./DATA/KNOWLEDGEBASE/{subject}_data_converted.md")
#     vectorstore_path = Path(f"./DATA/VECTORSTORES/{subject}_vectorstore.pkl")

#     if not md_path.exists():
#         if not doc_path.exists():
#             print(f"No document found: {doc_path}")
#             return None
#         doc_format = get_document_format(doc_path)
#         if not doc_format:
#             print(f"Unsupported document format: {doc_path.suffix}")
#             return None
#         convert_document_to_markdown(doc_path, md_path)

#     try:
#         return setup_qa_chain(md_path, vectorstore_path)
#     except Exception as e:
#         print(f"Error setting up QA chain: {e}")
#         return None


# def chat_with_rag(subject: str):
#     qa_chain = setup_qa_session(subject)
#     if not qa_chain:
#         return
#     print("\nChat with the RAG model. Type 'exit' to quit.\n")
#     while True:
#         question = input("You: ")
#         if question.lower() in ["exit", "quit", "bye"]:
#             print("Goodbye!")
#             break
#         ask_question(qa_chain, question)


# if __name__ == "__main__":
#     subject_input = input("Enter subject name: ")
#     chat_with_rag(subject_input)

#.....

import os
import shutil
import tempfile
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption, SimplePipeline
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from src.FUNCTION.Tools.get_env import EnvManager

class RAGPipeline:
    def __init__(self):
        self.embedding_model = EnvManager.load_variable("Embedding_model")
        self.rag_model = EnvManager.load_variable("Rag_model")
        self.qa_chain = None

    def get_paths(self, subject: str):
        subject_clean = subject.lower().strip().replace(" ", "_")
        doc_path = Path(f"./DATA/RAWKNOWLEDGEBASE/{subject_clean}_data.pdf")
        md_path = Path(f"./DATA/KNOWLEDGEBASE/{subject_clean}_data_converted.md")
        vectorstore_path = Path(f"./DATA/VECTORSTORES/{subject_clean}_vectorstore.pkl")
        return doc_path, md_path, vectorstore_path

    def get_document_format(self, file_path) -> InputFormat:
        ext = Path(file_path).suffix.lower()
        return {
            '.pdf': InputFormat.PDF,
            '.docx': InputFormat.DOCX,
            '.doc': InputFormat.DOCX,
            '.pptx': InputFormat.PPTX,
            '.html': InputFormat.HTML,
            '.htm': InputFormat.HTML
        }.get(ext, None)

    def convert_document_to_markdown(self, subject: str) -> bool:
        try:
            doc_path, md_path, _ = self.get_paths(subject)
            if not doc_path.exists():
                print(f"No document found: {doc_path}")
                return False

            doc_format = self.get_document_format(doc_path)
            if not doc_format:
                print(f"Unsupported format: {doc_path.suffix}")
                return False

            input_path = os.path.abspath(str(doc_path))
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_input = os.path.join(temp_dir, os.path.basename(input_path))
                shutil.copy2(input_path, temp_input)

                pipeline_options = PdfPipelineOptions(do_ocr=True, do_table_structure=True)
                converter = DocumentConverter(
                    allowed_formats=[doc_format],
                    format_options={
                        doc_format: PdfFormatOption(pipeline_options=pipeline_options),
                        InputFormat.DOCX: WordFormatOption(pipeline_cls=SimplePipeline)
                    }
                )

                conv_result = converter.convert(temp_input)
                if not conv_result or not conv_result.document:
                    print(f"Conversion failed for: {doc_path}")
                    return False

                markdown = conv_result.document.export_to_markdown()
                md_path.parent.mkdir(parents=True, exist_ok=True)
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(markdown)
                return True
        except Exception as e:
            print(f"[Conversion Error] {e}")
            return False

    def load_or_create_vectorstore(self, subject: str):
        try:
            _, md_path, vectorstore_path = self.get_paths(subject)
            vectorstore_path.parent.mkdir(parents=True, exist_ok=True)
            embeddings = OllamaEmbeddings(model=self.embedding_model)

            if vectorstore_path.exists():
                print(f"Loading existing vectorstore from: {vectorstore_path}")
                return FAISS.load_local(str(vectorstore_path), embeddings, allow_dangerous_deserialization=True)

            print(f"Creating vectorstore for: {md_path}")
            loader = UnstructuredMarkdownLoader(str(md_path))
            documents = loader.load()

            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_documents(documents)

            vectorstore = FAISS.from_documents(chunks, embeddings)
            vectorstore.save_local(str(vectorstore_path))
            return vectorstore
        except Exception as e:
            print(f"[Vectorstore Error] {e}")
            return None

    def setup_chain(self, subject: str):
        try:
            _, md_path, _ = self.get_paths(subject)

            if not md_path.exists():
                if not self.convert_document_to_markdown(subject):
                    return None

            vectorstore = self.load_or_create_vectorstore(subject)
            if not vectorstore:
                return None

            llm = OllamaLLM(model=self.rag_model, temperature=0)
            memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)

            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
                memory=memory,
                return_source_documents=False
            )
            return self.qa_chain
        except Exception as e:
            print(f"[QA Chain Error] {e}")
            return None

    def ask(self, qa_chain , question: str) -> str:
        if not qa_chain:
            print("QA chain not initialized.")
            return "No QA chain available."
        try:
            result = qa_chain.invoke({"question": question})
            return result.get("answer", "No answer found.")
        except Exception as e:
            return f"Error: {e}"

    def interactive_chat(self , subject:str):
        if not self.setup_chain(subject):
            print("Could not set up RAG chain.")
            return
        print("\nChat with the RAG model. Type 'exit' to quit.\n")
        while True:
            question = input("You: ")
            if question.lower() in {"exit", "quit", "bye"}:
                print("Goodbye!")
                break
            print("AI:", self.ask(question))


if __name__ == "__main__":
    rag = RAGPipeline()
    rag.interactive_chat()

