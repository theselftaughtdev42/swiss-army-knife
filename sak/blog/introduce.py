import typer
from typing_extensions import Annotated
from pathlib import Path
from openai import OpenAI
from rich import print
import json
import pyperclip

EXCERPT_GENERATOR_CONTENT = """
You are a skilled content summariser specialising in technical blog posts. Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your task is to craft **three distinct one-paragraph excerpts** that effectively introduce the article's main ideas, setting the stage for readers and sparking their interest to continue reading.
Be concise and casual.
Refer to the reader in the second person (you).
Do not refer to the title of the article.
Use UK spelling and grammar.

**Respond ONLY with a JSON array of strings, formatted as follows:**
[
    "First excerpt",
    "Second excerpt",
    "Third excerpt"
]
**Do not include any additional commentary or formatting outside of the JSON array.**
"""

app = typer.Typer()


@app.command()
def introduce(
    filepath: Annotated[
        Path,
        typer.Argument(
            help="The filepath of the blog post being introduced (generate an excerpt)."
        ),
    ],
):
    """
    Send a blog post to ChatGPT to generate an introduction.
    """
    if not filepath.exists():
        print(f"[bold red]File not found:[/bold red] {filepath}")
        raise typer.Exit(code=1)

    user_content = filepath.open().read()
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXCERPT_GENERATOR_CONTENT},
            {
                "role": "user",
                "content": f"Introduce this article: ```{user_content}```",
            },
        ],
    )

    try:
        excerpts = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Response was not in JSON format...")
        raise typer.Abort()

    for i, excerpt in enumerate(excerpts, start=1):
        print(f"[bold underline dark_orange]Excerpt {i}[/]\n{excerpt}\n")

    selection = int(
        typer.prompt("Which except would you like to copy to your clipboard?")
    )

    pyperclip.copy(excerpts[selection - 1])
