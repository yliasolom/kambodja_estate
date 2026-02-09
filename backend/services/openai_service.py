from openai import AsyncOpenAI
from config import settings
from pathlib import Path

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def load_system_prompt() -> str:
    """Load system prompt from file"""
    prompt_file = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()

def build_prompt(property_data, knowledge: str, question: str) -> str:
    """
    Build a prompt for OpenAI based on property data and question
    """
    prompt = f"""
Property Details:
- Type: {property_data.type}
- Price: ${property_data.price_usd:,.0f} USD
- Bedrooms: {property_data.bedrooms}
- Bathrooms: {property_data.bathrooms}
- Floor Area: {property_data.size_sqm} m²
- Land Size: {property_data.land_size_sqm} m² (if applicable)
- Ownership Type: {property_data.ownership_type}
- Location: {property_data.location}
- Floor Level: {property_data.floor_level if property_data.floor_level else 'N/A (not a condo)'}

Eligibility for Foreigners:
- Can own directly: {"Yes" if property_data.is_foreign_eligible_direct else "No"}
- Has land: {"Yes" if property_data.has_land else "No"}
- Recommended structures: {", ".join(property_data.recommended_structures) if property_data.recommended_structures else "None"}

Relevant Cambodia Property Law Information:
{knowledge}

User Question: {question}

Please answer the user's question about THIS SPECIFIC property. Use the property details and legal information provided above. Remember to:
- Be positive and focus on possibilities
- Use simple language
- Mention this is common for foreigners
- Suggest consulting a lawyer
- Keep it under 350 words
"""
    
    return prompt

async def call_openai(property_data, knowledge: str, question: str) -> str:
    """
    Call OpenAI API to generate answer (non-streaming)
    """
    try:
        system_prompt = load_system_prompt()
        user_prompt = build_prompt(property_data, knowledge, question)
        
        response = await client.chat.completions.create(
            model=settings.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Low temperature for consistent, predictable answers
            max_tokens=800
        )
        
        answer = response.choices[0].message.content
        
        return answer
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        raise

async def stream_openai_response(property_data, knowledge: str, question: str):
    """
    Stream OpenAI response word by word
    """
    try:
        system_prompt = load_system_prompt()
        user_prompt = build_prompt(property_data, knowledge, question)
        
        stream = await client.chat.completions.create(
            model=settings.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800,
            stream=True  # Enable streaming
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        
    except Exception as e:
        print(f"OpenAI streaming error: {e}")
        raise
