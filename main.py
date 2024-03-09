from ast import literal_eval
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel, constr
from typing import List, Optional


class TOORequestModel(BaseModel):
    bin: constr(min_length=12, max_length=12)
    head_iin: constr(min_length=12, max_length=12)
    request_date: str
    p1: Optional[int]
    p2: Optional[int]
    p3: Optional[int]
    p4: Optional[int]
    p5: Optional[int]
    p6: Optional[int]


class ItemModel(BaseModel):
    amount: int
    val: float


class TOOResponseModel(BaseModel):
    result: Optional[List[ItemModel]]
    statusCode: Optional[int]
    timestamp: Optional[str]
    code: Optional[str]
    message: Optional[str]
    description: Optional[str]


df = pd.read_excel("mok_table.xlsx")
df['iin'] = df['iin'].apply(lambda x: f'{x:012}')
app = FastAPI()


@app.post('/TOO-score', response_model=TOOResponseModel)
async def too_score(data: TOORequestModel):
    request_date = data.request_date
    owner_iin = data.head_iin
    if owner_iin in df['iin'].values:
        statusCode = df.loc[df['iin'] == owner_iin, 'statusCode'].iloc[0]
        if pd.notna(statusCode):
            statusCode = int(statusCode)
            code = df.loc[df['iin'] == owner_iin, 'code'].iloc[0]
            time = df.loc[df['iin'] == owner_iin, 'timestamp'].iloc[0]
            message = df.loc[df['iin'] == owner_iin, 'message'].iloc[0]
            description = df.loc[df['iin'] == owner_iin, 'description'].iloc[0]
            return {
                "result": None,
                "statusCode": statusCode,
                "timestamp": time,
                'code': code,
                'message': message,
                'description': description
            }

        result_str = df.loc[df['iin'] == owner_iin, 'result'].iloc[0]
        try:
            result = literal_eval(result_str)
        except (ValueError, SyntaxError) as e:
            print(f"Error evaluating result: {e}")
            return {
                "result": None,
                "statusCode": None,
                "timestamp": None,
                'code': None,
                'message': None,
                'description': None
            }
        return {
            "result": [{"amount": int(item['amount']), "val": float(item['val'])} for item in result],
            "statusCode": None,
            "timestamp": None,
            'code': None,
            'message': None,
            'description': None
        }
    else:
        return {
            "result": None,
            "statusCode": None,
            "timestamp": None,
            'code': None,
            'message': None,
            'description': None
        }