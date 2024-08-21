

jacket_data = {
    "product_name": "Winter Parka",
    "current_price": 129.99,
    "cost": 50.00,
    "inventory": 500,
    "season": "Winter",
    "competitor_prices": [119.99, 134.99, 129.99],
    "last_month_sales": 300,
    "customer_rating": 4.5
}



prompt = f"""
Given the following data for Carry Bag, suggest an optimal price:

Product Name: {jacket_data['product_name']}
Current Price: ${jacket_data['current_price']}
Cost: ${jacket_data['cost']}
Inventory: {jacket_data['inventory']} units
Season: {jacket_data['season']}
Competitor Prices: {', '.join(['$' + str(price) for price in jacket_data['competitor_prices']])}
Last Month's Sales: {jacket_data['last_month_sales']} units
Customer Rating: {jacket_data['customer_rating']}/5

Consider factors such as profit margin, competitive pricing, demand, and seasonality. 
Provide a suggested price and a brief explanation for the recommendation. 
Return your response in the following JSON format:
    {{
        "suggested_price": float,
        "explanation": string,
        "factors_considered": [string],
        "confidence_score": float
    }}
"""

print(prompt)