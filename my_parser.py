from langchain.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

class MyParser:
    def __init__(self, model_name: str = "gpt-5", api_key: str = os.getenv("OPENAI_API_KEY"), temperature: float = 0.0, max_tokens: int = None):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.parser_llm = ChatOpenAI(model=self.model_name, api_key=self.api_key, temperature=self.temperature, max_tokens=self.max_tokens)
        self.reviewer_llm = ChatOpenAI(model=self.model_name, api_key=self.api_key, temperature=self.temperature, max_tokens=self.max_tokens)
        self.system_prompt_parser = ""
        self.system_prompt_reviewer = ""

    def _build_system_prompt_parser(self):
        return """
        You are a parser. You are given a file and you need to parse it.
        You need to return the parsed file.
        """

    def _build_system_prompt_reviewer(self):
        return """
        You are a reviewer. You are given a file and you need to review it.
        You need to return the reviewed file.
        """

    def extract_text_from_pdf(self, pdf_path, output_txt_path=None):
        import fitz  # PyMuPDF
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        full_text = []
        
        print(f"Processing {len(doc)} pages...")
        
        # Iterate through each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Extract text. "text" mode gives plain text.
            # You can also use "blocks" to get text with coordinates if needed later.
            text = page.get_text("text")
            
            # Optional: Add a page marker to know where text came from
            page_marker = f"\n\n--- Page {page_num + 1} ---\n\n"
            full_text.append(page_marker + text)
            
        joined_text = "".join(full_text)
        
        # Save to file if path is provided
        if output_txt_path:
            with open(output_txt_path, "w", encoding="utf-8") as f:
                f.write(joined_text)
            print(f"Done! Text saved to {output_txt_path}")
            
        return joined_text
        

    def _parse_llm_invoke(self, messages: list[AnyMessage]) -> str:
        response = self.parser_llm.invoke(messages)
        return response.content
    
    def _review_llm_invoke(self, messages: list[AnyMessage]) -> str:
        response = self.reviewer_llm.invoke(messages)
        return response.content

    def parse_pdf(self, pdf_path: str | Path) -> str:
        import base64

        text = self.extract_text_from_pdf(pdf_path)

        with open(pdf_path, "rb") as file:
            pdf_content = file.read()
        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        messages_parser = []
        messages_parser.append(SystemMessage(self._build_system_prompt_parser()))
        messages_parser.append(HumanMessage(content=[
            {"type": "text", "text": f"Parse the following text and return the parsed text.{f' \n\nExtracted text: \n\n{text}' if text else ''}"},
            {
                "type": "file",
                "file": {
                    "filename": Path(pdf_path).name,
                    "file_data": f"data:application/pdf;base64,{pdf_base64}"
                }
            }
        ]))

        
        parsed_text = self._parse_llm_invoke(messages_parser)
        messages_parser.append(AIMessage(content=[{"type": "text", "text": parsed_text}]))

        messages_reviewer = []
        messages_reviewer.append(SystemMessage(self._build_system_prompt_reviewer()))
        messages_reviewer.append(HumanMessage(content=[
            {"type": "text", "text": f"Review the following text and return the suggestions for improvement. \n\n Parsed text: \n\n{parsed_text}"},
            {
                "type": "file",
                "file": {
                    "filename": Path(pdf_path).name,
                    "file_data": f"data:application/pdf;base64,{pdf_base64}"
                }
            }
        ]))

        for _ in range(1):
            review_text = self._review_llm_invoke(messages_reviewer)
            messages_reviewer.append(AIMessage(content=[{"type": "text", "text": review_text}]))
            messages_parser.append(HumanMessage(content=[{"type": "text", "text": review_text}]))
            
            parsed_text = self._parse_llm_invoke(messages_parser)
            messages_reviewer.append(HumanMessage(content=[{"type": "text", "text": f"Review the following text and return the suggestions for improvement. \n\n Parsed text: \n\n{parsed_text}"}]))

        
        print("messages_parser:")
        for message in messages_parser:
            print(message.pretty_print())

        print("messages_reviewer:")
        for message in messages_reviewer:
            print(message.pretty_print())
        return parsed_text


if __name__ == "__main__":
    parser = MyParser()
    answer = parser.parse_pdf("research/Uni-Verse-Files/part1_guide_discipline_selection.pdf")
    print(answer)