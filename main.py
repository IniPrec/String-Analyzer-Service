from fastapi import FastAPI, HTTPException, Depends, Response # Error handling (Used to send proper error codes.)
from database import Base, engine, SessionLocal
from models import StringRecord
from pydantic import BaseModel
from utils import analyze_string
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional # Each filter is optional - th euser can use any combination.
import re

app = FastAPI()

def interpret_query(query: str): # This interprets natural language query
    """
    Interprets simple natural language filters.
    Returns a dictionary of filter parameters.
    """
    query = query.lower()
    filters = {}

    # Palindrome filter
    if "palindrome" in query:
        filters["is_palindrome"] = True
    elif "not a palindrome" in query or "non-palindrome" in query:
        filters["is_palindrome"] = False

    # Word count filter
    word_count_match = re.search(r'(\d+)\s+word(?:s)?', query)
    if word_count_match:
        filters["word_count"] = int(word_count_match.group(1))
    
    # Length filters
    # Minimum length
    min_length_match = re.search(r"(?:more|greater|longer)\s+than\s+(\d+)", query)
    if min_length_match:
        filters["min_length"] = int(min_length_match.group(1)) + 1
    
    # Maximum length
    max_length_match = re.search(r"(?:less|shorter)\s+than\s+(\d+)", query)
    if max_length_match:
        filters["max_length"] = int(max_length_match.group(1))

    # Contains a character
    char_match = re.search(r"letter\s+([a-z])", query)
    if char_match:
        filters["contains_character"] = char_match.group(1)

    return filters

# Create the database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request schema (Pydantic)
class StringRequest(BaseModel): # Validates that incoming data contains a string field 'value'.
    value: str


@app.post("/strings", status_code=201) # Creates the first POST endpoint
def create_string(request: StringRequest, db: Session = Depends(get_db)):
    if request.value is None:
        raise HTTPException(status_code=400, detail="Input must be a string.")
    value = request.value.strip()

    # Validate input
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="Input must be a string.")
    if not value:
        raise HTTPException(status_code=400, detail="Input string cannot be empty.")

    # Analyze the string
    properties = analyze_string(value) # Calls the logic from 'utils.py'
    string_id = properties["sha256_hash"]

    # Check if string already exists
    existing = db.query(StringRecord).filter(StringRecord.id == string_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="String already exists.")
    
    # Store in database
    new_record = StringRecord(
        id=string_id,
        value=value,
        properties=properties,
        created_at=datetime.utcnow()
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "id": new_record.id,
        "value": new_record.value,
        "properties": new_record.properties,
        "created_at": new_record.created_at
    }

# GET /string/{string_value} - retrieves a specific string from the database by its raw text
@app.get("/strings/{string_value}")
def get_string(string_value: str, db: Session = Depends(get_db)):
    value = string_value.strip()
    sha256_hash = analyze_string(value)["sha256_hash"]

    record = db.query(StringRecord).filter(StringRecord.id == sha256_hash).first()

    if not record:
        raise HTTPException(status_code=404, detail="String not found.")
    
    return {
        "id": record.id,
        "value": record.value,
        "properties": record.properties,
        "created_at": record.created_at.isoformat() + "Z"
    }

# GET /strings - retrieves all stored strings from the database
@app.get("/strings")
def get_all_strings(
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # This will fetch all records first
    records = db.query(StringRecord).all() # This will get all stored strings
    filtered_records = []

    for record in records: # Loops through the records and applies the filters
        props = record.properties
        keep = True

        if is_palindrome is not None and props["is_palindrome"] != is_palindrome:
            keep = False
        if min_length is not None and props["length"] < min_length:
            keep = False    
        if max_length is not None and props["length"] > max_length:
            keep = False
        if word_count is not None and props["word_count"] != word_count:
            keep = False
        if contains_character is not None and contains_character not in record.value:
            keep = False
        
        if keep:
            filtered_records.append({ # Adds only matching records to the result list.
                "id": record.id,
                "value": record.value,
                "properties": props,
                "created_at": record.created_at.isoformat() + "Z"
            })

    return {
        "data": filtered_records,
        "count": len(filtered_records),
        "filters_applied": {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character
        }
    }

# Natural Language Route
@app.get("/strings/filter-by-natural-language")
def filter_by_natural_language(query: str, db: Session = Depends(get_db)):
    filters = interpret_query(query)
    
    # This will fetch all records first
    records = db.query(StringRecord).all() # This will get all stored strings
    filtered_records = []

    for record in records: # Loops through the records and applies the filters
        props = record.properties
        keep = True

        if "is_palindrome" in filters and props["is_palindrome"] != filters["is_palindrome"]:
            keep = False
        if "min_length" in filters and props["length"] < filters["min_length"]:
            keep = False    
        if "max_length" in filters and props["length"] > filters["max_length"]:
            keep = False
        if "word_count" in filters and props["word_count"] != filters["word_count"]:
            keep = False
        if "contains_character" in filters and filters["contains_character"] not in record.value:
            keep = False
        
        if keep:
            filtered_records.append({ # Adds only matching records to the result list.
                "id": record.id,
                "value": record.value,
                "properties": props,
                "created_at": record.created_at.isoformat() + "Z"
            })

    return {
        "query": query,
        "data": filtered_records,
        "count": len(filtered_records),
        "interpreted_filters": filters
    }

@app.delete("/strings/{string_value}", status_code=204) # This set the success code 204 (No content).
def delete_string(string_value: str, db: Session = Depends(get_db)):
    sha256_hash = analyze_string(string_value.strip())["sha256_hash"]
    record = db.query(StringRecord).filter(StringRecord.id == sha256_hash).first() # Finds the string record in the database.
    if not record:
        raise HTTPException(status_code=404, detail="String not found.") # If no record is found, raise a 404 error
    
    db.delete(record) # Remove the record from the database.
    db.commit() # Commit the changes to the database.
    return Response(status_code=204) # Return a 204 No Content response.