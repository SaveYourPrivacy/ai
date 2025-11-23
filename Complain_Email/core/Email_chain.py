from Complain_Email.schemas.Email_dto import ComplaintResponse
from Complain_Email.core.Email_config import PROMPT_COMPLAIN_TEXT

#-------[LangChain Core]--------------------
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.output_parsers import JsonOutputParser

#--------------------------------------------
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
#--------------------------------------------

# 불공정 약관 분석과 lang chain 형태는 동일

term_llm = ChatOpenAI(temperature=0.1, model="gpt-4o-mini").bind(
    response_format={"type": "json_object"}
)

parser = JsonOutputParser(pydantic_object=ComplaintResponse)

complain_prompt = ChatPromptTemplate.from_template(
    PROMPT_COMPLAIN_TEXT,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def get_llm_chain(
        llm: ChatOpenAI, 
        prompt: ChatPromptTemplate, 
        parser: JsonOutputParser
) -> RunnableSequence:
    
    chain = ( 
        prompt
        | llm
        | parser
    )
    return chain

complain_chain = get_llm_chain(
    term_llm,
    complain_prompt,
    parser
)

