from Company_Terms_Analzye.schemas.Company_dto import CompanyAnalysisResponse
from Company_Terms_Analzye.core.Company_config import PROMPT_COMPANY_TEXT

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

term_llm = ChatOpenAI(temperature=0.1, model="gpt-4o-mini").bind(
    response_format={"type": "json_object"}
)

# 불공정 약관과 langChain 형태 동일

parser = JsonOutputParser(pydantic_object=CompanyAnalysisResponse)

company_prompt = ChatPromptTemplate.from_template(
    PROMPT_COMPANY_TEXT,
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

company_chain = get_llm_chain(
    term_llm,
    company_prompt,
    parser
)