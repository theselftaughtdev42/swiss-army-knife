import typer
from typing_extensions import Annotated
from pathlib import Path
from openai import OpenAI
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.config import DEFAULT_AI_MODEL
from ..utils.helpers import validate_model


POST_REVIEWER_CONTENT = """
You are a skilled, concise proofreader specialising in technical blog posts. Articles provided within triple backticks are in markdown format (for 'Material for MKDocs') and may include front matter you can ignore.

Your tasks for each article:
1. **Correctness:** Rate spelling/grammar accuracy (UK English).
2. **Clarity:** Rate how clearly complex ideas are explained.
3. **Accuracy:** Verify technical accuracy (facts, code snippets).
4. **Structure:** Check for logical flow, clear headings, smooth transitions.
5. **Consistency:** Ensure consistent tone, terminology, and formatting.
6. **Readability:** Identify any overly complex sentences; suggest lists where helpful.
7. **Story:** Check if any 'setup, conflict, resolution' structure would enhance flow.

Rate each task out of 5.

**Only comment on tasks rated below 5/5 if you identify a significant improvement. Minor feedback or comments should be omitted.**
For example, respond with: 
`Correctness: 5/5\nClarity: 5/5`
"""


app = typer.Typer()


@app.command()
def review(
    filepath: Annotated[
        Path, typer.Argument(help="The filepath of the blog post being reviewed.")
    ],
    model: Annotated[
        str, typer.Option(help="The model you wish to use.")
    ] = DEFAULT_AI_MODEL,
):
    """
    Send a blog post to ChatGPT for review.
    """
    if not filepath.exists():
        print(f"[bold red]File not found:[/bold red] {filepath}")
        raise typer.Exit(code=1)

    validate_model(model)

    user_content = filepath.open().read()
    client = OpenAI()

    with Progress(
        SpinnerColumn(style="purple3"),
        TextColumn("[bold purple3]Reviewing blog post..."),
        transient=True,
    ) as progress:
        progress.add_task("")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": POST_REVIEWER_CONTENT},
                {
                    "role": "user",
                    "content": f"Analyse this article: ```{user_content}```",
                },
            ],
        )

    print(completion.choices[0].message.content)
