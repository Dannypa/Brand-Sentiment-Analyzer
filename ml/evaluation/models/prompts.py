DEFAULT_SYSTEM_PROMPT = """
You will receive a JSON array of objects. Each object has these fields:
- "title": string — the video title,
- "brand": string — the brand to evaluate,
- "comment": string — the YouTube comment text.

Task: For each object, produce the sentiment **of the comment toward the specified brand** as a single numeric value on the continuous scale **-1.00 to 1.00** (inclusive), where:
- -1.00 = very negative toward the brand,
-  0.00 = neutral or no detectable sentiment toward the brand,
-  1.00 = very positive toward the brand.

Guidelines:
1. Use only the information in "title", "brand", and "comment". Use the title for context if the comment is ambiguous.
2. If the comment mentions the brand implicitly (e.g., "this product", "their service") and the context clearly links it to the brand, infer sentiment toward the brand.
3. If the comment is unrelated to the brand or contains no opinion about the brand, return 0.00.
4. Handle negation, sarcasm, emojis, comparisons, and mixed sentiment if possible. 
5. Return a JSON array of objects in the same order as input. **Each output object must contain exactly one field: "sentiment"** with a numeric value formatted as a decimal with two digits after the decimal point (e.g., 0.00, -0.50, 1.00).
6. If the language is not English, set score = 0.00.
7. Do not include any additional keys, metadata, explanations, or text. Output must be valid JSON only.

Example input:
[
  {"title":"Unboxing the new AlphaPhone","brand":"AlphaCorp","comment":"I love this! AlphaCorp nailed it 😊"},
  {"title":"AlphaPhone teardown","brand":"AlphaCorp","comment":"Terrible battery life — wasted my money."},
  {"title":"Tech news roundup","brand":"AlphaCorp","comment":"The editing of the video is great!"},
  {"title":"Is the AlphaPhone worth it?","brand":"AlphaCorp","comment":"Design is great, but their support is awful."}
]

Example output:
[
  {"sentiment": 0.90},
  {"sentiment": -0.95},
  {"sentiment": 0.00},
  {"sentiment": -0.10}
]
"""

SAMPLE_JSON = """
[
{"brand":"nike","title":"I Tested The World's First POWERED Shoes (They're Insane)","comment":"There's a fashion company in brazil (Insider Store, currently #1 in online sales) specialised in making \"tech shirts\" that are designed to be smart and also sustainable friendly as possible. They've been around for almost a decade, so this is not \"the first time ever performance\" clothing is done. This is just one example, so there might be more companies similarly around the world."},
{"brand":"nike","title":"I Tested The World's First POWERED Shoes (They're Insane)","comment":"Americans will not sleep until they figure out how to stop walking alltogether"},
{"brand":"nike","title":"I Tested The World's First POWERED Shoes (They're Insane)","comment":"Nice to see a company that still employs an R&D department"},

{"brand":"nike","title":"I Tested The World's First POWERED Shoes (They're Insane)","comment":"interesting but these are made for the top 2% of people. nobody can afford this stuff, and because if that I lose just about all interest in any of this. you don\u2019t even need to go into pricing, we know."}
]
"""

SHORTENED_PROMPT = """
Task: For each object, produce the sentiment **of the comment toward the specified brand** as a single numeric value on the continuous scale **-1.00 to 1.00** (inclusive), where:
- -1.00 = very negative toward the brand,
-  0.00 = neutral or no detectable sentiment toward the brand,
-  1.00 = very positive toward the brand.
Return an array of json objects, each with a single field "sentiment". Ensure the order is the same as in input.
"""
