# src/modules/product/scraping
from playwright.async_api import async_playwright
from openai import OpenAI
from core.config import settings
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import random
import asyncio


client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def scrape_and_extract(url: str, base_url: str, timeout=60) -> dict:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=settings.USER_AGENT)

            page = await context.new_page()

            await page.goto(url, timeout=timeout*1000)

            await asyncio.sleep(random.uniform(3, 10))

            content = await page.content()

            await browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        body = soup.body
        page_text = body.get_text(separator='\n', strip=True)


        image_tags = body.find_all('img', src=True)
        images = []
        for img in image_tags:
            src = img['src']
            if not src.startswith("data:"):
                images.append(urljoin(base_url, src))

        images = list(dict.fromkeys(images))[:10] 

    except Exception as e:
        raise ValueError(f"Failed to fetch URL content: {e}")

    prompt = f"""
        Given the HTML content extracted from the body of a webpage, carefully extract the information from the specified tags provided below:

        1. **Product title:** Clearly identify the main title or name of the product.
        2. **Product description:** Provide a detailed description of the product.
        3. **AI-generated social media content:** Write a catchy and engaging social media caption or content based on the product details, suitable for platforms like Instagram. 
        Ensure the content is concise and does not exceed 3000 characters.

        Return your response strictly in JSON format. Here is an example of the expected response format:

        {{
            "title": "Men's Speedcat Leather Sneakers",
            "description": "Classic sneakers with premium leather upper for style and durability.",
            "ai_content": "Step up your sneaker game with Puma's iconic Speedcat Leather Sneakers! 🏁👟 Style meets comfort for everyday adventures. #Puma #Speedcat #SneakerLove",
        }}

        Now extract details from the following webpage content:
        {page_text[:25000]}
    """

    completion = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in programming, specifically skilled in parsing HTML tags and converting data into structured JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1000,
        response_format={"type": "json_object"}
    )

    try:
        ai_result = json.loads(completion.choices[0].message.content)
        
    except json.JSONDecodeError as e:
        print("Raw AI Response:", completion.choices[0].message.content)
        raise ValueError("Failed to parse AI response as JSON") from e
    
    ai_result["media_urls"] = images
    print("AI JSON Parsed Result:", ai_result)
    return ai_result

