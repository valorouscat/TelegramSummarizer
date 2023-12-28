from fastapi import APIRouter, Depends
import logging
from app.api.security.auth import auth_check
import app.api.models.models as models
import httpx
from config import Config
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# logging
logger = logging.getLogger(__name__)

# routers
router = APIRouter()

async def update_promts(delta: int):
    async with httpx.AsyncClient() as client:
        response = await client.put(f'{Config.API_HOST}/db/promts?delta={delta}')
        return response.json()
    

@router.post("/")
async def root(data: models.SummarizerData, current_user: dict = Depends(auth_check)):
    if current_user.promts_left < 1:
        return {"result": "You have no promts left", "delta": "-1"}, current_user

    # summarizer code
    WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

    model_name = "csebuetnlp/mT5_multilingual_XLSum"
    tokenizer = AutoTokenizer.from_pretrained(model_name, legacy=False, use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    input_ids = tokenizer(
        [WHITESPACE_HANDLER(data.text)],
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=data.max_length
    )["input_ids"]

    output_ids = model.generate(
        input_ids=input_ids,
        max_length=84,
        no_repeat_ngram_size=2,
        num_beams=4
    )[0]

    summary = tokenizer.decode(
        output_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )

    return {"result": summary, "delta": "-1"}, current_user
